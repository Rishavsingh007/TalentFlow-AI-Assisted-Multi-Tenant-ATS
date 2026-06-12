#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
until python -c "
import os, sys, time
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development'))
django.setup()
from django.db import connection
for i in range(30):
    try:
        connection.ensure_connection()
        sys.exit(0)
    except Exception:
        time.sleep(1)
sys.exit(1)
"; do
  echo "PostgreSQL unavailable - retrying..."
  sleep 2
done

echo "Running migrations..."
python manage.py migrate --noinput

exec "$@"
