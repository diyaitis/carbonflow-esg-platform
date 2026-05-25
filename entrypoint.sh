#!/bin/sh
set -e

echo "==> Running database migrations..."
python3 manage.py migrate --noinput

echo "==> Migrations complete. Starting server..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}