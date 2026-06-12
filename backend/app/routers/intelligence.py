from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from typing import Optional
from ..dependencies import get_async_session
from ..models import Customer, Order, CustomerProfile

router = APIRouter(prefix="/intelligence", tags=["intelligence"])


@router.post("/generate-profiles")
async def generate_profiles(session: AsyncSession = Depends(get_async_session)):
    # Raw SQL upsert as specified in the implementation brief
    sql = text("""
    INSERT INTO customer_profiles (customer_id, total_orders, total_spend, average_order_value, last_purchase_date, days_since_last_purchase, purchase_frequency, customer_segment, created_at, updated_at)
    SELECT 
        c.id,
        COUNT(o.id) AS total_orders,
        COALESCE(SUM(o.amount), 0) AS total_spend,
        COALESCE(AVG(o.amount), 0) AS average_order_value,
        MAX(o.order_date) AS last_purchase_date,
        EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date))::INTEGER AS days_since_last_purchase,
        CASE 
            WHEN EXTRACT(MONTH FROM AGE(CURRENT_TIMESTAMP, c.signup_date)) > 0 
            THEN (COUNT(o.id)::DECIMAL / NULLIF(EXTRACT(MONTH FROM AGE(CURRENT_TIMESTAMP, c.signup_date)), 0))::DECIMAL
            ELSE COUNT(o.id)::DECIMAL
        END AS purchase_frequency,
        CASE
            WHEN COALESCE(SUM(o.amount), 0) > 5000 AND EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date)) < 30 AND COUNT(o.id) > 10 THEN 'vip'
            WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date)) > 60 THEN 'dormant'
            WHEN COUNT(o.id) > 5 AND COALESCE(AVG(o.amount), 0) > 100 THEN 'frequent'
            WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - c.signup_date) <= 30 THEN 'new'
            WHEN EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.order_date)) > 30 AND COUNT(o.id) > 3 THEN 'at_risk'
            ELSE 'regular'
        END AS customer_segment,
        CURRENT_TIMESTAMP,
        CURRENT_TIMESTAMP
    FROM customers c
    LEFT JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.signup_date
    ON CONFLICT (customer_id) DO UPDATE SET
        total_orders = EXCLUDED.total_orders,
        total_spend = EXCLUDED.total_spend,
        average_order_value = EXCLUDED.average_order_value,
        last_purchase_date = EXCLUDED.last_purchase_date,
        days_since_last_purchase = EXCLUDED.days_since_last_purchase,
        purchase_frequency = EXCLUDED.purchase_frequency,
        customer_segment = EXCLUDED.customer_segment,
        updated_at = CURRENT_TIMESTAMP;
    """)

    await session.execute(sql)
    return {"success": True, "data": None, "message": "Profiles generated/updated"}


@router.get("/profiles")
async def list_profiles(segment: Optional[str] = Query(None), min_spend: Optional[float] = Query(None), max_days_inactive: Optional[int] = Query(None), page: int = 1, per_page: int = 50, session: AsyncSession = Depends(get_async_session)):
    stmt = select(CustomerProfile).join(Customer)
    if segment:
        stmt = stmt.where(CustomerProfile.customer_segment == segment)
    if min_spend is not None:
        stmt = stmt.where(CustomerProfile.total_spend >= min_spend)
    if max_days_inactive is not None:
        stmt = stmt.where(CustomerProfile.days_since_last_purchase <= max_days_inactive)

    total_q = await session.execute(select(func.count()).select_from(stmt.subquery()))
    total = total_q.scalar_one()

    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    res = await session.execute(stmt)
    profiles = [r[0].__dict__ for r in res.all()]
    # remove SQLAlchemy state keys
    for p in profiles:
        p.pop("_sa_instance_state", None)

    return {"success": True, "data": {"total": total, "page": page, "per_page": per_page, "items": profiles}, "message": "OK"}


@router.get("/profiles/{customer_id}")
async def get_profile(customer_id: int, session: AsyncSession = Depends(get_async_session)):
    stmt = select(CustomerProfile).where(CustomerProfile.customer_id == customer_id)
    res = await session.execute(stmt)
    profile = res.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # fetch orders
    orders_q = await session.execute(select(Order).where(Order.customer_id == customer_id).order_by(Order.order_date.desc()).limit(100))
    orders = [o._asdict() if hasattr(o, '_asdict') else o.__dict__ for o in orders_q.scalars().all()]
    for o in orders:
        o.pop("_sa_instance_state", None)

    data = profile.__dict__.copy()
    data.pop("_sa_instance_state", None)
    data["orders"] = orders
    return {"success": True, "data": data, "message": "OK"}


@router.get("/segments")
async def segments(session: AsyncSession = Depends(get_async_session)):
    stmt = select(CustomerProfile.customer_segment, func.count()).group_by(CustomerProfile.customer_segment)
    res = await session.execute(stmt)
    rows = res.fetchall()
    data = {r[0] if r[0] is not None else 'unknown': int(r[1]) for r in rows}
    return {"success": True, "data": data, "message": "OK"}


@router.get("/summary")
async def summary(session: AsyncSession = Depends(get_async_session)):
    total_customers_q = await session.execute(select(func.count()).select_from(Customer))
    total_customers = total_customers_q.scalar_one()

    total_orders_q = await session.execute(select(func.count()).select_from(Order))
    total_orders = total_orders_q.scalar_one()

    total_revenue_q = await session.execute(select(func.coalesce(func.sum(Order.amount), 0)))
    total_revenue = float(total_revenue_q.scalar_one() or 0)

    campaigns_count = 0

    # top spenders
    top_q = await session.execute(select(CustomerProfile.customer_id, CustomerProfile.total_spend).order_by(CustomerProfile.total_spend.desc()).limit(10))
    top = [{"customer_id": int(r[0]), "total_spend": float(r[1] or 0)} for r in top_q.fetchall()]

    data = {
        "total_customers": int(total_customers),
        "total_orders": int(total_orders),
        "total_revenue": total_revenue,
        "total_campaigns": campaigns_count,
        "top_spenders": top,
    }
    return {"success": True, "data": data, "message": "OK"}
