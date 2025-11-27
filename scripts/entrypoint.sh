#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Default settings
APP_MODULE="socialfeed.wsgi:application"
GUNICORN_BIND="0.0.0.0:8000"
GUNICORN_WORKERS=${GUNICORN_WORKERS:-3}

echo "Waiting for dependent services (db/redis) if needed..."
# Wait for DB to be ready before running migrations. Use a Django management
# command in a retry loop which is portable and does not depend on system
# binaries like pg_isready being present in the image.
RETRIES=${DB_WAIT_RETRIES:-60}
SLEEP_TIME=${DB_WAIT_SLEEP:-2}
count=0
until python manage.py showmigrations >/dev/null 2>&1; do
	count=$((count+1))
	if [ "$count" -ge "$RETRIES" ]; then
		echo "Timed out waiting for the database after ${RETRIES} attempts"
		exit 1
	fi
	echo "Database unavailable - sleeping ${SLEEP_TIME}s (attempt ${count}/${RETRIES})"
	sleep $SLEEP_TIME
done

echo "Running database migrations..."
# Ensure static and media dirs are writable by the application user. This is
# important when those paths are mounted as Docker named volumes which are
# created as root-owned by default.
STATIC_DIR=/app/staticfiles
MEDIA_DIR=/app/media
if [ -d "$STATIC_DIR" ]; then
	chown -R appuser:appuser "$STATIC_DIR" || true
else
	mkdir -p "$STATIC_DIR" && chown -R appuser:appuser "$STATIC_DIR" || true
fi
if [ -d "$MEDIA_DIR" ]; then
	chown -R appuser:appuser "$MEDIA_DIR" || true
else
	mkdir -p "$MEDIA_DIR" && chown -R appuser:appuser "$MEDIA_DIR" || true
fi

echo "Running database migrations as appuser..."
su -s /bin/sh appuser -c "python manage.py migrate --no-input"

echo "Collecting static files as appuser..."
su -s /bin/sh appuser -c "python manage.py collectstatic --no-input"

# If arguments are provided, run them (useful for ad-hoc commands)
if [ "$#" -ne 0 ]; then
	echo "Running supplied command: $@"
	exec "$@"
else
	echo "Starting Gunicorn as appuser: bind=${GUNICORN_BIND}, workers=${GUNICORN_WORKERS}"
	exec su -s /bin/sh appuser -c "exec gunicorn ${APP_MODULE} --bind ${GUNICORN_BIND} --workers ${GUNICORN_WORKERS}"
fi
