"""
XIQ API Client
Pulls configuration directly from Extreme Cloud IQ via REST API
Based on ExtremeCloud IQ Extractor patterns
"""

import requests
import json
from typing import Dict, List, Any, Optional
import warnings

warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class XIQAPIClient:
    """Client for interacting with Extreme Cloud IQ API"""

    def __init__(self, api_token: str, base_url: str = "https://api.extremecloudiq.com", verify_ssl: bool = True, verbose: bool = False):
        """
        Initialize XIQ API client with existing API token

        Args:
            api_token: XIQ API token (from XIQ Global Settings > API Token Management)
            base_url: API base URL (default: https://api.extremecloudiq.com)
            verify_ssl: Whether to verify SSL certificates
            verbose: Enable verbose logging
        """
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.verbose = verbose
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.verify = verify_ssl

    @classmethod
    def login(cls, username: str, password: str, base_url: str = "https://api.extremecloudiq.com", verify_ssl: bool = True, verbose: bool = False):
        """
        Authenticate with username and password to get access token

        Args:
            username: ExtremeCloud IQ username (email)
            password: ExtremeCloud IQ password
            base_url: API base URL (default: https://api.extremecloudiq.com)
            verify_ssl: Whether to verify SSL certificates
            verbose: Enable verbose logging

        Returns:
            XIQAPIClient instance

        Raises:
            Exception: If authentication fails
        """
        if verbose:
            print("  Authenticating to ExtremeCloud IQ...")

        login_url = f"{base_url}/login"

        payload = {
            "username": username,
            "password": password
        }

        try:
            response = requests.post(login_url, json=payload, verify=verify_ssl)

            if response.status_code == 401:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error_message', 'Invalid credentials')
                    raise Exception(f"Authentication failed: {error_msg}")
                except:
                    raise Exception("Authentication failed: Invalid username or password")

            response.raise_for_status()

            data = response.json()
            access_token = data.get("access_token")

            if not access_token:
                raise Exception("No access token received from login")

            if verbose:
                print("  ✓ Authentication successful")

            return cls(access_token, base_url, verify_ssl, verbose)

        except requests.exceptions.RequestException as e:
            if "Authentication failed:" not in str(e):
                raise Exception(f"Authentication failed: {e}")
            raise

    def _make_request(self, endpoint: str, method: str = "GET", params: dict = None) -> Optional[Dict]:
        """Make an API request with error handling"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, headers=self.headers, params=params, verify=self.verify_ssl)
            response.raise_for_status()
            result = response.json()

            if self.verbose:
                print(f"    DEBUG: {endpoint} returned type: {type(result)}")
                if isinstance(result, dict):
                    print(f"    DEBUG: Keys: {list(result.keys())}")
                elif isinstance(result, list):
                    print(f"    DEBUG: List length: {len(result)}")

            return result
        except requests.exceptions.RequestException as e:
            if self.verbose:
                print(f"  Error fetching {endpoint}: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"    Status code: {e.response.status_code}")
                    try:
                        print(f"    Response: {e.response.text[:200]}")
                    except:
                        pass
            return None

    def _make_request_with_pagination(self, endpoint: str) -> List[Dict]:
        """Make paginated API requests and return all items"""
        all_items = []
        page = 1

        while True:
            params = {"page": page, "limit": 100}
            result = self._make_request(endpoint, params=params)

            if not result:
                break

            # XIQ API uses 'data' field for paginated responses
            items = []
            if isinstance(result, list):
                # Response is already a list
                items = result
            elif isinstance(result, dict):
                # XIQ specifically uses 'data' field
                items = result.get('data', result.get('items', result.get('results', [])))

            if not items:
                break

            all_items.extend(items)

            # Check pagination info
            if isinstance(result, dict):
                total_pages = result.get('total_pages', result.get('totalPages', 1))
                if page >= total_pages:
                    break
            else:
                # If response is a list, we got everything
                break

            page += 1

        if self.verbose and all_items:
            print(f"    DEBUG: Retrieved {len(all_items)} total items")

        return all_items

    def get_configuration(self, network_policy_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get wireless configuration from XIQ

        Args:
            network_policy_id: Optional network policy ID to filter by

        Returns:
            Dictionary containing extracted configuration
        """
        if self.verbose:
            print("Retrieving configuration from Extreme Cloud IQ...")

        # Get all configuration objects
        network_policies = self.get_network_policies()
        user_profiles = self.get_user_profiles()
        all_vlans = self.get_vlans()
        all_ssids = self.get_ssids()

        # Create lookup tables
        user_profile_map = {p['id']: p for p in user_profiles if isinstance(p, dict)}
        vlan_map = {v['user_profile_id']: v for v in all_vlans if isinstance(v, dict)}

        # Link SSIDs to VLANs via user profiles
        for ssid in all_ssids:
            user_profile_id = ssid.get('default_user_profile')

            if user_profile_id and user_profile_id in user_profile_map:
                user_profile = user_profile_map[user_profile_id]
                vlan_profile = user_profile.get('vlan_profile', {})
                vlan_id = vlan_profile.get('default_vlan_id')

                # Add VLAN ID to SSID
                if vlan_id:
                    ssid['vlan_id'] = vlan_id

                # Add user profile name for reference
                ssid['user_profile_name'] = user_profile.get('name')

        config = {
            'ssids': all_ssids,
            'vlans': all_vlans,
            'radio_profiles': self.get_radio_profiles(),
            'network_policies': network_policies,
            'authentication': self.get_radius_servers(),
            'qos_profiles': [],
            'captive_portals': [],
            'user_profiles': user_profiles
        }

        if self.verbose:
            print(f"\n✓ Configuration retrieved from XIQ")
            print(f"  - SSIDs: {len(all_ssids)}")
            print(f"  - VLANs: {len(all_vlans)}")
            print(f"  - User Profiles: {len(user_profiles)}")
            print(f"  - Network Policies: {len(network_policies)}")
            print(f"  - RADIUS Servers: {len(config['authentication'])}")
            print(f"  - Radio Profiles: {len(config['radio_profiles'])}")

        return config

    def get_network_policies(self) -> List[Dict[str, Any]]:
        """Get network policies from XIQ"""
        if self.verbose:
            print("  Fetching network policies...")

        policies = self._make_request_with_pagination("/network-policies")

        if policies:
            if self.verbose:
                print(f"    ✓ Retrieved {len(policies)} network policies")
            return policies
        else:
            if self.verbose:
                print("    ⚠ No network policies found")
            return []

    def get_ssids(self) -> List[Dict[str, Any]]:
        """
        Get all SSIDs from XIQ

        Returns:
            List of SSID configurations
        """
        if self.verbose:
            print("  Fetching SSIDs...")

        endpoint = "/ssids"
        ssids = self._make_request_with_pagination(endpoint)

        if ssids:
            if self.verbose:
                print(f"    ✓ Retrieved {len(ssids)} SSIDs")

            # Normalize SSID data to common format
            normalized_ssids = []
            for ssid in ssids:
                normalized_ssids.append({
                    'name': ssid.get('ssid_name', ssid.get('name', '')),
                    'enabled': ssid.get('enabled_status') == 'ENABLE' if 'enabled_status' in ssid else ssid.get('enabled', True),
                    'broadcast_ssid': ssid.get('broadcast_ssid', True),
                    'vlan_id': ssid.get('access_vlan', ssid.get('vlan_id')),
                    'default_user_profile': ssid.get('default_user_profile'),  # XIQ user profile ID reference
                    'security': self._normalize_security(ssid),
                    'max_clients': ssid.get('user_limit', 0),
                    'band_steering': ssid.get('band_steering_mode') == 'ENABLED' if 'band_steering_mode' in ssid else False,
                    'fast_roaming': ssid.get('fast_roaming_802_11r') == 'ENABLED' if 'fast_roaming_802_11r' in ssid else False,
                    'radio_profile': ssid.get('radio_profile_id'),
                    'qos_profile': ssid.get('qos_profile_id'),
                    'captive_portal': ssid.get('captive_web_portal_id'),
                    'policy_id': ssid.get('network_policy_id'),
                    'original': ssid
                })

            return normalized_ssids
        else:
            if self.verbose:
                print(f"    ⚠ No SSIDs found")
            return []

    def get_vlans(self) -> List[Dict[str, Any]]:
        """
        Get all VLANs from XIQ
        In XIQ, VLANs are embedded in user profiles under vlan_profile

        Returns:
            List of VLAN configurations
        """
        if self.verbose:
            print("  Fetching VLANs from user profiles...")

        # Get user profiles which contain VLAN information
        user_profiles = self._make_request_with_pagination("/user-profiles")

        if not user_profiles:
            if self.verbose:
                print("    ⚠ No user profiles found")
            return []

        # Extract unique VLANs from user profiles
        vlans_dict = {}
        for profile in user_profiles:
            vlan_profile = profile.get('vlan_profile', {})
            vlan_id = vlan_profile.get('default_vlan_id')

            if vlan_id and vlan_id not in vlans_dict:
                vlans_dict[vlan_id] = {
                    # Core VLAN identifiers
                    'vlan_id': vlan_id,
                    'name': vlan_profile.get('name', f'VLAN_{vlan_id}'),
                    'description': f"VLAN from user profile: {profile.get('name', '')}",

                    # XIQ-specific fields
                    'vlan_profile_id': vlan_profile.get('id'),
                    'user_profile_name': profile.get('name'),
                    'user_profile_id': profile.get('id'),

                    # Classification
                    'enable_classification': vlan_profile.get('enable_classification', False),
                    'classification_rules': vlan_profile.get('classified_entries', []),

                    # Defaults (XIQ doesn't store full VLAN config in user profiles)
                    'subnet': None,
                    'gateway': None,
                    'netmask': None,
                    'dhcp_enabled': False,
                    'dhcp_start': None,
                    'dhcp_end': None,
                    'dhcp_lease_time': None,
                    'dhcp_dns_servers': [],
                    'group': 0,
                    'tagged': False,
                    'mtu': 1500,
                    'enabled': True,

                    # Metadata
                    'original': vlan_profile
                }

        normalized_vlans = list(vlans_dict.values())

        if self.verbose:
            print(f"    ✓ Extracted {len(normalized_vlans)} unique VLANs from user profiles")

        return normalized_vlans

    def get_radio_profiles(self) -> List[Dict[str, Any]]:
        """Get radio profiles from XIQ"""
        if self.verbose:
            print("  Fetching radio profiles...")

        profiles = self._make_request_with_pagination("/radio-profiles")

        if profiles:
            if self.verbose:
                print(f"    ✓ Retrieved {len(profiles)} radio profiles")

            # Normalize radio profile data
            normalized_profiles = []
            for profile in profiles:
                normalized_profiles.append({
                    'name': profile.get('name', ''),
                    'band': profile.get('radio_band', profile.get('band', '2.4GHz')),
                    'channel': profile.get('channel', 'auto'),
                    'channel_width': profile.get('channel_width', profile.get('bandwidth', '20MHz')),
                    'tx_power': profile.get('tx_power', profile.get('power', 'auto')),
                    'min_rssi': profile.get('min_rssi', None),
                    'max_clients': profile.get('max_clients', 0),
                    'original': profile
                })

            return normalized_profiles
        else:
            if self.verbose:
                print("    ⚠ No radio profiles found")
            return []

    def get_radius_servers(self) -> List[Dict[str, Any]]:
        """Get RADIUS server configurations from XIQ"""
        if self.verbose:
            print("  Fetching RADIUS servers...")

        # Try external RADIUS servers endpoint first
        servers = self._make_request_with_pagination("/radius-servers/external")

        # Also try alternative endpoints if no results
        if not servers:
            if self.verbose:
                print("    ⚠ No servers at /radius-servers/external, trying /radius-servers...")
            servers = self._make_request_with_pagination("/radius-servers")

        if not servers:
            if self.verbose:
                print("    ⚠ No servers at /radius-servers, trying /aaa-servers...")
            servers = self._make_request_with_pagination("/aaa-servers")

        if servers:
            if self.verbose:
                print(f"    ✓ Retrieved {len(servers)} RADIUS servers")

            # Normalize RADIUS server data
            normalized_servers = []
            for server in servers:
                normalized_servers.append({
                    'name': server.get('name', server.get('server_name', '')),
                    'ip': server.get('ip_address', server.get('ip', '')),
                    'auth_port': server.get('auth_port', server.get('authentication_port', 1812)),
                    'acct_port': server.get('acct_port', server.get('accounting_port', 1813)),
                    'secret': server.get('shared_secret', server.get('secret', '')),
                    'timeout': server.get('timeout', 5),
                    'retries': server.get('retries', 3),
                    'enabled': server.get('enabled', True),
                    'original': server
                })

            return normalized_servers
        else:
            if self.verbose:
                print("    ⚠ No RADIUS servers found")
            return []

    def get_devices(self) -> List[Dict[str, Any]]:
        """
        Get all devices (APs) from XIQ

        Returns:
            List of device configurations with names and locations
        """
        if self.verbose:
            print("  Fetching devices...")

        devices = self._make_request_with_pagination("/devices")

        if devices:
            # Filter for Access Points only
            aps = [d for d in devices if d.get('device_function') == 'AP' or d.get('product_type', '').startswith('AP')]

            if self.verbose:
                print(f"    ✓ Retrieved {len(aps)} Access Points (out of {len(devices)} total devices)")

            # Normalize device data
            normalized_devices = []
            for device in aps:
                normalized_devices.append({
                    'serial_number': device.get('serial_number'),
                    'name': device.get('hostname', device.get('device_name', device.get('serial_number'))),
                    'location': device.get('location', ''),
                    'model': device.get('product_type', device.get('model', '')),
                    'mac_address': device.get('mac_address', device.get('mac', '')),
                    'connected': device.get('connected', False),
                    'ip_address': device.get('ip_address', ''),
                    'original': device
                })

            return normalized_devices
        else:
            if self.verbose:
                print("    ⚠ No devices found")
            return []

    def get_user_profiles(self) -> List[Dict[str, Any]]:
        """Get user profiles from XIQ"""
        if self.verbose:
            print("  Fetching user profiles...")

        profiles = self._make_request_with_pagination("/user-profiles")

        if profiles:
            if self.verbose:
                print(f"    ✓ Retrieved {len(profiles)} user profiles")
            return profiles
        else:
            if self.verbose:
                print("    ⚠ No user profiles found")
            return []

    def _normalize_security(self, ssid: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize XIQ SSID security settings to common format"""
        # XIQ uses 'access_security' object
        access_security = ssid.get('access_security', {})

        if not access_security:
            return {
                'type': 'open',
                'encryption': 'none',
                'psk': None,
                'radius_servers': [],
                'wpa_version': 'WPA2',
                'pmf': 'optional'
            }

        # Get security_type from access_security
        security_type = access_security.get('security_type', 'OPEN').upper()

        # Map XIQ security_type to our format
        type_mapping = {
            'OPEN': 'open',
            'PSK': 'psk',
            'PPSK': 'ppsk',
            '802DOT1X': 'dot1x',
            'ENHANCED-OPEN': 'owe'  # OWE (Opportunistic Wireless Encryption)
        }

        sec_type = type_mapping.get(security_type, 'open')

        # Get PSK (key_value field)
        psk = access_security.get('key_value', None)
        if psk == '':
            psk = None

        # Get encryption method
        encryption_method = access_security.get('encryption_method', 'CCMP')
        encryption_mapping = {
            'CCMP': 'aes',
            'AES': 'aes',
            'TKIP': 'tkip',
            'NONE': 'none'
        }
        encryption = encryption_mapping.get(encryption_method, 'aes')

        # Get key_management (WPA2_PSK, WPA3_PSK, WPA3_8021X, etc.)
        key_management = access_security.get('key_management', '')

        # Determine WPA version from key_management
        wpa_version = 'WPA2'
        if 'WPA3' in str(key_management):
            wpa_version = 'WPA3'
        elif 'WPA2' in str(key_management):
            wpa_version = 'WPA2'

        # PMF mode (from transition_mode or inferred from WPA3)
        if 'WPA3' in str(key_management):
            pmf_mode = 'required'
        elif access_security.get('transition_mode'):
            pmf_mode = 'optional'
        else:
            pmf_mode = 'optional'

        # Get RADIUS client profile for 802.1X
        radius_client_object_id = None
        if sec_type == 'dot1x':
            radius_client_profile = ssid.get('radius_client_profile', {})
            radius_client_object_id = radius_client_profile.get('default_radius_client_object_id')

        return {
            'type': sec_type,
            'encryption': encryption,
            'psk': psk,
            'radius_client_object_id': radius_client_object_id,
            'radius_servers': [],  # Will be populated later by linking IDs
            'wpa_version': wpa_version,
            'pmf': pmf_mode,
            'key_management': key_management
        }

    def test_connection(self) -> bool:
        """
        Test connection to XIQ API

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get network policies as a connectivity test
            response = self.session.get(
                f'{self.base_url}/network-policies',
                headers=self.headers,
                verify=self.verify_ssl,
                timeout=10
            )
            return response.status_code in [200, 401]  # 401 means connected but auth issue
        except Exception:
            return False

    def save_to_file(self, config: Dict[str, Any], output_file: str):
        """
        Save retrieved configuration to file

        Args:
            config: Configuration dictionary
            output_file: Path to output file
        """
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)

        if self.verbose:
            print(f"\n✓ Configuration saved to {output_file}")
