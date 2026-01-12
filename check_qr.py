#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Check specific extension metadata"""
import requests

APP_ID = '696ea9dc5efce88cc8e174c5'
params = {
    'os': 'linux',
    'arch': 'amd64',
    'app_revision': '32516',
    'limit': 0
}

resp = requests.get(
    f'http://127.0.0.1:8081/api/v1/app/{APP_ID}/extension',
    params=params
)

if resp.ok:
    exts = resp.json()
    
    # Find QuantitativeReporting
    for ext in exts:
        if ext.get('meta', {}).get('baseName') == 'QuantitativeReporting':
            meta = ext['meta']
            print(f"QuantitativeReporting metadata:")
            print(f"  ID: {ext['_id']}")
            print(f"  dicom_support_rule: {meta.get('dicom_support_rule')}")
            break
else:
    print(f"Error: {resp.status_code}")
