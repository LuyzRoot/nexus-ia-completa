#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Template robusto para scripts do projeto NEXUS
ENV_FILE=".env"
VERBOSE=0
SCRIPT_NAME="$(basename "$0")"

usage() {
  cat <<EOF
$SCRIPT_NAME - Template de script

Usage: $SCRIPT_NAME [--env FILE] [--verbose] <command> [args...]

Options:
  --env FILE     Carregar variáveis de ambiente de FILE (default: .env)
  --verbose      Habilitar logs mais verbosos
  help           Mostrar esta ajuda

Commands (exemplo):
  init
  migrate
EOF
}

log() {
  local level="$1"; shift
  if [[ "$VERBOSE" -eq 1 || "$level" != "DEBUG" ]]; then
    echo "[$(date -u +'%Y-%m-%dT%H:%M:%SZ')] [$level] $*"
  fi
}

# parse flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --env) ENV_FILE="$2"; shift 2;;
    --verbose) VERBOSE=1; shift;;
    help|-h|--help) usage; exit 0;;
    *) break;;
  esac
done

COMMAND="${1:-help}"; shift || true

# load .env if present
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC1090
  set -a; source "$ENV_FILE"; set +a
  log INFO "Loaded env from $ENV_FILE"
fi

case "$COMMAND" in
  init)
    log INFO "Exec: init (example)"
    ;;
  migrate)
    log INFO "Exec: migrate (example)"
    ;;
  *)
    usage
    exit 1
    ;;
esac