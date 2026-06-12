import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ..models import Customer, CustomerProfile, CampaignAudience
from typing import Any

logger = logging.getLogger(__name__)

ALLOWED_CUSTOMER_FIELDS = {"city", "signup_date", "name"}
ALLOWED_PROFILE_FIELDS = {
    "total_orders",
    "total_spend",
    "average_order_value",
    "days_since_last_purchase",
    "purchase_frequency",
    "customer_segment",
}


class AudienceService:
    def build_query(self, filters: list[dict]):
        """Build a SQLAlchemy query from a list of filter dicts."""
        query = (
            select(Customer)
            .join(CustomerProfile, CustomerProfile.customer_id == Customer.id)
        )

        conditions = []
        for f in filters:
            field_name = f["field"]
            operator = f["operator"]
            value = f["value"]

            if field_name in ALLOWED_PROFILE_FIELDS:
                col = getattr(CustomerProfile, field_name)
            elif field_name in ALLOWED_CUSTOMER_FIELDS:
                col = getattr(Customer, field_name)
            else:
                raise ValueError(f"Invalid filter field: {field_name}")

            if operator == ">":
                conditions.append(col > value)
            elif operator == "<":
                conditions.append(col < value)
            elif operator == ">=":
                conditions.append(col >= value)
            elif operator == "<=":
                conditions.append(col <= value)
            elif operator == "=":
                conditions.append(col == value)
            elif operator == "!=":
                conditions.append(col != value)
            else:
                raise ValueError(f"Invalid operator: {operator}")

        if conditions:
            query = query.where(and_(*conditions))

        return query

    async def preview_audience(
        self, filters: list[dict], db: AsyncSession
    ) -> dict[str, Any]:
        """Return audience size and 10-row sample."""
        query = self.build_query(filters)

        # Count
        from sqlalchemy import func, select as sa_select
        count_q = sa_select(func.count()).select_from(query.subquery())
        count_res = await db.execute(count_q)
        total = count_res.scalar_one()

        # Sample
        sample_q = query.limit(10)
        sample_res = await db.execute(sample_q)
        sample = []
        for row in sample_res.scalars().all():
            sample.append(
                {
                    "id": row.id,
                    "name": row.name,
                    "email": row.email,
                    "city": row.city,
                    "phone": row.phone,
                }
            )

        return {"audience_size": int(total), "sample": sample}

    async def build_audience(
        self, campaign_id: int, filters: list[dict], db: AsyncSession
    ) -> int:
        """Insert matching customers into campaign_audience and return count."""
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from sqlalchemy import update

        query = self.build_query(filters)
        result = await db.execute(query)
        customers = result.scalars().all()

        # Clear existing audience for this campaign
        from sqlalchemy import delete
        await db.execute(
            delete(CampaignAudience).where(CampaignAudience.campaign_id == campaign_id)
        )

        # Insert new audience
        if customers:
            audience_records = [
                {"campaign_id": campaign_id, "customer_id": c.id} for c in customers
            ]
            await db.execute(
                pg_insert(CampaignAudience)
                .values(audience_records)
                .on_conflict_do_nothing()
            )

        # Update campaign audience_size
        from ..models import Campaign
        await db.execute(
            update(Campaign)
            .where(Campaign.id == campaign_id)
            .values(audience_size=len(customers))
        )

        return len(customers)


audience_service = AudienceService()
