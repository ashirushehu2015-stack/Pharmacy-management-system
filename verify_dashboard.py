import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pharmacy_management_system.settings')
django.setup()

from django.test.utils import setup_test_environment
setup_test_environment()

from django.test import Client
from django.contrib.auth.models import AnonymousUser
from pharmcore.models import User, Medicine, Prescription
from pharmcore.views import dashboard

def verify_dashboard_context():
    client = Client()
    roles_to_check = ['ADMIN', 'PHARMACIST', 'ASSISTANT']
    
    for role_name in roles_to_check:
        username = f"test_{role_name.lower()}"
        user, _ = User.objects.get_or_create(username=username, defaults={'role': role_name})
        
        client.force_login(user)
        response = client.get('/dashboard/', SERVER_NAME='localhost')
        
        print(f"Status Code for {role_name}: {response.status_code}")
        if response.status_code == 302:
            print(f"Redirect URL: {response.url}")
            
        context = response.context if response.context else {}
        
        print(f"--- Verifying role: {role_name} ---")
        print(f"Keys in context: {list(context.keys())}")
        
        if role_name == 'PHARMACIST':
            assert 'recent_pending_prescriptions' in context, "Pharmacist should see pending prescriptions"
            assert 'low_stock_medicines' not in context, "Pharmacist should not see low stock medicines in specialized table"
        else:
            assert 'low_stock_medicines' in context, f"{role_name} should see low stock medicines"
            assert 'recent_pending_prescriptions' not in context, f"{role_name} should not see specialized pending prescriptions"
        
        print(f"Role {role_name} verification: SUCCESS")

if __name__ == "__main__":
    try:
        verify_dashboard_context()
        print("\nAll role-specific dashboard contexts verified!")
    except Exception as e:
        print(f"\nVerification FAILED: {e}")
        exit(1)
