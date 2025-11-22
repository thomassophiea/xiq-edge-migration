"""
XIQ Configuration Parser
Extracts SSIDs, VLANs, Radio Profiles, and other wireless objects from XIQ configuration
"""

import json
from typing import Dict, List, Any
from pathlib import Path


class XIQParser:
    """Parser for Extreme Cloud IQ configuration files"""

    def __init__(self, config_file: str):
        """
        Initialize the XIQ parser

        Args:
            config_file: Path to XIQ configuration file (JSON format)
        """
        self.config_file = Path(config_file)
        self.raw_config = None

    def parse(self) -> Dict[str, Any]:
        """
        Parse XIQ configuration and extract relevant objects

        Returns:
            Dictionary containing extracted configuration objects
        """
        # Load the configuration file
        with open(self.config_file, 'r') as f:
            self.raw_config = json.load(f)

        # Extract different configuration components
        extracted_config = {
            'ssids': self._extract_ssids(),
            'vlans': self._extract_vlans(),
            'radio_profiles': self._extract_radio_profiles(),
            'wlan_policies': self._extract_wlan_policies(),
            'authentication': self._extract_authentication(),
            'qos_profiles': self._extract_qos_profiles(),
            'captive_portals': self._extract_captive_portals(),
            'user_profiles': self._extract_user_profiles()
        }

        return extracted_config

    def _extract_ssids(self) -> List[Dict[str, Any]]:
        """Extract SSID configurations"""
        ssids = []

        # XIQ typically stores SSIDs in various possible locations
        # Check multiple common paths in the configuration
        possible_paths = [
            ['ssids'],
            ['wireless', 'ssids'],
            ['network_policy', 'ssids'],
            ['wlan', 'ssids']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    ssids.extend(data)
                elif isinstance(data, dict):
                    ssids.extend(data.values())
                break

        # Normalize SSID data
        normalized_ssids = []
        for ssid in ssids:
            normalized_ssids.append({
                'name': ssid.get('ssid_name', ssid.get('name', '')),
                'enabled': ssid.get('enabled', ssid.get('status') == 'enabled'),
                'broadcast_ssid': ssid.get('broadcast_ssid', True),
                'vlan_id': ssid.get('vlan_id', ssid.get('vlan', None)),
                'security': self._extract_ssid_security(ssid),
                'max_clients': ssid.get('max_clients', ssid.get('client_limit', 0)),
                'band_steering': ssid.get('band_steering', False),
                'fast_roaming': ssid.get('fast_roaming', False),
                'radio_profile': ssid.get('radio_profile', None),
                'qos_profile': ssid.get('qos_profile', None),
                'captive_portal': ssid.get('captive_portal', None),
                'original': ssid  # Keep original for reference
            })

        return normalized_ssids

    def _extract_ssid_security(self, ssid: Dict[str, Any]) -> Dict[str, Any]:
        """Extract security settings from SSID configuration"""
        security = ssid.get('security', ssid.get('security_settings', {}))

        return {
            'type': security.get('type', security.get('auth_type', 'open')),
            'encryption': security.get('encryption', security.get('cipher', 'none')),
            'psk': security.get('psk', security.get('passphrase', None)),
            'radius_servers': security.get('radius_servers', []),
            'wpa_version': security.get('wpa_version', security.get('wpa', 'WPA2')),
            'pmf': security.get('pmf', security.get('management_frame_protection', 'optional'))
        }

    def _extract_vlans(self) -> List[Dict[str, Any]]:
        """Extract VLAN configurations"""
        vlans = []

        possible_paths = [
            ['vlans'],
            ['network', 'vlans'],
            ['network_policy', 'vlans']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    vlans.extend(data)
                elif isinstance(data, dict):
                    vlans.extend(data.values())
                break

        # Normalize VLAN data
        normalized_vlans = []
        for vlan in vlans:
            normalized_vlans.append({
                'vlan_id': vlan.get('vlan_id', vlan.get('id', None)),
                'name': vlan.get('name', vlan.get('vlan_name', f"VLAN_{vlan.get('vlan_id')}")),
                'description': vlan.get('description', ''),
                'subnet': vlan.get('subnet', None),
                'gateway': vlan.get('gateway', None),
                'dhcp_enabled': vlan.get('dhcp_enabled', False),
                'original': vlan
            })

        return normalized_vlans

    def _extract_radio_profiles(self) -> List[Dict[str, Any]]:
        """Extract radio profile configurations"""
        profiles = []

        possible_paths = [
            ['radio_profiles'],
            ['wireless', 'radio_profiles'],
            ['rf_profiles']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    profiles.extend(data)
                elif isinstance(data, dict):
                    profiles.extend(data.values())
                break

        # Normalize radio profiles
        normalized_profiles = []
        for profile in profiles:
            normalized_profiles.append({
                'name': profile.get('name', ''),
                'band': profile.get('band', profile.get('radio_band', '2.4GHz')),
                'channel': profile.get('channel', 'auto'),
                'channel_width': profile.get('channel_width', profile.get('bandwidth', '20MHz')),
                'tx_power': profile.get('tx_power', profile.get('power', 'auto')),
                'min_rssi': profile.get('min_rssi', None),
                'max_clients': profile.get('max_clients', 0),
                'original': profile
            })

        return normalized_profiles

    def _extract_wlan_policies(self) -> List[Dict[str, Any]]:
        """Extract WLAN policy configurations"""
        policies = []

        possible_paths = [
            ['wlan_policies'],
            ['policies', 'wlan'],
            ['network_policy']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    policies.extend(data)
                elif isinstance(data, dict):
                    policies.extend(data.values())
                break

        return policies

    def _extract_authentication(self) -> List[Dict[str, Any]]:
        """Extract authentication server configurations"""
        auth_servers = []

        possible_paths = [
            ['authentication', 'radius'],
            ['radius_servers'],
            ['aaa', 'radius']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    auth_servers.extend(data)
                elif isinstance(data, dict):
                    auth_servers.extend(data.values())
                break

        return auth_servers

    def _extract_qos_profiles(self) -> List[Dict[str, Any]]:
        """Extract QoS profile configurations"""
        qos_profiles = []

        possible_paths = [
            ['qos_profiles'],
            ['qos'],
            ['wireless', 'qos']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    qos_profiles.extend(data)
                elif isinstance(data, dict):
                    qos_profiles.extend(data.values())
                break

        return qos_profiles

    def _extract_captive_portals(self) -> List[Dict[str, Any]]:
        """Extract captive portal configurations"""
        portals = []

        possible_paths = [
            ['captive_portals'],
            ['captive_portal'],
            ['guest_access', 'portals']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    portals.extend(data)
                elif isinstance(data, dict):
                    portals.extend(data.values())
                break

        return portals

    def _extract_user_profiles(self) -> List[Dict[str, Any]]:
        """Extract user profile configurations"""
        profiles = []

        possible_paths = [
            ['user_profiles'],
            ['users', 'profiles'],
            ['guest_access', 'user_profiles']
        ]

        for path in possible_paths:
            data = self._get_nested_value(self.raw_config, path)
            if data:
                if isinstance(data, list):
                    profiles.extend(data)
                elif isinstance(data, dict):
                    profiles.extend(data.values())
                break

        return profiles

    def _get_nested_value(self, data: Dict, path: List[str]) -> Any:
        """
        Get a value from nested dictionary using path

        Args:
            data: Dictionary to search
            path: List of keys representing the path

        Returns:
            Value at the path, or None if not found
        """
        current = data
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
