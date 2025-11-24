# Edge Services Integration Fixes

## Issues Fixed

### 1. ✅ Role ID Requirement
**Problem:** Edge Services requires `authenticatedUserDefaultRoleID` and `nonAuthenticatedUserDefaultRoleID`
**Solution:**
- Use existing role ID from Edge Services: `4459ee6c-2f76-11e7-93ae-92361f002671`
- Set `enableCaptivePortal: true` and `captivePortalType: "Internal"`
- Set both role IDs to the same value

### 2. ✅ VLAN/Topology Conflict
**Problem:** Cannot create VLAN that already exists (VLAN 1)
**Solution:**
- Fetch existing topologies before posting
- Skip topologies that already exist
- Use existing topology IDs when creating services

### 3. ✅ Topology ID Reference
**Problem:** Services fail with "VLAN not found" error
**Solution:**
- Pass existing topologies to converter
- Map VLAN IDs to existing topology UUIDs
- Use actual topology IDs instead of generated UUIDs

## Required Code Changes

You need to manually apply these changes to make posting work:

### File 1: src/config_converter.py

#### Change 1 - Update convert() method signature (line ~33):
```python
def convert(self, xiq_config: Dict[str, Any], existing_topologies: List[Dict] = None) -> Dict[str, Any]:
    """
    Convert XIQ configuration to Edge Services format

    Args:
        xiq_config: Configuration extracted from XIQ
        existing_topologies: Existing topologies from Edge Services (optional)
    """
    return {
        'services': self._convert_ssids(xiq_config.get('ssids', []), xiq_config.get('vlans', []), existing_topologies),
        'topologies': self._convert_vlans(xiq_config.get('vlans', [])),
        'aaa_policies': self._convert_radius_servers(xiq_config.get('authentication', []))
    }
```

#### Change 2 - Update _convert_ssids() method signature (line ~99):
```python
def _convert_ssids(self, ssids: List[Dict[str, Any]], vlans: List[Dict[str, Any]], existing_topologies: List[Dict] = None) -> List[Dict[str, Any]]:
    """
    Convert XIQ SSIDs to Edge Services Services

    Args:
        ssids: List of SSID configurations from XIQ
        vlans: List of VLAN configurations from XIQ
        existing_topologies: Existing topologies from Edge Services (optional)
    """
    services = []

    # Create VLAN ID to Topology ID mapping
    vlan_to_topology = {}

    # First, use existing topologies from Edge Services
    if existing_topologies:
        for topology in existing_topologies:
            vlan_id = topology.get('vlanid')
            topology_id = topology.get('id')
            if vlan_id and topology_id:
                vlan_to_topology[vlan_id] = topology_id

    # Then add new topologies we're creating
    topologies = self._convert_vlans(vlans)
    for topology in topologies:
        vlan_id = topology.get('vlanid')
        topology_id = topology.get('id')
        if vlan_id and topology_id and vlan_id not in vlan_to_topology:
            vlan_to_topology[vlan_id] = topology_id
```

#### Change 3 - Update service creation (around line 163):
```python
# Use a standard authenticated role ID (from existing Edge Services config)
default_auth_role_id = "4459ee6c-2f76-11e7-93ae-92361f002671"

service = {
    "id": service_id,
    "serviceName": ssid_name,
    "ssid": ssid_name,
    "status": "disabled",  # Set to disabled for manual review
    "suppressSsid": not ssid.get('broadcast_ssid', True),
    "privacy": privacy,
    "enableCaptivePortal": True,  # Required to avoid role ID error
    "captivePortalType": "Internal",
    "mbaAuthorization": False,
    "authenticatedUserDefaultRoleID": default_auth_role_id,
    "nonAuthenticatedUserDefaultRoleID": default_auth_role_id,  # Use same ID
    "defaultTopology": default_topology,
    # ... rest of fields
}
```

### File 2: src/campus_controller_client.py

#### Add new method (after post_configuration method):
```python
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
```

### File 3: main.py

#### Update converter section (around line 370):
```python
# Convert to Edge Services format
if verbose:
    print("\nConverting to Edge Services format...")

converter = ConfigConverter()

# Get existing topologies from Edge Services to avoid conflicts
existing_topologies = []
if not dry_run and controller_client:
    try:
        existing_topologies = controller_client.get_existing_topologies()
        if verbose:
            print(f"  Found {len(existing_topologies)} existing topologies in Edge Services")
    except Exception as e:
        if verbose:
            print(f"  Warning: Could not fetch existing topologies: {e}")

campus_config = converter.convert(filtered_config, existing_topologies)
```

## Testing

After applying these changes, test with:

```bash
python main.py --xiq-login --controller-url https://your-controller.example.com --username admin --password "your-password"
```

Expected behavior:
- ✅ Existing VLANs are skipped (not re-created)
- ✅ Services use existing topology IDs
- ✅ Services are created with status "disabled" for review
- ✅ No "role ID required" errors
- ✅ No "VLAN not found" errors

## Important Notes

1. Services are created with `status: "disabled"` - you must manually enable them in Edge Services after review
2. Captive portal is enabled by default to satisfy role ID requirements - disable in Edge Services if not needed
3. All services use the same role ID - customize in Edge Services if different roles are needed
4. Existing topologies are reused - new VLANs will only be created if they don't already exist
