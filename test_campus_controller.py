#!/usr/bin/env python3
"""Test Edge Services API connection"""

import requests
import json
import warnings
warnings.filterwarnings('ignore')

base_url = "https://tsophiea.ddns.net"
username = "admin"
password = "TSts1232!!*7"

print("Testing Edge Services API...")
print("="*60)

# Step 1: Test OAuth 2.0 authentication
print("\n1. Testing OAuth 2.0 authentication...")
auth_url = f"{base_url}:5825/management/v1/oauth2/token"

print(f"   URL: {auth_url}")

auth_data = {
    "grant_type": "password",
    "username": username,
    "password": password
}

try:
    response = requests.post(
        auth_url,
        data=auth_data,
        verify=False,
        timeout=10
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        token_data = response.json()
        print(f"   ✓ Authentication successful")
        print(f"   Token type: {token_data.get('token_type')}")

        access_token = token_data.get('access_token')

        # Step 2: Test API endpoints with token
        print("\n2. Testing API endpoints...")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        endpoints = [
            "/management/v1/services",
            "/management/v1/topologies",
            "/management/v1/aaapolicy"
        ]

        for endpoint in endpoints:
            url = f"{base_url}:5825{endpoint}"
            print(f"\n   Testing: {endpoint}")

            resp = requests.get(url, headers=headers, verify=False, timeout=10)
            print(f"   Status: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                print(f"   Response type: {type(data).__name__}")
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
                elif isinstance(data, list):
                    print(f"   List length: {len(data)}")

    else:
        print(f"   ✗ Authentication failed")
        print(f"   Response: {response.text[:200]}")

except Exception as e:
    print(f"   ✗ Error: {e}")

# Step 3: Test creating a simple service
print("\n3. Testing POST to /services...")

if response.status_code == 200:
    test_service = {
        "serviceName": "TEST_SSID_FROM_XIQ",
        "ssid": "TEST_SSID_FROM_XIQ",
        "status": "disabled",
        "suppressSsid": False,
        "privacy": None,
        "enableCaptivePortal": False,
        "mbaAuthorization": False,
        "defaultTopology": None,
        "defaultCoS": None,
        "proxied": "Local",
        "features": ["CENTRALIZED-SITE"]
    }

    url = f"{base_url}:5825/management/v1/services"

    try:
        resp = requests.post(
            url,
            headers=headers,
            json=test_service,
            verify=False,
            timeout=10
        )

        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.text[:500]}")

    except Exception as e:
        print(f"   Error: {e}")
