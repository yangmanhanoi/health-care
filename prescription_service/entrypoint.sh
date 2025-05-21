#!/bin/bash

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
while ! nc -z ${MYSQL_HOST:-db} ${MYSQL_PORT:-3306}; do
  sleep 1
done
echo "MySQL is ready!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start server
echo "Starting server..."
python manage.py runserver 0.0.0.0:8000
