# XIQ to Edge Services Converter - Features

## 🎯 Interactive Object Selection (NEW!)

**You can now choose exactly which objects to migrate from XIQ to Edge Services!**

### How It Works

When you run `python main.py`, after connecting to XIQ and retrieving your configuration, you'll see:

```
======================================================================
SELECT OBJECTS TO MIGRATE
======================================================================
```

The tool shows you **everything** it found and lets you pick what to migrate.

## Selection Features

### 1. **SSID Selection**

Choose which wireless networks to migrate:

```
SSIDs Found: 5
----------------------------------------------------------------------
  1. [✓] Corporate-WiFi        (Security: psk    VLAN: 100)
  2. [✓] Guest-WiFi            (Security: open   VLAN: 200)
  3. [✓] Enterprise-Secure     (Security: dot1x  VLAN: 100)
  4. [✗] Test-Network          (Security: psk    VLAN: 999)
  5. [✓] IoT-Devices           (Security: psk    VLAN: 300)

Your selection: 1,2,3
```

**Options:**
- Type numbers: `1,2,3` - Select specific SSIDs
- Type `all` - Migrate all SSIDs
- Type `none` - Skip SSIDs entirely

**Shows:**
- ✓/✗ Enabled status
- SSID name
- Security type (open, psk, dot1x)
- VLAN assignment

### 2. **VLAN Selection with Auto-Detection**

Choose which VLANs to migrate:

```
VLANs Found: 3
----------------------------------------------------------------------
  1. VLAN 100  Corporate  (192.168.100.0/24  DHCP)
  2. VLAN 200  Guest      (192.168.200.0/24  DHCP)
  3. VLAN 300  IoT        (192.168.300.0/24  No DHCP)

Your selection: auto
```

**Options:**
- Type numbers: `1,2` - Select specific VLANs
- Type `all` - Migrate all VLANs
- Type `none` - Skip VLANs
- Type `auto` - **Automatically select only VLANs used by your selected SSIDs** ⭐

**Shows:**
- VLAN ID
- VLAN name
- IP subnet
- DHCP status

### 3. **RADIUS Server Selection**

Choose which authentication servers to migrate:

```
RADIUS Servers Found: 2
----------------------------------------------------------------------
  1. Primary-RADIUS      (192.168.1.10:1812)
  2. Secondary-RADIUS    (192.168.1.11:1812)

Your selection: all
```

**Options:**
- Type numbers: `1,2` - Select specific servers
- Type `all` - Migrate all RADIUS servers
- Type `none` - Skip RADIUS servers

**Shows:**
- Server name
- IP address and port

### 4. **Radio Profiles (Informational)**

Radio profiles are displayed but not migrated (Edge Services handles these differently):

```
Radio Profiles Found: 2
----------------------------------------------------------------------
Note: Radio profiles are informational only and not migrated directly
  1. Standard-2.4GHz  (Band: 2.4GHz, Channel: auto)
  2. Standard-5GHz    (Band: 5GHz, Channel: auto)
```

## Selection Summary & Confirmation

Before proceeding, you get a summary:

```
======================================================================
SELECTION SUMMARY
======================================================================
  SSIDs:          3
  VLANs:          2
  RADIUS Servers: 1

Proceed with these selections? (y/n):
```

Type `y` to continue or `n` to cancel and start over.

## Use Cases

### Use Case 1: Migrate Only Guest Network

Perfect for setting up a guest portal on Edge Services:

1. Select only your Guest SSID
2. Use `auto` for VLANs (automatically selects Guest VLAN)
3. Select `none` for RADIUS (guest doesn't need it)

**Result:** Clean guest network migration without corporate configs

### Use Case 2: Migrate Corporate Networks Only

Skip test/development networks:

1. Select SSIDs 1, 2, 3 (production SSIDs)
2. Skip SSID 4 (Test-Network)
3. Use `auto` for VLANs
4. Select `all` for RADIUS

**Result:** Only production networks migrated

### Use Case 3: Migrate Specific VLANs

You want specific VLANs on Edge Services:

1. Select desired SSIDs
2. Manually select VLANs: `1,3` (skip VLAN 2)
3. Select RADIUS as needed

**Result:** Granular control over VLAN migration

## Command-Line Options

### Skip Selection (Migrate Everything)

```bash
python main.py --select-all
```

Bypasses interactive selection and migrates all objects.

### Use in Scripts

```bash
python main.py \
    --xiq-username user@example.com \
    --controller-url https://10.10.10.100 \
    --username admin \
    --select-all  # ← No prompts, migrate everything
```

## Benefits

✅ **Granular Control** - Choose exactly what to migrate
✅ **Prevent Mistakes** - Don't migrate test/dev networks to production
✅ **Save Time** - Use `auto` to select only necessary VLANs
✅ **Safe Testing** - Try migrating one SSID first before doing all
✅ **Clean Migration** - Only move what you actually need

## Full Feature List

### XIQ Integration
- ✅ Username/password authentication
- ✅ API token authentication
- ✅ Multi-region support (Global, EU, APAC, California)
- ✅ Pulls SSIDs, VLANs, RADIUS servers, radio profiles
- ✅ **Interactive object selection**

### Edge Services Integration
- ✅ OAuth 2.0 authentication
- ✅ Posts Services (SSIDs)
- ✅ Posts Topologies (VLANs)
- ✅ Posts AAA Policies (RADIUS)
- ✅ Proper v5.26 API schemas

### Security Support
- ✅ Open networks
- ✅ WPA-PSK (WPA2/WPA3)
- ✅ WPA-Enterprise (802.1X)
- ✅ PMF (Protected Management Frames)

### Modes
- ✅ **Interactive mode** - Prompts for everything
- ✅ **Command-line mode** - Automation-friendly
- ✅ **Dry-run mode** - Test without posting
- ✅ **Verbose mode** - Detailed logging

### Quality of Life
- ✅ Smart VLAN auto-detection (`auto` option)
- ✅ Input validation with friendly error messages
- ✅ Confirmation before posting
- ✅ Progress indicators
- ✅ Summary of results
- ✅ Option to save config to file

## Quick Examples

### Example 1: Interactive (Default)

```bash
python main.py
```

Prompts for:
1. XIQ credentials
2. Object selection (SSIDs, VLANs, RADIUS)
3. Edge Services credentials
4. Final confirmation

### Example 2: Command-line with Selection

```bash
python main.py --xiq-token ABC123 --controller-url https://10.10.10.100
```

Prompts for:
1. Object selection (SSIDs, VLANs, RADIUS)
2. Edge Services credentials (if not provided)
3. Final confirmation

### Example 3: Fully Automated

```bash
python main.py \
    --xiq-token ABC123 \
    --controller-url https://10.10.10.100 \
    --username admin \
    --password secret \
    --select-all
```

No prompts - migrates everything automatically.

## Documentation

- **QUICKSTART.md** - Step-by-step guide with examples
- **README.md** - Complete documentation
- **USAGE_GUIDE.md** - Advanced usage and troubleshooting
- **FEATURES.md** - This file

## Version

Version: 1.0.0 with Interactive Selection
