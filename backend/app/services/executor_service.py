import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from ..models import Campaign, CampaignAudience, Customer, CustomerProfile, CommunicationLog
from .channel_client import channel_client

logger = logging.getLogger(__name__)


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

        sent_count = 0
        failed_count = 0
        batch_size = 100

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
                    logger.error(f"Failed to send message: {res}")
                else:
                    sent_count += 1

        # Determine final status
        total = sent_count + failed_count
        fail_rate = failed_count / total if total > 0 else 0
        final_status = "failed" if fail_rate > 0.5 else "completed"

        await db.execute(
            update(Campaign).where(Campaign.id == campaign_id).values(status=final_status)
        )
        await db.commit()
        logger.info(
            f"Campaign {campaign_id} {final_status}: {sent_count} sent, {failed_count} failed"
        )

    except Exception as e:
        logger.error(f"Campaign {campaign_id} execution error: {e}")
        try:
            await db.execute(
                update(Campaign).where(Campaign.id == campaign_id).values(status="failed")
            )
            await db.commit()
        except Exception:
            pass


async def _send_to_customer(
    campaign: Campaign,
    customer: Customer,
    profile: CustomerProfile | None,
    db: AsyncSession,
) -> None:
    """Personalize and send message to one customer."""
    days = str(profile.days_since_last_purchase) if profile and profile.days_since_last_purchase else "a while"
    template = campaign.message_template or ""

    personalized = (
        template.replace("{name}", customer.name or "Valued Customer")
        .replace("{days_since_last_purchase}", days)
        .replace("{city}", customer.city or "your city")
    )

    status = "sent"
    error_msg = None
    metadata = {}

    try:
        response = await channel_client.send_message(
            campaign_id=campaign.id,
            customer_id=customer.id,
            channel=campaign.channel,
            message=personalized,
            phone=customer.phone,
            email=customer.email,
            subject=campaign.subject_line,
        )
        metadata = {"channel_message_id": response.get("message_id")}
    except Exception as e:
        status = "failed"
        error_msg = str(e)
        logger.warning(f"Channel send failed for customer {customer.id}: {e}")

    # Log the communication — use a fresh session for logging to avoid conflicts
    log = CommunicationLog(
        campaign_id=campaign.id,
        customer_id=customer.id,
        channel=campaign.channel,
        message=template,
        personalized_message=personalized,
        status=status,
        error_message=error_msg,
        metadata_json=metadata,
    )
    db.add(log)
    await db.flush()

    if status == "failed":
        raise Exception(f"Send failed for customer {customer.id}: {error_msg}")
