#!/bin/bash

# Load config from env file
if [ -f gunicorn.env ]; then
    export $(grep -v '^#' gunicorn.env | xargs)
else
    echo "gunicorn.env not found, using defaults"
fi

# Defaults if not set in env file
WORKERS=${GUNICORN_WORKERS:-3}
BIND=${GUNICORN_BIND:-0.0.0.0:8000}
TIMEOUT=${GUNICORN_TIMEOUT:-30}
LOG_LEVEL=${GUNICORN_LOG_LEVEL:-info}
WORKER_CLASS=${GUNICORN_WORKER_CLASS:-sync}

echo "Starting Gunicorn with $WORKERS workers on $BIND"

gunicorn notification_service.wsgi:application \
    --workers $WORKERS \
    --bind $BIND \
    --timeout $TIMEOUT \
    --log-level $LOG_LEVEL \
    --worker-class $WORKER_CLASS
