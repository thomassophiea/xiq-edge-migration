# XIQ to Edge Services Migration Tool

This is the working migration folder with all fixes applied.

## Quick Start

### Step 1: Initial Setup (First Time Only)
```bash
cd /Users/thomassophieaii/Documents/Claude/migration
./setup.sh
```

This creates a Python virtual environment and installs all dependencies.

### Step 2: Run the Migration Tool

**Option A: Using the launcher script (recommended)**
```bash
cd /Users/thomassophieaii/Documents/Claude/migration

# Test with XIQ extraction only (dry-run)
./migrate.sh --xiq-username tsophiea@extremenetworks.com --xiq-password 'TSts1232!!*7' --dry-run --verbose

# Full migration to Edge Services
./migrate.sh \
  --xiq-username tsophiea@extremenetworks.com \
  --xiq-password 'TSts1232!!*7' \
  --controller-url https://tsophiea.ddns.net \
  --username admin \
  --password 'TSts1232!!*7' \
  --verbose
```

**Option B: Using the virtual environment directly**
```bash
cd /Users/thomassophieaii/Documents/Claude/migration
source venv/bin/activate

# Test with XIQ extraction only (dry-run)
python main.py --xiq-username tsophiea@extremenetworks.com --xiq-password 'TSts1232!!*7' --dry-run --verbose

# Full migration to Edge Services
python main.py \
  --xiq-username tsophiea@extremenetworks.com \
  --xiq-password 'TSts1232!!*7' \
  --controller-url https://tsophiea.ddns.net \
  --username admin \
  --password 'TSts1232!!*7' \
  --verbose

# When done, deactivate the virtual environment
deactivate
```

## All Fixes Applied

✅ **XIQ API Integration**
- SSIDs fetch from `/ssids` endpoint
- VLANs extract from user profiles
- RADIUS servers from `/radius-servers/external`
- Proper pagination with `data` field
- Security settings from `access_security` object

✅ **Edge Services Integration**
- Fetches existing topologies before conversion
- Skips duplicate VLANs (no conflicts)
- Uses existing topology IDs for services
- Correct role ID: `4459ee6c-2f76-11e7-93ae-92361f002671`
- Captive portal enabled for role requirement

✅ **Config Converter**
- Maps VLAN IDs to existing topology UUIDs
- Sets both authenticated and non-authenticated role IDs
- Creates services in "disabled" state for review

## What to Expect

### During Migration:
1. Connects to XIQ and fetches configuration
2. Shows SSIDs, VLANs, RADIUS servers found
3. Allows selection of objects to migrate
4. Connects to Edge Services
5. Fetches existing topologies (e.g., VLAN 1)
6. Converts configuration
7. Posts to Edge Services

### Expected Output:
```
✓ Configuration retrieved from XIQ
  - SSIDs: 20
  - VLANs: 5
  - RADIUS Servers: 3

✓ Connected to Edge Services
✓ Found 4 existing topologies

✓ Conversion complete
  - Services (SSIDs): 2
  - Topologies (VLANs): 2

Posting configuration...
  Posting Topology (VLAN) 2 - v2...
    Success
  Posting Topology (VLAN) 1 - 1...
    Skipped (VLAN 1 already exists)
  Posting Service (SSID) 'Skynet'...
    Success

Details:
  topologies: 1/2 topologies posted successfully (1 skipped - already exist)
  services: 2/2 services posted successfully
```

## Post-Migration Steps

1. **Login to Edge Services Web UI**
2. **Navigate to Services**
3. **Review migrated services** (they will be in "disabled" state)
4. **Adjust settings as needed:**
   - Disable captive portal if not using
   - Change role assignments if needed
   - Update any service-specific settings
5. **Enable services** one by one
6. **Test connectivity** for each SSID

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
cd /Users/thomassophieaii/Documents/Claude/migration
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
- ✅ Edge Services v5.26 at tsophiea.ddns.net
- ✅ 20 SSIDs with various security types (Open, PSK, PPSK, 802.1X, OWE)
- ✅ 5 VLANs (IDs: 1, 2, 3, 10, 666)
- ✅ 3 RADIUS servers

## Success Criteria

Migration successful when:
- ✅ All selected SSIDs appear in Edge Services
- ✅ SSIDs reference correct VLANs
- ✅ No errors during posting
- ✅ Services show as "disabled" (ready to enable)
- ✅ No duplicate VLANs created

---

**Ready to use! All fixes have been applied and tested.**
