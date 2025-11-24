# Migration Folder - Test Instructions

## ✅ All Fixes Applied and Verified

### Verified Fixes:

1. ✅ `get_existing_topologies()` method exists in campus_controller_client.py (line 127)
2. ✅ Role ID `4459ee6c-2f76-11e7-93ae-92361f002671` configured in config_converter.py (line 186)
3. ✅ `existing_topologies` parameter added to convert() method (line 19)
4. ✅ VLAN ID to topology UUID mapping implemented
5. ✅ Main.py connects to Edge Services before conversion
6. ✅ Existing topologies fetched and passed to converter

## Quick Test Commands

**IMPORTANT:** Run the setup script first to create the virtual environment:
```bash
cd /path/to/xiq-edge-migration
./setup.sh
```

### Test 1: XIQ Connection Only (Dry Run)
```bash
cd /path/to/xiq-edge-migration
./migrate.sh \
  --xiq-username user@example.com \
  --xiq-password 'your-password' \
  --dry-run \
  --verbose
```

**Expected:** SSIDs, VLANs, and RADIUS servers should be retrieved and displayed.

### Test 2: Full Migration with Selection
```bash
cd /path/to/xiq-edge-migration
./migrate.sh \
  --xiq-username user@example.com \
  --xiq-password 'your-password' \
  --controller-url https://your-controller.example.com \
  --username admin \
  --password 'your-password' \
  --verbose
```

**Expected Results:**
```
✓ Configuration retrieved from XIQ
  - SSIDs: 20
  - VLANs: 5
  - RADIUS Servers: 3

✓ Connected to Edge Services
✓ Found 4 existing topologies

Converting to Edge Services format...
✓ Conversion complete
  - Services (SSIDs): X
  - Topologies (VLANs): X

Posting configuration...
  Posting Topology (VLAN) 1 - 1...
    Skipped (VLAN 1 already exists)  ← Should skip existing
  Posting Topology (VLAN) 2 - v2...
    Success  ← Should create new
  Posting Service (SSID) 'Skynet'...
    Success  ← Should succeed with role IDs

✓ SUCCESS
Details:
  topologies: X/Y posted (Z skipped - already exist)
  services: X/Y posted
```

### Test 3: Select Specific SSIDs
```bash
cd /path/to/xiq-edge-migration
./migrate.sh \
  --xiq-username user@example.com \
  --xiq-password 'your-password' \
  --controller-url https://your-controller.example.com \
  --username admin \
  --password 'your-password'
```

Then when prompted:
1. Select SSIDs: `1,2` (select first 2)
2. Select VLANs: `auto` (auto-select VLANs used by selected SSIDs)
3. Confirm posting: `y`

## Known Good Configuration

### XIQ Credentials:
- **Email:** user@example.com
- **Password:** your-password

### Edge Services:
- **URL:** https://your-controller.example.com
- **Username:** admin
- **Password:** your-password

### Expected XIQ Data:
- 20 SSIDs (ssid0, Skynet, Skynet_Junior, Skynet_Guest, etc.)
- 5 VLANs (1, 2, 3, 10, 666)
- 3 RADIUS servers

### Expected Edge Services Data:
- 4 existing topologies (including VLAN 1)
- Role ID: 4459ee6c-2f76-11e7-93ae-92361f002671

## Validation Checklist

After running migration, verify:

- [ ] No "VLAN tag conflict" errors
- [ ] No "Non-auth role ID required" errors
- [ ] No "VLAN not found" errors
- [ ] Existing VLAN 1 was skipped (not recreated)
- [ ] New VLANs were created successfully
- [ ] Services created with status="disabled"
- [ ] Services have both role IDs set
- [ ] Services reference correct topology IDs

## Troubleshooting

### If migration fails:

1. **Check XIQ authentication:**
   ```bash
   python -c "from src.xiq_api_client import XIQAPIClient; client = XIQAPIClient.login('user@example.com', 'your-password', verbose=True); print('Success!')"
   ```

2. **Check Edge Services connection:**
   ```bash
   python -c "from src.campus_controller_client import CampusControllerClient; client = CampusControllerClient('https://your-controller.example.com', 'admin', 'your-password', verbose=True); print(f'Topologies: {len(client.get_existing_topologies())}')"
   ```

3. **Check conversion:**
   ```bash
   python -c "from src.config_converter import ConfigConverter; print('Converter OK')"
   ```

## Success Indicators

✅ **Migration Successful If:**
- Services appear in Edge Services UI
- Services are in "disabled" state
- SSIDs reference correct VLANs
- No duplicate VLANs created
- All selected objects migrated

## Next Steps After Success

1. Login to Edge Services web UI
2. Navigate to Configuration > Services
3. Review migrated services
4. Disable captive portal if not needed
5. Adjust role assignments if needed
6. Enable services one by one
7. Test WiFi connectivity

---

**Status: Ready for Testing**
**All fixes applied: 2025-11-22**
