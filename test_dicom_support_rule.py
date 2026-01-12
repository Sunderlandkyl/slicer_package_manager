#!/usr/bin/env python
"""
Test script for verifying dicom_support_rule metadata handling
"""
import os
import tempfile
from slicer_package_manager_client import SlicerPackageClient

# Configuration
HOST = 'localhost'
PORT = 8081
SCHEME = 'http'
USERNAME = 'admin'
PASSWORD = 'adminadmin'

def create_dummy_extension_file():
    """Create a temporary dummy extension file for testing"""
    fd, path = tempfile.mkstemp(suffix='.tar.gz', prefix='test_dicom_ext_')
    with os.fdopen(fd, 'w') as f:
        f.write('This is a test extension file for DICOM support rule testing\n')
    return path

def test_dicom_support_rule():
    """Test uploading an extension with dicom_support_rule metadata"""
    
    print("=" * 70)
    print("Testing DICOM Support Rule Metadata")
    print("=" * 70)
    
    # Initialize client
    print(f"\n1. Connecting to {SCHEME}://{HOST}:{PORT}")
    spc = SlicerPackageClient(host=HOST, port=PORT, scheme=SCHEME)
    
    # Authenticate
    print(f"2. Authenticating as '{USERNAME}'...")
    spc.authenticate(username=USERNAME, password=PASSWORD)
    print("   ✓ Authenticated successfully")
    
    # Create test application if it doesn't exist
    app_name = 'DICOMTestApp'
    print(f"\n3. Creating application '{app_name}'...")
    try:
        app = spc.createApp(
            name=app_name,
            desc='Test application for DICOM support rule testing'
        )
        print(f"   ✓ Application created: {app['_id']}")
    except Exception as e:
        print(f"   Note: {e}")
        apps = spc.listApp(name=app_name)
        if apps:
            print(f"   ✓ Using existing application: {apps[0]['_id']}")
    
    # Create a dummy extension file
    print("\n4. Creating dummy extension file...")
    ext_file = create_dummy_extension_file()
    print(f"   ✓ Created: {ext_file}")
    
    # Test Case 1: Upload extension with can_import_dicom using uploadExtension
    print("\n" + "=" * 70)
    print("TEST CASE 1: Extension with can_import_dicom (uploadExtension)")
    print("=" * 70)
    
    # First, let's check if the Python client supports it
    import inspect
    upload_sig = inspect.signature(spc.uploadExtension)
    has_can_import_dicom = 'can_import_dicom' in upload_sig.parameters
    
    print(f"\n   Python Client Check:")
    print(f"   - Has can_import_dicom parameter: {has_can_import_dicom}")
    
    if has_can_import_dicom:
        print("   ✓ Python client HAS can_import_dicom parameter")
        
        # Test with uploadExtension method
        extension_metadata_v2 = {
            'filepath': ext_file,
            'app_name': app_name,
            'ext_os': 'linux',
            'arch': 'amd64',
            'name': 'DICOMExtension2',
            'repo_type': 'git',
            'repo_url': 'https://github.com/test/dicom-ext2.git',
            'app_revision': '0000',
            'revision': '2000',
            'desc': 'Extension with DICOM support rule',
            'can_import_dicom': [
                'modality == "MR" and series_description contains "T1"',
                'modality == "CT" and slice_thickness < 2.0'
            ]
        }
        
        try:
            print("\n   Uploading extension with can_import_dicom...")
            ext2 = spc.uploadExtension(**extension_metadata_v2)
            print(f"   ✓ Extension uploaded successfully")
            
            # Retrieve and verify
            if isinstance(ext2, int):
                ext_list = spc.listExtension(
                    app_name=app_name, 
                    name='DICOMExtension2',
                    ext_os='linux',
                    arch='amd64'
                )
                if ext_list:
                    ext2 = ext_list[0]
            
            if isinstance(ext2, dict):
                print(f"\n   Extension Details:")
                print(f"   - Name: {ext2['name']}")
                print(f"   - ID: {ext2['_id']}")
                
                # Check if can_import_dicom is in metadata
                can_import_dicom = ext2.get('meta', {}).get('can_import_dicom')
                if can_import_dicom:
                    print(f"   ✓✓✓ SUCCESS: can_import_dicom found!")
                    print(f"   Rules:")
                    for i, rule in enumerate(can_import_dicom, 1):
                        print(f"      {i}. {rule}")
                else:
                    print(f"   ✗✗✗ FAILURE: can_import_dicom NOT in metadata")
                    print(f"   Available metadata keys: {list(ext2.get('meta', {}).keys())}")
                    
        except Exception as e:
            print(f"   ✗ Error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n   ⚠ Python client does NOT support can_import_dicom parameter yet")
        print("   This needs to be added to the client API")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print("\nTo fully support can_import_dicom, the following updates are needed:")
    print("\n1. Backend API (slicer_package_manager/api/app.py):")
    print("   - Add .jsonParam('can_import_dicom', ...) decorator")
    print("   - Add can_import_dicom parameter to createOrUpdateExtension()")
    print("   - Add to params dict if provided")
    print("\n2. Extension Model (slicer_package_manager/models/extension.py):")
    print("   - Add 'can_import_dicom' to extra_params set")
    print("   - Ensure array validation is working")
    print("\n3. Python Client (python_client/slicer_package_manager_client/):")
    print("   - Add can_import_dicom parameter to uploadExtension()")
    print("   - Add to CLI options")
    print("=" * 70)
    
    # Cleanup
    if os.path.exists(ext_file):
        os.remove(ext_file)
        print(f"\n✓ Cleaned up temporary file")

if __name__ == '__main__':
    test_can_import_dicom()
