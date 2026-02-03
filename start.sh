#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser..."
python manage.py create_superuser

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
gunicorn ppn.wsgi:application --bind 0.0.0.0:$PORT --log-file -
