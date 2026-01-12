"""
Script to upload extension metadata with dicom_support_rule to Girder server.
"""
import json
import sys
from pathlib import Path

# Add python_client to path
sys.path.insert(0, str(Path(__file__).parent / 'python_client'))

from slicer_package_manager_client import SlicerPackageClient


def load_extension_metadata(extension_name, extensions_index_dir):
    """Load extension metadata from ExtensionsIndex JSON file."""
    json_file = extensions_index_dir / f"{extension_name}.json"
    if not json_file.exists():
        raise FileNotFoundError(f"Extension file not found: {json_file}")
    
    with open(json_file, 'r') as f:
        return json.load(f)


def main():
    # Configuration
    host = "127.0.0.1"
    port = 8081
    scheme = "http"
    username = "admin"
    password = "adminadmin"
    app_name = "Slicer"
    
    extensions_index_dir = Path(__file__).parent.parent / "ExtensionsIndex"
    
    # Extensions to update
    extensions = [
        "PETDICOMExtension",
        "QuantitativeReporting",
        "SlicerHeart",
        "SlicerRT"
    ]
    
    print(f"Connecting to Girder at {scheme}://{host}:{port}...")
    client = SlicerPackageClient(host=host, port=port, scheme=scheme)
    
    print(f"Authenticating as {username}...")
    client.authenticate(username, password)
    
    print(f"\nLooking for application: {app_name}")
    apps = client.listApp()
    app = next((a for a in apps if a['name'] == app_name), None)
    
    if not app:
        print(f"Application '{app_name}' not found. Available applications:")
        for a in apps:
            print(f"  - {a['name']}")
        return 1
    
    app_id = app['_id']
    app_name_found = app['name']
    print(f"Found application: {app_name_found} (ID: {app_id})")
    
    # Get latest release
    releases = client.listRelease(app_name=app_name)
    if not releases:
        print(f"No releases found for {app_name}")
        return 1
    
    latest_release = releases[0]
    print(f"Using release: {latest_release['name']} (app_revision: {latest_release.get('meta', {}).get('app_revision', 'N/A')})")
    
    # Update each extension
    for ext_name in extensions:
        print(f"\n{'='*60}")
        print(f"Processing {ext_name}...")
        print(f"{'='*60}")
        
        try:
            metadata = load_extension_metadata(ext_name, extensions_index_dir)
            print(f"Loaded metadata from {ext_name}.json")
            
            # Get dicom_support_rule
            dicom_support_rule = metadata.get('dicom_support_rule')
            if dicom_support_rule:
                print(f"DICOM support rules ({len(dicom_support_rule)}):")
                for rule in dicom_support_rule:
                    print(f"  - {rule}")
            else:
                print("No dicom_support_rule found in metadata")
            
            # Find existing extension in Girder
            print(f"\nSearchching for existing extension...")
            extensions_list = client.listExtension(
                app_name=app_name,
                release=latest_release['name']
            )
            
            existing_ext = next(
                (e for e in extensions_list if e.get('meta', {}).get('baseName') == ext_name),
                None
            )
            
            if existing_ext:
                print(f"Found existing extension: {existing_ext['name']}")
                print(f"  ID: {existing_ext['_id']}")
                
                # Update metadata
                print(f"Updating metadata...")
                current_meta = existing_ext.get('meta', {})
                
                # Prepare update - only update dicom_support_rule
                if dicom_support_rule:
                    print(f"Setting dicom_support_rule field...")
                    # Use the raw REST API to update just the metadata
                    import json as json_mod
                    response = client.post(
                        f"/app/{app_id}/extension",
                        parameters={
                            'os': current_meta.get('os'),
                            'arch': current_meta.get('arch'),
                            'baseName': current_meta.get('baseName'),
                            'repository_type': current_meta.get('repository_type'),
                            'repository_url': metadata.get('scm_url', current_meta.get('repository_url', '')),
                            'revision': current_meta.get('revision'),
                            'app_revision': current_meta.get('app_revision'),
                            'description': current_meta.get('description', ''),
                            'dicom_support_rule': json_mod.dumps(dicom_support_rule)
                        }
                    )
                    print(f"✓ Successfully updated {ext_name}")
                else:
                    print(f"⚠ No dicom_support_rule to update")
            else:
                print(f"⚠ Extension not found in Girder release")
                print(f"  You may need to create it first or it may be in a different release")
                
        except Exception as e:
            print(f"✗ Error processing {ext_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Update complete!")
    print(f"{'='*60}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
