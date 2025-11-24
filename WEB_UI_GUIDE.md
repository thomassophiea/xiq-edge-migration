# Web UI Guide - XIQ to Edge Services Migration Tool

## Overview

The Web UI provides a user-friendly, browser-based interface for the XIQ to Edge Services Migration Tool. It offers an intuitive step-by-step workflow that guides you through the entire migration process.

---

## Features

### Visual Migration Workflow

1. **Step-by-Step Interface** - Clear progression through all migration stages
2. **Real-Time Progress Tracking** - Visual progress bar showing current status
3. **Interactive Object Selection** - Checkbox-based selection for SSIDs, VLANs, and RADIUS servers
4. **Profile Assignment UI** - Easy-to-use interface for assigning SSIDs to Associated Profiles
5. **Live Logs** - Real-time display of migration logs and status messages
6. **Migration Summary** - Visual summary of all objects before execution
7. **Responsive Design** - Works on desktop, tablet, and mobile devices

### Key Capabilities

- Connect to XIQ and Edge Services via web forms
- Select specific objects to migrate with checkboxes
- Assign SSIDs to Associated Profiles with radio selection
- Execute dry-run or live migrations
- View detailed results and statistics
- Start multiple migrations without command-line knowledge

---

## Getting Started

### Prerequisites

Before using the Web UI, ensure you have:

1. **Completed setup** - Run `./setup.sh` to create the virtual environment
2. **Network access** - Connectivity to both XIQ and Edge Services
3. **Credentials** - Valid login credentials for both systems
4. **Modern browser** - Chrome, Firefox, Safari, or Edge (latest versions)

### Installation

The Web UI is already included in the migration tool. Install dependencies:

```bash
cd /Users/thomassophieaii/Documents/Claude/migration

# Activate virtual environment
source venv/bin/activate

# Install web dependencies
pip install flask flask-cors
```

Or simply run the launcher script (it will install dependencies automatically):

```bash
./start_ui.sh
```

---

## Starting the Web UI

### Option 1: Using the Launcher Script (Recommended)

```bash
cd /Users/thomassophieaii/Documents/Claude/migration
./start_ui.sh
```

### Option 2: Manual Start

```bash
cd /Users/thomassophieaii/Documents/Claude/migration
source venv/bin/activate
python3 web_ui.py
```

### Expected Output

```
======================================================================
XIQ to Edge Services Migration Tool - Web UI
======================================================================

Starting web server...
Open your browser and navigate to: http://localhost:5000

Press Ctrl+C to stop the server
======================================================================
 * Serving Flask app 'web_ui'
 * Running on http://0.0.0.0:5000
```

### Accessing the UI

**Local Access:**
```
http://localhost:5000
```

**Remote Access (from another device on the same network):**
```
http://<your-server-ip>:5000
```

For example:
```
http://192.168.1.100:5000
```

---

## Using the Web UI

### Migration Workflow

The Web UI guides you through 6 steps:

```
Step 1: Connect to XIQ
   ↓
Step 2: Select Objects to Migrate
   ↓
Step 3: Connect to Edge Services
   ↓
Step 4: Assign SSIDs to Profiles
   ↓
Step 5: Review and Execute Migration
   ↓
Step 6: View Results
```

---

### Step 1: Connect to ExtremeCloud IQ

**Purpose:** Authenticate with XIQ and retrieve configuration

**Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| XIQ Username | Your XIQ account email | `tsophiea@extremenetworks.com` |
| XIQ Password | Your XIQ password | `********` |
| Region | XIQ region | Global, EU, APAC, California |

**Actions:**

1. Enter your XIQ credentials
2. Select your region from the dropdown
3. Click **"Connect to XIQ"**

**Results:**

Upon successful connection, you'll see:

- ✅ Number of SSIDs retrieved
- ✅ Number of VLANs retrieved
- ✅ Number of RADIUS servers retrieved
- ✅ Number of devices retrieved

**Example Output:**

```
Retrieved from XIQ:
  SSIDs: 19
  VLANs: 5
  RADIUS: 3
  Devices: 10
```

---

### Step 2: Select Objects to Migrate

**Purpose:** Choose which SSIDs, VLANs, and RADIUS servers to migrate

**Interface:**

The selection interface has three tabs:

#### SSIDs Tab

- Displays all SSIDs from XIQ
- Each SSID shows its name
- Use checkboxes to select SSIDs for migration

**Quick Actions:**
- **Select All** - Check all SSIDs
- **Select None** - Uncheck all SSIDs

#### VLANs Tab

- Displays all VLANs from XIQ
- Each VLAN shows its name and VLAN ID
- Use checkboxes to select VLANs for migration

**Quick Actions:**
- **Select All** - Check all VLANs
- **Select None** - Uncheck all VLANs

#### RADIUS Tab

- Displays all RADIUS servers from XIQ
- Each server shows its name and IP address
- Use checkboxes to select RADIUS servers for migration

**Quick Actions:**
- **Select All** - Check all RADIUS servers
- **Select None** - Uncheck all RADIUS servers

**Actions:**

1. Switch between tabs (SSIDs, VLANs, RADIUS)
2. Check the boxes next to objects you want to migrate
3. Use "Select All" / "Select None" for bulk selection
4. Click **"Continue"** to proceed

**Requirements:**

- ⚠️ At least one SSID must be selected to proceed

---

### Step 3: Connect to Edge Services

**Purpose:** Authenticate with Edge Services and retrieve Associated Profiles

**Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| Edge Services URL | HTTPS URL of your Edge Services controller | `https://tsophiea.ddns.net` |
| Username | Edge Services admin username | `admin` |
| Password | Edge Services admin password | `********` |

**Actions:**

1. Enter your Edge Services URL (must start with `https://`)
2. Enter your username (typically `admin`)
3. Enter your password
4. Click **"Connect to Edge Services"**

**Results:**

Upon successful connection, you'll see all Associated Profiles:

**Example Display:**

```
Associated Profiles:

┌─────────────────────────────────┐
│ AP3000/CorporateOnly            │
│ AP3000                [CUSTOM]  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ AP3000/GuestWiFi                │
│ AP3000                [CUSTOM]  │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ AP3000/default                  │
│ AP3000               [DEFAULT]  │
└─────────────────────────────────┘
```

- **Custom profiles** - Highlighted in blue with `[CUSTOM]` badge
- **Default profiles** - Shown in gray with `[DEFAULT]` badge

---

### Step 4: Assign SSIDs to Profiles

**Purpose:** Select which Associated Profiles each SSID should be assigned to, and which radios should broadcast them

**Interface:**

For each SSID you selected in Step 2, you'll see:

1. **SSID Name Header** - e.g., "SSID: Corporate-WiFi"
2. **Profile Selection Grid** - Checkboxes for each Available Profile
3. **Radio Selector** - Dropdown to choose which radios broadcast the SSID

**Profile Checkboxes:**

Each profile appears as a checkbox:

```
☐ AP3000/CorporateOnly
☐ AP3000/GuestWiFi
☐ AP3000/default
☐ AP4000/default
```

Check the profiles you want this SSID assigned to.

**Radio Selector:**

Choose which radios broadcast this SSID:

```
Broadcast on which radios?
┌─────────────────────────────────────────────────┐
│ All radios (2.4GHz + 5GHz + 6GHz)              │
│ Radio 1 only (typically 2.4GHz)                │
│ Radio 2 only (typically 5GHz)                  │
│ Radio 3 only (typically 6GHz)                  │
└─────────────────────────────────────────────────┘
```

| Option | Radio Index | Typical Frequency | Description |
|--------|-------------|-------------------|-------------|
| All radios | 0 | 2.4GHz + 5GHz + 6GHz | Broadcast on all available radios |
| Radio 1 only | 1 | 2.4GHz | Broadcast on 2.4GHz band only |
| Radio 2 only | 2 | 5GHz | Broadcast on 5GHz band only |
| Radio 3 only | 3 | 6GHz | Broadcast on 6GHz band only (if available) |

**Quick Actions:**

- **Assign All SSIDs to All Profiles** - Applies every SSID to every profile on all radios
- **Assign All to Custom Profiles Only** - Applies every SSID to custom profiles only

**Actions:**

1. For each SSID:
   - Check the profiles to assign
   - Select the radio configuration
2. Or use quick actions for bulk assignment
3. Click **"Continue to Migration"** when ready

**Example Workflow:**

```
SSID: Corporate-WiFi
☑ AP3000/CorporateOnly
☐ AP3000/GuestWiFi
☑ AP3000/default

Broadcast on which radios?
┌─────────────────────────────────────────────────┐
│ All radios (2.4GHz + 5GHz + 6GHz)              │  ← Selected
└─────────────────────────────────────────────────┘

Result: Corporate-WiFi will be assigned to:
  • AP3000/CorporateOnly (all radios)
  • AP3000/default (all radios)
```

---

### Step 5: Review and Execute Migration

**Purpose:** Review all selections and execute the migration

**Migration Summary:**

The summary displays totals for:

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│     SSIDs       │      VLANs      │     RADIUS      │  Assignments    │
│       19        │        5        │        3        │       38        │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

**Migration Options:**

```
☐ Dry Run (no changes will be made)
```

- **Unchecked** - Execute live migration (posts to Edge Services)
- **Checked** - Dry run mode (saves JSON file, no changes made)

**Actions:**

1. Review the migration summary
2. Optionally check "Dry Run" to test without making changes
3. Click **"Execute Migration"** to proceed
4. Or click **"Start Over"** to reset and begin again

**Confirmation:**

If not in dry-run mode, you'll see a confirmation dialog:

```
This will migrate the selected configuration to Edge Services.
Are you sure?

[Cancel] [OK]
```

---

### Step 6: View Results

**Purpose:** See the results of the migration

**Dry Run Results:**

```
Dry Run Complete

Configuration saved to: /tmp/migration_dry_run.json

No changes were made to Edge Services.
```

**Live Migration Results:**

```
Migration Successful!

┌─────────────────┬─────────────────┬─────────────────┐
│ Rate Limiters   │   CoS Policies  │   Topologies    │
│      2/2        │       2/2       │       5/5       │
└─────────────────┴─────────────────┴─────────────────┘

┌─────────────────┬─────────────────┬─────────────────┐
│  AAA Policies   │    Services     │   AP Configs    │
│      1/1        │      19/19      │      10/10      │
└─────────────────┴─────────────────┴─────────────────┘

┌─────────────────┐
│   Assignments   │
│       38        │
└─────────────────┘
```

**Format:** `posted/total` or `updated/total`

- **posted/total** - Number successfully posted out of total objects
- **updated/total** - Number successfully updated out of total objects

**Actions:**

- Click **"Start New Migration"** to reset and begin another migration

---

## Migration Logs

### Live Log Display

The **Migration Logs** panel at the bottom of the page shows real-time logs:

```
======================================================================
MIGRATION LOGS                                                [Clear]
======================================================================

14:32:15 [INFO]    Connecting to XIQ (Global)...
14:32:17 [INFO]    Successfully authenticated with XIQ
14:32:17 [INFO]    Fetching SSIDs...
14:32:19 [INFO]    Retrieved 19 SSIDs, 5 VLANs, 3 RADIUS servers, 10 devices
14:32:45 [INFO]    Connecting to Edge Services at https://tsophiea.ddns.net...
14:32:47 [INFO]    Successfully authenticated with Edge Services
14:32:47 [INFO]    Fetching Associated Profiles...
14:32:48 [INFO]    Retrieved 5 Associated Profiles
14:33:12 [INFO]    Converting configuration...
14:33:15 [INFO]    Starting migration...
14:33:16 [INFO]    Posting rate limiters...
14:33:17 [INFO]    Posting CoS policies...
14:33:18 [INFO]    Posting topologies...
14:33:19 [INFO]    Posting AAA policies...
14:33:20 [INFO]    Posting services...
14:33:22 [INFO]    Updating AP configurations...
14:33:25 [INFO]    Applying profile assignments...
14:33:30 [SUCCESS] Migration completed successfully!
```

**Log Levels:**

- **[INFO]** - General information (green)
- **[SUCCESS]** - Success messages (bright green)
- **[WARNING]** - Warnings (yellow)
- **[ERROR]** - Error messages (red)

**Actions:**

- Logs update automatically every second
- Click **"Clear"** to clear the log display
- Logs auto-scroll to show latest messages

---

## Progress Tracking

### Progress Bar

At the top of the page, a visual progress bar shows migration status:

```
┌────────────────────────────────────────────────────────────────────┐
│ ████████████████████████████████░░░░░░░░░░░░░░░░░░░░░░░  75%      │
└────────────────────────────────────────────────────────────────────┘
Converting configuration...
```

**Progress Stages:**

| Progress | Stage |
|----------|-------|
| 0% | Idle |
| 10% | Connecting to XIQ |
| 30% | Retrieving XIQ configuration |
| 50% | XIQ data retrieved |
| 60% | Connecting to Edge Services |
| 70% | Edge Services connection successful |
| 75% | Converting configuration |
| 80% | Configuration converted |
| 85% | Executing migration |
| 90% | Applying profile assignments |
| 100% | Migration complete |

---

## Common Workflows

### Scenario 1: Full Migration with All Objects

1. **Step 1:** Connect to XIQ
2. **Step 2:** Click "Select All" on all three tabs (SSIDs, VLANs, RADIUS)
3. **Step 3:** Connect to Edge Services
4. **Step 4:** Click "Assign All SSIDs to All Profiles"
5. **Step 5:** Review summary, uncheck "Dry Run", click "Execute Migration"
6. **Step 6:** View results

**Time:** ~2-3 minutes for typical environment

---

### Scenario 2: Selective Migration (Specific SSIDs Only)

1. **Step 1:** Connect to XIQ
2. **Step 2:**
   - SSIDs tab: Check only "Corporate-WiFi" and "Guest-WiFi"
   - VLANs tab: Click "Select All"
   - RADIUS tab: Click "Select All"
3. **Step 3:** Connect to Edge Services
4. **Step 4:**
   - Corporate-WiFi: Assign to AP3000/CorporateOnly, Radio 0 (all radios)
   - Guest-WiFi: Assign to AP3000/GuestWiFi, Radio 0 (all radios)
5. **Step 5:** Review, execute migration
6. **Step 6:** View results

**Time:** ~1-2 minutes

---

### Scenario 3: Dry Run Test

1. **Step 1:** Connect to XIQ
2. **Step 2:** Select objects to migrate
3. **Step 3:** Connect to Edge Services
4. **Step 4:** Assign profiles
5. **Step 5:**
   - **Check "Dry Run"**
   - Click "Execute Migration"
6. **Step 6:**
   - View output file path: `/tmp/migration_dry_run.json`
   - No changes made to Edge Services

**Time:** ~30 seconds

**Use Case:** Test migration configuration before going live

---

### Scenario 4: 5GHz-Only SSID Deployment

1. **Step 1:** Connect to XIQ
2. **Step 2:** Select SSIDs requiring 5GHz only
3. **Step 3:** Connect to Edge Services
4. **Step 4:**
   - For each SSID:
     - Check desired profiles
     - Select **"Radio 2 only (typically 5GHz)"** from dropdown
5. **Step 5:** Execute migration
6. **Step 6:** View results

**Result:** SSIDs broadcast only on 5GHz radios

---

## Troubleshooting

### Issue: "Failed to authenticate with XIQ"

**Causes:**
- Incorrect username or password
- Wrong region selected
- Network connectivity issues

**Solutions:**
1. Verify credentials are correct
2. Try different region (Global vs. EU vs. APAC)
3. Check network connectivity
4. Check XIQ portal to confirm account status

---

### Issue: "Failed to authenticate with Edge Services"

**Causes:**
- Incorrect Edge Services URL
- Invalid credentials
- Controller not reachable
- SSL/TLS certificate issues

**Solutions:**
1. Verify URL format: `https://controller.example.com` (not `http://`)
2. Confirm credentials (default username: `admin`)
3. Test connectivity: `curl -k https://controller.example.com/v1/system/info`
4. Ensure controller is running Edge Services v5.26+

---

### Issue: "No Associated Profiles found"

**Causes:**
- No profiles exist in Edge Services
- API connection issue

**Solutions:**
1. Log into Edge Services UI
2. Navigate to: Configuration → Profiles
3. Create at least one profile if none exist
4. Retry connection from Web UI

---

### Issue: Web UI not loading

**Causes:**
- Flask server not running
- Port 5000 already in use
- Firewall blocking connection

**Solutions:**
1. Check if server is running: `ps aux | grep web_ui.py`
2. Check port availability: `lsof -i :5000`
3. If port in use, kill existing process or change port in `web_ui.py`
4. Check firewall rules for port 5000

---

### Issue: Migration fails during execution

**Causes:**
- Network interruption
- Invalid configuration
- Edge Services API error

**Solutions:**
1. Check Migration Logs panel for error details
2. Verify Edge Services is responsive
3. Try dry-run mode first to validate configuration
4. Contact support with logs

---

## Security Considerations

### Credential Handling

- **Not Stored:** Credentials are not saved to disk
- **Session Only:** Credentials exist only in memory during session
- **HTTPS Required:** Always use HTTPS for Edge Services connection

### Network Security

- **Local Access:** UI binds to `0.0.0.0:5000` - accessible on local network
- **Firewall:** Consider firewall rules if exposing externally
- **VPN Recommended:** Use VPN when accessing from remote locations

### Best Practices

1. **Use HTTPS:** Always connect to Edge Services via HTTPS
2. **Strong Passwords:** Use complex passwords for both XIQ and Edge Services
3. **Dry Run First:** Test with dry-run mode before live migration
4. **Private Network:** Run on private/internal network only
5. **Close Browser:** Close browser when finished to clear session

---

## Performance

### Expected Response Times

| Operation | Typical Time |
|-----------|--------------|
| XIQ Connection | 2-5 seconds |
| Retrieve XIQ Data (20 SSIDs) | 5-10 seconds |
| Edge Services Connection | 2-3 seconds |
| Retrieve Profiles | 1-2 seconds |
| Convert Configuration | <1 second |
| Post Configuration | 10-15 seconds |
| Apply Profile Assignments | 5-10 seconds |
| **Total Migration** | **30-60 seconds** |

### Large Environments

For environments with 50+ SSIDs:

- XIQ retrieval: 15-30 seconds
- Posting: 30-60 seconds
- Profile assignments: 20-40 seconds
- **Total:** 2-3 minutes

---

## Browser Support

### Supported Browsers

| Browser | Minimum Version | Status |
|---------|-----------------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |

### Mobile Browsers

| Browser | Platform | Status |
|---------|----------|--------|
| Safari | iOS 14+ | ✅ Responsive Design |
| Chrome | Android 10+ | ✅ Responsive Design |

---

## Comparison: CLI vs Web UI

| Feature | CLI (`./migrate.sh`) | Web UI (`./start_ui.sh`) |
|---------|----------------------|--------------------------|
| **Ease of Use** | Moderate (command-line knowledge required) | Easy (point and click) |
| **Visual Feedback** | Text output | Rich visual interface |
| **Object Selection** | Interactive prompts | Checkbox selection |
| **Profile Assignment** | Text prompts | Visual grid |
| **Progress Tracking** | Text messages | Progress bar + logs |
| **Multiple Migrations** | Restart script | Click "Start Over" |
| **Remote Access** | SSH required | Web browser |
| **Automation** | `--select-all` flag | Quick action buttons |
| **Logs** | Verbose flag | Live log panel |
| **Best For** | Automation, scripts, advanced users | Manual migrations, visual preference |

---

## Advanced Usage

### Running on Custom Port

Edit `web_ui.py` line 350:

```python
# Change from:
app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)

# To:
app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)
```

Then access at: `http://localhost:8080`

---

### Running in Production Mode

For production deployments, use a WSGI server like Gunicorn:

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 web_ui:app
```

---

### Reverse Proxy with Nginx

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name migration.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Files and Structure

### Directory Layout

```
migration/
├── web_ui.py              # Flask application
├── start_ui.sh            # Launcher script
├── templates/
│   └── index.html         # Main UI template
├── static/
│   ├── css/
│   │   └── style.css      # UI styling
│   └── js/
│       └── app.js         # Frontend logic
└── src/
    ├── xiq_api_client.py          # XIQ API
    ├── campus_controller_client.py # Edge Services API
    └── config_converter.py         # Converter
```

### File Sizes

| File | Lines | Size |
|------|-------|------|
| web_ui.py | 380 | ~14 KB |
| index.html | 280 | ~12 KB |
| style.css | 680 | ~18 KB |
| app.js | 870 | ~28 KB |
| **Total** | **2,210** | **~72 KB** |

---

## API Endpoints

### Backend REST API

The Web UI uses these internal API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/connect_xiq` | POST | Connect to XIQ |
| `/api/connect_edge` | POST | Connect to Edge Services |
| `/api/convert` | POST | Convert configuration |
| `/api/migrate` | POST | Execute migration |
| `/api/status` | GET | Get migration status |
| `/api/reset` | POST | Reset migration state |

---

## Support and Feedback

### Getting Help

If you encounter issues with the Web UI:

1. Check the **Migration Logs** panel for error details
2. Review this guide's Troubleshooting section
3. Check the console (F12 in browser) for JavaScript errors
4. Try the CLI version to isolate UI-specific issues

### Reporting Issues

When reporting Web UI issues, include:

- Browser and version
- Error messages from logs panel
- Browser console errors (F12 → Console tab)
- Steps to reproduce

---

## Version History

### v1.3.0 (January 23, 2025)

**Initial Web UI Release**

- Complete web-based interface
- All CLI features available in UI
- Real-time progress tracking
- Interactive profile assignment
- Responsive design
- Live logging

---

## Summary

The Web UI provides a modern, user-friendly interface for the XIQ to Edge Services Migration Tool. It simplifies the migration process with:

- ✅ Visual step-by-step workflow
- ✅ Point-and-click object selection
- ✅ Interactive profile assignment
- ✅ Real-time progress tracking
- ✅ Live migration logs
- ✅ No command-line knowledge required

**Start the Web UI:**

```bash
cd /Users/thomassophieaii/Documents/Claude/migration
./start_ui.sh
```

**Then open:** `http://localhost:5000`

---

**Generated with:** [Claude Code](https://claude.com/claude-code)
**Repository:** https://github.com/thomassophiea/xiq-edge-migration
**Version:** 1.3.0
**Date:** January 23, 2025
