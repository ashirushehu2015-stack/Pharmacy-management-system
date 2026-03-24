# Create default users and sample data
echo "Setting up default users..."
python manage.py shell -c "
from pharmcore.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='ADMIN')
    print('Admin created.')
if not User.objects.filter(username='pharmacist').exists():
    u = User.objects.create_user('pharmacist', 'pharmacist@example.com', 'password123', role='PHARMACIST')
    print('Pharmacist created.')
if not User.objects.filter(username='assistant').exists():
    u = User.objects.create_user('assistant', 'assistant@example.com', 'password123', role='ASSISTANT')
    print('Assistant created.')
"

# Start Gunicorn server
echo "Starting gunicorn server on port ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} \
     --workers 2 \
     --timeout 120 \
     --access-logfile - \
     --error-logfile - \
     pharmacy_management_system.wsgi:application
