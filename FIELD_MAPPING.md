# XIQ to Edge Services - Complete Field Mapping

## VLAN Object Model (API-First Architecture)

### Complete Field Mapping from XIQ API

VLANs are treated as **first-class API manageable objects** with complete field extraction:

```python
# XIQ API Response → Internal Model → Edge Services
{
    # ===== Core Identifiers =====
    'vlanId'              → 'vlan_id'           → vlanId (Edge Services)
    'name'                → 'name'              → name (Edge Services)
    'vlan_name'           → 'name'              → name (Edge Services)
    'description'         → 'description'       → description (Edge Services)

    # ===== Network Configuration =====
    'subnet'              → 'subnet'            → ipAddress + cidr
    'ip_address'          → 'subnet'            → ipAddress + cidr
    'gateway'             → 'gateway'           → gateway
    'gatewayAddress'      → 'gateway'           → gateway
    'netmask'             → 'netmask'           → (converted to CIDR)
    'subnetMask'          → 'netmask'           → (converted to CIDR)

    # ===== DHCP Settings =====
    'dhcpEnabled'         → 'dhcp_enabled'      → dhcpMode
    'dhcp_server_enabled' → 'dhcp_enabled'      → dhcpMode
    'dhcpStartIp'         → 'dhcp_start'        → dhcpStartIpRange
    'dhcp_start_ip'       → 'dhcp_start'        → dhcpStartIpRange
    'dhcpEndIp'           → 'dhcp_end'          → dhcpEndIpRange
    'dhcp_end_ip'         → 'dhcp_end'          → dhcpEndIpRange
    'dhcpLeaseTime'       → 'dhcp_lease_time'   → dhcpDefaultLease
    'dhcp_lease_time'     → 'dhcp_lease_time'   → dhcpDefaultLease
    'dnsServers'          → 'dhcp_dns_servers'  → dhcpDnsServers
    'dhcp_dns_servers'    → 'dhcp_dns_servers'  → dhcpDnsServers

    # ===== Group & Classification (Platform ONE) =====
    'group'               → 'group'             → group (VLAN grouping)
    'vlan_group'          → 'group'             → group (VLAN grouping)
    'classificationRules' → 'classification_rules' → (device classification)
    'classification_rules'→ 'classification_rules' → (device classification)

    # ===== Additional Attributes =====
    'tagged'              → 'tagged'            → tagged
    'mtu'                 → 'mtu'               → mtu
    'enabled'             → 'enabled'           → (operational state)
    'status'              → 'enabled'           → (operational state)
}
```

## SSID Object Model

```python
# XIQ API Response → Internal Model
{
    'ssid_name'           → 'name'
    'name'                → 'name'
    'enabled_status'      → 'enabled'
    'broadcast_ssid'      → 'broadcast_ssid'
    'access_vlan'         → 'vlan_id'
    'vlan_id'             → 'vlan_id'
    'user_limit'          → 'max_clients'
    'band_steering_mode'  → 'band_steering'
    'fast_roaming_802_11r'→ 'fast_roaming'
}
```

## RADIUS Server Object Model

```python
# XIQ API Response → Internal Model
{
    'name'                → 'name'
    'server_name'         → 'name'
    'ip_address'          → 'ip'
    'ip'                  → 'ip'
    'auth_port'           → 'auth_port'
    'authentication_port' → 'auth_port'
    'acct_port'           → 'acct_port'
    'accounting_port'     → 'acct_port'
    'shared_secret'       → 'secret'
    'secret'              → 'secret'
}
```

## Bulk Export Formats

### 1. CSV Export (for migrations)

**Command:**
```bash
python main.py --xiq-token YOUR_TOKEN --export-csv ./export --dry-run
```

**Generated Files:**

#### `vlans.csv`
```csv
vlan_id,name,description,subnet,gateway,netmask,dhcp_enabled,dhcp_start,dhcp_end,dhcp_lease_time,dhcp_dns_servers,group,classification_rules,tagged,mtu,enabled,policy_id
100,Corporate,Corporate VLAN,192.168.100.0/24,192.168.100.1,255.255.255.0,true,192.168.100.10,192.168.100.250,86400,8.8.8.8;8.8.4.4,1,device_type:laptop;os:windows,false,1500,true,12345
200,Guest,Guest VLAN,192.168.200.0/24,192.168.200.1,255.255.255.0,true,192.168.200.10,192.168.200.250,3600,8.8.8.8,2,device_type:guest,false,1500,true,12345
300,IoT,IoT Devices,192.168.300.0/24,192.168.300.1,255.255.255.0,false,,,,,3,device_type:iot;vendor:*,true,1500,true,12345
```

**Key Fields for Migration:**
- `vlan_id` - VLAN ID (Platform ONE identifier)
- `name` - VLAN name
- `group` - VLAN group assignment (for policy/classification)
- `classification_rules` - Device classification rules (semicolon-separated)
- `dhcp_dns_servers` - DNS servers (semicolon-separated list)

#### `ssids.csv`
```csv
name,enabled,broadcast_ssid,vlan_id,security_type,security_encryption,psk,max_clients,band_steering,fast_roaming,wpa_version,pmf,policy_id
Corporate-WiFi,true,true,100,psk,aes,SecurePass123,200,true,true,WPA2,optional,12345
Guest-WiFi,true,true,200,open,none,,100,false,false,,,12345
Enterprise-Secure,true,true,100,dot1x,aes,,300,true,true,WPA2,required,12345
```

#### `radius_servers.csv`
```csv
name,ip,auth_port,acct_port,secret,timeout,retries,enabled
Primary-RADIUS,192.168.1.10,1812,1813,RadiusSecret123,5,3,true
Secondary-RADIUS,192.168.1.11,1812,1813,RadiusSecret456,5,3,true
```

### 2. JSON Export (complete API data)

**Command:**
```bash
python main.py --xiq-token YOUR_TOKEN --export-json xiq_config.json --dry-run
```

**Generated `xiq_config.json`:**
```json
{
  "ssids": [
    {
      "name": "Corporate-WiFi",
      "enabled": true,
      "broadcast_ssid": true,
      "vlan_id": 100,
      "security": {
        "type": "psk",
        "encryption": "aes",
        "psk": "SecurePass123",
        "wpa_version": "WPA2",
        "pmf": "optional"
      },
      "max_clients": 200,
      "band_steering": true,
      "fast_roaming": true,
      "policy_id": 12345,
      "original": { "...": "complete XIQ API response" }
    }
  ],
  "vlans": [
    {
      "vlan_id": 100,
      "name": "Corporate",
      "description": "Corporate VLAN",
      "subnet": "192.168.100.0/24",
      "gateway": "192.168.100.1",
      "netmask": "255.255.255.0",
      "dhcp_enabled": true,
      "dhcp_start": "192.168.100.10",
      "dhcp_end": "192.168.100.250",
      "dhcp_lease_time": 86400,
      "dhcp_dns_servers": ["8.8.8.8", "8.8.4.4"],
      "group": 1,
      "classification_rules": ["device_type:laptop", "os:windows"],
      "tagged": false,
      "mtu": 1500,
      "enabled": true,
      "policy_id": 12345,
      "original": { "...": "complete XIQ API response" }
    }
  ],
  "authentication": [...],
  "network_policies": [...],
  "radio_profiles": [...]
}
```

## API-First Architecture Implementation

### Code Structure (First-Class API Objects)

```python
# src/xiq_api_client.py - API extraction
class XIQAPIClient:
    def get_vlans_for_policy(self, policy_id: int) -> List[Dict]:
        """Fetch VLANs as first-class API objects"""
        endpoint = f"/network-policies/{policy_id}/vlans"
        vlans = self._make_request_with_pagination(endpoint)

        # Complete field mapping
        normalized_vlans = []
        for vlan in vlans:
            normalized_vlans.append({
                'vlan_id': vlan.get('vlanId', vlan.get('vlan_id')),
                'name': vlan.get('name', vlan.get('vlan_name')),
                'group': vlan.get('group', vlan.get('vlan_group', 0)),
                'classification_rules': vlan.get('classificationRules', []),
                # ... all other fields
            })
        return normalized_vlans
```

```python
# src/export_utils.py - Bulk export utilities
def export_vlans_to_csv(vlans: List[Dict], output_file: str):
    """Export VLANs as first-class API manageable objects to CSV"""
    fieldnames = [
        'vlan_id', 'name', 'description',
        'subnet', 'gateway', 'netmask',
        'dhcp_enabled', 'dhcp_start', 'dhcp_end',
        'dhcp_lease_time', 'dhcp_dns_servers',
        'group', 'classification_rules',  # Platform ONE fields
        'tagged', 'mtu', 'enabled', 'policy_id'
    ]
    # Write complete VLAN objects to CSV
```

## Usage Examples

### Example 1: Extract All VLANs for Migration Analysis

```bash
# Pull all VLANs from XIQ and export to CSV
python main.py \
    --xiq-token YOUR_XIQ_TOKEN \
    --export-csv ./vlan_migration_data \
    --dry-run \
    --verbose

# Output:
# ✓ Retrieved 3 network policies
# ✓ Retrieved 15 VLANs from policy 12345
# ✓ Retrieved 8 VLANs from policy 67890
# ✓ Configuration retrieved from XIQ
#   - VLANs: 23
# ✓ Exported to CSV:
#   - vlans: ./vlan_migration_data/vlans.csv
```

**Result:** `vlans.csv` with complete VLAN object data including:
- VLAN IDs and names
- VLAN groups for organization
- Classification rules for device types
- DHCP configuration
- All network settings

### Example 2: Complete Configuration Backup

```bash
# Backup everything from XIQ (JSON + CSV)
python main.py \
    --xiq-login \
    --export-json xiq_backup.json \
    --export-csv ./xiq_csv_export \
    --dry-run

# Creates:
# - xiq_backup.json (complete raw data)
# - ./xiq_csv_export/vlans.csv (VLAN objects)
# - ./xiq_csv_export/ssids.csv (SSID objects)
# - ./xiq_csv_export/radius_servers.csv (RADIUS objects)
```

### Example 3: Migration Pipeline

```bash
#!/bin/bash
# Migration pipeline script

# Step 1: Extract from XIQ
python main.py \
    --xiq-token $XIQ_TOKEN \
    --export-csv ./migration/xiq_source \
    --export-json ./migration/xiq_raw.json \
    --dry-run

# Step 2: Review/edit vlans.csv for classification rules and groups
# (manual review in Excel/Sheets)

# Step 3: Post to Edge Services
python main.py \
    --input-file ./migration/xiq_raw.json \
    --controller-url https://campus-controller \
    --username admin \
    --password $CC_PASSWORD \
    --output ./migration/campus_result.json
```

## VLAN Classification Rules Format

Classification rules in CSV are semicolon-separated:

```csv
device_type:laptop;os:windows
device_type:guest
device_type:iot;vendor:*;security:low
```

When exported to JSON, they're arrays:

```json
["device_type:laptop", "os:windows"]
```

## Platform ONE Integration Points

**VLAN Objects Support:**
1. ✅ **vlanId** - Primary identifier for API operations
2. ✅ **name** - Human-readable VLAN name
3. ✅ **group** - VLAN grouping for policy application
4. ✅ **classificationRules** - Device classification for automated assignment
5. ✅ **dhcp_* fields** - Complete DHCP server configuration
6. ✅ **subnet/gateway** - Network addressing
7. ✅ **tagged/mtu** - Layer 2 attributes
8. ✅ **enabled** - Operational state

All fields are **API-manageable** and preserved during extraction/conversion.

## Benefits of This Architecture

✅ **First-Class API Objects** - VLANs treated as complete API entities
✅ **Complete Field Mapping** - No data loss from XIQ
✅ **Bulk Operations** - Export all objects at once
✅ **CSV for Analysis** - Spreadsheet-compatible for review
✅ **JSON for Automation** - Programmatic consumption
✅ **Classification Support** - Device classification rules preserved
✅ **Group Management** - VLAN grouping maintained
✅ **Migration Ready** - Formats suitable for bulk import

## Command Reference

```bash
# Export only (no migration)
--export-csv DIR          # Export to CSV files
--export-json FILE        # Export raw XIQ data to JSON
--dry-run                 # Don't post to Edge Services

# Combined operations
--export-csv DIR --export-json FILE --output CONVERTED.json
# Exports: XIQ CSV + XIQ JSON + Edge Services JSON

# With migration
--export-csv DIR --controller-url URL --username USER --password PASS
# Exports CSV and migrates to Edge Services
```
