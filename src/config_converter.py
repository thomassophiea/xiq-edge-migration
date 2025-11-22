"""
Configuration Converter
Maps XIQ configuration objects to Edge Services format
Based on Edge Services ServiceElement and TopologyElement schemas
"""

from typing import Dict, List, Any, Optional
import uuid


class ConfigConverter:
    """Converts XIQ configuration to Edge Services format"""

    def __init__(self):
        """Initialize the configuration converter"""
        self.topology_id_map = {}  # Map VLAN IDs to Topology IDs
        self.aaa_policy_id_map = {}  # Map AAA policy names to IDs

    def convert(self, xiq_config: Dict[str, Any], existing_topologies: List[Dict] = None) -> Dict[str, Any]:
        """
        Convert XIQ configuration to Edge Services format

        Args:
            xiq_config: Parsed XIQ configuration
            existing_topologies: Existing topologies from Edge Services (optional)

        Returns:
            Dictionary in Edge Services format with services, topologies, and aaa_policies
        """
        # Convert VLANs to Topologies first (dependencies)
        topologies = self._convert_to_topologies(xiq_config.get('vlans', []))

        # Convert authentication servers to AAA policies
        aaa_policies = self._convert_to_aaa_policies(xiq_config.get('authentication', []))

        # Convert SSIDs to Services (pass existing topologies for ID mapping)
        services = self._convert_to_services(
            xiq_config.get('ssids', []),
            topologies,
            existing_topologies
        )

        campus_config = {
            'services': services,
            'topologies': topologies,
            'aaa_policies': aaa_policies
        }

        return campus_config

    def _convert_to_topologies(self, vlans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert XIQ VLANs to Edge Services Topologies

        Args:
            vlans: List of VLAN configurations from XIQ

        Returns:
            List of Topology configurations
        """
        topologies = []

        for vlan in vlans:
            vlan_id = vlan.get('vlan_id')
            if not vlan_id:
                continue

            # Generate a UUID for this topology
            topology_id = str(uuid.uuid4())
            self.topology_id_map[vlan_id] = topology_id

            # Parse subnet if present
            ip_address = "0.0.0.0"
            cidr = 0
            gateway = "0.0.0.0"

            subnet = vlan.get('subnet')
            if subnet and '/' in subnet:
                parts = subnet.split('/')
                ip_address = parts[0]
                cidr = int(parts[1])

            if vlan.get('gateway'):
                gateway = vlan.get('gateway')

            topology = {
                "id": topology_id,
                "name": vlan.get('name', f"VLAN_{vlan_id}"),
                "vlanid": vlan_id,
                "tagged": False,
                "multicastFilters": [],
                "multicastBridging": False,
                "mode": "BridgedAtAc",  # Bridged at Access Controller
                "group": 0,
                "members": [],
                "mtu": 1500,
                "enableMgmtTraffic": False,
                "dhcpServers": "",
                "l3Presence": True if subnet else False,
                "ipAddress": ip_address,
                "cidr": cidr,
                "gateway": gateway,
                "dhcpStartIpRange": "0.0.0.0",
                "dhcpEndIpRange": "0.0.0.0",
                "dhcpMode": "DHCPRelay" if vlan.get('dhcp_enabled') else "DHCPNone",
                "dhcpDomain": "",
                "dhcpDefaultLease": 36000,
                "dhcpMaxLease": 2592000,
                "dhcpDnsServers": "",
                "wins": "",
                "portName": f"vlan{vlan_id}",
                "vlanMapToEsa": -1,
                "dhcpExclusions": [],
                "foreignIpAddress": "0.0.0.0",
                "apRegistration": False,
                "fqdn": "",
                "isid": 0,
                "pool": [],
                "proxied": "Local",
                "features": ["CENTRALIZED-SITE"]
            }

            topologies.append(topology)

        return topologies

    def _convert_to_services(self, ssids: List[Dict[str, Any]], topologies: List[Dict[str, Any]], existing_topologies: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Convert XIQ SSIDs to Edge Services Services

        Args:
            ssids: List of SSID configurations from XIQ
            topologies: List of created topologies (for VLAN mapping)
            existing_topologies: Existing topologies from Edge Services (optional)

        Returns:
            List of Service configurations
        """
        services = []

        # Build VLAN ID to Topology ID mapping
        vlan_to_topology = {}

        # First, map existing topologies from Edge Services
        if existing_topologies:
            for topology in existing_topologies:
                vlan_id = topology.get('vlanid')
                topology_id = topology.get('id')
                if vlan_id and topology_id:
                    vlan_to_topology[vlan_id] = topology_id

        # Then add new topologies we're creating
        for topology in topologies:
            vlan_id = topology.get('vlanid')
            topology_id = topology.get('id')
            if vlan_id and topology_id and vlan_id not in vlan_to_topology:
                vlan_to_topology[vlan_id] = topology_id

        for ssid in ssids:
            ssid_name = ssid.get('name')
            if not ssid_name:
                continue

            # Generate UUIDs
            service_id = str(uuid.uuid4())

            # Get the topology ID for the VLAN using the mapping
            vlan_id = ssid.get('vlan_id')
            default_topology = vlan_to_topology.get(vlan_id, None)

            # If still no topology found, try legacy map or use first topology
            if not default_topology:
                default_topology = self.topology_id_map.get(vlan_id, None)
            if not default_topology and topologies:
                default_topology = topologies[0]['id']

            # Convert security settings
            security = ssid.get('security', {})
            privacy = self._convert_privacy_settings(security)

            # Skip SSIDs where privacy conversion failed (e.g., PPSK without a key)
            sec_type = security.get('type', 'open').lower()
            if sec_type in ['psk', 'ppsk'] and privacy is None:
                # Cannot migrate PSK/PPSK SSID without a preshared key
                continue

            # Determine if captive portal is enabled
            enable_captive_portal = ssid.get('captive_portal') is not None

            # Use a standard authenticated role ID (from existing Edge Services config)
            # This is a default role ID that exists in Edge Services
            default_auth_role_id = "4459ee6c-2f76-11e7-93ae-92361f002671"

            service = {
                "id": service_id,
                "serviceName": ssid_name,
                "ssid": ssid_name,  # Use same name for SSID
                "status": "disabled",  # Set to disabled so admin can enable after review
                "suppressSsid": not ssid.get('broadcast_ssid', True),
                "privacy": privacy,
                "proxied": "Local",
                "shutdownOnMeshpointLoss": False,
                "dot1dPortNumber": 101,  # Default bridge port number
                "enabled11kSupport": ssid.get('fast_roaming', False),
                "rm11kBeaconReport": False,
                "rm11kQuietIe": False,
                "uapsdEnabled": True,  # U-APSD (power save)
                "admissionControlVideo": False,
                "admissionControlVoice": False,
                "admissionControlBestEffort": False,
                "admissionControlBackgroundTraffic": False,
                "flexibleClientAccess": False,
                "mbaAuthorization": False,  # Disable MBA
                "accountingEnabled": False,
                "clientToClientCommunication": True,
                "includeHostname": False,
                "mbo": False,  # Multi-band Operation
                "oweAutogen": False,
                "oweCompanion": None,
                "purgeOnDisconnect": False,
                "enable11mcSupport": True,
                "beaconProtection": False,
                "enableCaptivePortal": False,  # Disable captive portal
                "captivePortalType": None,
                "eGuestPortalId": None,
                "eGuestSettings": [],
                "preAuthenticatedIdleTimeout": 300,
                "postAuthenticatedIdleTimeout": 1800,
                "sessionTimeout": 0,
                "defaultTopology": default_topology,
                "defaultCoS": None,
                "unAuthenticatedUserDefaultRoleID": default_auth_role_id,
                "authenticatedUserDefaultRoleID": default_auth_role_id,
                "cpNonAuthenticatedPolicyName": None,
                "aaaPolicyId": None,  # Explicitly set to null - no AAA policy
                "mbatimeoutRoleId": None,
                "roamingAssistPolicy": None,  # CRITICAL: This was missing!
                "vendorSpecificAttributes": ["apName", "vnsName", "ssid"],
                "hotspotType": "Disabled",
                "hotspot": None,
                "dscp": {
                    "codePoints": [2,0,0,0,0,0,0,0,0,0,2,0,2,0,2,0,1,0,3,0,3,0,3,0,3,0,4,0,4,0,4,0,4,0,5,0,5,0,5,0,5,0,0,0,0,0,6,0,6,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0]
                }
            }

            # Remove None values, but keep required fields
            required_fields = {
                'nonAuthenticatedUserDefaultRoleID',
                'authenticatedUserDefaultRoleID',
                'aaaPolicyId',  # Keep aaaPolicyId even if null
                'captivePortalType',  # Keep captivePortalType even if null
                'defaultCoS'  # Keep defaultCoS even if null
            }
            service = {k: v for k, v in service.items() if v is not None or k in required_fields}

            services.append(service)

        return services

    def _convert_privacy_settings(self, security: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert XIQ security settings to Edge Services privacy object

        Args:
            security: Security configuration from XIQ

        Returns:
            Privacy object for Edge Services (WpaPskElement, WpaEnterpriseElement, etc.)
        """
        sec_type = security.get('type', 'open').lower()

        if sec_type == 'open':
            # No privacy object for open networks
            return None

        elif sec_type in ['psk', 'ppsk']:
            # WPA-PSK or PPSK (Private PSK)
            psk = security.get('psk')

            # For PPSK, there's no single shared key - skip if no PSK is provided
            if not psk or psk == '':
                # PPSK networks require per-user keys - cannot be migrated with a single PSK
                # Return None to skip this SSID or use a placeholder
                return None

            pmf_mode = security.get('pmf', 'optional')

            # Map PMF mode
            pmf_mapping = {
                'disabled': 'disabled',
                'optional': 'enabled',  # In Edge Services, 'enabled' means optional
                'required': 'required'
            }

            privacy = {
                "WpaPskElement": {
                    "mode": "auto",  # WPA2/WPA3 auto
                    "pmfMode": pmf_mapping.get(pmf_mode, 'enabled'),
                    "keyHexEncoded": False,
                    "presharedKey": psk
                }
            }
            return privacy

        elif sec_type in ['dot1x', '802.1x', 'enterprise']:
            # WPA-Enterprise (802.1X)
            pmf_mode = security.get('pmf', 'optional')

            pmf_mapping = {
                'disabled': 'disabled',
                'optional': 'enabled',
                'required': 'required'
            }

            privacy = {
                "WpaEnterpriseElement": {
                    "mode": "auto",
                    "pmfMode": pmf_mapping.get(pmf_mode, 'enabled')
                }
            }
            return privacy

        else:
            # Default to open
            return None

    def _convert_to_aaa_policies(self, auth_servers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert XIQ authentication servers to Edge Services AAA Policies

        Args:
            auth_servers: List of authentication server configurations from XIQ

        Returns:
            List of AAA Policy configurations
        """
        aaa_policies = []

        # Group RADIUS servers into policies
        if auth_servers:
            # Create one AAA policy with all RADIUS servers
            policy_id = str(uuid.uuid4())
            policy_name = "XIQ_RADIUS_Policy"

            radius_servers = []
            for idx, server in enumerate(auth_servers):
                radius_server = {
                    "id": str(uuid.uuid4()),
                    "serverName": server.get('name', f"RADIUS-{idx+1}"),
                    "ipAddress": server.get('ip', server.get('address', '192.168.1.1')),
                    "authenticationPort": server.get('auth_port', server.get('port', 1812)),
                    "accountingPort": server.get('acct_port', server.get('accounting_port', 1813)),
                    "sharedSecret": server.get('secret', server.get('shared_secret', 'secret')),
                    "timeout": server.get('timeout', 5),
                    "retries": server.get('retries', 3),
                    "enabled": server.get('enabled', True)
                }
                radius_servers.append(radius_server)

            aaa_policy = {
                "id": policy_id,
                "policyName": policy_name,
                "radiusServers": radius_servers,
                "authenticationProtocol": "PAP",  # Default
                "accountingEnabled": False,
                "features": ["CENTRALIZED-SITE"]
            }

            self.aaa_policy_id_map[policy_name] = policy_id
            aaa_policies.append(aaa_policy)

        return aaa_policies
