#!/usr/bin/env python
"""
Test to verify how girder_client sends JSON data
"""
import json
from unittest.mock import patch
from slicer_package_manager_client import SlicerPackageClient

# Intercept the actual HTTP request
with patch('girder_client.GirderClient.sendRestRequest') as mock_send:
    mock_send.return_value = {'_id': 'test123', 'name': 'test', 'meta': {}}
    
    spc = SlicerPackageClient(host='localhost', port=8081, scheme='http')
    
    # Simulate what happens when we call sendRestRequest
    result = spc.sendRestRequest(
        'POST',
        '/app/test_id/extension',
        parameters={'os': 'linux', 'arch': 'amd64'},
        json={'can_import_dicom': ['rule1']}
    )
    
    # Check what was called
    print("Mock was called:", mock_send.called)
    print("Call count:", mock_send.call_count)
    print("\nCall args:")
    args, kwargs = mock_send.call_args
    print(f"  args: {args}")
    print(f"  kwargs: {json.dumps({k: v for k, v in kwargs.items() if v is not None}, indent=2)}")
