import urllib.request
import base64

BASE_URL = "http://127.0.0.1:8005"
auth_str = "admin:admin123"
auth_b64 = base64.b64encode(auth_str.encode()).decode()
headers = {"Authorization": f"Basic {auth_b64}"}

def check_url(path, search_text=None):
    print(f"Checking {path}...")
    req = urllib.request.Request(f"{BASE_URL}{path}", headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            text = response.read().decode()
            print(f"Status: {response.status} [OK]")
            if search_text:
                if search_text in text:
                    print(f"'{search_text}' found [OK]")
                else:
                    print(f"'{search_text}' NOT found [FAIL]")
            return text
    except Exception as e:
        print(f"Failed: {e} [FAIL]")
        return None

# Check Dashboard
check_url("/dashboard/", "Issued Today")

# Check Analytics
check_url("/analytics/", "Staff Prescription Performance")

# Check CSV Export
csv_text = check_url("/reports/export/prescriptions/")
if csv_text:
    lines = csv_text.splitlines()
    if len(lines) > 0 and "Prescribed By" in lines[0] and "Medicines" in lines[0]:
        print("CSV Header updated correctly [OK]")
        if len(lines) > 1:
            print(f"Example data row: {lines[1]}")

print("\nVerification complete.")
