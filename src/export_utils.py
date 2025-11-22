"""
Export Utilities
Handles exporting configurations to various formats (CSV, JSON, etc.)
"""

import csv
import json
from typing import Dict, List, Any
from pathlib import Path


def export_to_json(data: Dict[str, Any], output_file: str, pretty: bool = True):
    """
    Export data to JSON file

    Args:
        data: Dictionary to export
        output_file: Output file path
        pretty: Whether to pretty-print (indent) the JSON
    """
    with open(output_file, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)


def export_ssids_to_csv(ssids: List[Dict[str, Any]], output_file: str):
    """
    Export SSIDs to CSV format

    Args:
        ssids: List of SSID configurations
        output_file: Output CSV file path
    """
    if not ssids:
        return

    # Define CSV columns
    fieldnames = [
        'name',
        'enabled',
        'broadcast_ssid',
        'vlan_id',
        'security_type',
        'security_encryption',
        'psk',
        'max_clients',
        'band_steering',
        'fast_roaming',
        'wpa_version',
        'pmf',
        'policy_id'
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for ssid in ssids:
            security = ssid.get('security', {})
            row = {
                'name': ssid.get('name', ''),
                'enabled': ssid.get('enabled', True),
                'broadcast_ssid': ssid.get('broadcast_ssid', True),
                'vlan_id': ssid.get('vlan_id', ''),
                'security_type': security.get('type', 'open'),
                'security_encryption': security.get('encryption', 'none'),
                'psk': security.get('psk', ''),
                'max_clients': ssid.get('max_clients', 0),
                'band_steering': ssid.get('band_steering', False),
                'fast_roaming': ssid.get('fast_roaming', False),
                'wpa_version': security.get('wpa_version', ''),
                'pmf': security.get('pmf', ''),
                'policy_id': ssid.get('policy_id', '')
            }
            writer.writerow(row)


def export_vlans_to_csv(vlans: List[Dict[str, Any]], output_file: str):
    """
    Export VLANs to CSV format

    Args:
        vlans: List of VLAN configurations
        output_file: Output CSV file path
    """
    if not vlans:
        return

    # Define CSV columns - complete VLAN object model
    fieldnames = [
        'vlan_id',
        'name',
        'description',
        'subnet',
        'gateway',
        'netmask',
        'dhcp_enabled',
        'dhcp_start',
        'dhcp_end',
        'dhcp_lease_time',
        'dhcp_dns_servers',
        'group',
        'classification_rules',
        'tagged',
        'mtu',
        'enabled',
        'policy_id'
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for vlan in vlans:
            # Handle list fields for CSV
            dns_servers = vlan.get('dhcp_dns_servers', [])
            dns_servers_str = ';'.join(dns_servers) if isinstance(dns_servers, list) else str(dns_servers)

            classification = vlan.get('classification_rules', [])
            classification_str = ';'.join([str(r) for r in classification]) if isinstance(classification, list) else str(classification)

            row = {
                'vlan_id': vlan.get('vlan_id', ''),
                'name': vlan.get('name', ''),
                'description': vlan.get('description', ''),
                'subnet': vlan.get('subnet', ''),
                'gateway': vlan.get('gateway', ''),
                'netmask': vlan.get('netmask', ''),
                'dhcp_enabled': vlan.get('dhcp_enabled', False),
                'dhcp_start': vlan.get('dhcp_start', ''),
                'dhcp_end': vlan.get('dhcp_end', ''),
                'dhcp_lease_time': vlan.get('dhcp_lease_time', ''),
                'dhcp_dns_servers': dns_servers_str,
                'group': vlan.get('group', 0),
                'classification_rules': classification_str,
                'tagged': vlan.get('tagged', False),
                'mtu': vlan.get('mtu', 1500),
                'enabled': vlan.get('enabled', True),
                'policy_id': vlan.get('policy_id', '')
            }
            writer.writerow(row)


def export_radius_servers_to_csv(servers: List[Dict[str, Any]], output_file: str):
    """
    Export RADIUS servers to CSV format

    Args:
        servers: List of RADIUS server configurations
        output_file: Output CSV file path
    """
    if not servers:
        return

    fieldnames = [
        'name',
        'ip',
        'auth_port',
        'acct_port',
        'secret',
        'timeout',
        'retries',
        'enabled'
    ]

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for server in servers:
            row = {
                'name': server.get('name', ''),
                'ip': server.get('ip', ''),
                'auth_port': server.get('auth_port', 1812),
                'acct_port': server.get('acct_port', 1813),
                'secret': server.get('secret', ''),
                'timeout': server.get('timeout', 5),
                'retries': server.get('retries', 3),
                'enabled': server.get('enabled', True)
            }
            writer.writerow(row)


def export_all_to_csv(config: Dict[str, Any], output_dir: str):
    """
    Export all configuration objects to separate CSV files

    Args:
        config: Configuration dictionary with ssids, vlans, authentication
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Export each object type
    if config.get('ssids'):
        export_ssids_to_csv(
            config['ssids'],
            str(output_path / 'ssids.csv')
        )

    if config.get('vlans'):
        export_vlans_to_csv(
            config['vlans'],
            str(output_path / 'vlans.csv')
        )

    if config.get('authentication'):
        export_radius_servers_to_csv(
            config['authentication'],
            str(output_path / 'radius_servers.csv')
        )

    return {
        'ssids': str(output_path / 'ssids.csv') if config.get('ssids') else None,
        'vlans': str(output_path / 'vlans.csv') if config.get('vlans') else None,
        'radius_servers': str(output_path / 'radius_servers.csv') if config.get('authentication') else None
    }
