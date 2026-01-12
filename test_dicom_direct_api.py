#!/usr/bin/env python
"""
Simple direct API test for can_import_dicom
"""
import requests
import json

API_URL = "http://localhost:8081/api/v1"
USERNAME = "admin"
PASSWORD = "adminadmin"

# Authenticate
resp = requests.get(f"{API_URL}/user/authentication", auth=(USERNAME, PASSWORD))
token = resp.json()['authToken']['token']
headers = {'Girder-Token': token}

# Get app
resp = requests.get(f"{API_URL}/app", headers=headers, params={'name': 'DICOMTestApp'})
app_id = resp.json()[0]['_id']

print(f"App ID: {app_id}")

# Test 1: Create extension with can_import_dicom via JSON body
print("\n" + "="*70)
print("TEST: Creating extension with JSON body can_import_dicom")
print("="*70)

import time
timestamp = int(time.time())

params = {
    'os': 'linux',
    'arch': 'amd64',
    'baseName': f'DICOMExtTest{timestamp}',
    'repository_type': 'git',
    'repository_url': 'https://github.com/test/ext.git',
    'app_revision': '0000',
    'revision': '3000',
    'description': 'Test extension with DICOM support rule'
}

json_body = {
    'can_import_dicom': [
        'modality == "MR"',
        'modality == "CT"'
    ]
}

print(f"\nSending POST with:")
print(f"  Query params: {params}")
print(f"  JSON body: {json.dumps(json_body, indent=2)}")

resp = requests.post(
    f"{API_URL}/app/{app_id}/extension",
    headers=headers,
    params=params,
    json=json_body
)

print(f"\nResponse status: {resp.status_code}")
print(f"Response: {json.dumps(resp.json(), indent=2)}")

if resp.status_code == 200:
    ext_id = resp.json()['_id']
    print(f"\nExtension created: {ext_id}")
    
    # Retrieve and check
    resp2 = requests.get(f"{API_URL}/item/{ext_id}", headers=headers)
    ext_data = resp2.json()
    
    print(f"\nExtension metadata:")
    for key, value in sorted(ext_data.get('meta', {}).items()):
        print(f"  {key}: {value}")
    
    can_import_dicom = ext_data.get('meta', {}).get('can_import_dicom')
    
    print(f"\n{'='*70}")
    if can_import_dicom:
        print("✓✓✓ SUCCESS: can_import_dicom is present!")
        print(f"  Values: {can_import_dicom}")
    else:
        print("✗✗✗ FAILURE: can_import_dicom is NOT present")
    print("="*70)
