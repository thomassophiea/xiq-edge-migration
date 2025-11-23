# Associated Profile Assignment Guide

## Overview

When migrating SSIDs from XIQ to Edge Services, **Associated Profiles** determine which Access Points will broadcast which wireless networks. This guide explains how the profile assignment workflow works.

---

## What are Associated Profiles?

**Associated Profiles** in Edge Services (formerly Campus Controller) are configuration templates that define:
- Which SSIDs are broadcast
- Which radios broadcast each SSID (2.4 GHz, 5 GHz, 6 GHz)
- Which APs use this configuration

**Profile Naming Format:**
- Default profiles: `AP3000/default`, `AP4000/default`
- Custom profiles: `AP3000/GuestOnly`, `AP4000/CorporateWiFi`

**Profile Assignment is Critical:**
- SSIDs created but NOT assigned to profiles will **not** be broadcast
- You must assign SSIDs to profiles for APs to advertise them

---

## Migration Workflow

### Step-by-Step Process

```
1. XIQ Configuration Retrieved
   ↓
2. SSIDs Converted to Edge Services Format
   ↓
3. SSIDs Posted to Edge Services
   ↓
4. PROFILE ASSIGNMENT WORKFLOW  ⬅ NEW!
   │
   ├─ Fetch Available Profiles
   ├─ Sort Profiles (Custom First, Then Defaults)
   ├─ For Each SSID:
   │  ├─ Select Which Profiles
   │  └─ Select Which Radios
   └─ Apply Assignments to Profiles
```

---

## Interactive Profile Selection

### When It Happens

After SSIDs are successfully posted to Edge Services, the system will:

1. **Fetch Profiles** from `/v3/profiles` API endpoint
2. **Display Available Profiles** sorted by type
3. **Prompt for Each SSID** to assign profiles and radios

### Example Workflow

```
======================================================================
ASSOCIATE SSIDs WITH PROFILES
======================================================================

Available Associated Profiles:
----------------------------------------------------------------------
  1. AP3000/CorporateOnly       (AP3000)  [CUSTOM]
  2. AP3000/GuestWiFi           (AP3000)  [CUSTOM]
  3. AP4000/CustomProfile       (AP4000)  [CUSTOM]
  4. AP3000/default             (AP3000)  [DEFAULT]
  5. AP4000/default             (AP4000)  [DEFAULT]

----------------------------------------------------------------------
SSID: Corporate-WiFi
----------------------------------------------------------------------

Would you like to associate 'Corporate-WiFi' with any Associated Profiles?
  Options:
    • Enter numbers (e.g., 1,2,3) to select specific profiles
    • Enter 'all' to apply to all profiles
    • Enter 'custom' to apply to all custom profiles only
    • Enter 'none' to skip (manually assign later)

Your selection: 1,4

✓ Selected 2 profile(s)

  Profile: AP3000/CorporateOnly
  Which radios should broadcast this SSID?
    0. All radios (default)
    1. Radio 1 only (typically 2.4 GHz)
    2. Radio 2 only (typically 5 GHz)
    3. Radio 3 only (typically 6 GHz)
  Enter radio index [0]: 0
  ✓ 'Corporate-WiFi' → 'AP3000/CorporateOnly' on all radios

  Profile: AP3000/default
  Which radios should broadcast this SSID?
    0. All radios (default)
    1. Radio 1 only (typically 2.4 GHz)
    2. Radio 2 only (typically 5 GHz)
    3. Radio 3 only (typically 6 GHz)
  Enter radio index [0]: 2
  ✓ 'Corporate-WiFi' → 'AP3000/default' on radio 2 (5 GHz)
```

---

## Selection Options

### Profile Selection

| Option | Description | Example |
|--------|-------------|---------|
| **Numbers** | Select specific profiles by number | `1,2,4` |
| **all** | Apply to ALL profiles (custom + default) | `all` |
| **custom** | Apply to custom profiles only | `custom` |
| **none** | Skip this SSID (manual assignment later) | `none` |

### Radio Selection

| Index | Radio | Typical Frequency | Use Case |
|-------|-------|-------------------|----------|
| **0** | All radios | All bands | Default - broadcast on all available radios |
| **1** | Radio 1 | 2.4 GHz | Legacy devices, maximum coverage |
| **2** | Radio 2 | 5 GHz | High performance, less interference |
| **3** | Radio 3 | 6 GHz | WiFi 6E only, ultra-high performance |

---

## Profile Sorting

The system automatically sorts profiles for easier selection:

### Custom Profiles First
- Any profile **without** `/default` in the name
- Typically your custom-created profiles
- **Shown first** with `[CUSTOM]` marker

### Default Profiles Second
- Profiles with `/default` in the name
- Factory defaults or system-generated
- **Shown last** with `[DEFAULT]` marker

### Example Sorted List

```
1. AP3000/5GHz-Only          (AP3000)  [CUSTOM]   ← Custom
2. AP3000/Guest              (AP3000)  [CUSTOM]   ← Custom
3. AP4000/Conference-Rooms   (AP4000)  [CUSTOM]   ← Custom
4. AP3000/default            (AP3000)  [DEFAULT]  ← Default
5. AP3912/default            (AP3912)  [DEFAULT]  ← Default
6. AP4000/default            (AP4000)  [DEFAULT]  ← Default
```

---

## Automated Mode (--select-all)

When using `--select-all` flag, the system will:

```bash
python main.py --select-all --controller-url https://controller.com --username admin
```

**Behavior:**
- ✓ Applies **all SSIDs** to **all profiles**
- ✓ Uses **all radios** (index 0) for every assignment
- ✓ No interactive prompts
- ✓ Shows assignment summary

**Use Cases:**
- Quick testing
- Uniform deployment (all SSIDs everywhere)
- Automation/scripting

---

## Assignment Summary

After selections, you'll see a comprehensive summary:

```
======================================================================
PROFILE ASSIGNMENT SUMMARY
======================================================================
Total SSIDs with assignments: 3
Total profile assignments: 7

Assignments:

  Corporate-WiFi:
    • AP3000/CorporateOnly (all radios)
    • AP3000/default (radio 2)
    • AP4000/default (all radios)

  Guest-WiFi:
    • AP3000/GuestWiFi (all radios)
    • AP3000/default (all radios)

  IoT-Network:
    • AP3000/default (radio 1)
    • AP4000/default (radio 1)
```

---

## Technical Details

### API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v3/profiles` | GET | Fetch all Associated Profiles |
| `/v3/profiles/{id}` | GET | Get specific profile details |
| `/v3/profiles/{id}` | PUT | Update profile with SSID assignments |

### Profile Element Structure

```json
{
  "id": "uuid",
  "name": "AP3000/CustomProfile",
  "apPlatform": "AP3000",
  "radioIfList": [
    {
      "serviceId": "ssid-uuid-1",
      "index": 0
    },
    {
      "serviceId": "ssid-uuid-2",
      "index": 2
    }
  ],
  "wiredIfList": [],
  "roleIDs": []
}
```

### Interface Assignment Element

```json
{
  "serviceId": "804078cd-1b76-48f4-a70f-d01f07c75c47",
  "index": 0
}
```

**Fields:**
- `serviceId`: UUID of the SSID/service
- `index`: Radio index (0=all, 1-3=specific radio)

---

## Assignment Logic

### How Assignments Are Applied

1. **Fetch Current Profile** - GET `/v3/profiles/{id}`
2. **Get Existing Assignments** - Extract `radioIfList`
3. **Add New Assignments** - Merge without duplicates
4. **Update Profile** - PUT `/v3/profiles/{id}` with updated `radioIfList`

### Duplicate Prevention

The system checks for existing assignments:
```python
existing_service_ids = {r.get('serviceId') for r in existing_radios}
if assignment.get('serviceId') not in existing_service_ids:
    existing_radios.append(assignment)
```

**Result:** SSIDs are added, not replaced. Existing assignments are preserved.

---

## Common Scenarios

### Scenario 1: Corporate WiFi on All APs

**Goal:** Broadcast corporate SSID on all APs, all radios

**Selections:**
- Profile: `all`
- Radio: `0` (all radios)

**Result:** Every AP broadcasts the SSID on all available radios

---

### Scenario 2: Guest WiFi on Specific Profile

**Goal:** Guest network only on designated APs

**Selections:**
- Profile: `1` (AP3000/GuestWiFi)
- Radio: `0` (all radios)

**Result:** Only APs using the GuestWiFi profile broadcast this SSID

---

### Scenario 3: 5GHz-Only High Performance

**Goal:** High-speed network on 5 GHz only

**Selections:**
- Profile: `custom` (all custom profiles)
- Radio: `2` (5 GHz only)

**Result:** All custom profiles broadcast on 5 GHz radio only

---

### Scenario 4: IoT on 2.4 GHz Only

**Goal:** IoT devices need 2.4 GHz for range

**Selections:**
- Profile: `all`
- Radio: `1` (2.4 GHz)

**Result:** All profiles broadcast on 2.4 GHz radio only

---

## Troubleshooting

### Issue: SSIDs Not Appearing on APs

**Cause:** SSID created but not assigned to any profiles

**Solution:**
1. Check if profiles were assigned during migration
2. Manually assign in Edge Services UI
3. Or re-run migration with profile assignments

### Issue: SSID on Wrong Radio

**Cause:** Incorrect radio index selected

**Solution:**
1. Edit profile in Edge Services UI
2. Or re-run migration with correct radio selection

### Issue: No Profiles Found

**Cause:** Edge Services has no Associated Profiles configured

**Solution:**
1. Create profiles in Edge Services UI first
2. Assign APs to profiles
3. Then run migration

---

## Manual Assignment (Alternative)

If you skip profile assignment during migration (`none`):

1. **Log into Edge Services Web UI**
2. **Navigate to:** Configuration → Profiles
3. **Edit Profile** (e.g., AP3000/default)
4. **Radio Interfaces Section:**
   - Select radio (Radio 1, Radio 2, Radio 3)
   - Choose SSID from dropdown
   - Add assignment
5. **Save** profile
6. **APs using this profile** will now broadcast the SSID

---

## Best Practices

### 1. Plan Profile Strategy
- Create custom profiles before migration
- Group APs by location/purpose
- Use descriptive profile names

### 2. Use Custom Profiles
- Separate guest/corporate networks
- Different radios for different uses
- Easier management long-term

### 3. Test with One SSID First
- Migrate one SSID
- Verify it appears on APs
- Then migrate remaining SSIDs

### 4. Document Assignments
- Note which SSIDs go on which profiles
- Keep radio assignments documented
- Helps troubleshooting

### 5. Review Before Applying
- Check assignment summary
- Verify radio selections
- Confirm before proceeding

---

## Command Reference

### Interactive Mode (Full Control)

```bash
python main.py \
  --xiq-username user@example.com \
  --controller-url https://controller.example.com \
  --username admin \
  --password secret
```

**Prompts for:**
- SSID selection
- VLAN selection
- RADIUS selection
- **Profile assignments** ⭐
- **Radio selections** ⭐

### Automated Mode (All SSIDs, All Profiles)

```bash
python main.py \
  --xiq-username user@example.com \
  --controller-url https://controller.example.com \
  --username admin \
  --password secret \
  --select-all
```

**Behavior:**
- Migrates all objects
- Assigns all SSIDs to all profiles
- Uses all radios (index 0)

---

## JSON Output Format

The profile assignment function returns:

```json
{
  "ssid-uuid-1": [
    {
      "profile_id": "profile-uuid-1",
      "profile_name": "AP3000/CorporateOnly",
      "radio_index": 0
    },
    {
      "profile_id": "profile-uuid-2",
      "profile_name": "AP3000/default",
      "radio_index": 2
    }
  ],
  "ssid-uuid-2": [
    {
      "profile_id": "profile-uuid-3",
      "profile_name": "AP4000/Guest",
      "radio_index": 1
    }
  ]
}
```

---

## Version History

- **v1.3.0** - Added Associated Profile assignment workflow
- **v1.2.0** - Quick Wins Phase 1 (DNS, APs, Rate Limiters, CoS)
- **v1.1.0** - Interactive object selection
- **v1.0.0** - Initial release

---

## Support

If you encounter issues with profile assignments:

1. Check Edge Services version (requires v5.26+)
2. Verify profiles exist in Edge Services
3. Check AP-to-profile assignments
4. Review verbose logs (`--verbose` flag)
5. Report issues at: https://github.com/thomassophiea/xiq-edge-migration/issues

---

**Generated with:** [Claude Code](https://claude.com/claude-code)
**Repository:** https://github.com/thomassophiea/xiq-edge-migration
