# Edge Services Integration - Fixes Applied

## Quick Start

Run this command to apply all fixes automatically:

```bash
python3 apply_fixes.py
```

This will:
- ✅ Patch all necessary files
- ✅ Create `.backup` files for safety
- ✅ Fix all Edge Services posting issues

## What Was Fixed

### Problem 1: Role ID Requirement Error
```
"Non-auth role ID is required when captive portal is not enabled."
```

**Root Cause:** Edge Services requires specific role IDs even when not using captive portal

**Fix Applied:**
- Services now use existing role ID: `4459ee6c-2f76-11e7-93ae-92361f002671`
- Enabled captive portal by default (can be disabled in Edge Services UI)
- Both `authenticatedUserDefaultRoleID` and `nonAuthenticatedUserDefaultRoleID` are set

### Problem 2: VLAN Conflict Error
```
"VLAN tag conflict"
```

**Root Cause:** Trying to create VLANs that already exist (like VLAN 1)

**Fix Applied:**
- Fetch existing topologies before posting
- Skip topologies that already exist
- Only create new VLANs that don't exist

### Problem 3: VLAN Not Found Error
```
"VLAN not found"
```

**Root Cause:** Services were using generated UUIDs instead of actual topology IDs

**Fix Applied:**
- Fetch existing topologies from Edge Services
- Map VLAN IDs to actual topology UUIDs
- Use real topology IDs when creating services

## Files Modified

1. **src/config_converter.py**
   - Added `existing_topologies` parameter
   - Maps VLAN IDs to existing topology UUIDs
   - Uses standard role ID
   - Enables captive portal

2. **src/campus_controller_client.py**
   - Added `get_existing_topologies()` method
   - Fetches existing VLANs to avoid conflicts

3. **main.py**
   - Fetches existing topologies before conversion
   - Passes topology info to converter

## Testing

After applying fixes, test with:

```bash
# Interactive mode
python main.py --xiq-login

# Or with credentials
python main.py \
  --xiq-token YOUR_XIQ_TOKEN \
  --controller-url https://your-controller.example.com \
  --username admin \
  --password 'your-password'
```

## Expected Results

✅ **Before fixes:**
- ❌ "Non-auth role ID required" error
- ❌ "VLAN tag conflict" error
- ❌ "VLAN not found" error
- ❌ 0/X services posted successfully

✅ **After fixes:**
- ✅ Existing VLANs skipped (with message)
- ✅ Services created successfully
- ✅ Services in "disabled" state for review
- ✅ X/X services posted successfully

## Post-Migration Steps

After migration completes:

1. **Review Services in Edge Services UI**
   - Services are created with `status: "disabled"`
   - Review configuration before enabling

2. **Adjust Captive Portal Settings**
   - Captive portal is enabled by default to satisfy role requirements
   - Disable if not needed

3. **Customize Role Assignments**
   - All services use the same default role ID
   - Assign specific roles as needed

4. **Enable Services**
   - Enable services one by one after verification
   - Test connectivity for each SSID

## Rollback

If you need to rollback:

```bash
# Restore from backups
cp src/config_converter.py.backup src/config_converter.py
cp src/campus_controller_client.py.backup src/campus_controller_client.py
cp main.py.backup main.py
```

## Summary of Changes

| File | Lines Changed | Purpose |
|------|---------------|---------|
| config_converter.py | ~50 lines | Topology mapping, role IDs |
| campus_controller_client.py | ~15 lines | Fetch existing topologies |
| main.py | ~10 lines | Pre-fetch topologies |

Total: ~75 lines of code changes across 3 files

## Support

If you encounter issues:

1. Check `FIXES_APPLIED.md` for detailed explanations
2. Review backup files (`.backup` extension)
3. Check Edge Services logs
4. Verify network connectivity to Edge Services

## Known Limitations

1. **Role IDs:** All services use the same role ID - customize manually if different roles needed
2. **Captive Portal:** Enabled by default - disable in Edge Services if not using
3. **Service Status:** Services created as "disabled" - must enable manually
4. **VLAN Properties:** Only basic VLAN properties migrated - advanced settings must be configured manually

## Success Criteria

Migration is successful when:
- ✅ All selected SSIDs appear in Edge Services
- ✅ SSIDs reference correct VLANs
- ✅ Security settings preserved (WPA2/WPA3/Open/etc)
- ✅ No errors in migration output
- ✅ Services show as "disabled" awaiting activation

---

**Last Updated:** 2025-11-22
**Tested With:** Edge Services v5.26, XIQ API v1
