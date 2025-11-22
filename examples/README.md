# Example Configurations

This directory contains sample configuration files to help you understand the expected formats.

## sample_xiq_config.json

This is an example of XIQ configuration that can be used as input to the converter tool.

### Structure

The XIQ configuration file includes:

- **ssids**: List of SSID configurations
  - `name`: SSID name
  - `enabled`: Whether SSID is enabled
  - `broadcast_ssid`: Whether to broadcast the SSID
  - `vlan_id`: VLAN assignment
  - `security`: Security settings (PSK, 802.1X, open)
  - `max_clients`: Maximum client limit
  - `band_steering`: Band steering enabled/disabled
  - `fast_roaming`: 802.11k/r fast roaming

- **vlans**: List of VLAN configurations
  - `vlan_id`: VLAN ID number
  - `name`: VLAN name
  - `subnet`: Network subnet in CIDR notation
  - `gateway`: Gateway IP address
  - `dhcp_enabled`: DHCP relay/server enabled

- **authentication**: RADIUS server configurations
  - `ip`: RADIUS server IP
  - `auth_port`: Authentication port (typically 1812)
  - `acct_port`: Accounting port (typically 1813)
  - `secret`: Shared secret

## Usage Examples

### Basic Conversion

Convert the sample XIQ config to Edge Services format:

```bash
python main.py --input-file examples/sample_xiq_config.json \
    --controller-url https://campus-controller.example.com \
    --username admin \
    --password yourpassword \
    --verbose
```

### Dry Run Test

Test the conversion without posting to controller:

```bash
python main.py --input-file examples/sample_xiq_config.json \
    --controller-url https://campus-controller.example.com \
    --dry-run \
    --output examples/converted_config.json
```

### Pull from XIQ API

Pull configuration directly from XIQ and post to Edge Services:

```bash
python main.py --xiq-token YOUR_XIQ_API_TOKEN \
    --controller-url https://campus-controller.example.com \
    --username admin \
    --password yourpassword
```

## Security Settings

The converter supports these security types:

1. **Open**: No encryption
   ```json
   "security": {
     "type": "open"
   }
   ```

2. **WPA-PSK**: Pre-shared key
   ```json
   "security": {
     "type": "psk",
     "psk": "YourPassword123",
     "pmf": "optional"
   }
   ```

3. **WPA-Enterprise (802.1X)**: RADIUS authentication
   ```json
   "security": {
     "type": "dot1x",
     "wpa_version": "WPA2",
     "pmf": "required",
     "radius_servers": [...]
   }
   ```

## Notes

- All VLAN IDs in SSIDs must match VLANs defined in the vlans section
- RADIUS servers referenced in SSID security must be defined in the authentication section
- The converter automatically generates UUIDs for Edge Services objects
- Edge Services uses "Services" terminology for SSIDs
- Edge Services uses "Topologies" terminology for VLANs
