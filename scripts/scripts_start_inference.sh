#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

PORT=8001
WORKERS=1
ENV_FILE=".env"
PYTHON_BIN=${PYTHON_BIN:-python}

usage(){
  cat <<EOF
start_inference.sh - Inicia o serviço de inference (uvicorn)

Usage:
  ./scripts/start_inference.sh [--port 8001] [--workers 1] [--env .env]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --port) PORT="$2"; shift 2;;
    --workers) WORKERS="$2"; shift 2;;
    --env) ENV_FILE="$2"; shift 2;;
    --help|-h) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

echo "Starting inference service on :$PORT (workers=$WORKERS)"
$PYTHON_BIN -m uvicorn inference.server:app --host 0.0.0.0 --port "$PORT" --workers "$WORKERS"