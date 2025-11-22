# Quick Start Guide

## Super Simple Usage

Just run:

```bash
python main.py
```

That's it! The tool will guide you through everything, including letting you **choose exactly which objects to migrate**.

## What You'll Need

Before running, have ready:

### 1. XIQ Credentials (one of):
   - **Username and password** for Extreme Cloud IQ, OR
   - **API token** from XIQ Global Settings, OR
   - **Saved config file** from previous run

### 2. Edge Services Info:
   - **IP address or hostname** (e.g., 10.10.10.100)
   - **Username** (usually "admin")
   - **Password**

## Step-by-Step Walkthrough

### 1. Start the Tool

```bash
$ python main.py
```

### 2. Choose XIQ Authentication

```
How would you like to authenticate to XIQ?
  1. Username and Password    ← Easiest
  2. API Token               ← Most secure
  3. Use existing configuration file

Enter choice (1-3): 1
```

Choose **1** for username/password (recommended for first time)

### 3. Select Region

```
Select your ExtremeCloud IQ region:
  1. Global (api.extremecloudiq.com)    ← Most common
  2. EU (api-eu.extremecloudiq.com)
  3. APAC (api-apac.extremecloudiq.com)
  4. California (cal-api.extremecloudiq.com)

Enter choice (1-4) [default: 1]: 1
```

Press **Enter** for Global (default)

### 4. Enter XIQ Credentials

```
XIQ Username (email): your.email@company.com
XIQ Password: ********
```

### 5. **NEW! Select Which Objects to Migrate**

The tool retrieves all objects from XIQ, then lets you choose which ones to migrate:

#### SSIDs Selection

```
======================================================================
SELECT OBJECTS TO MIGRATE
======================================================================

----------------------------------------------------------------------
SSIDs Found: 5
----------------------------------------------------------------------
  1. [✓] Corporate-WiFi                  (Security: psk        VLAN: 100)
  2. [✓] Guest-WiFi                      (Security: open       VLAN: 200)
  3. [✓] Enterprise-Secure               (Security: dot1x      VLAN: 100)
  4. [✗] Test-Network                    (Security: psk        VLAN: 999)
  5. [✓] IoT-Devices                     (Security: psk        VLAN: 300)

Select SSIDs to migrate:
  • Enter numbers separated by commas (e.g., 1,2,4)
  • Enter 'all' to select all SSIDs
  • Enter 'none' to skip SSIDs

Your selection: 1,2,3,5
```

Choose which SSIDs you want. Type:
- `1,2,3` to select specific SSIDs
- `all` to migrate everything
- `none` to skip SSIDs

#### VLANs Selection

```
----------------------------------------------------------------------
VLANs Found: 3
----------------------------------------------------------------------
  1. VLAN 100    Corporate                 (192.168.100.0/24     DHCP)
  2. VLAN 200    Guest                     (192.168.200.0/24     DHCP)
  3. VLAN 300    IoT                       (192.168.300.0/24     No DHCP)

Select VLANs to migrate:
  • Enter numbers separated by commas (e.g., 1,2,3)
  • Enter 'all' to select all VLANs
  • Enter 'none' to skip VLANs
  • Enter 'auto' to auto-select VLANs used by selected SSIDs

Your selection: auto
```

Type `auto` to automatically include only VLANs used by your selected SSIDs!

#### RADIUS Servers Selection

```
----------------------------------------------------------------------
RADIUS Servers Found: 2
----------------------------------------------------------------------
  1. Primary-RADIUS                  (192.168.1.10:1812)
  2. Secondary-RADIUS                (192.168.1.11:1812)

Select RADIUS servers to migrate:
  • Enter numbers separated by commas (e.g., 1,2)
  • Enter 'all' to select all RADIUS servers
  • Enter 'none' to skip RADIUS servers

Your selection: all
```

#### Selection Summary

```
======================================================================
SELECTION SUMMARY
======================================================================
  SSIDs:          4
  VLANs:          3
  RADIUS Servers: 2

Proceed with these selections? (y/n): y
```

Review and confirm your selections!

### 6. Enter Edge Services Info

```
----------------------------------------------------------------------
STEP 2: Edge Services Configuration
----------------------------------------------------------------------

Edge Services: 10.10.10.100
Edge Services Username [admin]: admin
Edge Services Password: ********
```

### 7. Final Confirmation

```
----------------------------------------------------------------------
STEP 3: Post Configuration to Edge Services
----------------------------------------------------------------------

Ready to post configuration to: https://10.10.10.100:5825
  - 4 Services (SSIDs)
  - 3 Topologies (VLANs)
  - 1 AAA Policies

Proceed with posting to Edge Services? (y/n): y
```

Type **y** and press Enter

### 8. Done!

```
✓ SUCCESS: Configuration posted to Edge Services!

Details:
  topologies: 3/3 topologies posted successfully
  aaa_policies: 1/1 AAA policies posted successfully
  services: 4/4 services posted successfully

✓ Process completed successfully!
```

## Selection Tips

### Smart VLAN Selection

Use `auto` when selecting VLANs to automatically include only the VLANs that your selected SSIDs actually use. This prevents migrating unused VLANs.

**Example:**
- You select SSIDs 1, 2, 3 which use VLANs 100, 200
- Type `auto` for VLAN selection
- Only VLANs 100 and 200 are migrated (VLAN 300 is skipped)

### Select All

If you want to migrate everything without choosing, use the `--select-all` flag:

```bash
python main.py --select-all
```

This skips the interactive selection and migrates all objects.

### Comma-Separated Selection

You can select multiple objects at once:

```
Your selection: 1,2,5,7
```

This selects items 1, 2, 5, and 7.

## Common Questions

### Q: What if I don't want to post yet, just test?

Use `--dry-run`:

```bash
python main.py --dry-run --output test.json
```

You'll still get the interactive selection!

### Q: Can I skip the selection and migrate everything?

Yes! Use `--select-all`:

```bash
python main.py --select-all
```

### Q: What if I mess up my selection?

When you see the summary, you can say 'n' to cancel and start over.

### Q: Can I automate this?

Yes! Use command-line mode with `--select-all`:

```bash
python main.py \
    --xiq-username user@example.com \
    --xiq-password "yourpass" \
    --controller-url https://10.10.10.100 \
    --username admin \
    --password "adminpass" \
    --select-all
```

### Q: What happens to Radio Profiles?

Radio profiles are shown for information but not migrated directly to Edge Services (they're configured differently in Edge Services).

## Troubleshooting

### "Authentication failed"
- Check your username/password
- Verify you selected the correct XIQ region
- For SSO accounts, use API token instead

### "Connection refused"
- Verify Edge Services IP address
- Check port 5825 is accessible
- Ensure Edge Services is running

### "No SSIDs found"
- Verify you have SSIDs configured in XIQ
- Check your XIQ account has proper permissions
- Run with `--verbose` to see details

### Selection Errors

**"Invalid selection"**
- Make sure you use commas between numbers: `1,2,3`
- Don't use spaces: `1, 2, 3` won't work
- Or just type `all` to select everything

## Next Steps

- Check the full **README.md** for all options
- See **USAGE_GUIDE.md** for advanced usage
- Look at **examples/** for sample configurations

## Need Help?

Run with `--verbose` to see detailed logs:

```bash
python main.py --verbose
```

This shows exactly what the tool is doing at each step.

## Example: Migrating Only Guest WiFi

Here's a real example of migrating just your guest network:

```bash
$ python main.py

# Choose XIQ login...
# After retrieving configuration:

SSIDs Found: 5
  1. Corporate-WiFi
  2. Guest-WiFi          ← You want this one
  3. Enterprise-Secure
  4. Test-Network
  5. IoT-Devices

Your selection: 2

VLANs Found: 3
  1. VLAN 100 Corporate
  2. VLAN 200 Guest      ← Auto-selected because Guest-WiFi uses it
  3. VLAN 300 IoT

Your selection: auto

RADIUS Servers Found: 2
  1. Primary-RADIUS
  2. Secondary-RADIUS

Your selection: none     ← Guest WiFi doesn't need RADIUS

SELECTION SUMMARY
  SSIDs:          1 (Guest-WiFi only)
  VLANs:          1 (Guest VLAN only)
  RADIUS Servers: 0

Proceed? y
```

Perfect! You've migrated just your guest network!
