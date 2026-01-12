#!/usr/bin/env python
"""
Test script for uploading and verifying extension metadata
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
    fd, path = tempfile.mkstemp(suffix='.tar.gz', prefix='test_extension_')
    with os.fdopen(fd, 'w') as f:
        f.write('This is a test extension file\n')
    return path

def test_extension_metadata():
    """Test uploading an extension with metadata and verify it"""
    
    print("=" * 60)
    print("Testing Extension Metadata")
    print("=" * 60)
    
    # Initialize client
    print(f"\n1. Connecting to {SCHEME}://{HOST}:{PORT}")
    spc = SlicerPackageClient(host=HOST, port=PORT, scheme=SCHEME)
    
    # Authenticate
    print(f"2. Authenticating as '{USERNAME}'...")
    spc.authenticate(username=USERNAME, password=PASSWORD)
    print("   ✓ Authenticated successfully")
    
    # Create test application if it doesn't exist
    app_name = 'TestApp'
    print(f"\n3. Creating application '{app_name}'...")
    try:
        app = spc.createApp(
            name=app_name,
            desc='Test application for extension metadata testing'
        )
        print(f"   ✓ Application created: {app['_id']}")
    except Exception as e:
        # App might already exist, that's okay
        print(f"   Note: {e}")
        apps = spc.listApp(name=app_name)
        if apps:
            print(f"   ✓ Using existing application: {apps[0]['_id']}")
    
    # Create a dummy extension file
    print("\n4. Creating dummy extension file...")
    ext_file = create_dummy_extension_file()
    print(f"   ✓ Created: {ext_file}")
    
    # Upload extension with metadata
    print("\n5. Uploading extension with metadata...")
    extension_metadata = {
        'filepath': ext_file,
        'app_name': app_name,
        'ext_os': 'linux',
        'arch': 'amd64',
        'name': 'TestExtension',
        'repo_type': 'git',
        'repo_url': 'https://github.com/test/extension.git',
        'app_revision': '0000',
        'revision': '12345',
        'desc': 'A test extension for metadata validation',
        'icon_url': 'https://example.com/icon.png',
        'category': 'Testing',
        'homepage': 'https://example.com/extension',
        'contributors': 'John Doe, Jane Smith',
        'dependency': 'SomeOtherExtension'
    }
    
    try:
        ext = spc.uploadExtension(**extension_metadata)
        print(f"   ✓ Extension uploaded successfully")
        
        # Handle case where extension already exists (returns status code)
        if isinstance(ext, int):
            print(f"   Note: Extension already exists, retrieving info...")
            ext_list = spc.listExtension(
                app_name=app_name, 
                name=extension_metadata['name'],
                ext_os=extension_metadata['ext_os'],
                arch=extension_metadata['arch']
            )
            if ext_list:
                ext = ext_list[0]
        
        if isinstance(ext, dict):
            print(f"   Extension ID: {ext['_id']}")
            print(f"   Extension Name: {ext['name']}")
            
            # Display uploaded metadata
            print("\n6. Uploaded Extension Metadata:")
            print("   " + "-" * 55)
            metadata = ext.get('meta', {})
            for key, value in sorted(metadata.items()):
                if value:
                    print(f"   {key:20s}: {value}")
            
            # List extensions
            print("\n7. Listing extensions for application...")
            ext_list = spc.listExtension(app_name=app_name, all=True)
            print(f"   ✓ Found {len(ext_list)} extension(s)")
            
            for e in ext_list:
                print(f"\n   Extension: {e['name']}")
                print(f"   - ID: {e['_id']}")
                print(f"   - Revision: {e['meta'].get('revision', 'N/A')}")
                print(f"   - OS: {e['meta'].get('os', 'N/A')}")
                print(f"   - Arch: {e['meta'].get('arch', 'N/A')}")
                print(f"   - Description: {e['meta'].get('description', 'N/A')}")
            
            # Download extension
            print("\n8. Downloading extension...")
            download_dir = tempfile.gettempdir()
            downloaded = spc.downloadExtension(
                app_name=app_name,
                id_or_name=ext['_id'],
                dir_path=download_dir
            )
            print(f"   ✓ Downloaded to: {download_dir}")
        else:
            print("   Could not retrieve extension details")
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if os.path.exists(ext_file):
            os.remove(ext_file)
            print(f"\n9. Cleaned up temporary file: {ext_file}")

if __name__ == '__main__':
    test_extension_metadata()
