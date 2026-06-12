from __future__ import with_statement
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from alembic import context

import os
import sys
from pathlib import Path

# ensure backend package dir is on path so `import app` works
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Load DATABASE_URL from environment or backend/.env if present
repo_root = Path(os.path.dirname(os.path.dirname(__file__))).resolve()
env_file = repo_root / ".env"
if not os.environ.get("DATABASE_URL") and env_file.exists():
    for line in env_file.read_text().splitlines():
        if not line or line.strip().startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and v:
            os.environ.setdefault(k, v)

if os.environ.get("DATABASE_URL"):
    try:
        config.set_main_option("sqlalchemy.url", os.environ.get("DATABASE_URL"))
    except Exception:
        pass

from app.base import Base

# Interpret the config file for Python logging (tolerant to minimal ini)
try:
    fileConfig(config.config_file_name)
except Exception:
    pass

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    from sqlalchemy import create_engine

    connectable = create_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
