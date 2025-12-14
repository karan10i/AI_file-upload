#!/bin/bash

echo "Starting Django Backend for AI Workspace..."

# Wait for database
echo "Waiting for PostgreSQL..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Create initial data
echo "Setting up initial data..."
python manage.py setup_initial_data

# Start server
echo "Starting Django server..."
python manage.py runserver 0.0.0.0:8000