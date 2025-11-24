# Web UI Quick Start

## Launch the Web UI

```bash
cd /Users/thomassophieaii/Documents/Claude/migration
./start_ui.sh
```

Then open your browser to: **http://localhost:5000**

---

## 6-Step Migration Process

### Step 1: Connect to XIQ
- Enter XIQ username and password
- Select your region
- Click "Connect to XIQ"

### Step 2: Select Objects
- Use tabs to switch between SSIDs, VLANs, RADIUS
- Check boxes next to objects you want to migrate
- Use "Select All" for quick selection
- Click "Continue"

### Step 3: Connect to Edge Services
- Enter Edge Services URL (e.g., https://controller.example.com)
- Enter username (typically "admin") and password
- Click "Connect to Edge Services"

### Step 4: Assign SSIDs to Profiles
- For each SSID, check which profiles to assign
- Select which radios to use (All/2.4GHz/5GHz/6GHz)
- Or use "Assign All to All Profiles" for quick setup
- Click "Continue to Migration"

### Step 5: Review and Execute
- Review the migration summary
- Optionally check "Dry Run" to test without making changes
- Click "Execute Migration"

### Step 6: View Results
- See migration statistics
- Review logs for details
- Click "Start New Migration" to begin again

---

## Quick Actions

**Select All Objects:**
- Click "Select All" on SSIDs, VLANs, and RADIUS tabs

**Quick Profile Assignment:**
- Click "Assign All SSIDs to All Profiles"

**Test Before Going Live:**
- Check "Dry Run" in Step 5

---

## Typical Migration Time

**Small Environment (1-20 SSIDs):** 30-60 seconds
**Medium Environment (20-50 SSIDs):** 1-2 minutes
**Large Environment (50+ SSIDs):** 2-3 minutes

---

## Troubleshooting

**Can't connect to XIQ?**
- Verify username and password
- Try different region in dropdown

**Can't connect to Edge Services?**
- Ensure URL starts with "https://"
- Verify credentials

**Web UI won't load?**
- Check that server is running
- Try http://localhost:5000 (not https)

---

## Documentation

**Complete Guide:** [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md)
**Technical Details:** [WEB_UI_IMPLEMENTATION_SUMMARY.md](WEB_UI_IMPLEMENTATION_SUMMARY.md)

---

## CLI Alternative

Prefer command-line? Use:
```bash
./migrate.sh --xiq-username user@example.com --controller-url https://controller.example.com --verbose
```

Both interfaces produce identical results!

---

**Version:** 1.4.0 | **Repository:** https://github.com/thomassophiea/xiq-edge-migration
