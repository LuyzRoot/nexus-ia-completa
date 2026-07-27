#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

ENV_FILE=".env"
COMMAND="${1:-help}"

usage(){
  cat <<EOF
manage_db.sh - Gerencia banco de dados (dev)

Usage:
  ./scripts/manage_db.sh init        # create_all tables (dev)
  ./scripts/manage_db.sh migrate     # alembic upgrade head (if alembic configured)
  ./scripts/manage_db.sh revision    # alembic revision --autogenerate -m "msg"
  ./scripts/manage_db.sh drop        # drop all tables (dev only)
  ./scripts/manage_db.sh help
EOF
}

if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

case "$COMMAND" in
  init)
    echo "Initializing DB (create_all) - development use only"
    python - <<PY
from app.database import utils
utils.init_db(create_tables=True)
PY
    ;;
  migrate)
    if command -v alembic >/dev/null 2>&1; then
      alembic upgrade head
    else
      echo "alembic not installed or no alembic.ini present; falling back to create_all"
      python - <<PY
from app.database import utils
utils.create_all_tables()
PY
    fi
    ;;
  revision)
    shift || true
    MSG="${1:-'autogen'}"
    if command -v alembic >/dev/null 2>&1; then
      alembic revision --autogenerate -m "$MSG"
    else
      echo "alembic not available; install alembic to use revision"
      exit 1
    fi
    ;;
  drop)
    read -p "DROP ALL TABLES? This is destructive. Type YES to continue: " CONF
    if [[ "$CONF" == "YES" ]]; then
      python - <<PY
from app.database import utils
utils.drop_all_tables()
PY
    else
      echo "Aborted"
    fi
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown command: $COMMAND"
    usage
    exit 1
    ;;
esac