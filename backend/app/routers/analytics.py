import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, text
from datetime import datetime

from ..dependencies import get_async_session
from ..models import Campaign, CommunicationLog, Customer, CustomerProfile
from ..schemas import WebhookCallback

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analytics"])


# ─── Admin: Clear Database ─────────────────────────────────────────────────────

@router.post("/admin/clear-database")
async def clear_database(
    body: dict = None,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Clear all data from the database.
    - mode='campaigns_only'  → deletes campaigns + logs + audience (keeps customers/orders/profiles)
    - mode='all' (default)   → wipes everything (all tables)
    """
    mode = (body or {}).get("mode", "all")

    if mode == "campaigns_only":
        tables = [
            "campaign_conversions",
            "communication_logs",
            "campaign_audience",
            "campaigns",
        ]
    else:
        # Full wipe — children before parents
        tables = [
            "campaign_conversions",
            "communication_logs",
            "campaign_audience",
            "campaigns",
            "customer_profiles",
            "orders",
            "customers",
        ]

    cleared = []
    for table in tables:
        await session.execute(
            text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE')
        )
        cleared.append(table)

    await session.commit()
    logger.info(f"[ADMIN] Database cleared. Mode={mode}. Tables: {cleared}")

    return {
        "success": True,
        "data": {"cleared_tables": cleared, "mode": mode},
        "message": f"Database cleared successfully ({mode} mode). {len(cleared)} tables wiped.",
    }



# ─── Webhook Callback from Channel Service ─────────────────────────────────────

@router.post("/webhook/callback")
async def webhook_callback(
    body: WebhookCallback,
    session: AsyncSession = Depends(get_async_session),
):
    """Receive status updates from the channel service."""
    log_id = body.communication_log_id
    event = body.event
    ts = body.timestamp

    update_vals: dict = {"status": event}
    if event == "delivered":
        update_vals["delivered_at"] = ts
    elif event == "opened":
        update_vals["opened_at"] = ts
    elif event == "clicked":
        update_vals["clicked_at"] = ts
    elif event == "failed":
        update_vals["failed_at"] = ts

    await session.execute(
        update(CommunicationLog).where(CommunicationLog.id == log_id).values(**update_vals)
    )
    await session.commit()

    return {"success": True, "data": None, "message": f"Event '{event}' recorded"}


# ─── Campaign Analytics ─────────────────────────────────────────────────────────

@router.get("/analytics/campaigns/{campaign_id}")
async def get_campaign_analytics(
    campaign_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Full analytics for a single campaign."""
    # Get campaign
    camp_res = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = camp_res.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Aggregate metrics from communication_logs
    metrics_q = await session.execute(
        select(CommunicationLog.status, func.count())
        .where(CommunicationLog.campaign_id == campaign_id)
        .group_by(CommunicationLog.status)
    )
    raw = {row[0]: int(row[1]) for row in metrics_q.fetchall()}

    sent = raw.get("sent", 0) + raw.get("delivered", 0) + raw.get("opened", 0) + raw.get("clicked", 0) + raw.get("failed", 0)
    delivered = raw.get("delivered", 0) + raw.get("opened", 0) + raw.get("clicked", 0)
    opened = raw.get("opened", 0) + raw.get("clicked", 0)
    clicked = raw.get("clicked", 0)
    failed = raw.get("failed", 0)

    def pct(num, den):
        return f"{(num / den * 100):.1f}%" if den > 0 else "0.0%"

    metrics = {
        "sent": sent,
        "delivered": delivered,
        "opened": opened,
        "clicked": clicked,
        "failed": failed,
    }

    funnel = {
        "sent_to_delivered": pct(delivered, sent),
        "delivered_to_opened": pct(opened, delivered),
        "opened_to_clicked": pct(clicked, opened),
        "overall_engagement": pct(clicked, sent),
    }

    return {
        "success": True,
        "data": {
            "campaign_id": campaign_id,
            "name": campaign.name,
            "status": campaign.status,
            "audience_size": campaign.audience_size,
            "channel": campaign.channel,
            "metrics": metrics,
            "funnel": funnel,
        },
        "message": "OK",
    }


@router.get("/analytics/campaigns/{campaign_id}/timeline")
async def get_campaign_timeline(
    campaign_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Time-series data grouped by hour for Recharts."""
    from sqlalchemy import text

    sql = text("""
        SELECT
            DATE_TRUNC('hour', sent_at) AS hour,
            SUM(CASE WHEN status IN ('sent','delivered','opened','clicked') THEN 1 ELSE 0 END) AS sent,
            SUM(CASE WHEN status IN ('delivered','opened','clicked') THEN 1 ELSE 0 END) AS delivered,
            SUM(CASE WHEN status IN ('opened','clicked') THEN 1 ELSE 0 END) AS opened,
            SUM(CASE WHEN status = 'clicked' THEN 1 ELSE 0 END) AS clicked,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
        FROM communication_logs
        WHERE campaign_id = :campaign_id
        GROUP BY DATE_TRUNC('hour', sent_at)
        ORDER BY hour ASC
    """)
    res = await session.execute(sql, {"campaign_id": campaign_id})
    rows = res.fetchall()

    timeline = [
        {
            "hour": row[0].isoformat() if row[0] else None,
            "sent": int(row[1] or 0),
            "delivered": int(row[2] or 0),
            "opened": int(row[3] or 0),
            "clicked": int(row[4] or 0),
            "failed": int(row[5] or 0),
        }
        for row in rows
    ]

    return {"success": True, "data": timeline, "message": "OK"}


@router.get("/analytics/dashboard")
async def get_dashboard(session: AsyncSession = Depends(get_async_session)):
    """Aggregate dashboard stats across all campaigns."""
    # Customer & order totals
    total_customers_res = await session.execute(select(func.count()).select_from(Customer))
    total_customers = int(total_customers_res.scalar_one())

    from ..models import Order
    total_orders_res = await session.execute(select(func.count()).select_from(Order))
    total_orders = int(total_orders_res.scalar_one())

    total_revenue_res = await session.execute(
        select(func.coalesce(func.sum(Order.amount), 0))
    )
    total_revenue = float(total_revenue_res.scalar_one() or 0)

    # Campaign totals
    total_campaigns_res = await session.execute(select(func.count()).select_from(Campaign))
    total_campaigns = int(total_campaigns_res.scalar_one())

    active_campaigns_res = await session.execute(
        select(func.count()).where(Campaign.status.in_(["running", "approved"]))
    )
    active_campaigns = int(active_campaigns_res.scalar_one())

    # Communication metrics
    comm_metrics_res = await session.execute(
        select(CommunicationLog.status, func.count())
        .group_by(CommunicationLog.status)
    )
    comm_raw = {row[0]: int(row[1]) for row in comm_metrics_res.fetchall()}

    total_sent = sum(comm_raw.get(s, 0) for s in ["sent", "delivered", "opened", "clicked", "failed"])
    total_delivered = sum(comm_raw.get(s, 0) for s in ["delivered", "opened", "clicked"])
    total_opened = sum(comm_raw.get(s, 0) for s in ["opened", "clicked"])
    total_clicked = comm_raw.get("clicked", 0)

    # Segment distribution
    seg_res = await session.execute(
        select(CustomerProfile.customer_segment, func.count())
        .group_by(CustomerProfile.customer_segment)
    )
    segments = {(r[0] or "unknown"): int(r[1]) for r in seg_res.fetchall()}

    # Recent campaigns (last 5)
    recent_res = await session.execute(
        select(Campaign).order_by(Campaign.created_at.desc()).limit(5)
    )
    recent = recent_res.scalars().all()
    recent_campaigns = [
        {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "channel": c.channel,
            "audience_size": c.audience_size,
            "created_at": c.created_at.isoformat(),
        }
        for c in recent
    ]

    return {
        "success": True,
        "data": {
            "total_customers": total_customers,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "overall_metrics": {
                "total_sent": total_sent,
                "total_delivered": total_delivered,
                "total_opened": total_opened,
                "total_clicked": total_clicked,
            },
            "segment_distribution": segments,
            "recent_campaigns": recent_campaigns,
        },
        "message": "OK",
    }
