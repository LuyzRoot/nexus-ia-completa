"""
Alembic env.py (gerado a partir do template em database/).
Este arquivo usa o settings.DATABASE_URL do projeto para configurar a conexão.
Certifique-se de que `app.config.settings.settings.DATABASE_URL` está definido no seu .env e carregado pelo app antes de rodar alembic.
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
# Ajuste os imports se a configuração de seu projeto usar caminhos diferentes
from app.config.settings import settings
# Ensure models are imported so metadata is populated
import app.models as models  # noqa: F401

target_metadata = models.Base.metadata

# Override sqlalchemy.url from settings if available
if getattr(settings, "DATABASE_URL", None):
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
