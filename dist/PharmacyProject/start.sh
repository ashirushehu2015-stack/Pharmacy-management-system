#!/bin/sh
# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create default users and sample data
echo "Setting up default users and data..."
python manage.py shell -c "
from pharmcore.models import User, Supplier
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123', role='ADMIN')
    print('Admin created.')
if not User.objects.filter(username='pharmacist').exists():
    u = User.objects.create_user('pharmacist', 'pharmacist@example.com', 'password123', role='PHARMACIST')
    print('Pharmacist created.')
if not User.objects.filter(username='assistant').exists():
    u = User.objects.create_user('assistant', 'assistant@example.com', 'password123', role='ASSISTANT')
    print('Assistant created.')

suppliers = [
    {'name': 'MedCorp International', 'contact_person': 'Alice Brown', 'phone': '555-1111', 'email': 'alice@medcorp.com', 'address': '100 Health Way, Boston, MA'},
    {'name': 'PharmaTrust', 'contact_person': 'Bob Smith', 'phone': '555-2222', 'email': 'bob@pharmatrust.com', 'address': '200 Cure Lane, Seattle, WA'},
]
for s_data in suppliers:
    Supplier.objects.get_or_create(name=s_data['name'], defaults=s_data)
print('Default suppliers ensured.')
"

# Start Gunicorn server
echo "Starting gunicorn server on port ${PORT:-8000}..."
exec gunicorn --bind 0.0.0.0:${PORT:-8000} \
     --workers 2 \
     --timeout 120 \
     --access-logfile - \
     --error-logfile - \
     pharmacy_management_system.wsgi:application
