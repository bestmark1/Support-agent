#!/usr/bin/env bash
set -euo pipefail

docker-entrypoint.sh postgres &
postgres_pid=$!

cleanup() {
  if kill -0 "$postgres_pid" 2>/dev/null; then
    kill "$postgres_pid" 2>/dev/null || true
    wait "$postgres_pid" || true
  fi
}

trap cleanup EXIT

until pg_isready -h 127.0.0.1 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; do
  sleep 1
done

escaped_password=${POSTGRES_PASSWORD//\'/\'\'}

gosu postgres psql -d "${POSTGRES_DB}" -v ON_ERROR_STOP=1 <<SQL
ALTER USER "${POSTGRES_USER}" WITH PASSWORD '${escaped_password}';
SQL

trap - EXIT
wait "$postgres_pid"
