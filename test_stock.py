import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pharmacy_management_system.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import Group
from pharmcore.models import User, Medicine, Supplier, StockEntry
from pharmcore.views import stock_entry_create

user, _ = User.objects.get_or_create(username='pharmacist', email='p@p.com', role=User.Role.PHARMACIST)
if not Medicine.objects.exists():
    Medicine.objects.create(name='Med1', brand='Brand', category='Cat', price=10, expiry_date='2025-01-01')
med = Medicine.objects.first()
supplier = Supplier.objects.first()
factory = RequestFactory()
data = {'medicine': med.id, 'quantity': 10, 'unit_cost': 5.0}
if supplier:
    data['supplier'] = supplier.id
request = factory.post('/stock/add/', data)
request.user = user

from django.contrib.messages.storage.fallback import FallbackStorage
setattr(request, 'session', 'session')
messages = FallbackStorage(request)
setattr(request, '_messages', messages)

response = stock_entry_create(request)
print("Response status:", response.status_code)
print("Response location:", response.get('Location', ''))
