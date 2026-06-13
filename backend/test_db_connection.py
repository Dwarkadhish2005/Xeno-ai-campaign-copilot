import asyncio
from sqlalchemy import text
from app.database import engine

async def main():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("DB connection OK")
    except Exception as e:
        print("DB connection failed:", e)

if __name__ == "__main__":
    asyncio.run(main())
