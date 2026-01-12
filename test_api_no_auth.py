#!/usr/bin/env python
"""Test the REST API without authentication (like Slicer does)"""
import requests

# Test parameters
APP_ID = '696ea9dc5efce88cc8e174c5'
params = {
    'os': 'linux',
    'arch': 'amd64',
    'app_revision': '32516',
    'release': '5.11.0',
    'limit': 0
}

print("="*70)
print("TESTING REST API WITHOUT AUTHENTICATION")
print("="*70)
print(f"URL: http://127.0.0.1:8081/api/v1/app/{APP_ID}/extension")
print(f"Params: {params}")
print()

# Query WITHOUT authentication
resp = requests.get(
    f'http://127.0.0.1:8081/api/v1/app/{APP_ID}/extension',
    params=params
)

print(f"Status: {resp.status_code}")

if resp.ok:
    exts = resp.json()
    print(f"✓ SUCCESS - Total extensions: {len(exts)}")
    
    # Check for DICOM extensions
    dicom_exts = [e for e in exts if e.get('meta', {}).get('dicom_support_rule')]
    print(f"✓ Extensions with dicom_support_rule: {len(dicom_exts)}")
else:
    print(f"❌ FAILED")
    print(f"Response: {resp.text}")

print()
print("="*70)
print("TESTING ALTERNATIVE ENDPOINT FORMAT")
print("="*70)

# Try the format Slicer might use
url2 = 'http://127.0.0.1:8081/api/v1/app/696ea9dc5efce88cc8e174c5/extension'
params2 = {
    'os': 'linux',
    'arch': 'amd64',
    'app_revision': '32516',
    'limit': 0
}

print(f"URL: {url2}")
print(f"Params (no release): {params2}")
print()

resp2 = requests.get(url2, params=params2)
print(f"Status: {resp2.status_code}")
if resp2.ok:
    exts2 = resp2.json()
    print(f"✓ Total extensions: {len(exts2)}")
else:
    print(f"Response: {resp2.text[:200]}")
