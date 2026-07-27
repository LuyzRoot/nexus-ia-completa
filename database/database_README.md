# database/ (NEXUS)

Esta pasta contém utilitários para conexão e gerenciamento do banco de dados no NEXUS.

Arquivos principais
- session.py: engine sync, SessionLocal, Base, get_db() (FastAPI dependency)
- async_session.py: async engine (best-effort conversion), AsyncSessionLocal, get_async_db()
- utils.py: helpers para create_all, drop_all, run_raw_sql e dica de Alembic
- alembic_env_template.py: template do env.py do Alembic (copie para `alembic/env.py` se usar Alembic)

Como usar (dev)
1. Configurar DB URL em `.env` (p.ex. DATABASE_URL=postgresql://user:pass@host:5432/dbname)
2. Em desenvolvimento você pode inicializar tabelas automaticamente (não recomendado em produção):
   from app.database import utils
   utils.init_db(create_tables=True)

FastAPI dependency example (já disponível)
- from app.database import get_db
- def endpoint(db: Session = Depends(get_db)): ...

Alembic (migrations)
- Copy `database/alembic_env_template.py` to `<repo-root>/alembic/env.py` and add an `alembic.ini` in repo root.
- Ensure your `env.py` imports models (e.g., `import app.models`) so `target_metadata` contains all tables.
- Example commands:
  - alembic revision --autogenerate -m "create initial tables"
  - alembic upgrade head

Async sessions
- If you want to use async DB features, ensure DATABASE_URL uses an async driver (e.g. `postgresql+asyncpg://...`).
- The async session factory tries to convert common sync DSNs (postgresql/sqlite) to async forms; verify correctness.

Boas práticas
- Use Alembic in produção (não create_all).
- Não guarde segredos no repositório; use variáveis de ambiente ou vault.
- Teste migrações em staging antes de aplicar em produção.