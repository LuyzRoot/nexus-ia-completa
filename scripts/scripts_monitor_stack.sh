#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Levanta Prometheus + Grafana (desenvolvimento) usando monitoring/docker-compose.yml
COMPOSE_FILE="monitoring/docker-compose.yml"

usage(){
  cat <<EOF
monitor_stack.sh up|down|restart

Examples:
  ./scripts/monitor_stack.sh up
  ./scripts/monitor_stack.sh down
EOF
}

if [[ $# -lt 1 ]]; then
  usage; exit 1
fi

ACTION="$1"

case "$ACTION" in
  up)
    docker compose -f "$COMPOSE_FILE" up -d
    ;;
  down)
    docker compose -f "$COMPOSE_FILE" down
    ;;
  restart)
    docker compose -f "$COMPOSE_FILE" down
    docker compose -f "$COMPOSE_FILE" up -d
    ;;
  *)
    usage
    exit 1
    ;;
esac