# Phase 3 Summary

What was built:
- `POST /intelligence/generate-profiles`: computes aggregations from `orders` and upserts into `customer_profiles`.
- `GET /intelligence/profiles`: paginated list with filters (segment, min_spend, max_days_inactive).
- `GET /intelligence/profiles/{customer_id}`: single profile with recent orders.
- `GET /intelligence/segments`: distribution counts by segment.
- `GET /intelligence/summary`: basic business summary and top spenders.

Notes:
- Uses a raw SQL upsert matching the implementation brief for accurate aggregation logic.
- `generate-profiles` updates `customer_profiles` in-place; ensure Alembic migrations created the table.

Next steps:
- Add unit tests for each endpoint.
- Add pagination limits and caching for heavy queries.
