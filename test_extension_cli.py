#!/usr/bin/env python
"""
Simple CLI test for extension metadata
Run this after the server is up at http://localhost:8081
"""
import os
import sys

# Test configuration
API_URL = "http://localhost:8081/api/v1"
USERNAME = "admin"
PASSWORD = "adminadmin"
APP_NAME = "TestApp"

def print_section(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def run_command(cmd):
    """Run a shell command and print it"""
    print(f"\n$ {cmd}")
    return os.system(cmd)

# Instructions
print_section("Extension Metadata Testing Guide")

print("""
This guide will help you test extension metadata using the CLI.

Prerequisites:
1. Docker container running at http://localhost:8081
2. Python client installed (already done ✓)

Commands to test:
""")

print("\n1. Create an application:")
print(f"""
slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} \\
  app create {APP_NAME} "Test application for metadata testing"
""")

print("\n2. Create a test extension file:")
print("""
echo "Test extension content" > test_extension.tar.gz
""")

print("\n3. Upload extension with basic metadata:")
print(f"""
slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} \\
  extension upload {APP_NAME} test_extension.tar.gz \\
  --os linux \\
  --arch amd64 \\
  --name MyTestExtension \\
  --repo_type git \\
  --repo_url https://github.com/user/extension.git \\
  --app_revision 0000 \\
  --revision 12345 \\
  --desc "A test extension with metadata"
""")

print("\n4. Upload extension with FULL metadata:")
print(f"""
slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} \\
  extension upload {APP_NAME} test_extension.tar.gz \\
  --os linux \\
  --arch amd64 \\
  --name MyTestExtension \\
  --repo_type git \\
  --repo_url https://github.com/user/extension.git \\
  --app_revision 0000 \\
  --revision 12346 \\
  --desc "A test extension with full metadata" \\
  --icon_url "https://example.com/icon.png" \\
  --category "Testing" \\
  --homepage "https://example.com/extension" \\
  --contributors "John Doe, Jane Smith" \\
  --dependency "SomeOtherExtension"
""")

print("\n5. List all extensions:")
print(f"""
slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} \\
  extension list {APP_NAME} --all
""")

print("\n6. Download an extension:")
print(f"""
slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} \\
  extension download {APP_NAME} MyTestExtension
""")

print_section("Interactive Testing")
response = input("\nWould you like to run automated tests now? (y/n): ")

if response.lower() == 'y':
    print("\nRunning automated tests...")
    
    # Create dummy file
    print_section("Step 1: Creating test file")
    with open('test_extension.tar.gz', 'w') as f:
        f.write("Test extension content\n")
    print("✓ Created test_extension.tar.gz")
    
    # Create app
    print_section("Step 2: Creating application")
    cmd = f'slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} app create {APP_NAME} "Test application"'
    run_command(cmd)
    
    # Upload extension
    print_section("Step 3: Uploading extension with metadata")
    cmd = (f'slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} '
           f'extension upload {APP_NAME} test_extension.tar.gz '
           f'--os linux --arch amd64 --name TestExt --repo_type git '
           f'--repo_url https://github.com/test/ext.git --app_revision 0000 --revision 12345 '
           f'--desc "Test extension with metadata"')
    run_command(cmd)
    
    # List extensions
    print_section("Step 4: Listing extensions")
    cmd = f'slicer_package_manager_client --api-url {API_URL} --username {USERNAME} --password {PASSWORD} extension list {APP_NAME} --all'
    run_command(cmd)
    
    print_section("Testing Complete!")
    print("Check the output above to verify metadata was saved correctly.")
    
    # Cleanup
    if os.path.exists('test_extension.tar.gz'):
        os.remove('test_extension.tar.gz')
        print("\n✓ Cleaned up test_extension.tar.gz")
else:
    print("\nYou can run the commands above manually.")
    print("Exiting...")
