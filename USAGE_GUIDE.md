# XIQ to Edge Services - Complete Usage Guide

## Overview

This tool converts Extreme Cloud IQ (XIQ) wireless configurations to Extreme Edge Services format and automatically posts them via REST API.

**Based on:**
- XIQ API patterns from the ExtremeCloud IQ Extractor
- Edge Services v5.26 REST API Gateway (learned from swagger specification)

## Quick Start

### Option 1: Pull from XIQ with Username/Password
```bash
python main.py --xiq-login \
    --xiq-region global \
    --controller-url https://edge-services.example.com \
    --username admin \
    --password yourpassword \
    --verbose
```

### Option 2: Pull from XIQ with API Token
```bash
python main.py --xiq-token YOUR_XIQ_API_TOKEN \
    --xiq-region global \
    --controller-url https://edge-services.example.com \
    --username admin \
    --password yourpassword
```

### Option 3: Convert from XIQ Config File
```bash
python main.py --input-file examples/sample_xiq_config.json \
    --controller-url https://edge-services.example.com \
    --username admin \
    --password yourpassword
```

## XIQ Authentication Methods

### Method 1: Username/Password Login

Uses the XIQ `/login` endpoint to authenticate and get an access token.

```bash
python main.py --xiq-login \
    --xiq-region global \
    --controller-url https://controller.example.com \
    --username admin \
    --password secret
```

You'll be prompted for:
- XIQ Username (email)
- XIQ Password

**Advantages:**
- No need to manage API tokens
- Works with any XIQ account
- Supports all XIQ regions

### Method 2: API Token

Uses a pre-generated API token from XIQ Global Settings.

**Get an API Token:**
1. Log into Extreme Cloud IQ
2. Navigate to **Global Settings** > **API Token Management**
3. Click **Generate** to create a new token
4. Copy the token

```bash
python main.py --xiq-token ABC123XYZ... \
    --controller-url https://controller.example.com \
    --username admin \
    --password secret
```

**Advantages:**
- No credential prompts
- Better for automation/scripts
- Token can have limited permissions

### Method 3: Configuration File

Use a previously saved XIQ configuration JSON file.

```bash
python main.py --input-file my_xiq_config.json \
    --controller-url https://controller.example.com \
    --username admin \
    --password secret
```

**Advantages:**
- Offline conversion
- Edit/modify config before conversion
- No API access needed

## XIQ Regions

XIQ has different regional API endpoints. Specify with `--xiq-region`:

| Region | Flag | API URL |
|--------|------|---------|
| Global (default) | `--xiq-region global` | `https://api.extremecloudiq.com` |
| Europe | `--xiq-region eu` | `https://api-eu.extremecloudiq.com` |
| Asia Pacific | `--xiq-region apac` | `https://api-apac.extremecloudiq.com` |
| California | `--xiq-region cal` | `https://cal-api.extremecloudiq.com` |

## Edge Services Authentication

The tool uses OAuth 2.0 to authenticate with Edge Services:

- **Endpoint:** `https://controller:5825/management/v1/oauth2/token`
- **Method:** Password grant type
- **Default Port:** 5825 (automatically added if not specified)

```bash
--controller-url https://controller.example.com  # Port 5825 added automatically
--username admin                                  # Edge Services admin user
--password yourpassword                           # Edge Services password
```

## What Gets Converted

### From XIQ → Edge Services

| XIQ Object | Edge Services Object | Notes |
|------------|-------------------------|-------|
| SSIDs | Services (ServiceElement) | Includes security, VLANs, settings |
| VLANs | Topologies (TopologyElement) | Includes IP addressing, DHCP |
| RADIUS Servers | AAA Policies | Groups servers into policies |
| Radio Profiles | (Info only) | Not directly created in Edge Services |
| Network Policies | (Referenced) | Used to extract VLANs |

### Security Types Supported

✅ **Open Networks**
- No encryption
- Broadcast or hidden SSID

✅ **WPA-PSK (Personal)**
- WPA2-PSK
- WPA3-PSK (auto mode)
- Pre-shared key authentication
- PMF (Protected Management Frames): disabled, optional, required

✅ **WPA-Enterprise (802.1X)**
- WPA2-Enterprise
- WPA3-Enterprise (auto mode)
- RADIUS authentication
- PMF support

## API Endpoints Used

### XIQ API Endpoints (from Extractor patterns)

```
POST   /login                    - Authenticate and get token
GET    /devices                  - Get all devices
GET    /ssids                    - Get all SSIDs
GET    /network-policies         - Get network policies
GET    /vlans                    - Get VLANs
GET    /radio-profiles           - Get radio profiles
GET    /radius-servers/external  - Get RADIUS servers
GET    /user-profiles            - Get user profiles
```

### Edge Services API Endpoints (v5.26)

```
POST   /management/v1/oauth2/token    - OAuth authentication
POST   /management/v1/services        - Create services (SSIDs)
POST   /management/v1/topologies      - Create topologies (VLANs)
POST   /management/v1/aaapolicy       - Create AAA policies
GET    /management/v1/services        - List existing services
GET    /management/v1/topologies      - List existing topologies
```

## Command Line Options

### Required (one of):
- `--input-file <file>` - Path to XIQ config JSON file
- `--xiq-token <token>` - XIQ API token
- `--xiq-login` - Prompt for XIQ username/password

### Required:
- `--controller-url <url>` - Edge Services URL

### Optional:
- `--username <user>` - Edge Services username (required if not --dry-run)
- `--password <pass>` - Edge Services password (required if not --dry-run)
- `--dry-run` - Convert without posting to controller
- `--output <file>` - Save converted config to JSON file
- `--verbose` - Enable detailed logging
- `--xiq-region <region>` - XIQ region: global, eu, apac, cal (default: global)

## Examples

### Example 1: Complete Migration with Login

Pull from XIQ and push to Edge Services:

```bash
python main.py --xiq-login \
    --xiq-region global \
    --controller-url https://10.10.10.100 \
    --username admin \
    --password Extreme123! \
    --verbose
```

**What happens:**
1. Prompts for XIQ credentials
2. Authenticates to XIQ
3. Retrieves SSIDs, VLANs, RADIUS servers
4. Converts to Edge Services format
5. Authenticates to Edge Services
6. Posts Services, Topologies, AAA Policies
7. Shows summary

### Example 2: Test Conversion First (Dry Run)

Test the conversion without posting:

```bash
python main.py --xiq-token ABC123 \
    --controller-url https://controller.example.com \
    --dry-run \
    --output preview.json \
    --verbose
```

**What happens:**
1. Connects to XIQ with token
2. Retrieves configuration
3. Converts to Edge Services format
4. Saves to `preview.json`
5. Shows preview (no posting)

### Example 3: Offline Conversion

Convert a saved config file:

```bash
python main.py --input-file my_saved_config.json \
    --controller-url https://controller.example.com \
    --dry-run \
    --output campus_config.json
```

**What happens:**
1. Reads local JSON file
2. Converts to Edge Services format
3. Saves to `campus_config.json`
4. No network calls

### Example 4: EU Region with API Token

Pull from XIQ EU region:

```bash
python main.py --xiq-token XYZ789 \
    --xiq-region eu \
    --controller-url https://campus.example.com:5825 \
    --username ccadmin \
    --password SecurePass \
    --output backup.json
```

**What happens:**
1. Connects to `api-eu.extremecloudiq.com`
2. Retrieves config with token
3. Converts configuration
4. Saves backup to `backup.json`
5. Posts to Edge Services
6. Shows results

## Troubleshooting

### XIQ Authentication Errors

**Error:** "Authentication failed: Invalid username or password"
- Verify credentials are correct
- Check if account uses SSO/SAML (not supported for login method, use API token instead)
- Try the correct region (--xiq-region)

**Error:** "Failed to connect to XIQ API"
- Check internet connectivity
- Verify XIQ region is correct
- Check firewall rules

### Edge Services Errors

**Error:** "Authentication failed: 401"
- Verify Edge Services credentials
- Check user has Full admin permissions
- Verify controller URL is correct

**Error:** "Connection refused" or "timeout"
- Check Edge Services is reachable
- Verify port 5825 is accessible
- Check firewall rules
- Verify HTTPS is configured

**Error:** "Failed to post Service/Topology"
- Check verbose output for details
- Verify VLAN IDs don't conflict
- Check service names are unique
- Review required fields in converted config

### Configuration Issues

**No SSIDs found:**
- Verify XIQ account has access to SSIDs
- Check network policies are configured
- Try --verbose to see API responses

**VLANs not converting:**
- VLANs may be embedded in network policies
- Check VLAN IDs are valid (1-4094)
- Verify network policies have VLAN assignments

## Advanced Usage

### Save XIQ Config for Later

Pull from XIQ and save without posting:

```bash
python main.py --xiq-login \
    --controller-url https://dummy.local \
    --dry-run \
    --output xiq_backup_$(date +%Y%m%d).json \
    --verbose
```

### Chain with jq for Filtering

Extract only SSIDs from converted config:

```bash
python main.py --input-file config.json \
    --controller-url https://controller \
    --dry-run \
    --output /dev/stdout | jq '.services'
```

### Automated Migration Script

```bash
#!/bin/bash
# migrate.sh - Automated XIQ to Edge Services migration

XIQ_TOKEN="your-token-here"
CC_URL="https://campus-controller.local"
CC_USER="admin"
CC_PASS="password"
BACKUP_DIR="./migrations/$(date +%Y%m%d_%H%M%S)"

mkdir -p "$BACKUP_DIR"

# Step 1: Pull and backup XIQ config
echo "Pulling from XIQ..."
python main.py --xiq-token "$XIQ_TOKEN" \
    --controller-url "$CC_URL" \
    --dry-run \
    --output "$BACKUP_DIR/xiq_config.json" \
    --verbose

# Step 2: Convert and post to Edge Services
echo "Posting to Edge Services..."
python main.py --input-file "$BACKUP_DIR/xiq_config.json" \
    --controller-url "$CC_URL" \
    --username "$CC_USER" \
    --password "$CC_PASS" \
    --output "$BACKUP_DIR/campus_config.json" \
    --verbose

echo "Migration complete. Backups in: $BACKUP_DIR"
```

## File Structure

```
xiq-to-campus-converter/
├── main.py                          # Main CLI application
├── requirements.txt                 # Python dependencies
├── README.md                        # Project overview
├── USAGE_GUIDE.md                   # This file
├── src/
│   ├── xiq_parser.py               # Parse XIQ JSON files
│   ├── xiq_api_client.py           # Pull from XIQ API (Extractor patterns)
│   ├── campus_controller_client.py # Post to Edge Services API
│   └── config_converter.py         # Convert XIQ → Edge Services
└── examples/
    ├── sample_xiq_config.json      # Example XIQ config
    └── README.md                   # Examples documentation
```

## Security Notes

- Credentials are never stored or logged
- Use `--verbose` carefully in production (shows detailed API calls)
- API tokens and passwords are sensitive - use environment variables for automation
- Edge Services SSL verification is disabled by default (self-signed certs)
- XIQ SSL verification is enabled by default

## Next Steps

1. **Test with dry-run:** Always test conversion first with `--dry-run`
2. **Review converted config:** Check `--output` file before posting
3. **Start small:** Test with one or two SSIDs first
4. **Backup:** Save Edge Services config before migration
5. **Verify:** Check Edge Services after posting to ensure configs are correct

## Support

For issues:
- XIQ API: Check Extreme Cloud IQ documentation
- Edge Services API: Check Edge Services v5.26 REST API docs
- This tool: Review logs with `--verbose` flag
