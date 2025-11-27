"""
Configuration Converter - OPTIMIZED VERSION
Maps XIQ configuration objects to Edge Services format
Based on Edge Services ServiceElement and TopologyElement schemas

IMPROVEMENTS:
- VLAN ID validation (1-4094 range)
- Duplicate VLAN ID detection
- CIDR validation (0-32)
- Improved DHCP mode detection (DHCPServer, DHCPRelay, DHCPNone)
- Better L3 presence logic
- DNS server handling without unnecessary defaults
- DHCP range validation
- Error handling for invalid subnet formats
"""

from typing import Dict, List, Any, Optional
import uuid
import re

# Import configuration constants
try:
    from .config import DEFAULT_AUTHENTICATED_ROLE_ID
except ImportError:
    # Fallback if config.py doesn't exist
    DEFAULT_AUTHENTICATED_ROLE_ID = "4459ee6c-2f76-11e7-93ae-92361f002671"


# Validation helper functions
def validate_ip_address(ip: str) -> bool:
    """Validate IPv4 address format"""
    if not ip or not isinstance(ip, str):
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, TypeError):
        return False


def validate_name(name: str, min_len: int = 1, max_len: int = 255) -> bool:
    """
    Validate name field according to API spec
    Valid characters: Alphanumeric, special characters except semicolon, colon, ampersand
    """
    if not name or not isinstance(name, str):
        return False
    if len(name) < min_len or len(name) > max_len:
        return False
    # Check for invalid characters (semicolon, colon, ampersand)
    invalid_chars = [';', ':', '&']
    return not any(char in name for char in invalid_chars)


def validate_port(port: Any, default: int = 1812) -> int:
    """Validate port number (1-65535)"""
    try:
        port_int = int(port) if port is not None else default
        return port_int if 1 <= port_int <= 65535 else default
    except (ValueError, TypeError):
        return default


def validate_timeout(timeout: Any, min_val: int = 1, max_val: int = 360, default: int = 5) -> int:
    """Validate timeout value"""
    try:
        timeout_int = int(timeout) if timeout is not None else default
        return timeout_int if min_val <= timeout_int <= max_val else default
    except (ValueError, TypeError):
        return default


def validate_retries(retries: Any, min_val: int = 1, max_val: int = 32, default: int = 3) -> int:
    """Validate retry count"""
    try:
        retries_int = int(retries) if retries is not None else default
        return retries_int if min_val <= retries_int <= max_val else default
    except (ValueError, TypeError):
        return default


class ConfigConverter:
    """Converts XIQ configuration to Edge Services format"""

    def __init__(self, verbose: bool = False):
        """Initialize the configuration converter

        Args:
            verbose: Enable verbose logging
        """
        self.topology_id_map = {}  # Map VLAN IDs to Topology IDs
        self.aaa_policy_id_map = {}  # Map AAA policy names to IDs
        self.verbose = verbose

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
        seen_vlan_ids = set()  # Track VLAN IDs to detect duplicates

        for vlan in vlans:
            vlan_id = vlan.get('vlan_id')
            if not vlan_id:
                continue

            # Validate VLAN ID range (1-4094)
            if not isinstance(vlan_id, int) or vlan_id < 1 or vlan_id > 4094:
                print(f"  WARNING: Skipping invalid VLAN ID {vlan_id} - must be integer 1-4094")
                continue

            # Check for duplicate VLAN IDs
            if vlan_id in seen_vlan_ids:
                print(f"  WARNING: Duplicate VLAN ID {vlan_id} detected - skipping duplicate")
                continue

            seen_vlan_ids.add(vlan_id)

            # Generate a UUID for this topology
            topology_id = str(uuid.uuid4())
            self.topology_id_map[vlan_id] = topology_id

            # Get and validate topology name
            topo_name = vlan.get('name', f"VLAN_{vlan_id}")
            if not validate_name(topo_name, min_len=1, max_len=255):
                if self.verbose:
                    print(f"  WARNING: Invalid topology name '{topo_name}', using default")
                topo_name = f"VLAN_{vlan_id}"

            # Parse subnet if present
            ip_address = "0.0.0.0"
            cidr = 0
            gateway = "0.0.0.0"
            l3_presence = False

            subnet = vlan.get('subnet')
            if subnet and '/' in subnet:
                try:
                    parts = subnet.split('/')
                    ip_address = parts[0]

                    # Validate IP address format
                    if not validate_ip_address(ip_address):
                        print(f"  WARNING: Invalid IP address '{ip_address}' for VLAN {vlan_id}")
                        ip_address = "0.0.0.0"
                        l3_presence = False
                    else:
                        cidr = int(parts[1])

                        # Validate CIDR range (0-32 for IPv4)
                        if cidr < 0 or cidr > 32:
                            print(f"  WARNING: Invalid CIDR {cidr} for VLAN {vlan_id}, using 0")
                            cidr = 0
                            l3_presence = False
                        else:
                            l3_presence = True
                except (ValueError, IndexError):
                    print(f"  WARNING: Invalid subnet format '{subnet}' for VLAN {vlan_id}")
                    cidr = 0
                    l3_presence = False

            # Validate gateway IP if present
            if vlan.get('gateway'):
                gateway = vlan.get('gateway')
                if gateway != "0.0.0.0":
                    if not validate_ip_address(gateway):
                        if self.verbose:
                            print(f"  WARNING: Invalid gateway IP '{gateway}' for VLAN {vlan_id}, using 0.0.0.0")
                        gateway = "0.0.0.0"
                    else:
                        l3_presence = True

            # Determine DHCP mode
            dhcp_mode = "DHCPNone"
            dhcp_start = "0.0.0.0"
            dhcp_end = "0.0.0.0"

            # Check if DHCP server is configured (has start/end range)
            dhcp_start_ip = vlan.get('dhcp_start', vlan.get('dhcp_start_ip'))
            dhcp_end_ip = vlan.get('dhcp_end', vlan.get('dhcp_end_ip'))

            if dhcp_start_ip and dhcp_end_ip and dhcp_start_ip != "0.0.0.0" and dhcp_end_ip != "0.0.0.0":
                dhcp_mode = "DHCPServer"
                dhcp_start = str(dhcp_start_ip)
                dhcp_end = str(dhcp_end_ip)
            elif vlan.get('dhcp_enabled'):
                # DHCP enabled but no server config = relay mode
                dhcp_mode = "DHCPRelay"

            # Format DNS servers (comma-separated string)
            dns_servers = vlan.get('dns_servers', vlan.get('name_servers', vlan.get('dhcp_dns_servers', [])))
            if isinstance(dns_servers, list):
                dns_servers_str = ','.join(str(s) for s in dns_servers if s) if dns_servers else ""
            else:
                dns_servers_str = str(dns_servers) if dns_servers else ""

            # Only use default DNS if DHCP server mode is enabled and no DNS servers provided
            if not dns_servers_str and dhcp_mode == "DHCPServer":
                dns_servers_str = "8.8.8.8,8.8.4.4"

            # Get DNS domain
            dns_domain = vlan.get('dns_domain', vlan.get('domain', ''))

            # Get DHCP lease times
            dhcp_lease = vlan.get('dhcp_lease_time', vlan.get('dhcp_default_lease', 36000))
            if isinstance(dhcp_lease, int) and dhcp_lease > 0:
                dhcp_default_lease = dhcp_lease
            else:
                dhcp_default_lease = 36000

            topology = {
                "id": topology_id,
                "name": topo_name,
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
                "l3Presence": l3_presence,
                "ipAddress": ip_address,
                "cidr": cidr,
                "gateway": gateway,
                "dhcpStartIpRange": dhcp_start,
                "dhcpEndIpRange": dhcp_end,
                "dhcpMode": dhcp_mode,
                "dhcpDomain": dns_domain,
                "dhcpDefaultLease": dhcp_default_lease,
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

            # Validate SSID name length (1-32 characters per API spec)
            if len(ssid_name) > 32:
                if self.verbose:
                    print(f"  Warning: SSID name '{ssid_name}' exceeds 32 characters, truncating...")
                ssid_name = ssid_name[:32]

            # Service name can be up to 64 characters, use SSID name as base
            service_name = ssid_name
            if len(service_name) > 64:
                service_name = service_name[:64]

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

            # Validate topology UUID exists
            if not default_topology:
                if self.verbose:
                    print(f"  WARNING: No topology found for SSID '{ssid_name}' with VLAN ID {vlan_id}, skipping...")
                continue

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

            # Use a standard authenticated role ID (from configuration)
            default_auth_role_id = DEFAULT_AUTHENTICATED_ROLE_ID

            # Link AAA policy for enterprise SSIDs
            aaa_policy_id = None
            if sec_type in ['dot1x', '802.1x', 'enterprise']:
                # Try to find AAA policy ID from the map
                # For now, set to None - will be linked manually or via AAA policy creation
                aaa_policy_id = None

            service = {
                "id": service_id,
                "serviceName": service_name,  # Use validated service name
                "ssid": ssid_name,  # Use validated SSID name
                "status": "disabled",  # Start disabled for safety
                "suppressSsid": not ssid.get('broadcast_ssid', True),
                "privacy": privacy,
                "proxied": "Local",
                "shutdownOnMeshpointLoss": False,
                "dot1dPortNumber": 101,
                "enabled11kSupport": ssid.get('fast_roaming', False),
                "rm11kBeaconReport": False,
                "rm11kQuietIe": False,
                "uapsdEnabled": True,
                "admissionControlVideo": False,
                "admissionControlVoice": False,
                "admissionControlBestEffort": False,
                "admissionControlBackgroundTraffic": False,
                "flexibleClientAccess": False,
                "mbaAuthorization": False,
                "accountingEnabled": False,
                "clientToClientCommunication": True,
                "includeHostname": False,
                "mbo": False,
                "oweAutogen": False,
                "oweCompanion": None,
                "purgeOnDisconnect": False,
                "enable11mcSupport": True,
                "beaconProtection": False,
                "enableCaptivePortal": enable_captive_portal,
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
                "aaaPolicyId": aaa_policy_id,
                "mbatimeoutRoleId": None,
                "roamingAssistPolicy": None,
                "features": ["CENTRALIZED-SITE"],
                "vendorSpecificAttributes": ["apName", "vnsName", "ssid"],
                "hotspotType": "Disabled",
                "hotspot": None,
                "dscp": {
                    "codePoints": [2,0,0,0,0,0,0,0,0,0,2,0,2,0,2,0,1,0,3,0,3,0,3,0,3,0,4,0,4,0,4,0,4,0,5,0,5,0,5,0,5,0,0,0,0,0,6,0,6,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0]
                }
            }

            # Remove None values, but keep required fields
            required_fields = {
                'unAuthenticatedUserDefaultRoleID',
                'authenticatedUserDefaultRoleID',
                'aaaPolicyId',
                'captivePortalType',
                'defaultCoS'
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
            return None

        elif sec_type in ['psk', 'ppsk']:
            psk = security.get('psk')

            if not psk or psk == '':
                return None

            pmf_mode = security.get('pmf', 'optional')

            pmf_mapping = {
                'disabled': 'disabled',
                'optional': 'enabled',
                'required': 'required'
            }

            privacy = {
                "WpaPskElement": {
                    "mode": "auto",
                    "pmfMode": pmf_mapping.get(pmf_mode, 'enabled'),
                    "keyHexEncoded": False,
                    "presharedKey": psk
                }
            }
            return privacy

        elif sec_type in ['dot1x', '802.1x', 'enterprise']:
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

        if auth_servers:
            policy_id = str(uuid.uuid4())
            policy_name = "XIQ_RADIUS_Policy"

            radius_servers = []
            for idx, server in enumerate(auth_servers):
                # Get and validate IP address
                ip_addr = server.get('ip', server.get('address', '192.168.1.1'))
                if not validate_ip_address(ip_addr):
                    if self.verbose:
                        print(f"  WARNING: Invalid RADIUS server IP '{ip_addr}', using default")
                    ip_addr = '192.168.1.1'

                # Validate port, timeout, and retries using helper functions
                port = validate_port(server.get('acct_port', server.get('accounting_port')), default=1813)
                timeout = validate_timeout(server.get('timeout'), default=5)
                retries = validate_retries(server.get('retries'), default=3)

                radius_server = {
                    "id": str(uuid.uuid4()),
                    "ipAddress": ip_addr,
                    "sharedSecret": server.get('secret', server.get('shared_secret', 'secret')),
                    "port": port,
                    "timeout": timeout,
                    "totalRetries": retries,
                    "pollInterval": 60
                }
                radius_servers.append(radius_server)

            aaa_policy = {
                "id": policy_id,
                "name": policy_name,
                "authenticationRadiusServers": radius_servers,
                "accountingRadiusServers": [],
                "authenticationType": "PAP",
                "serverPoolingMode": "failover",
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

            if location and len(location) > 32:
                location = location[:32]

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

            bandwidth_kbps = limiter.get('bandwidth', limiter.get('rate', limiter.get('cir', 0)))

            if limiter.get('unit', '').lower() == 'mbps':
                bandwidth_kbps = bandwidth_kbps * 1000

            bandwidth_kbps = int(bandwidth_kbps)

            if bandwidth_kbps <= 0:
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

        rate_limiter_map = {rl.get('name'): rl.get('id') for rl in rate_limiters}

        for policy in cos_policies:
            policy_id = str(uuid.uuid4())
            name = policy.get('name', f'CoS-{len(edge_cos_policies) + 1}')

            ingress_limiter_name = policy.get('ingress_rate_limiter', policy.get('upload_limiter'))
            egress_limiter_name = policy.get('egress_rate_limiter', policy.get('download_limiter'))

            ingress_limiter_id = rate_limiter_map.get(ingress_limiter_name) if ingress_limiter_name else None
            egress_limiter_id = rate_limiter_map.get(egress_limiter_name) if egress_limiter_name else None

            dscp = policy.get('dscp', 0)
            dot1p = policy.get('dot1p', policy.get('priority', 0))

            if not isinstance(dscp, int) or dscp < 0 or dscp > 63:
                dscp = 0
            if not isinstance(dot1p, int) or dot1p < 0 or dot1p > 7:
                dot1p = 0

            cos_policy = {
                "id": policy_id,
                "cosName": name,
                "cosQos": {
                    "priority": dot1p,
                    "tosDscp": dscp,
                    "mask": 0,
                    "useLegacyMarking": None
                },
                "transmitQueue": 0,
                "predefined": False,
                "features": ["CENTRALIZED-SITE"]
            }

            if ingress_limiter_id:
                cos_policy["inboundRateLimiterId"] = ingress_limiter_id
            if egress_limiter_id:
                cos_policy["outboundRateLimiterId"] = egress_limiter_id

            edge_cos_policies.append(cos_policy)

        return edge_cos_policies
