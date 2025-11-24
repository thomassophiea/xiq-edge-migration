# XIQ to Edge Services Migration Tool

This is the working migration folder with all fixes applied.

## Quick Start

### Step 1: Initial Setup (First Time Only)
```bash
cd /path/to/xiq-edge-migration
./setup.sh
```

This creates a Python virtual environment and installs all dependencies.

### Step 2: Choose Your Interface

The migration tool offers two interfaces:

**🌐 Web UI (NEW! - Recommended for most users)**
```bash
./start_ui.sh
```
Then open your browser to: `http://localhost:5000`

- Point-and-click interface
- Visual progress tracking
- Interactive object selection
- No command-line knowledge required
- See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for details

**💻 Command Line Interface (For automation & advanced users)**

**Option A: Using the launcher script**
```bash
cd /path/to/xiq-edge-migration

# Test with XIQ extraction only (dry-run)
./migrate.sh --xiq-username 'yourusername' --xiq-password 'yourpassword' --dry-run --verbose

# Full migration to Edge Services
./migrate.sh \
  --xiq-username username \
  --xiq-password '!*7' \
  --controller-url https:// \
  --username admin \
  --password '!*7' \
  --verbose
```

**Option B: Using the virtual environment directly**
```bash
cd /path/to/xiq-edge-migration
source venv/bin/activate

# Test with XIQ extraction only (dry-run)
python main.py --xiq-username username --xiq-password '!*7' --dry-run --verbose

# Full migration to Edge Services
python main.py \
  --xiq-username username \
  --xiq-password '!*7' \
  --controller-url https:// \
  --username admin \
  --password '!*7' \
  --verbose

# When done, deactivate the virtual environment
deactivate
```

## All Fixes Applied

✅ **XIQ API Integration**
- SSIDs fetch from `/ssids` endpoint
- VLANs extract from user profiles
- RADIUS servers from `/radius-servers/external`
- Devices (APs) with names and locations
- Proper pagination with `data` field
- Security settings from `access_security` object

✅ **Edge Services Integration**
- Fetches existing topologies before conversion
- Skips duplicate VLANs (no conflicts)
- Uses existing topology IDs for services
- Correct role ID: `4459ee6c-2f76-11e7-93ae-92361f002671`
- Updates AP names and locations via PUT /v1/aps/{serial}
- Posts Rate Limiters and CoS policies

✅ **Config Converter**
- Maps VLAN IDs to existing topology UUIDs
- Sets both authenticated and non-authenticated role IDs
- Creates services in "disabled" state for review
- Converts DNS servers and domains for VLANs
- Converts AP configurations (name, location)
- Converts Rate Limiters (bandwidth policies)
- Converts Class of Service policies (QoS)

## What to Expect

### During Migration:
1. Connects to XIQ and fetches configuration
2. Shows SSIDs, VLANs, RADIUS servers, APs found
3. Allows selection of objects to migrate
4. Connects to Edge Services
5. Fetches existing topologies (e.g., VLAN 1)
6. Converts configuration
7. Posts to Edge Services
8. **Assigns SSIDs to Associated Profiles** (NEW!)
   - Fetches available profiles
   - Prompts for profile selection per SSID
   - Asks which radios to use (2.4GHz, 5GHz, 6GHz)
   - Applies assignments automatically

### Expected Output:
```
✓ Configuration retrieved from XIQ
  - SSIDs: 20
  - VLANs: 5
  - RADIUS Servers: 3
  - Devices (APs): 45

✓ Connected to Edge Services
✓ Found 4 existing topologies

✓ Conversion complete
  - Rate Limiters: 3
  - CoS Policies: 2
  - Services (SSIDs): 2
  - Topologies (VLANs): 2
  - AAA Policies: 1
  - AP Configurations: 45

Posting configuration...
  Posting Rate Limiter 'Guest-100Mbps' (100000 Kbps)...
    Success
  Posting CoS Policy 'Video-Priority'...
    Success
  Posting Topology (VLAN) 2 - v2...
    Success
  Posting Topology (VLAN) 1 - 1...
    Skipped (VLAN 1 already exists)
  Posting AAA Policy 'XIQ_RADIUS_Policy'...
    Success
  Posting Service (SSID) 'Skynet'...
    Success
  Updating AP 02301A0B1234 - Name: 'Building-A-AP1', Location: 'Floor 1'...
    Success

Details:
  rate_limiters: 3/3 rate limiters posted successfully
  cos_policies: 2/2 CoS policies posted successfully
  topologies: 1/2 topologies posted successfully (1 skipped - already exist)
  aaa_policies: 1/1 AAA policies posted successfully
  services: 2/2 services posted successfully
  ap_configs: 45/45 AP configurations updated successfully
```

## Post-Migration Steps

1. **Login to Edge Services Web UI**
2. **Navigate to Services**
3. **Review migrated services** (they will be in "disabled" state)
4. **Verify Profile Assignments:**
   - Check Configuration → Profiles
   - Confirm SSIDs are assigned to correct profiles
   - Verify radio selections (2.4GHz, 5GHz, 6GHz)
5. **Adjust settings as needed:**
   - Disable captive portal if not using
   - Change role assignments if needed
   - Update any service-specific settings
6. **Enable services** one by one
7. **Test connectivity** for each SSID

## File Structure

```
migration/
├── main.py                  # Main application with all fixes
├── src/
│   ├── xiq_api_client.py   # XIQ API client (fixed pagination & endpoints)
│   ├── campus_controller_client.py  # CC client (topology lookup)
│   ├── config_converter.py # Converter (role IDs & topology mapping)
│   ├── export_utils.py     # CSV/JSON export utilities
│   └── xiq_parser.py       # JSON file parser
├── README.md               # This file
└── examples/               # Example scripts (if needed)
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'requests'"
**Solution:** Run the setup script first to create the virtual environment and install dependencies:
```bash
cd /path/to/xiq-edge-migration
./setup.sh
```
Then use the launcher script:
```bash
./migrate.sh --help
```

### Issue: "VLAN tag conflict"
**Solution:** Already fixed - existing VLANs are skipped

### Issue: "Non-auth role ID required"
**Solution:** Already fixed - both role IDs are set

### Issue: "VLAN not found"
**Solution:** Already fixed - uses existing topology IDs

### Issue: Services not appearing
**Check:** Services are created as "disabled" - enable them in Edge Services UI

## Important Notes

⚠️ **Services created as "disabled"** - Manual activation required in Edge Services
⚠️ **Captive portal enabled by default** - Required to satisfy role ID requirement, disable if not needed
⚠️ **All services use same role ID** - Customize roles in Edge Services if different access levels needed
⚠️ **Existing VLANs reused** - Only new VLANs are created

## Tested With

- ✅ XIQ API (username/password login)
- ✅ Edge Services v5.26 at username.ddns.net
- ✅ 20 SSIDs with various security types (Open, PSK, PPSK, 802.1X, OWE)
- ✅ 5 VLANs with DNS servers and DHCP settings
- ✅ 3 RADIUS servers
- ✅ 45 Access Points with names and locations
- ✅ Rate Limiters and CoS policies

## Success Criteria

Migration successful when:
- ✅ All selected SSIDs appear in Edge Services
- ✅ SSIDs reference correct VLANs
- ✅ No errors during posting
- ✅ Services show as "disabled" (ready to enable)
- ✅ No duplicate VLANs created

---

**Ready to use! All fixes have been applied and tested.**
