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
        # Convert Rate Limiters first (dependency for CoS and Services)
        rate_limiters = self._convert_to_rate_limiters(xiq_config.get('rate_limiters', []))

        # Convert Class of Service policies (depends on rate limiters)
        cos_policies = self._convert_to_cos_policies(xiq_config.get('cos_policies', []), rate_limiters)

        # Convert VLANs to Topologies
        topologies = self._convert_to_topologies(xiq_config.get('vlans', []))

        # Convert authentication servers to AAA policies
        aaa_policies = self._convert_to_aaa_policies(xiq_config.get('authentication', []))

        # Convert SSIDs to Services (pass existing topologies for ID mapping)
        services = self._convert_to_services(
            xiq_config.get('ssids', []),
            topologies,
            existing_topologies
        )

        # Convert AP devices (names and locations)
        ap_configs = self._convert_ap_configs(xiq_config.get('devices', []))

        campus_config = {
            'services': services,
            'topologies': topologies,
            'aaa_policies': aaa_policies,
            'ap_configs': ap_configs,
            'rate_limiters': rate_limiters,
            'cos_policies': cos_policies
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

            # Format DNS servers (comma-separated string)
            dns_servers = vlan.get('dns_servers', vlan.get('name_servers', []))
            if isinstance(dns_servers, list):
                dns_servers_str = ','.join(dns_servers) if dns_servers else "8.8.8.8,8.8.4.4"
            else:
                dns_servers_str = str(dns_servers) if dns_servers else "8.8.8.8,8.8.4.4"

            # Get DNS domain
            dns_domain = vlan.get('dns_domain', vlan.get('domain', ''))

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
                "dhcpDomain": dns_domain,
                "dhcpDefaultLease": 36000,
                "dhcpMaxLease": 2592000,
                "dhcpDnsServers": dns_servers_str,
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

    def _convert_ap_configs(self, devices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert XIQ device information to Edge Services AP configurations

        Args:
            devices: List of device (AP) configurations from XIQ

        Returns:
            List of AP configuration updates for Edge Services
        """
        ap_configs = []

        for device in devices:
            serial = device.get('serial_number')
            name = device.get('name')
            location = device.get('location', '')

            if not serial:
                continue

            # Truncate location to 32 characters (Edge Services API limit)
            if location and len(location) > 32:
                location = location[:32]

            # Build AP configuration update
            # Only include fields we want to update
            ap_config = {
                'serial': serial,
                'name': name if name else serial,
                'location': location
            }

            ap_configs.append(ap_config)

        return ap_configs

    def _convert_to_rate_limiters(self, rate_limiters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert XIQ rate limiters/bandwidth profiles to Edge Services Rate Limiters

        Args:
            rate_limiters: List of rate limiter/QoS configurations from XIQ

        Returns:
            List of Rate Limiter configurations for Edge Services
        """
        edge_rate_limiters = []

        for limiter in rate_limiters:
            limiter_id = str(uuid.uuid4())
            name = limiter.get('name', f'RateLimiter-{len(edge_rate_limiters) + 1}')

            # Get bandwidth in Kbps - XIQ might use different field names
            # Try common field names: rate, bandwidth, cir, max_bandwidth
            bandwidth_kbps = limiter.get('bandwidth', limiter.get('rate', limiter.get('cir', 0)))

            # Convert from Mbps to Kbps if needed
            if limiter.get('unit', '').lower() == 'mbps':
                bandwidth_kbps = bandwidth_kbps * 1000

            # Ensure integer
            bandwidth_kbps = int(bandwidth_kbps)

            if bandwidth_kbps <= 0:
                # Skip invalid rate limiters
                continue

            rate_limiter = {
                "id": limiter_id,
                "name": name,
                "cirKbps": bandwidth_kbps,
                "features": ["CENTRALIZED-SITE"]
            }

            edge_rate_limiters.append(rate_limiter)

        return edge_rate_limiters

    def _convert_to_cos_policies(self, cos_policies: List[Dict[str, Any]], rate_limiters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert XIQ Class of Service policies to Edge Services CoS policies

        Args:
            cos_policies: List of CoS/QoS configurations from XIQ
            rate_limiters: List of converted rate limiters for ID mapping

        Returns:
            List of CoS policy configurations for Edge Services
        """
        edge_cos_policies = []

        # Build rate limiter name to ID mapping
        rate_limiter_map = {rl.get('name'): rl.get('id') for rl in rate_limiters}

        for policy in cos_policies:
            policy_id = str(uuid.uuid4())
            name = policy.get('name', f'CoS-{len(edge_cos_policies) + 1}')

            # Get rate limiter references by name
            ingress_limiter_name = policy.get('ingress_rate_limiter', policy.get('upload_limiter'))
            egress_limiter_name = policy.get('egress_rate_limiter', policy.get('download_limiter'))

            ingress_limiter_id = rate_limiter_map.get(ingress_limiter_name) if ingress_limiter_name else None
            egress_limiter_id = rate_limiter_map.get(egress_limiter_name) if egress_limiter_name else None

            # Get DSCP and 802.1p values
            dscp = policy.get('dscp', 0)
            dot1p = policy.get('dot1p', policy.get('priority', 0))

            # Validate values
            if not isinstance(dscp, int) or dscp < 0 or dscp > 63:
                dscp = 0
            if not isinstance(dot1p, int) or dot1p < 0 or dot1p > 7:
                dot1p = 0

            cos_policy = {
                "id": policy_id,
                "name": name,
                "dscp": dscp,
                "dot1p": dot1p,
                "features": ["CENTRALIZED-SITE"]
            }

            # Add rate limiter IDs if available
            if ingress_limiter_id:
                cos_policy["ingressRateLimiterId"] = ingress_limiter_id
            if egress_limiter_id:
                cos_policy["egressRateLimiterId"] = egress_limiter_id

            edge_cos_policies.append(cos_policy)

        return edge_cos_policies
