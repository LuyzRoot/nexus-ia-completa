"""
Alembic env.py (ajustado para fallback SQLite dev.db)
Este env.py tenta usar, por ordem:
 1) app.config.settings.settings.DATABASE_URL (se o módulo existir)
 2) variável de ambiente DATABASE_URL
 3) fallback: sqlite:///dev.db

Ele também tenta importar metadados de modelos de `app.models` e, se não existir, de `models`.
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

# Determine DATABASE_URL: try project settings, then env var, then fallback to sqlite dev.db
database_url = None
try:
    # Try to import project settings (common layout: app.config.settings)
    from app.config.settings import settings as project_settings
    database_url = getattr(project_settings, "DATABASE_URL", None)
except Exception:
    # ignore import errors - project might not have that path
    database_url = os.environ.get("DATABASE_URL")

if not database_url:
    database_url = os.environ.get("DATABASE_URL", "sqlite:///dev.db")

# Ensure sqlalchemy.url is set (alembic.ini has a default but we override for clarity)
config.set_main_option("sqlalchemy.url", database_url)

# Import models metadata: try app.models then models
try:
    import app.models as models  # type: ignore
except Exception:
    try:
        import models  # type: ignore
    except Exception:
        models = None

if models is None:
    target_metadata = None
else:
    target_metadata = getattr(models, "Base", None)


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
