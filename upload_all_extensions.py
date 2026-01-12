#!/usr/bin/env python
"""
Upload ALL extensions from ExtensionsIndex to recreate the database
"""
import os
import json
import tempfile
import glob
from slicer_package_manager_client import SlicerPackageClient

# Configuration
HOST = 'localhost'
PORT = 8081
SCHEME = 'http'
USERNAME = 'admin'
PASSWORD = 'adminadmin'
APP_NAME = 'Slicer'
EXTENSIONS_INDEX_PATH = r'c:\d\s\ExtensionsIndex'

def create_dummy_extension_file():
    """Create a temporary dummy extension file"""
    fd, path = tempfile.mkstemp(suffix='.tar.gz', prefix='ext_')
    with os.fdopen(fd, 'wb') as f:
        f.write(b'Dummy extension package\n')
    return path

def upload_extension_from_json(client, json_path, ext_file):
    """Upload an extension based on its JSON metadata file"""
    extension_name = os.path.splitext(os.path.basename(json_path))[0]
    
    try:
        # Read JSON metadata
        with open(json_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Extract metadata
        params = {
            'filepath': ext_file,
            'app_name': APP_NAME,
            'ext_os': 'linux',
            'arch': 'amd64',
            'name': extension_name,
            'repo_type': 'git',
            'repo_url': metadata.get('scm_url', f'https://github.com/test/{extension_name}.git'),
            'revision': metadata.get('scm_revision', 'master')[:7],
            'app_revision': '32516',
            'desc': metadata.get('description', f'Extension {extension_name}'),
        }
        
        # Add optional fields
        if 'category' in metadata:
            params['category'] = metadata['category']
        
        if 'homepage' in metadata:
            params['homepage'] = metadata['homepage']
        
        if 'contributors' in metadata:
            params['contributors'] = metadata['contributors']
        
        if 'screenshoturls' in metadata:
            params['screenshots'] = metadata['screenshoturls']
        
        # Add dicom_support_rule if present
        if 'dicom_support_rule' in metadata:
            params['dicom_support_rule'] = metadata['dicom_support_rule']
        
        # Upload
        ext = client.uploadExtension(**params)
        
        if isinstance(ext, int):
            if ext == 32:  # Already exists
                print(f"  ⚠️  {extension_name:40} - Already exists")
            else:
                print(f"  ❌ {extension_name:40} - Error code: {ext}")
        else:
            dicom_marker = " [DICOM]" if 'dicom_support_rule' in metadata else ""
            print(f"  ✓  {extension_name:40}{dicom_marker}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ {extension_name:40} - Error: {str(e)[:50]}")
        return False

def main():
    print("="*70)
    print("UPLOADING ALL EXTENSIONS FROM EXTENSIONSINDEX")
    print("="*70)
    
    # Connect
    client = SlicerPackageClient(host=HOST, port=PORT, scheme=SCHEME)
    client.authenticate(USERNAME, PASSWORD)
    print(f"✓ Connected to {SCHEME}://{HOST}:{PORT}")
    
    # Get app info
    apps = client.listApp()
    if apps:
        app = apps[0]
        print(f"✓ Using app: {app['name']} (ID: {app['_id']})")
        print(f"\n⚠️  UPDATE YOUR SLICER SETTINGS TO USE THIS APP ID: {app['_id']}\n")
    else:
        print("❌ No application found! Run test_upload_extensions_from_index.py first")
        return
    
    # Create dummy file
    ext_file = create_dummy_extension_file()
    print(f"✓ Created temp file: {ext_file}\n")
    
    # Get all JSON files
    json_files = glob.glob(os.path.join(EXTENSIONS_INDEX_PATH, '*.json'))
    print(f"Found {len(json_files)} extensions to upload\n")
    
    # Upload all
    success_count = 0
    for json_path in sorted(json_files):
        if upload_extension_from_json(client, json_path, ext_file):
            success_count += 1
    
    # Cleanup
    try:
        os.unlink(ext_file)
    except:
        pass
    
    print(f"\n{'='*70}")
    print(f"COMPLETE: {success_count}/{len(json_files)} extensions processed")
    print(f"{'='*70}")
    print(f"\n⚠️  IMPORTANT: Update Slicer's app ID to: {app['_id']}")

if __name__ == '__main__':
    main()
