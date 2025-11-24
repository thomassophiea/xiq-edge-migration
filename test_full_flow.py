#!/usr/bin/env python3
"""Test full XIQ to Edge Services flow"""

from src.xiq_api_client import XIQAPIClient
from src.config_converter import ConfigConverter
from src.campus_controller_client import CampusControllerClient

print('Step 1: Getting config from XIQ...')
xiq = XIQAPIClient.login('user@example.com', 'your-xiq-password', verbose=False)
config = xiq.get_configuration()

print(f'  SSIDs: {len(config["ssids"])}')
print(f'  VLANs: {len(config["vlans"])}')
print(f'  RADIUS: {len(config["authentication"])}')

print('\nStep 2: Converting config...')
converter = ConfigConverter()

# Test with just one SSID and one VLAN
test_config = {
    'ssids': [config['ssids'][0]],  # Just first SSID
    'vlans': config['vlans'][:1] if config['vlans'] else [],
    'authentication': []
}

print(f'\nTest SSID: {test_config["ssids"][0]["name"]}')
print(f'  Security: {test_config["ssids"][0]["security"]["type"]}')
print(f'  VLAN ID: {test_config["ssids"][0].get("vlan_id")}')

campus_config = converter.convert(test_config)

print(f'\nConverted to Edge Services format:')
print(f'  Services: {len(campus_config["services"])}')
print(f'  Topologies: {len(campus_config["topologies"])}')

if campus_config['services']:
    service = campus_config['services'][0]
    print(f'\nFirst Service:')
    print(f'  Name: {service.get("serviceName")}')
    print(f'  SSID: {service.get("ssid")}')
    print(f'  Status: {service.get("status")}')
    print(f'  Privacy: {service.get("privacy")}')

print('\nStep 3: Connecting to Edge Services...')
try:
    cc = CampusControllerClient(
        'https://your-controller.example.com',
        'admin',
        'your-password',
        verbose=True
    )
    print('  ✓ Connected!')

    print('\nStep 4: Posting configuration...')
    results = cc.post_configuration(campus_config)

    print('\nResults:')
    print(f'  Success: {results["success"]}')
    print(f'  Details: {results["details"]}')
    if results['errors']:
        print(f'  Errors:')
        for error in results['errors']:
            print(f'    - {error}')

except Exception as e:
    print(f'  ✗ Error: {e}')
    import traceback
    traceback.print_exc()
