import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..dependencies import get_async_session
from ..models import Customer, CustomerProfile, CampaignAudience
from ..schemas import AudiencePreviewRequest, AudienceBuildRequest
from ..services.audience_service import audience_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/audience", tags=["audience"])


@router.post("/preview")
async def preview_audience(
    body: AudiencePreviewRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Preview audience size and sample from filters. Does not save anything."""
    try:
        result = await audience_service.preview_audience(
            [f.model_dump() for f in body.filters], session
        )
        return {"success": True, "data": result, "message": "OK"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audience preview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/build")
async def build_audience(
    body: AudienceBuildRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """Build and store audience for a campaign from filters."""
    try:
        count = await audience_service.build_audience(
            body.campaign_id, [f.model_dump() for f in body.filters], session
        )
        await session.commit()
        return {
            "success": True,
            "data": {"audience_size": count, "campaign_id": body.campaign_id},
            "message": f"Audience built: {count} customers",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Audience build error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/campaign/{campaign_id}")
async def get_campaign_audience(
    campaign_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_async_session),
):
    """Get paginated audience for a campaign with customer details."""
    # Total count
    count_q = select(func.count()).where(CampaignAudience.campaign_id == campaign_id)
    total_res = await session.execute(count_q)
    total = total_res.scalar_one()

    # Fetch with customer details
    stmt = (
        select(Customer, CustomerProfile)
        .join(CampaignAudience, CampaignAudience.customer_id == Customer.id)
        .outerjoin(CustomerProfile, CustomerProfile.customer_id == Customer.id)
        .where(CampaignAudience.campaign_id == campaign_id)
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    res = await session.execute(stmt)
    rows = res.all()

    items = []
    for customer, profile in rows:
        item = {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "phone": customer.phone,
            "city": customer.city,
        }
        if profile:
            item["segment"] = profile.customer_segment
            item["total_spend"] = float(profile.total_spend or 0)
            item["days_since_last_purchase"] = profile.days_since_last_purchase
        items.append(item)

    return {
        "success": True,
        "data": {"total": int(total), "page": page, "per_page": per_page, "items": items},
        "message": "OK",
    }
