import os
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management_system.settings')
django.setup()

User = get_user_model()
client = Client()

# Ensure we have an admin user
admin = User.objects.filter(is_superuser=True).first()
if not admin:
    admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

client.force_login(admin)

def check_feature(url, name, search_texts):
    print(f"Testing {name} ({url})...")
    response = client.get(url)
    if response.status_code == 200:
        print(f"  [OK] Status 200")
        content = response.content.decode()
        for text in search_texts:
            if text in content:
                print(f"  [OK] Found: '{text}'")
            else:
                print(f"  [FAIL] Missing: '{text}'")
    else:
        print(f"  [FAIL] Status {response.status_code}")

# 1. Dashboard
check_feature('/dashboard/', 'Dashboard', ['Issued Today', 'Recent Pending Prescriptions'])

# 2. Analytics
check_feature('/analytics/', 'Analytics', ['Staff Prescription Performance', 'total_prescriptions', 'filled_count'])

# 3. CSV Export
print("\nTesting CSV Export (/reports/export/prescriptions/)...")
response = client.get('/reports/export/prescriptions/')
if response.status_code == 200:
    print(f"  [OK] Status 200")
    header = response.content.decode().splitlines()[0]
    if 'Prescribed By' in header and 'Medicines' in header:
        print("  [OK] CSV Header updated")
    else:
        print(f"  [FAIL] CSV Header missing fields: {header}")
else:
    print(f"  [FAIL] Status {response.status_code}")

print("\nInternal verification complete.")
