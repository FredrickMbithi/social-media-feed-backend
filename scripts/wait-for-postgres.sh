#!/bin/sh
# Wait for Postgres to be available, then exec the provided command
set -e

DB_CHECK_CMD="PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c '\\q'"

echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
until PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' >/dev/null 2>&1; do
  echo "Database unavailable - sleeping 2s"
  sleep 2
done

echo "Postgres is available; executing: $@"
exec "$@"
