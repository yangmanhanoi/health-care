#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
max_retries=30
counter=0
while ! nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
  sleep 2
  counter=$((counter+1))
  if [ $counter -ge $max_retries ]; then
    echo "Error: PostgreSQL did not become available in time."
    exit 1
  fi
done
echo "PostgreSQL is ready!"

# Wait a bit more to ensure PostgreSQL is fully initialized
sleep 5

# Try to connect to the database
echo "Testing database connection..."
python -c "
import sys
import os
import django
import time
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laboratory_service.settings')
django.setup()
from django.db import connections
from django.db.utils import OperationalError

retries = 5
while retries > 0:
    try:
        conn = connections['default']
        conn.cursor()
        print('Database connection successful!')
        sys.exit(0)
    except OperationalError as e:
        print(f'Database connection error: {e}')
        retries -= 1
        if retries == 0:
            print('Failed to connect to the database after multiple attempts.')
            sys.exit(1)
        print(f'Retrying in 5 seconds... ({retries} attempts left)')
        time.sleep(5)
"

if [ $? -ne 0 ]; then
  echo "Error: Could not connect to the database."
  exit 1
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py makemigrations laboratory
python manage.py migrate

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
