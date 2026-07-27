#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Faz backup do DB: detecta POSTGRES_URL ou SQLite local
ENV_FILE=".env"
OUT_DIR="${1:-backups}"
TIMESTAMP=$(date -u +'%Y%m%dT%H%M%SZ')

usage(){
  cat <<EOF
backup_db.sh [OUT_DIR]

Detects DATABASE_URL from .env and performs:
- pg_dump for Postgres
- copy for sqlite file
EOF
}

if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

mkdir -p "$OUT_DIR"

DATABASE_URL="${DATABASE_URL:-}"

if [[ -z "$DATABASE_URL" ]]; then
  echo "DATABASE_URL not set in env; aborting"
  exit 1
fi

if [[ "$DATABASE_URL" =~ ^postgresql ]]; then
  # need pg_dump
  if ! command -v pg_dump >/dev/null 2>&1; then
    echo "pg_dump not found; install postgres client utilities"
    exit 1
  fi
  FNAME="$OUT_DIR/pg_backup_${TIMESTAMP}.sql"
  echo "Running pg_dump -> $FNAME"
  # If using env var PG* the pg_dump will pick them up, else parse URL (left simple)
  pg_dump "$DATABASE_URL" -Fc -f "$FNAME"
  echo "Backup written to $FNAME"
elif [[ "$DATABASE_URL" =~ sqlite ]]; then
  # sqlite:///./path.db
  FILE="${DATABASE_URL#sqlite:///}"
  if [[ -f "$FILE" ]]; then
    FNAME="$OUT_DIR/sqlite_backup_${TIMESTAMP}.db"
    cp "$FILE" "$FNAME"
    echo "SQLite DB copied to $FNAME"
  else
    echo "SQLite file not found: $FILE"
    exit 1
  fi
else
  echo "Unsupported DATABASE_URL scheme: $DATABASE_URL"
  exit 1
fi