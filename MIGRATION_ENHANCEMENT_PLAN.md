# XIQ to Edge Services Migration - Comprehensive Enhancement Plan

## Executive Summary

This document outlines a comprehensive enhancement plan to expand the migration tool from basic SSID/VLAN/RADIUS migration to a full-featured configuration migration system that covers all compatible objects between XIQ and Edge Services.

---

## Current State (v1.0)

### What We Currently Migrate:
1. **SSIDs** → Services
2. **VLANs** → Topologies
3. **RADIUS Servers** → AAA Policies

### Limitations:
- No role/user profile migration
- No QoS/CoS migration
- No AP configuration migration
- No global settings migration
- No guest portal migration
- Missing DNS/NTP configuration

---

## Phase 1: Core Policy & Access Control (Priority: HIGH)

### 1.1 User Profiles / Roles Migration
**XIQ Object:** User Profiles
**Edge Services Object:** RoleElement (v3 API)

**Capabilities:**
- L2/L3/L7 firewall rules
- Default topology assignment
- CoS assignment
- Captive portal redirect settings
- Default allow/deny actions

**Implementation:**
```python
# XIQ API
GET /userprofiles - List user profiles
GET /userprofiles/{id} - Get profile details

# Edge Services API
POST /v3/roles - Create role
GET /v3/roles - List existing roles
```

**Complexity:** Medium
- Need to map XIQ firewall rules to Edge Services L2/L3/L7 filters
- Handle VLAN/topology references
- Map QoS markings

### 1.2 Classification Rules
**XIQ Object:** Classification Rules
**Edge Services Object:** Part of RoleElement filters

**Capabilities:**
- Device type classification
- MAC OUI matching
- Application-based rules

**Implementation:**
```python
# Convert XIQ classification rules to Role L2/L3 filters
```

**Complexity:** Medium

---

## Phase 2: Quality of Service (Priority: HIGH)

### 2.1 Class of Service (CoS) Policies
**XIQ Object:** QoS Profiles
**Edge Services Object:** PolicyClassOfServiceElement

**Capabilities:**
- Layer 2/3 QoS marking (DSCP, 802.1p)
- Inbound/outbound rate limiting
- Transmit queue assignment

**Implementation:**
```python
# Edge Services API
GET /v1/cos - List CoS policies
POST /v1/cos - Create CoS policy
GET /v1/cos/default - Get default template

# CoS Schema:
{
  "cosName": "High-Priority",
  "cosQos": {
    "priority": 6,  # 802.1p priority
    "tosDscp": 46,  # DSCP marking
  },
  "inboundRateLimiterId": "uuid",
  "outboundRateLimiterId": "uuid",
  "transmitQueue": 3
}
```

**Complexity:** Medium
- Map XIQ QoS profiles to Edge Services CoS
- Handle rate limiter references

### 2.2 Rate Limiters
**XIQ Object:** Bandwidth policies
**Edge Services Object:** RateLimiterElement

**Capabilities:**
- Per-user rate limiting
- Per-SSID rate limiting
- Upload/download limits

**Implementation:**
```python
# Edge Services API
GET /v1/ratelimiters - List rate limiters
POST /v1/ratelimiters - Create rate limiter
GET /v1/ratelimiters/default - Get default template

# Rate Limiter Schema:
{
  "rateLimiterName": "10Mbps-Limit",
  "upstreamRate": 10000,  # kbps
  "downstreamRate": 10000,
  "burstSize": 1000
}
```

**Complexity:** Low

---

## Phase 3: Access Point Configuration (Priority: HIGH)

### 3.1 AP Names & Descriptions
**XIQ Object:** Device properties
**Edge Services Object:** AccessPointElement

**Capabilities:**
- AP friendly name
- AP description
- AP notes/comments

**Implementation:**
```python
# XIQ API
GET /devices - List all devices
GET /devices/{id} - Get device details

# Edge Services API
PUT /v1/aps/{apSerialNumber} - Update AP
{
  "name": "Building-A-Floor-2-AP01",
  "description": "Conference Room AP",
  "location": "Building A, Floor 2, Room 201"
}
```

**Complexity:** Low
- Simple name/description mapping
- Serial number matching between systems

### 3.2 AP Location Information
**XIQ Object:** Location hierarchy
**Edge Services Object:** Location field in AP

**Capabilities:**
- Building/floor assignment
- GPS coordinates
- Address information

**Implementation:**
```python
# XIQ API
GET /locations - Get location hierarchy
GET /devices/{id}/location - Get device location

# Edge Services API
PUT /v1/aps/{apSerialNumber}
{
  "location": "Building A > Floor 2 > Conference Room"
}
```

**Complexity:** Low

### 3.3 AP Radio Profiles
**XIQ Object:** Radio profiles
**Edge Services Object:** AP radio configuration

**Capabilities:**
- Channel assignment
- Transmit power
- Radio mode (802.11a/b/g/n/ac/ax)
- Channel width

**Implementation:**
```python
# XIQ API
GET /radioprofiles - List radio profiles

# Edge Services API
PUT /v1/aps/{apSerialNumber}
{
  "radio24": {
    "channel": 6,
    "power": 12,
    "mode": "11ng"
  },
  "radio5": {
    "channel": 36,
    "power": 15,
    "mode": "11ac"
  }
}
```

**Complexity:** Medium
- Radio profile to AP config mapping
- Channel/power validation

---

## Phase 4: Guest Access & Captive Portal (Priority: MEDIUM)

### 4.1 Captive Portal Configurations
**XIQ Object:** Captive Web Portal (CWP)
**Edge Services Object:** eGuest profiles

**Capabilities:**
- Self-registration portals
- Sponsored guest access
- Social media authentication
- Custom portal pages

**Implementation:**
```python
# Edge Services API
GET /v1/eguest - List eGuest profiles
POST /v1/eguest - Create eGuest profile

# eGuest Schema:
{
  "eGuestPortalName": "Guest-Portal",
  "authMethod": "SelfRegistration",
  "expirationTime": 86400,
  "maxDevices": 2,
  "socialAuth": {
    "facebook": true,
    "google": true
  }
}
```

**Complexity:** High
- Complex portal configuration mapping
- Social auth integration
- Custom HTML/CSS handling

### 4.2 Guest User Provisioning
**XIQ Object:** Guest users
**Edge Services Object:** Guest user accounts

**Capabilities:**
- Bulk guest creation
- Expiration dates
- Bandwidth limits
- Sponsor approval workflow

**Complexity:** Medium

---

## Phase 5: Global Infrastructure Settings (Priority: MEDIUM)

### 5.1 NTP Configuration
**XIQ Object:** Global NTP settings
**Edge Services Object:** GlobalSettingsElement or system config

**Capabilities:**
- Primary/secondary NTP servers
- Time zone configuration
- Automatic time sync

**Implementation:**
```python
# Check Edge Services NTP configuration API
# May be in /v1/globalsettings or separate endpoint

# Example:
PUT /v1/globalsettings
{
  "ntpServers": [
    "pool.ntp.org",
    "time.google.com"
  ],
  "timezone": "America/New_York"
}
```

**Complexity:** Low
**Note:** Need to verify exact Edge Services NTP API

### 5.2 DNS Configuration
**XIQ Object:** DNS settings
**Edge Services Object:** Topology DHCP settings or global

**Capabilities:**
- Primary/secondary DNS servers
- DNS domain suffixes
- Per-VLAN DNS

**Implementation:**
```python
# Option 1: Per-topology DNS (DHCP settings)
POST /v1/topologies
{
  "dhcpDnsServers": "8.8.8.8,8.8.4.4",
  "dhcpDomain": "example.com"
}

# Option 2: Global DNS (if supported)
PUT /v1/globalsettings
{
  "dnsServers": ["8.8.8.8", "8.8.4.4"]
}
```

**Complexity:** Low

### 5.3 SNMP Configuration
**XIQ Object:** SNMP settings
**Edge Services Object:** SNMP configuration

**Capabilities:**
- SNMP v2c/v3
- Community strings
- Trap receivers

**Implementation:**
```python
# Edge Services API
GET /v1/snmp - Get SNMP config
PUT /v1/snmp - Update SNMP config
GET /v1/snmp/default - Get default template

# SNMP Schema:
{
  "snmpEnabled": true,
  "version": "v2c",
  "communityString": "public",
  "trapReceivers": [
    {
      "ipAddress": "10.0.0.100",
      "port": 162,
      "community": "public"
    }
  ]
}
```

**Complexity:** Low

### 5.4 Syslog Configuration
**XIQ Object:** Syslog settings
**Edge Services Object:** Syslog configuration

**Capabilities:**
- Remote syslog servers
- Log levels
- Facility codes

**Implementation:**
```python
# Check if Edge Services has syslog API
# May be part of globalsettings or separate
```

**Complexity:** Low
**Note:** Need to verify Edge Services syslog API

---

## Phase 6: Advanced Features (Priority: LOW)

### 6.1 IoT Profiles
**XIQ Object:** IoT profiles
**Edge Services Object:** IotProfileElement

**Capabilities:**
- IoT device classification
- VLAN assignment for IoT
- Security policies

**Implementation:**
```python
# Edge Services API has IoT profile support
GET /v1/iotprofiles
POST /v1/iotprofiles
```

**Complexity:** Medium

### 6.2 Analytics Profiles
**XIQ Object:** Analytics configuration
**Edge Services Object:** AnalyticsProfileElement

**Capabilities:**
- Application visibility
- User behavior analytics
- Network usage monitoring

**Complexity:** Medium

### 6.3 RTLS Profiles
**XIQ Object:** Location services
**Edge Services Object:** RtlsProfileElement

**Capabilities:**
- Real-time location tracking
- Asset tracking
- Proximity detection

**Complexity:** Medium

---

## Implementation Priority Matrix

| Feature | Priority | Complexity | User Value | Dependencies |
|---------|----------|------------|------------|--------------|
| User Profiles/Roles | HIGH | Medium | High | CoS, Topologies |
| Class of Service | HIGH | Medium | High | Rate Limiters |
| Rate Limiters | HIGH | Low | High | None |
| AP Names/Locations | HIGH | Low | High | None |
| DNS/NTP Config | MEDIUM | Low | Medium | None |
| SNMP Config | MEDIUM | Low | Medium | None |
| Captive Portal | MEDIUM | High | Medium | Roles, eGuest |
| Radio Profiles | MEDIUM | Medium | Medium | None |
| IoT Profiles | LOW | Medium | Low | Roles |
| Analytics | LOW | Medium | Low | None |
| RTLS | LOW | Medium | Low | None |

---

## Recommended Implementation Phases

### Phase 1 (Week 1-2): Foundation
1. ✅ SSID/VLAN/RADIUS (Already done)
2. Rate Limiters
3. Class of Service
4. AP Names & Locations

### Phase 2 (Week 3-4): Access Control
1. User Profiles/Roles migration
2. Firewall rule conversion
3. Classification rules

### Phase 3 (Week 5): Infrastructure
1. DNS configuration
2. NTP configuration
3. SNMP configuration
4. Syslog configuration

### Phase 4 (Week 6+): Advanced
1. Captive Portal/eGuest
2. Radio profile migration
3. IoT profiles
4. Analytics profiles

---

## Technical Architecture Changes

### 1. Enhanced Data Model

```python
# Expanded XIQ configuration structure
xiq_config = {
    # Existing
    'ssids': [],
    'vlans': [],
    'authentication': [],

    # New additions
    'user_profiles': [],      # User profiles/roles
    'qos_profiles': [],       # QoS/CoS policies
    'rate_limiters': [],      # Bandwidth policies
    'classification_rules': [], # Device classification
    'captive_portals': [],    # Guest portals
    'radio_profiles': [],     # RF profiles
    'devices': [],            # AP list with names/locations
    'global_settings': {      # Infrastructure settings
        'ntp_servers': [],
        'dns_servers': [],
        'snmp': {},
        'syslog': {}
    },
    'iot_profiles': [],       # IoT configurations
    'analytics_profiles': []  # Analytics settings
}
```

### 2. Converter Enhancements

```python
class ConfigConverter:
    def convert(self, xiq_config, existing_resources=None):
        """Convert XIQ config to Edge Services format"""
        edge_config = {
            # Existing
            'services': self._convert_ssids(...),
            'topologies': self._convert_vlans(...),
            'aaa_policies': self._convert_radius(...),

            # New
            'roles': self._convert_user_profiles(...),
            'cos_policies': self._convert_qos_profiles(...),
            'rate_limiters': self._convert_rate_limiters(...),
            'eguest_portals': self._convert_captive_portals(...),
            'ap_configurations': self._convert_ap_configs(...),
            'global_settings': self._convert_global_settings(...),
            'iot_profiles': self._convert_iot_profiles(...)
        }
        return edge_config
```

### 3. Interactive Selection Enhancement

```python
def select_objects_to_migrate(xiq_config):
    """Enhanced selection with all object types"""

    # Existing selections
    select_ssids(xiq_config['ssids'])
    select_vlans(xiq_config['vlans'])
    select_radius_servers(xiq_config['authentication'])

    # New selections
    select_user_profiles(xiq_config['user_profiles'])
    select_qos_profiles(xiq_config['qos_profiles'])
    select_rate_limiters(xiq_config['rate_limiters'])
    select_captive_portals(xiq_config['captive_portals'])
    select_ap_configs(xiq_config['devices'])

    # Global settings (yes/no choice)
    confirm_migrate_global_settings(xiq_config['global_settings'])
```

---

## Validation & Testing Strategy

### 1. Pre-Migration Validation
- Check for naming conflicts
- Validate UUID references
- Verify dependency order
- Check for unsupported features

### 2. Dry-Run Mode Enhancements
- Show what would be migrated
- Identify potential conflicts
- Generate migration report
- Export configuration comparison

### 3. Post-Migration Verification
- Verify all objects created
- Check configuration accuracy
- Test connectivity
- Generate validation report

---

## Documentation Updates

### 1. Enhanced README
- Complete feature list
- Migration scope matrix
- Supported/unsupported features
- Known limitations

### 2. Field Mapping Guide
- XIQ → Edge Services mappings for all objects
- Default value translations
- Required transformations

### 3. Troubleshooting Guide
- Common migration issues
- Conflict resolution
- Error messages and fixes

---

## API Research Needed

Before implementation, verify these Edge Services APIs:

1. ✅ Services - Verified
2. ✅ Topologies - Verified
3. ✅ AAA Policies - Verified
4. ✅ Roles (v3) - Verified
5. ✅ CoS - Verified
6. ✅ Rate Limiters - Verified
7. ✅ eGuest - Verified
8. ✅ Global Settings - Verified
9. ✅ SNMP - Verified
10. ⚠️ NTP - Need to verify endpoint
11. ⚠️ DNS (global) - May be topology-only
12. ⚠️ Syslog - Need to verify endpoint
13. ⚠️ AP radio config - Need exact PUT schema
14. ⚠️ IoT profiles - Verified existence, need schema details

---

## Success Metrics

### Quantitative
- Number of object types supported: Target 12+
- Migration success rate: Target 95%+
- Time to migrate: Target <10 minutes for typical deployment
- Error rate: Target <5%

### Qualitative
- User satisfaction with selection UI
- Completeness of migration
- Clarity of documentation
- Ease of troubleshooting

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API incompatibility | High | Medium | Thorough API testing, fallback options |
| Data loss | High | Low | Dry-run mode, backups, validation |
| Performance issues | Medium | Low | Batch operations, rate limiting |
| Complex rule conversion | Medium | High | Manual review required, clear warnings |
| Authentication timeout | Low | Medium | Token refresh, session management |

---

## Next Steps

1. **Immediate (This Session)**
   - Implement Rate Limiters migration
   - Implement CoS migration
   - Add AP name/location migration
   - Update interactive selection UI

2. **Short Term (Next Session)**
   - Implement User Profiles/Roles migration
   - Add DNS/NTP configuration
   - Enhance validation logic

3. **Medium Term**
   - Implement Captive Portal migration
   - Add radio profile migration
   - Complete documentation

4. **Long Term**
   - IoT profile support
   - Analytics integration
   - Advanced reporting
