"""
Alembic env.py template.

If you use Alembic, copy this file to <repo-root>/alembic/env.py and adapt paths if needed.
The template expects your ORM Base to be importable as `from app.database import Base`
and reads DB URL from app.config.settings.DATABASE_URL.

Notes:
- For autogenerate to work, your models must be importable so SQLAlchemy metadata includes tables.
- In some projects you might import app.models before Base to ensure all models are registered.
"""
from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# this assumes alembic.ini is in repo root and alembic package is used from there
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# import settings and models
from app.config.settings import settings
# Ensure models are imported so metadata is populated (adjust if your models live elsewhere)
import app.models as models  # noqa: F401

target_metadata = models.Base.metadata

# Set SQLALCHEMY URL from settings (overrides alembic.ini)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()