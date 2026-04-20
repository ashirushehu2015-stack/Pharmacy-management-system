import os
import shutil
import subprocess

def bundle():
    dist_dir = 'dist'
    project_name = 'PharmacyProject'
    target_dir = os.path.join(dist_dir, project_name)

    print(f"--- Bundling Pharmacy Management System into '{target_dir}' ---")

    # 1. Clean existing dist
    if os.path.exists(dist_dir):
        print(f"[*] Cleaning old {dist_dir} folder...")
        try:
            shutil.rmtree(dist_dir)
        except Exception as e:
            print(f"[!] Warning: Could not fully remove {dist_dir} ({e}). Retrying individual files...")
            # Fallback: try to delete files inside but keep going
            pass
    
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)

    # 2. Define files and directories to include
    to_copy = [
        'pharmacy_management_system',
        'pharmcore',
        'templates',
        'static',
        'staticfiles',
        'manage.py',
        'requirements.txt',
        '.env.example',
        'Dockerfile',
        'docker-compose.yml',
        'render.yaml',
        'start.sh',
        'runtime.txt',
        'DEPLOYMENT_GUIDE.md',
        'setup_desktop.bat',
        'run_pharmacy.bat',
    ]

    # 3. Copy items
    for item in to_copy:
        if not os.path.exists(item):
            print(f"[!] Warning: '{item}' not found, skipping.")
            continue
            
        print(f"[*] Copying {item}...")
        if os.path.isdir(item):
            shutil.copytree(item, os.path.join(target_dir, item), dirs_exist_ok=True, 
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
        else:
            shutil.copy2(item, os.path.join(target_dir, item))

    # 4. Optional: Create an empty db.sqlite3 if it doesn't exist in target
    # We don't copy the current db.sqlite3 to keep the dist "clean"
    # But we can provide a seed version if needed. 
    # For now, setup_desktop.bat handles migration.

    print(f"\n--- Success! ---")
    print(f"Your 'compiled' project is ready in: {os.path.abspath(target_dir)}")
    print(f"You can now ZIP this folder and share it.")

if __name__ == "__main__":
    bundle()
