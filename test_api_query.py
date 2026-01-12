#!/usr/bin/env python
"""Test the REST API query that Slicer would use"""
import requests

# Test parameters
APP_ID = '696ea9dc5efce88cc8e174c5'
params = {
    'os': 'linux',
    'arch': 'amd64',
    'app_revision': '32516',
    'release': '5.11.0',
    'limit': 0  # Get all
}

print("="*70)
print("TESTING REST API QUERY")
print("="*70)
print(f"URL: http://127.0.0.1:8081/api/v1/app/{APP_ID}/extension")
print(f"Params: {params}")
print()

# Query
resp = requests.get(
    f'http://127.0.0.1:8081/api/v1/app/{APP_ID}/extension',
    params=params
)

print(f"Status: {resp.status_code}")

if resp.ok:
    exts = resp.json()
    print(f"Total extensions: {len(exts)}")
    print()
    
    # Check for DICOM extensions
    dicom_exts = [e for e in exts if e.get('meta', {}).get('dicom_support_rule')]
    print(f"Extensions with dicom_support_rule: {len(dicom_exts)}")
    print()
    
    if dicom_exts:
        print("DICOM Extensions:")
        for e in dicom_exts:
            meta = e.get('meta', {})
            name = meta.get('baseName', 'Unknown')
            rules = meta.get('dicom_support_rule', [])
            print(f"\n  {name}:")
            for rule in rules:
                print(f"    - {rule}")
    else:
        print("⚠️ No extensions with dicom_support_rule found!")
        print("\nSample extension metadata:")
        if exts:
            sample = exts[0]['meta']
            print(f"  baseName: {sample.get('baseName')}")
            print(f"  Keys: {list(sample.keys())[:10]}")
else:
    print(f"Error: {resp.text}")
