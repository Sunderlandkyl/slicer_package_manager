"""Enable slicer_package_manager plugin via Girder API."""
import requests
import time

# Configuration
host = "127.0.0.1"
port = 8081
username = "admin"
password = "adminadmin"

base_url = f"http://{host}:{port}/api/v1"

print(f"Connecting to Girder at {base_url}...")

# Authenticate
auth_url = f"{base_url}/user/authentication"
response = requests.get(auth_url, auth=(username, password))
response.raise_for_status()
token = response.json()['authToken']['token']
print(f"Authenticated successfully")

# Enable plugin
headers = {"Girder-Token": token}
plugins_url = f"{base_url}/system/plugins"

print("\nEnabling slicer_package_manager plugin...")
response = requests.put(
    plugins_url,
    headers=headers,
    json={"plugins": ["slicer_package_manager"]}
)
response.raise_for_status()
print("Plugin enabled")

# Restart Girder
print("\nRestarting Girder...")
restart_url = f"{base_url}/system/restart"
response = requests.put(restart_url, headers=headers)
response.raise_for_status()
print("Restart initiated")

print("\nWaiting for Girder to restart...")
time.sleep(10)

# Verify plugin is active
print("Verifying plugin is active...")
response = requests.get(f"{base_url}/system/plugins", headers=headers)
if response.status_code == 200:
    plugins = response.json()
    enabled_plugins = plugins.get("enabled", [])
    if "slicer_package_manager" in enabled_plugins:
        print("✓ slicer_package_manager plugin is enabled!")
    else:
        print(f"⚠ Plugin not in enabled list. Enabled plugins: {enabled_plugins}")
else:
    print(f"Could not verify (server may still be restarting): {response.status_code}")

print("\nDone!")
