"""
Edge Services API Client
Handles authentication and configuration posting to Extreme Edge Services
Based on Edge Services v5.26 REST API Gateway
"""

import requests
import json
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
import warnings

# Suppress SSL warnings for self-signed certificates (common in enterprise environments)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')


class CampusControllerClient:
    """Client for interacting with Extreme Edge Services API"""

    def __init__(self, base_url: str, username: str, password: str, verify_ssl: bool = False, verbose: bool = False):
        """
        Initialize Edge Services API client

        Args:
            base_url: Base URL of Edge Services (e.g., https://controller.example.com:5825)
            username: Username for authentication
            password: Password for authentication
            verify_ssl: Whether to verify SSL certificates (default: False for self-signed certs)
            verbose: Enable verbose logging
        """
        # Ensure port is included
        if ':5825' not in base_url and not base_url.startswith('http://localhost'):
            base_url = base_url.replace('https://', 'https://').replace('http://', 'http://')
            if ':' not in base_url.split('//')[-1]:
                base_url = base_url + ':5825'

        self.base_url = base_url.rstrip('/') + '/management'
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.verbose = verbose
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.access_token = None

        # Authenticate on initialization
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Edge Services using OAuth 2.0 and obtain access token"""
        auth_url = f'{self.base_url}/v1/oauth2/token'

        try:
            if self.verbose:
                print(f"  Authenticating to {auth_url}...")

            response = self.session.post(
                auth_url,
                json={
                    'grantType': 'password',
                    'userId': self.username,
                    'password': self.password
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get('access_token')
                token_type = data.get('token_type', 'Bearer')

                self.session.headers.update({
                    'Authorization': f'{token_type} {self.access_token}',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                })

                if self.verbose:
                    print("  Authentication successful")
                    print(f"  Token expires in: {data.get('expires_in')} seconds")
            else:
                raise Exception(f"Authentication failed: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Edge Services: {str(e)}")

    def post_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post configuration to Edge Services

        Args:
            config: Converted configuration dictionary

        Returns:
            Dictionary with success status and details
        """
        results = {
            'success': True,
            'details': {},
            'errors': []
        }

        # Post different configuration components in dependency order
        try:
            # 1. Post Topologies (VLANs) first - these are dependencies
            if config.get('topologies'):
                topology_result = self._post_topologies(config['topologies'])
                results['details']['topologies'] = topology_result

            # 2. Post AAA Policies (RADIUS servers)
            if config.get('aaa_policies'):
                aaa_result = self._post_aaa_policies(config['aaa_policies'])
                results['details']['aaa_policies'] = aaa_result

            # 3. Post Services (SSIDs) - depend on topologies and AAA policies
            if config.get('services'):
                service_result = self._post_services(config['services'])
                results['details']['services'] = service_result

        except Exception as e:
            results['success'] = False
            results['error'] = str(e)
            results['errors'].append(str(e))

        return results

    def get_existing_topologies(self) -> List[Dict[str, Any]]:
        """Get existing topologies from Edge Services to avoid conflicts"""
        url = f'{self.base_url}/v1/topologies'
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                topologies = response.json()
                return topologies if isinstance(topologies, list) else []
        except Exception as e:
            if self.verbose:
                print(f"  Warning: Could not fetch existing topologies: {e}")
        return []

    def _post_topologies(self, topologies: List[Dict[str, Any]]) -> str:
        """
        Post Topologies (VLANs) to Edge Services

        Args:
            topologies: List of topology configurations

        Returns:
            Result summary string
        """
        url = f'{self.base_url}/v1/topologies'
        success_count = 0
        skipped_count = 0

        # Get existing topologies to avoid conflicts
        existing_vlans = set()
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code == 200:
                existing_topos = response.json()
                if isinstance(existing_topos, list):
                    existing_vlans = {t.get('vlanid') for t in existing_topos if t.get('vlanid')}
        except:
            pass

        for topology in topologies:
            try:
                vlan_id = topology.get('vlanid')

                if self.verbose:
                    print(f"  Posting Topology (VLAN) {vlan_id} - {topology.get('name')}...")

                # Check if VLAN already exists
                if vlan_id in existing_vlans:
                    if self.verbose:
                        print(f"    Skipped (VLAN {vlan_id} already exists)")
                    skipped_count += 1
                    continue

                response = self.session.post(url, json=topology, timeout=30)

                if response.status_code in [200, 201]:
                    success_count += 1
                    if self.verbose:
                        print(f"    Success")
                else:
                    error_msg = response.text
                    if self.verbose:
                        print(f"    Warning: Failed ({response.status_code}): {error_msg}")

            except Exception as e:
                if self.verbose:
                    print(f"    Error: {str(e)}")

        result = f"{success_count}/{len(topologies)} topologies posted successfully"
        if skipped_count > 0:
            result += f" ({skipped_count} skipped - already exist)"
        return result

    def _post_services(self, services: List[Dict[str, Any]]) -> str:
        """
        Post Services (SSIDs) to Edge Services

        Args:
            services: List of service configurations

        Returns:
            Result summary string
        """
        url = f'{self.base_url}/v1/services'
        success_count = 0

        for service in services:
            try:
                if self.verbose:
                    print(f"  Posting Service (SSID) '{service.get('serviceName')}' (SSID: {service.get('ssid')}...)...")

                response = self.session.post(url, json=service, timeout=30)

                if response.status_code in [200, 201]:
                    success_count += 1
                    if self.verbose:
                        print(f"    Success")
                else:
                    error_msg = response.text
                    if self.verbose:
                        print(f"    Warning: Failed ({response.status_code}): {error_msg}")

            except Exception as e:
                if self.verbose:
                    print(f"    Error: {str(e)}")

        return f"{success_count}/{len(services)} services posted successfully"

    def _post_aaa_policies(self, policies: List[Dict[str, Any]]) -> str:
        """
        Post AAA Policies (including RADIUS servers) to Edge Services

        Args:
            policies: List of AAA policy configurations

        Returns:
            Result summary string
        """
        url = f'{self.base_url}/v1/aaapolicy'
        success_count = 0

        for policy in policies:
            try:
                if self.verbose:
                    print(f"  Posting AAA Policy '{policy.get('policyName', 'Unknown')}'...")

                response = self.session.post(url, json=policy, timeout=30)

                if response.status_code in [200, 201]:
                    success_count += 1
                    if self.verbose:
                        print(f"    Success")
                else:
                    error_msg = response.text
                    if self.verbose:
                        print(f"    Warning: Failed ({response.status_code}): {error_msg}")

            except Exception as e:
                if self.verbose:
                    print(f"    Error: {str(e)}")

        return f"{success_count}/{len(policies)} AAA policies posted successfully"

    def get_existing_topologies(self) -> List[Dict[str, Any]]:
        """
        Get existing topologies from Edge Services

        Returns:
            List of existing topology configurations
        """
        try:
            url = f'{self.base_url}/v1/topologies'
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                if self.verbose:
                    print(f"Failed to retrieve topologies: {response.status_code}")
                return []

        except Exception as e:
            if self.verbose:
                print(f"Error retrieving topologies: {str(e)}")
            return []

    def get_existing_services(self) -> List[Dict[str, Any]]:
        """
        Get existing services from Edge Services

        Returns:
            List of existing service configurations
        """
        try:
            url = f'{self.base_url}/v1/services'
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                if self.verbose:
                    print(f"Failed to retrieve services: {response.status_code}")
                return []

        except Exception as e:
            if self.verbose:
                print(f"Error retrieving services: {str(e)}")
            return []

    def test_connection(self) -> bool:
        """
        Test connection to Edge Services

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to get services as a connectivity test
            url = f'{self.base_url}/v1/services'
            response = self.session.get(url, timeout=10)
            return response.status_code in [200, 401]  # 401 means connected but auth expired
        except Exception:
            return False
