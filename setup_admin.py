#!/usr/bin/env python
"""
Setup admin user for Girder
"""
import requests
import time

API_URL = "http://localhost:8081/api/v1"

def setup_admin():
    """Create admin user if not exists"""
    print("Setting up Girder admin user...")
    
    # Wait for Girder to be ready
    print("Waiting for Girder to be ready...")
    for i in range(30):
        try:
            resp = requests.get(f"{API_URL}/system/version", timeout=2)
            if resp.status_code == 200:
                print("✓ Girder is ready")
                break
        except:
            pass
        time.sleep(1)
        print(f"  Attempt {i+1}/30...")
    else:
        print("✗ Girder did not start in time")
        return False
    
    # Check if admin exists
    token = None
    try:
        resp = requests.get(f"{API_URL}/user/authentication", 
                          auth=('admin', 'adminadmin'))
        if resp.status_code == 200:
            print("✓ Admin user already exists and credentials are correct")
            token = resp.json()['authToken']['token']
        else:
            # Create admin user
            print("Creating admin user...")
            resp = requests.post(f"{API_URL}/user", params={
                'login': 'admin',
                'email': 'admin@example.com',
                'firstName': 'Admin',
                'lastName': 'User',
                'password': 'adminadmin',
                'admin': True
            })
            
            if resp.status_code in [200, 201]:
                print("✓ Admin user created successfully")
                print(f"  Username: admin")
                print(f"  Password: adminadmin")
                # Get token
                resp = requests.get(f"{API_URL}/user/authentication", 
                                  auth=('admin', 'adminadmin'))
                if resp.status_code == 200:
                    token = resp.json()['authToken']['token']
            else:
                print(f"Response: {resp.status_code}")
                print(f"Message: {resp.text}")
                return False
    except Exception as e:
        print(f"✗ Error with admin user: {e}")
        return False
    
    if not token:
        print("✗ Could not get authentication token")
        return False
        
    # Create assetstore
    print("\nSetting up assetstore...")
    headers = {'Girder-Token': token}
    
    # Check if assetstore exists
    resp = requests.get(f"{API_URL}/assetstore", headers=headers)
    if resp.status_code == 200 and len(resp.json()) > 0:
        print("✓ Assetstore already exists")
        return True
    
    # Create filesystem assetstore
    resp = requests.post(f"{API_URL}/assetstore", headers=headers, params={
        'type': 0,  # Filesystem type
        'name': 'Default',
        'root': '/data'
    })
    
    if resp.status_code in [200, 201]:
        print("✓ Assetstore created successfully")
        return True
    else:
        print(f"✗ Error creating assetstore: {resp.status_code}")
        print(f"  Message: {resp.text}")
        return False

if __name__ == '__main__':
    if setup_admin():
        print("\n" + "="*60)
        print("Setup complete! You can now run:")
        print("  python test_extension_metadata.py")
        print("  or")
        print("  python test_extension_cli.py")
        print("="*60)
