from django.test import RequestFactory
from pharmcore.models import User, Medicine, Prescription
from pharmcore.views import dashboard

def verify_dashboard_context():
    factory = RequestFactory()
    roles_to_check = ['ADMIN', 'PHARMACIST', 'ASSISTANT']
    
    for role_name in roles_to_check:
        username = f"test_{role_name.lower()}_{User.objects.count()}"
        user, _ = User.objects.get_or_create(username=username, defaults={'role': role_name})
        
        request = factory.get('/dashboard/')
        request.user = user
        
        # Call the dashboard view directly
        # Note: we need to handle the template response context
        response = dashboard(request)
        context = response.context_data if hasattr(response, 'context_data') else getattr(response, 'context', {})
        
        print(f"--- Verifying role: {role_name} ---")
        print(f"Keys in context: {list(context.keys())}")
        
        if role_name == 'PHARMACIST':
            if 'recent_pending_prescriptions' not in context:
                print(f"FAILED: Pharmacist should see pending prescriptions")
                return False
            if 'low_stock_medicines' in context:
                print(f"FAILED: Pharmacist should not see specialized low stock table")
                return False
        else:
            if 'low_stock_medicines' not in context:
                print(f"FAILED: {role_name} should see low stock medicines")
                return False
            if 'recent_pending_prescriptions' in context:
                print(f"FAILED: {role_name} should not see specialized pending prescriptions")
                return False
        
        print(f"Role {role_name} verification: SUCCESS")
    return True

if verify_dashboard_context():
    print("\nAll role-specific dashboard contexts verified!")
else:
    print("\nVerification FATAL ERROR")
    exit(1)
