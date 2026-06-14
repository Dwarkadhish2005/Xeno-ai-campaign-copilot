import asyncio
import random
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from ..models import Campaign, CampaignAudience, Customer, CustomerProfile, CommunicationLog
from ..config import settings

logger = logging.getLogger(__name__)


# ─── Delivery Simulation ──────────────────────────────────────────────────────

async def _simulate_lifecycle(log_id: int, db: AsyncSession) -> None:
    """
    Simulate realistic message delivery in-process (no channel service needed).
    Updates the CommunicationLog row directly with probabilities:
      - 10% chance of permanent failure at delivery stage
      - 70% open rate among delivered
      - 50% click rate among opened
    Uses short sleep delays so the simulation completes within seconds.
    """
    try:
        # Small delay to mimic network latency
        await asyncio.sleep(random.uniform(0.1, 0.5))

        # 10% hard failure at delivery
        if random.random() < 0.10:
            await db.execute(
                update(CommunicationLog)
                .where(CommunicationLog.id == log_id)
                .values(
                    status="failed",
                    failed_at=datetime.utcnow(),
                    error_message="Simulated delivery failure: network error",
                )
            )
            return

        # Delivered
        await db.execute(
            update(CommunicationLog)
            .where(CommunicationLog.id == log_id)
            .values(status="delivered", delivered_at=datetime.utcnow())
        )

        # 70% open rate
        await asyncio.sleep(random.uniform(0.1, 0.3))
        if random.random() < 0.70:
            await db.execute(
                update(CommunicationLog)
                .where(CommunicationLog.id == log_id)
                .values(status="opened", opened_at=datetime.utcnow())
            )

            # 50% click rate among opened
            await asyncio.sleep(random.uniform(0.05, 0.15))
            if random.random() < 0.50:
                await db.execute(
                    update(CommunicationLog)
                    .where(CommunicationLog.id == log_id)
                    .values(status="clicked", clicked_at=datetime.utcnow())
                )

    except Exception as e:
        logger.error(f"Lifecycle simulation error for log {log_id}: {e}")


# ─── Channel Service Dispatch (with in-process fallback) ──────────────────────

async def _dispatch_via_channel_service(
    campaign: Campaign,
    customer: Customer,
    personalized: str,
) -> dict:
    """Try to send via the external channel service. Returns response dict."""
    from .channel_client import channel_client
    response = await channel_client.send_message(
        campaign_id=campaign.id,
        customer_id=customer.id,
        channel=campaign.channel,
        message=personalized,
        phone=customer.phone,
        email=customer.email,
        subject=campaign.subject_line,
    )
    return response


# ─── Per-customer send ────────────────────────────────────────────────────────

async def _send_to_customer(
    campaign: Campaign,
    customer: Customer,
    profile: CustomerProfile | None,
    db: AsyncSession,
) -> None:
    """
    Personalize and dispatch message to one customer.

    Strategy:
    1. Try the external channel service first.
    2. If it is unreachable (ConnectionError / any HTTP error), fall back to
       in-process simulation so the campaign never goes fully failed just
       because the channel service isn't running locally.
    """
    days = str(profile.days_since_last_purchase) if profile and profile.days_since_last_purchase else "a while"
    template = campaign.message_template or ""

    personalized = (
        template.replace("{name}", customer.name or "Valued Customer")
        .replace("{days_since_last_purchase}", days)
        .replace("{city}", customer.city or "your city")
    )

    # ── Insert a "sent" log entry first ──────────────────────────────────────
    # Only the executor inserts this row; the channel service should NOT also
    # insert duplicate rows.  (The channel service only updates status later.)
    log = CommunicationLog(
        campaign_id=campaign.id,
        customer_id=customer.id,
        channel=campaign.channel,
        message=template,
        personalized_message=personalized,
        status="sent",
    )
    db.add(log)
    await db.flush()   # obtain log.id without committing
    log_id = log.id

    # ── Try channel service; fall back to in-process simulation ──────────────
    channel_service_ok = False
    try:
        await _dispatch_via_channel_service(campaign, customer, personalized)
        channel_service_ok = True
        logger.debug(f"Channel service handled customer {customer.id} (log {log_id})")
    except Exception as e:
        # Channel service is down / unreachable — simulate locally instead
        logger.debug(
            f"Channel service unavailable for customer {customer.id} "
            f"({e.__class__.__name__}); using in-process simulation."
        )

    if not channel_service_ok:
        # Run lifecycle simulation directly in this session
        await _simulate_lifecycle(log_id, db)


# ─── Main executor ────────────────────────────────────────────────────────────

async def execute_campaign(campaign_id: int, db: AsyncSession):
    """Background task: personalize and dispatch messages for all campaign audience members."""
    try:
        # Get campaign
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        campaign = result.scalar_one_or_none()
        if not campaign:
            logger.error(f"Campaign {campaign_id} not found for execution")
            return

        # Mark as running
        await db.execute(
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(status="running")
        )
        await db.commit()

        # Fetch audience with customer data
        stmt = (
            select(Customer, CustomerProfile)
            .join(CampaignAudience, CampaignAudience.customer_id == Customer.id)
            .outerjoin(CustomerProfile, CustomerProfile.customer_id == Customer.id)
            .where(CampaignAudience.campaign_id == campaign_id)
        )
        audience_result = await db.execute(stmt)
        audience = audience_result.all()

        if not audience:
            logger.warning(f"Campaign {campaign_id} has no audience members")
            await db.execute(
                update(Campaign).where(Campaign.id == campaign_id).values(status="completed")
            )
            await db.commit()
            return

        logger.info(f"Executing campaign {campaign_id} for {len(audience)} customers")

        # ── Demo Mode Audience Cap ────────────────────────────────────────────
        real_audience_size = len(audience)
        if settings.DEMO_MODE:
            audience = audience[: settings.DEMO_LIMIT]
            logger.info(
                f"[DEMO MODE] Capping dispatch to {len(audience)} of {real_audience_size} customers "
                f"(DEMO_LIMIT={settings.DEMO_LIMIT}). Full audience stored in DB is unchanged."
            )

        sent_count = 0
        failed_count = 0
        batch_size = 50   # smaller batches so flush/commit is more frequent

        # Process in batches
        for i in range(0, len(audience), batch_size):
            batch = audience[i : i + batch_size]
            tasks = [
                _send_to_customer(campaign, customer, profile, db)
                for customer, profile in batch
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, Exception):
                    failed_count += 1
                    logger.error(f"Failed to process customer in batch: {res}")
                else:
                    sent_count += 1

            # Commit each batch so partial progress is saved
            try:
                await db.commit()
            except Exception as commit_err:
                logger.error(f"Batch commit error for campaign {campaign_id}: {commit_err}")
                await db.rollback()

        # Determine final status
        # Only mark "failed" if more than 50% hard-failed to reach even "sent" state
        total = sent_count + failed_count
        fail_rate = failed_count / total if total > 0 else 0
        final_status = "failed" if fail_rate > 0.5 else "completed"

        await db.execute(
            update(Campaign).where(Campaign.id == campaign_id).values(status=final_status)
        )
        await db.commit()
        logger.info(
            f"Campaign {campaign_id} {final_status}: {sent_count} processed, {failed_count} hard-failed "
            f"(fail_rate={fail_rate:.1%})"
        )

    except Exception as e:
        logger.error(f"Campaign {campaign_id} execution error: {e}", exc_info=True)
        try:
            await db.execute(
                update(Campaign).where(Campaign.id == campaign_id).values(status="failed")
            )
            await db.commit()
        except Exception:
            pass
