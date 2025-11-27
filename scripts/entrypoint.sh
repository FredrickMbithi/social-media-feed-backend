#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Default settings
APP_MODULE="socialfeed.wsgi:application"
GUNICORN_BIND="0.0.0.0:8000"
GUNICORN_WORKERS=${GUNICORN_WORKERS:-3}

echo "Waiting for dependent services (db/redis) if needed..."
# simple wait-for logic could be added here if desired

echo "Running database migrations..."
python manage.py migrate --no-input

echo "Collecting static files..."
python manage.py collectstatic --no-input

# If arguments are provided, run them (useful for ad-hoc commands)
if [ "$#" -ne 0 ]; then
	echo "Running supplied command: $@"
	exec "$@"
else
	echo "Starting Gunicorn: bind=${GUNICORN_BIND}, workers=${GUNICORN_WORKERS}"
	exec gunicorn ${APP_MODULE} --bind ${GUNICORN_BIND} --workers ${GUNICORN_WORKERS}
fi
