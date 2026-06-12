import asyncio
import random
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from ..database import get_async_session, async_session_maker
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["messages"])


# ─── Schemas ──────────────────────────────────────────────────────────────────

class SendMessageRequest(BaseModel):
    campaign_id: int
    customer_id: int
    channel: str
    message: str
    phone: Optional[str] = None
    email: Optional[str] = None
    subject: Optional[str] = None


# ─── Helper: update communication log status in shared DB ─────────────────────

async def _update_log_status(log_id: int, status: str, **kwargs):
    """Update communication_logs status in the shared database."""
    from sqlalchemy import text
    async with async_session_maker() as session:
        try:
            set_clauses = ["status = :status"]
            params = {"status": status, "log_id": log_id}

            if "delivered_at" in kwargs and kwargs["delivered_at"]:
                set_clauses.append("delivered_at = :delivered_at")
                params["delivered_at"] = kwargs["delivered_at"]
            if "opened_at" in kwargs and kwargs["opened_at"]:
                set_clauses.append("opened_at = :opened_at")
                params["opened_at"] = kwargs["opened_at"]
            if "clicked_at" in kwargs and kwargs["clicked_at"]:
                set_clauses.append("clicked_at = :clicked_at")
                params["clicked_at"] = kwargs["clicked_at"]
            if "failed_at" in kwargs and kwargs["failed_at"]:
                set_clauses.append("failed_at = :failed_at")
                params["failed_at"] = kwargs["failed_at"]
            if "error_message" in kwargs and kwargs["error_message"]:
                set_clauses.append("error_message = :error_message")
                params["error_message"] = kwargs["error_message"]

            sql = text(f"UPDATE communication_logs SET {', '.join(set_clauses)} WHERE id = :log_id")
            await session.execute(sql, params)
            await session.commit()
        except Exception as e:
            logger.error(f"Failed to update log {log_id} status to {status}: {e}")


async def _notify_backend(campaign_id: int, customer_id: int, log_id: int, event: str, ts: datetime):
    """Send webhook callback to main backend."""
    payload = {
        "campaign_id": campaign_id,
        "customer_id": customer_id,
        "communication_log_id": log_id,
        "event": event,
        "timestamp": ts.isoformat(),
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{settings.MAIN_BACKEND_URL}/webhook/callback",
                json=payload,
            )
            response.raise_for_status()
    except Exception as e:
        logger.warning(f"Callback to backend failed for log {log_id}, event {event}: {e}")


# ─── State Machine Simulation ──────────────────────────────────────────────────

async def simulate_message_lifecycle(
    log_id: int, campaign_id: int, customer_id: int
):
    """Simulate realistic message delivery lifecycle with probabilities."""
    try:
        # Delivery delay: 1-5 seconds
        await asyncio.sleep(random.uniform(1, 5))

        # 10% chance of failure at delivery
        if random.random() < 0.10:
            now = datetime.utcnow()
            await _update_log_status(log_id, "failed", failed_at=now, error_message="Delivery failed: network error")
            await _notify_backend(campaign_id, customer_id, log_id, "failed", now)
            return

        # Delivered
        delivered_at = datetime.utcnow()
        await _update_log_status(log_id, "delivered", delivered_at=delivered_at)
        await _notify_backend(campaign_id, customer_id, log_id, "delivered", delivered_at)

        # Open delay: 5-30 seconds, 70% open rate
        await asyncio.sleep(random.uniform(5, 30))
        if random.random() > 0.30:  # 70% open
            opened_at = datetime.utcnow()
            await _update_log_status(log_id, "opened", opened_at=opened_at)
            await _notify_backend(campaign_id, customer_id, log_id, "opened", opened_at)

            # Click delay: 1-10 seconds, 50% of opened click
            await asyncio.sleep(random.uniform(1, 10))
            if random.random() > 0.50:
                clicked_at = datetime.utcnow()
                await _update_log_status(log_id, "clicked", clicked_at=clicked_at)
                await _notify_backend(campaign_id, customer_id, log_id, "clicked", clicked_at)

    except Exception as e:
        logger.error(f"Lifecycle simulation error for log {log_id}: {e}")


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/send")
async def send_message(
    body: SendMessageRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    """Accept a message and simulate sending it through the channel."""
    # Insert into communication_logs (using raw SQL to write to shared table)
    from sqlalchemy import text

    now = datetime.utcnow()
    insert_sql = text("""
        INSERT INTO communication_logs
            (campaign_id, customer_id, channel, message, personalized_message, status, sent_at, metadata)
        VALUES
            (:campaign_id, :customer_id, :channel, :message, :message, 'sent', :sent_at, :metadata::jsonb)
        RETURNING id
    """)
    result = await session.execute(
        insert_sql,
        {
            "campaign_id": body.campaign_id,
            "customer_id": body.customer_id,
            "channel": body.channel,
            "message": body.message,
            "sent_at": now,
            "metadata": f'{{"subject": "{body.subject or ""}"}}',
        },
    )
    log_id = result.scalar_one()
    await session.commit()

    # Schedule lifecycle simulation in background
    background_tasks.add_task(
        simulate_message_lifecycle, log_id, body.campaign_id, body.customer_id
    )

    return {
        "success": True,
        "data": {"message_id": log_id, "status": "sent", "timestamp": now.isoformat()},
        "message": "Message sent",
    }


@router.get("/messages/{message_id}/status")
async def get_message_status(
    message_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Get current status and timeline of a message."""
    from sqlalchemy import text

    result = await session.execute(
        text("SELECT id, status, channel, sent_at, delivered_at, opened_at, clicked_at, failed_at, error_message FROM communication_logs WHERE id = :id"),
        {"id": message_id},
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Message not found")

    def fmt(dt):
        return dt.isoformat() if dt else None

    return {
        "success": True,
        "data": {
            "id": row[0],
            "status": row[1],
            "channel": row[2],
            "timeline": {
                "sent_at": fmt(row[3]),
                "delivered_at": fmt(row[4]),
                "opened_at": fmt(row[5]),
                "clicked_at": fmt(row[6]),
                "failed_at": fmt(row[7]),
            },
            "error_message": row[8],
        },
        "message": "OK",
    }


@router.get("/health")
async def health():
    return {"success": True, "data": {"status": "ok"}, "message": "Channel service running"}
