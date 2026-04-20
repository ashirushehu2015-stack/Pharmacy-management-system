import requests
import os

BASE_URL = "http://127.0.0.1:8005"
auth = ('admin', 'admin123')

# Check Dashboard
print("Checking Dashboard...")
r = requests.get(f"{BASE_URL}/", auth=auth)
if r.status_code == 200:
    print("Dashboard [OK]")
    if "Issued Today" in r.text:
        print("Metric Card found [OK]")
    else:
        print("Metric Card NOT found [FAIL]")
else:
    print(f"Dashboard failed with {r.status_code} [FAIL]")

# Check Analytics
print("\nChecking Analytics...")
r = requests.get(f"{BASE_URL}/analytics/", auth=auth)
if r.status_code == 200:
    print("Analytics [OK]")
    if "Staff Prescription Performance" in r.text:
        print("Accountability chart found [OK]")
else:
    print(f"Analytics failed with {r.status_code} [FAIL]")

# Check CSV Export
print("\nChecking CSV Export...")
r = requests.get(f"{BASE_URL}/prescriptions/export/", auth=auth)
if r.status_code == 200:
    print("CSV Export [OK]")
    lines = r.text.splitlines()
    if len(lines) > 0 and "Prescribed By" in lines[0] and "Medicines" in lines[0]:
        print("CSV Header updated correctly [OK]")
        if len(lines) > 1:
            print(f"Example data row: {lines[1]}")
else:
    print(f"CSV Export failed with {r.status_code} [FAIL]")

print("\nVerification complete.")
