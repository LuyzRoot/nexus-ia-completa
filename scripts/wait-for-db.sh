#!/usr/bin/env bash
set -e
host="$1"
shift || true
until pg_isready -h "${host:-localhost}"; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done
>&2 echo "Postgres is up - executing command"
exec "$@"
