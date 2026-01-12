#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Update extension metadata from JSON files using the createOrUpdate API
"""
import os
import json
import glob
import requests
import sys

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
HOST = 'localhost'
PORT = 8081
SCHEME = 'http'
USERNAME = 'admin'
PASSWORD = 'adminadmin'
APP_NAME = 'Slicer'
APP_ID = '696ea9dc5efce88cc8e174c5'
EXTENSIONS_INDEX_PATH = r'c:/d/s/ExtensionsIndex'

def update_extension_from_json(session, json_path):
    """Update an extension using the createOrUpdateExtension API"""
    extension_name = os.path.splitext(os.path.basename(json_path))[0]
    
    try:
        # Read JSON metadata
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Prepare URL parameters for POST
        url_params = {
            'os': 'linux',
            'arch': 'amd64',
            'baseName': extension_name,
            'repository_type': 'git',
            'repository_url': metadata.get('scm_url', f'https://github.com/test/{extension_name}.git'),
            'revision': metadata.get('scm_revision', 'master')[:7],
            'app_revision': '32516',
            'description': metadata.get('description', f'Extension {extension_name}'),
        }
        
        # Add optional fields
        if 'category' in metadata:
            url_params['category'] = metadata['category']
        if 'homepage' in metadata:
            url_params['homepage'] = metadata['homepage']
        if 'contributors' in metadata:
            url_params['contributors'] = metadata['contributors']
        if 'screenshoturls' in metadata:
            url_params['screenshots'] = metadata['screenshoturls']
        
        # Build JSON payload for dicom_support_rule
        json_payload = {}
        if 'dicom_support_rule' in metadata:
            json_payload['dicom_support_rule'] = metadata['dicom_support_rule']
        
        # POST to createOrUpdateExtension
        url = f'{SCHEME}://{HOST}:{PORT}/api/v1/app/{APP_ID}/extension'
        resp = session.post(url, params=url_params, json=json_payload if json_payload else None)
        
        if resp.status_code in [200, 201]:
            dicom_marker = " [DICOM]" if 'dicom_support_rule' in metadata else ""
            print(f"  ✓  {extension_name:40}{dicom_marker}")
            return True
        else:
            print(f"  ❌ {extension_name:40} - {resp.status_code}: {resp.text[:50]}")
            return False
        
    except Exception as e:
        print(f"  ❌ {extension_name:40} - Error: {str(e)[:50]}")
        return False

def main():
    print("="*70)
    print("UPDATING EXTENSION METADATA FROM JSON FILES")
    print("="*70)
    
    # Authenticate and get API key
    auth_resp = requests.get(
        f'{SCHEME}://{HOST}:{PORT}/api/v1/user/authentication',
        auth=(USERNAME, PASSWORD)
    )
    
    if not auth_resp.ok:
        print(f"❌ Authentication failed: {auth_resp.text}")
        return
    
    auth_data = auth_resp.json()
    api_key = auth_data['authToken']['token']
    
    # Create session with API key
    session = requests.Session()
    session.headers.update({'Girder-Token': api_key})
    
    print(f"✓ Connected to {SCHEME}://{HOST}:{PORT}")
    print(f"✓ Authenticated as {auth_data['user']['login']}")
    print(f"✓ Using app ID: {APP_ID}\n")
    
    # Get all JSON files
    json_files = glob.glob(os.path.join(EXTENSIONS_INDEX_PATH, '*.json'))
    print(f"Found {len(json_files)} extensions to update\n")
    
    # Update all
    success_count = 0
    for json_path in sorted(json_files):
        if update_extension_from_json(session, json_path):
            success_count += 1
    
    print(f"\n{'='*70}")
    print(f"COMPLETE: {success_count}/{len(json_files)} extensions updated")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
