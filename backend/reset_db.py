"""
reset_db.py — Wipes ALL data from Supabase and resets auto-increment sequences.
Run from the backend/ directory:  python reset_db.py
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    print("❌  DATABASE_URL not found in .env")
    sys.exit(1)

# Ensure asyncpg driver
if DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Tables in correct deletion order (children before parents)
TRUNCATE_ORDER = [
    "campaign_conversions",
    "communication_logs",
    "campaign_audience",
    "campaigns",
    "customer_profiles",
    "orders",
    "customers",
]

async def reset():
    print("WARNING: This will permanently delete ALL data in Supabase.")
    confirm = input("Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        print("Aborted.")
        return

    engine = create_async_engine(
        DATABASE_URL,
        connect_args={
            "ssl": "require",
            "server_settings": {"application_name": "xeno_reset"},
            "statement_cache_size": 0,
        },
    )

    async with engine.begin() as conn:
        print("\nTruncating tables...")
        for table in TRUNCATE_ORDER:
            await conn.execute(text(f'TRUNCATE TABLE "{table}" RESTART IDENTITY CASCADE'))
            print(f"   OK  {table}")

    await engine.dispose()
    print("\nDONE. All tables cleared. Supabase is back to a clean initial state.")

if __name__ == "__main__":
    asyncio.run(reset())
