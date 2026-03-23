#!/bin/sh
# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser (ignore if fails/already exists)
echo "Creating superuser..."
python manage.py createsuperuser --noinput || true

# Start Gunicorn server
echo "Starting gunicorn server on port ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} \
     --workers 2 \
     --timeout 120 \
     --access-logfile - \
     --error-logfile - \
     pharmacy_management_system.wsgi:application
