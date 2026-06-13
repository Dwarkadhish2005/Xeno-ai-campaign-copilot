from sqlalchemy import create_engine, text
# from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

# Load environment variables from .env
load_dotenv()

# Fetch variables
USER = os.getenv("user")
PASSWORD = quote_plus(os.getenv("password", ""))  # URL-encode special chars like @
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
# If using Transaction Pooler or Session Pooler, we want to ensure we disable SQLAlchemy client side pooling -
# https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
# engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Test the connection
try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        print("Connection successful!")
        print(f"PostgreSQL version: {result.fetchone()[0]}")
except Exception as e:
    print(f"Failed to connect: {e}")
