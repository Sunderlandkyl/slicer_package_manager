#!/usr/bin/env python
"""
Test script to upload extensions from ExtensionsIndex JSON files
"""
import os
import json
import tempfile
from slicer_package_manager_client import SlicerPackageClient

# Configuration
HOST = 'localhost'
PORT = 8081
SCHEME = 'http'
USERNAME = 'admin'
PASSWORD = 'adminadmin'
APP_NAME = 'Slicer'
COLLECTION_NAME = 'Applications'

# Extensions to test (with dicom_support_rule)
EXTENSIONS_TO_TEST = [
    'PETDICOMExtension.json',
    'QuantitativeReporting.json',
    'SlicerHeart.json',
    'SlicerRT.json',
]

def create_dummy_extension_file():
    """Create a temporary dummy extension file for testing"""
    fd, path = tempfile.mkstemp(suffix='.tar.gz', prefix='test_ext_')
    with os.fdopen(fd, 'wb') as f:
        f.write(b'Dummy extension package content\n')
    return path

def clear_database_and_setup(client):
    """DON'T clear - just ensure app/release exists"""
    print("\n" + "="*70)
    print("CHECKING APPLICATION AND RELEASE")
    print("="*70)
    
    # Check if app exists
    apps = client.listApp()
    app = None
    for a in apps:
        if a['name'] == APP_NAME:
            app = a
            print(f"✓ Found existing application: {app['_id']}")
            break
    
    if not app:
        # Create fresh application only if it doesn't exist
        print(f"\nCreating application: {APP_NAME}")
        app = client.createApp(
            name=APP_NAME,
            desc='3D Slicer',
            coll_name=COLLECTION_NAME,
            coll_desc='Applications collection',
            public=True
        )
        print(f"✓ Application created: {app['_id']}")
        
        # Create a release
        print("\nCreating release: 5.11.0")
        release = client.createRelease(
            app_name=APP_NAME,
            name='5.11.0',
            revision='32516',
            desc='Slicer 5.11.0 release'
        )
        print(f"✓ Release created")
    else:
        print("✓ Using existing application (not clearing database)")
    
    return app

def upload_extension_from_json(client, json_path, ext_file):
    """Upload an extension based on its JSON metadata file"""
    print(f"\n{'='*70}")
    print(f"UPLOADING: {os.path.basename(json_path)}")
    print("="*70)
    
    # Read JSON metadata
    with open(json_path, 'r') as f:
        metadata = json.load(f)
    
    extension_name = os.path.splitext(os.path.basename(json_path))[0]
    
    # Extract metadata
    params = {
        'filepath': ext_file,
        'app_name': APP_NAME,
        'ext_os': 'linux',
        'arch': 'amd64',
        'name': extension_name,
        'repo_type': 'git',
        'repo_url': metadata.get('scm_url', 'https://github.com/test/test.git'),
        'revision': metadata.get('scm_revision', 'master')[:7],  # Short SHA
        'app_revision': '32516',  # Match our release
        'desc': f"Extension {extension_name}",
    }
    
    # Add optional fields
    if 'category' in metadata:
        params['category'] = metadata['category']
    
    # Add dicom_support_rule if present
    if 'dicom_support_rule' in metadata:
        params['dicom_support_rule'] = metadata['dicom_support_rule']
        print(f"\n  📋 dicom_support_rule from JSON:")
        for rule in metadata['dicom_support_rule']:
            print(f"     - {rule}")
    
    print(f"\n  Uploading extension: {extension_name}")
    print(f"    OS: {params['ext_os']}")
    print(f"    Arch: {params['arch']}")
    print(f"    Repo: {params['repo_url']}")
    print(f"    Revision: {params['revision']}")
    
    try:
        ext = client.uploadExtension(**params)
        
        # Retrieve and verify
        if isinstance(ext, int):
            ext_list = client.listExtension(
                app_name=APP_NAME,
                name=extension_name,
                ext_os='linux',
                arch='amd64'
            )
            if ext_list:
                ext = ext_list[0]
        
        if isinstance(ext, dict):
            print(f"\n  ✓ Extension uploaded: {ext['_id']}")
            
            # Check metadata
            meta = ext.get('meta', {})
            print(f"\n  📊 Stored Metadata:")
            print(f"     baseName: {meta.get('baseName')}")
            print(f"     category: {meta.get('category')}")
            print(f"     revision: {meta.get('revision')}")
            
            # Check dicom_support_rule
            stored_rule = meta.get('dicom_support_rule')
            if stored_rule:
                print(f"\n  ✓✓✓ SUCCESS: dicom_support_rule stored!")
                print(f"     Type: {type(stored_rule)}")
                print(f"     Value:")
                for rule in stored_rule:
                    print(f"       - {rule}")
                
                # Verify it matches what we sent
                if 'dicom_support_rule' in metadata:
                    if stored_rule == metadata['dicom_support_rule']:
                        print(f"\n  ✅ MATCH: Stored rule matches JSON file!")
                    else:
                        print(f"\n  ⚠️  MISMATCH:")
                        print(f"     Expected: {metadata['dicom_support_rule']}")
                        print(f"     Got:      {stored_rule}")
            else:
                if 'dicom_support_rule' in metadata:
                    print(f"\n  ✗✗✗ FAILURE: dicom_support_rule NOT stored (was in JSON)")
                else:
                    print(f"\n  ℹ️  No dicom_support_rule in JSON file")
            
            return ext
        else:
            print(f"  ⚠️  Extension status: {ext}")
            return None
            
    except Exception as e:
        print(f"\n  ✗ Error uploading extension: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function"""
    print("="*70)
    print("TEST: Upload Extensions from ExtensionsIndex")
    print("="*70)
    
    # Initialize client
    print(f"\nConnecting to {SCHEME}://{HOST}:{PORT}")
    client = SlicerPackageClient(host=HOST, port=PORT, scheme=SCHEME)
    client.authenticate(USERNAME, PASSWORD)
    print("✓ Authenticated")
    
    # Clear and setup
    app = clear_database_and_setup(client)
    
    # Create dummy extension file
    print("\nCreating dummy extension file...")
    ext_file = create_dummy_extension_file()
    print(f"✓ Created: {ext_file}")
    
    # Upload extensions
    extensions_dir = os.path.join(os.path.dirname(__file__), '..', 'ExtensionsIndex')
    results = []
    
    for ext_json in EXTENSIONS_TO_TEST:
        json_path = os.path.join(extensions_dir, ext_json)
        if os.path.exists(json_path):
            ext = upload_extension_from_json(client, json_path, ext_file)
            results.append({
                'name': ext_json,
                'success': ext is not None,
                'extension': ext
            })
        else:
            print(f"\n⚠️  File not found: {json_path}")
    
    # Clean up
    os.unlink(ext_file)
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"{status} {result['name']}")
        if result['success'] and result['extension']:
            meta = result['extension'].get('meta', {})
            if meta.get('dicom_support_rule'):
                print(f"  → dicom_support_rule: STORED ✓")
            else:
                print(f"  → dicom_support_rule: NOT STORED")
    
    print("\n" + "="*70)

if __name__ == '__main__':
    main()
