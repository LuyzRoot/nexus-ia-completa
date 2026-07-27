#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Inicia backend (uvicorn) e frontend (vite) em modo dev.
# Uso: ./scripts/run_dev.sh [--backend-port 8000] [--frontend-port 5173] [--env .env]

BACKEND_PORT=8000
FRONTEND_PORT=5173
ENV_FILE=".env"
PYTHON_BIN=${PYTHON_BIN:-python}
NPM_BIN=${NPM_BIN:-npm}

usage(){
  cat <<EOF
run_dev.sh - Inicia backend (uvicorn) e frontend (vite) em dev

Options:
  --backend-port PORT
  --frontend-port PORT
  --env FILE
  --no-frontend    não inicia o frontend
  --no-backend     não inicia o backend
  --help
EOF
}

START_FRONTEND=1
START_BACKEND=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --backend-port) BACKEND_PORT="$2"; shift 2;;
    --frontend-port) FRONTEND_PORT="$2"; shift 2;;
    --env) ENV_FILE="$2"; shift 2;;
    --no-frontend) START_FRONTEND=0; shift;;
    --no-backend) START_BACKEND=0; shift;;
    --help|-h) usage; exit 0;;
    *) echo "Unknown arg: $1"; usage; exit 1;;
  esac
done

if [[ -f "$ENV_FILE" ]]; then
  set -a; source "$ENV_FILE"; set +a
fi

PIDS=()

cleanup(){
  echo "Stopping background processes..."
  for pid in "${PIDS[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" || true
      wait "$pid" 2>/dev/null || true
    fi
  done
  exit 0
}
trap cleanup INT TERM

if [[ "$START_BACKEND" -eq 1 ]]; then
  echo "Starting backend (uvicorn) on :$BACKEND_PORT..."
  $PYTHON_BIN -m uvicorn app.main:app --reload --port "$BACKEND_PORT" &
  PIDS+=($!)
  sleep 1
fi

if [[ "$START_FRONTEND" -eq 1 ]]; then
  if [[ -d "frontend" ]]; then
    echo "Starting frontend (vite) on :$FRONTEND_PORT..."
    (cd frontend && $NPM_BIN run dev -- --port "$FRONTEND_PORT") &
    PIDS+=($!)
    sleep 1
  else
    echo "Frontend folder not found; skipping frontend"
  fi
fi

# wait for children
wait