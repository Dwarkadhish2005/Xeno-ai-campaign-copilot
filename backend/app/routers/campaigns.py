import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime

from ..dependencies import get_async_session
from ..models import Campaign
from ..schemas import CampaignCreate, CampaignOut, CampaignPlan
from ..services.groq_service import groq_service
from ..services.audience_service import audience_service
from ..services.executor_service import execute_campaign
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

# Valid status transitions
VALID_TRANSITIONS = {
    "draft": ["ready", "failed"],
    "ready": ["approved", "draft"],
    "approved": ["running", "failed"],
    "running": ["completed", "failed"],
    "completed": [],
    "failed": ["draft"],
}


# ─── Phase 4: AI Campaign Planner ─────────────────────────────────────────────

@router.post("/plan")
async def generate_campaign_plan(
    body: dict,
    session: AsyncSession = Depends(get_async_session),
):
    """Generate an AI campaign plan from a business goal. Does NOT save to DB."""
    business_goal = body.get("business_goal", "").strip()
    if not business_goal:
        raise HTTPException(status_code=400, detail="business_goal is required")

    try:
        plan = await groq_service.generate_campaign_plan(business_goal)
        # Validate with Pydantic
        validated = CampaignPlan(**plan)
        return {
            "success": True,
            "data": validated.model_dump(),
            "message": "Campaign plan generated successfully",
        }
    except Exception as e:
        logger.error(f"Failed to generate campaign plan: {e}")
        raise HTTPException(status_code=500, detail=f"AI plan generation failed: {str(e)}")


# ─── Phase 6: Campaign CRUD ────────────────────────────────────────────────────

@router.post("")
async def create_campaign(
    body: CampaignCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Save AI plan as a draft campaign and auto-build audience."""
    campaign = Campaign(
        name=body.name,
        business_goal=body.business_goal,
        audience_name=body.audience_name,
        filters=[f.model_dump() for f in body.filters] if body.filters else None,
        channel=body.channel,
        strategy=body.strategy,
        ai_reasoning=body.ai_reasoning,
        message_template=body.message_template,
        subject_line=body.subject_line,
        status="draft",
    )
    session.add(campaign)
    await session.flush()  # Get the ID

    # Auto-build audience if filters provided
    if body.filters:
        try:
            count = await audience_service.build_audience(
                campaign.id, [f.model_dump() for f in body.filters], session
            )
            logger.info(f"Auto-built audience of {count} for campaign {campaign.id}")
        except Exception as e:
            logger.warning(f"Audience build failed for campaign {campaign.id}: {e}")

    await session.commit()
    await session.refresh(campaign)

    return {
        "success": True,
        "data": CampaignOut.model_validate(campaign).model_dump(),
        "message": f"Campaign '{campaign.name}' created as draft",
    }


@router.get("")
async def list_campaigns(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
):
    """List all campaigns with optional status filter."""
    from sqlalchemy import func

    stmt = select(Campaign).order_by(Campaign.created_at.desc())
    if status:
        stmt = stmt.where(Campaign.status == status)

    count_q = select(func.count()).select_from(stmt.subquery())
    total_res = await session.execute(count_q)
    total = total_res.scalar_one()

    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    res = await session.execute(stmt)
    campaigns = res.scalars().all()

    return {
        "success": True,
        "data": {
            "total": int(total),
            "page": page,
            "per_page": per_page,
            "items": [CampaignOut.model_validate(c).model_dump() for c in campaigns],
        },
        "message": "OK",
    }


@router.get("/{campaign_id}")
async def get_campaign(
    campaign_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Get full campaign details."""
    from ..models import CommunicationLog
    from sqlalchemy import func

    res = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get metrics summary
    metrics_q = await session.execute(
        select(CommunicationLog.status, func.count())
        .where(CommunicationLog.campaign_id == campaign_id)
        .group_by(CommunicationLog.status)
    )
    metrics = {row[0]: int(row[1]) for row in metrics_q.fetchall()}

    data = CampaignOut.model_validate(campaign).model_dump()
    data["metrics"] = metrics
    return {"success": True, "data": data, "message": "OK"}


@router.post("/{campaign_id}/generate-message")
async def generate_message(
    campaign_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Use AI to generate a personalized message template for the campaign."""
    res = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status not in ("draft", "ready"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot generate message for campaign with status '{campaign.status}'",
        )

    try:
        result = await groq_service.generate_message(
            channel=campaign.channel,
            strategy=campaign.strategy or "general marketing",
            audience_name=campaign.audience_name or "customers",
        )
        message = result.get("message", "")
        subject = result.get("subject", "")

        await session.execute(
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(
                message_template=message,
                subject_line=subject if subject else campaign.subject_line,
                status="ready",
                updated_at=datetime.utcnow(),
            )
        )
        await session.commit()

        return {
            "success": True,
            "data": {"message": message, "subject": subject},
            "message": "Message generated and campaign marked as ready",
        }
    except Exception as e:
        logger.error(f"Message generation failed for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Message generation failed: {str(e)}")


@router.post("/{campaign_id}/reset")
async def reset_campaign(
    campaign_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Force-reset a campaign back to 'draft' status.
    Clears communication logs so it can be re-launched cleanly.
    Useful for stuck 'running' campaigns or demo resets.
    """
    from ..models import CommunicationLog
    from sqlalchemy import delete

    res = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status == "draft":
        raise HTTPException(status_code=400, detail="Campaign is already in 'draft' status")

    # Clear existing communication logs
    await session.execute(
        delete(CommunicationLog).where(CommunicationLog.campaign_id == campaign_id)
    )

    # Reset campaign to draft
    await session.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status="draft", updated_at=datetime.utcnow())
    )
    await session.commit()

    logger.info(f"Campaign {campaign_id} reset to 'draft' from '{campaign.status}'")

    return {
        "success": True,
        "data": {"campaign_id": campaign_id, "previous_status": campaign.status},
        "message": f"Campaign reset to draft (was '{campaign.status}'). Communication logs cleared.",
    }


@router.post("/{campaign_id}/approve")
async def approve_campaign(
    campaign_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Approve a ready campaign."""
    res = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "ready":
        raise HTTPException(
            status_code=400,
            detail=f"Campaign must be in 'ready' status to approve. Current: '{campaign.status}'",
        )
    if not campaign.message_template:
        raise HTTPException(status_code=400, detail="Campaign must have a message template to approve")
    if not campaign.audience_size or campaign.audience_size == 0:
        raise HTTPException(status_code=400, detail="Campaign must have an audience to approve")

    await session.execute(
        update(Campaign)
        .where(Campaign.id == campaign_id)
        .values(status="approved", updated_at=datetime.utcnow())
    )
    await session.commit()

    return {"success": True, "data": None, "message": "Campaign approved"}


@router.post("/{campaign_id}/launch")
async def launch_campaign(
    campaign_id: int,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    """Launch an approved campaign. Execution runs in the background."""
    res = await session.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = res.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "approved":
        raise HTTPException(
            status_code=400,
            detail=f"Campaign must be 'approved' to launch. Current: '{campaign.status}'",
        )

    # Schedule background execution
    from ..database import async_session_maker

    async def _run():
        async with async_session_maker() as bg_session:
            await execute_campaign(campaign_id, bg_session)

    background_tasks.add_task(_run)

    # Build demo-aware response metadata
    demo_info = None
    if settings.DEMO_MODE:
        audience_size = campaign.audience_size or 0
        dispatched = min(audience_size, settings.DEMO_LIMIT)
        demo_info = {
            "demo_mode": True,
            "full_audience_size": audience_size,
            "messages_simulated": dispatched,
            "demo_limit": settings.DEMO_LIMIT,
        }
        logger.info(
            f"[DEMO MODE] Campaign {campaign_id} launched — "
            f"Audience: {audience_size}, Messages Simulated: {dispatched}"
        )

    return {
        "success": True,
        "data": {"campaign_id": campaign_id, **(demo_info or {})},
        "message": (
            f"[DEMO MODE] Campaign launch initiated — "
            f"{demo_info['messages_simulated']} of {demo_info['full_audience_size']} messages simulated."
            if settings.DEMO_MODE
            else "Campaign launch initiated. Execution running in background."
        ),
    }
