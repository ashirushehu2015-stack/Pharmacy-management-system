from django.test import RequestFactory
from pharmcore.models import User
from pharmcore.views import dashboard

def run_verify():
    factory = RequestFactory()
    roles = ['ADMIN', 'PHARMACIST', 'ASSISTANT']
    
    with open('verification_results.txt', 'w') as f:
        for r in roles:
            user, _ = User.objects.get_or_create(username=f'v_{r.lower()}', defaults={'role': r})
            req = factory.get('/')
            req.user = user
            resp = dashboard(req)
            ctx = resp.context_data if hasattr(resp, 'context_data') else getattr(resp, 'context', {})
            has_p = 'recent_pending_prescriptions' in ctx
            has_l = 'low_stock_medicines' in ctx
            
            # Check results
            status = "PASS"
            if r == 'PHARMACIST':
                if not has_p or has_l: status = "FAIL"
            else:
                if has_p or not has_l: status = "FAIL"
                
            line = f"Role {r}: Pending={has_p}, LowStock={has_l} -> {status}\n"
            print(line.strip())
            f.write(line)

if __name__ == "__main__":
    run_verify()
