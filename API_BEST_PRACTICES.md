# Edge Services API - Best Practices and Migration Guide

**Based on:** Extreme Campus Controller REST API Gateway v1.25.1
**OpenAPI Specification:** swagger.json
**Last Updated:** 2025-11-27

---

## Table of Contents

1. [Authentication & Authorization](#authentication--authorization)
2. [API Schema Compliance](#api-schema-compliance)
3. [Field Validation Requirements](#field-validation-requirements)
4. [Network/Topology Best Practices](#networktopology-best-practices)
5. [Service/SSID Best Practices](#servicessid-best-practices)
6. [AAA Policy Best Practices](#aaa-policy-best-practices)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)
9. [Migration Workflow](#migration-workflow)
10. [Common Pitfalls](#common-pitfalls)

---

## Authentication & Authorization

### Token Management

**Endpoint:** `POST /management/v1/oauth2/token`

```json
{
  "grantType": "password",
  "userId": "admin",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "f06f6f285e364e59fd317bd74da9e837",
  "token_type": "Bearer",
  "expires_in": 7200,
  "idle_timeout": 604800,
  "refresh_token": "3e33d8f724e69024811f1cf5869dbaf7"
}
```

### Best Practices:

1. **Token Expiry:**
   - Default: 7200 seconds (2 hours)
   - Implement auto-refresh 5 minutes before expiry
   - Handle 401 responses with automatic re-authentication

2. **Token Storage:**
   - Store in memory only during session
   - Never log tokens
   - Clear tokens on application exit

3. **Headers:**
   ```python
   headers = {
       "Authorization": f"Bearer {access_token}",
       "Content-Type": "application/json",
       "Accept": "application/json"
   }
   ```

---

## API Schema Compliance

### Critical Schema Requirements

#### 1. Topology Element (VLAN)

**Endpoint:** `POST /v1/topologies`

**Required Fields:**
- `name` (string, 1-255 chars)
- `vlanid` (number, 1-4094)
- `mode` (enum: "BridgedAtAc", "BridgedAtAp", "ISC")

**Schema:**
```json
{
  "id": "uuid",
  "name": "Corporate_VLAN",
  "vlanid": 100,
  "mode": "BridgedAtAc",
  "tagged": false,
  "multicastFilters": [],
  "multicastBridging": false,
  "group": 0,
  "members": [],
  "mtu": 1500,
  "enableMgmtTraffic": false,
  "dhcpServers": "",
  "l3Presence": true,
  "ipAddress": "192.168.100.1",
  "cidr": 24,
  "gateway": "192.168.100.1",
  "dhcpStartIpRange": "192.168.100.10",
  "dhcpEndIpRange": "192.168.100.250",
  "dhcpMode": "DHCPServer",
  "dhcpDomain": "example.com",
  "dhcpDefaultLease": 36000,
  "dhcpMaxLease": 2592000,
  "dhcpDnsServers": "8.8.8.8,8.8.4.4",
  "wins": "",
  "portName": "vlan100",
  "vlanMapToEsa": -1,
  "dhcpExclusions": [],
  "foreignIpAddress": "0.0.0.0",
  "apRegistration": false,
  "fqdn": "",
  "isid": 0,
  "pool": [],
  "proxied": "Local",
  "features": ["CENTRALIZED-SITE"]
}
```

**⚠️ INVALID FIELDS (NOT in API spec):**
- `description` - Do NOT include (will cause 400 error)
- Any custom fields not in swagger.json

#### 2. Service Element (SSID)

**Endpoint:** `POST /v1/services`

**Required Fields:**
- `serviceName` (string, 1-64 chars)
- `ssid` (string, 1-32 chars)
- `status` (enum: "enabled", "disabled")
- `enableCaptivePortal` (boolean)
- `mbaAuthorization` (boolean)
- `authenticatedUserDefaultRoleID` (UUID string)
- `defaultTopology` (UUID string)

**Schema:**
```json
{
  "id": "uuid",
  "serviceName": "Corporate-WiFi",
  "ssid": "Corporate-WiFi",
  "status": "disabled",
  "suppressSsid": false,
  "privacy": {
    "WpaPskElement": {
      "mode": "auto",
      "pmfMode": "enabled",
      "keyHexEncoded": false,
      "presharedKey": "SecurePassword123"
    }
  },
  "proxied": "Local",
  "shutdownOnMeshpointLoss": false,
  "dot1dPortNumber": 101,
  "enabled11kSupport": false,
  "rm11kBeaconReport": false,
  "rm11kQuietIe": false,
  "uapsdEnabled": true,
  "admissionControlVideo": false,
  "admissionControlVoice": false,
  "admissionControlBestEffort": false,
  "admissionControlBackgroundTraffic": false,
  "flexibleClientAccess": false,
  "mbaAuthorization": false,
  "accountingEnabled": false,
  "clientToClientCommunication": true,
  "includeHostname": false,
  "mbo": false,
  "oweAutogen": false,
  "oweCompanion": null,
  "purgeOnDisconnect": false,
  "enable11mcSupport": true,
  "beaconProtection": false,
  "enableCaptivePortal": false,
  "captivePortalType": null,
  "eGuestPortalId": null,
  "eGuestSettings": [],
  "preAuthenticatedIdleTimeout": 300,
  "postAuthenticatedIdleTimeout": 1800,
  "sessionTimeout": 0,
  "defaultTopology": "topology-uuid",
  "defaultCoS": null,
  "unAuthenticatedUserDefaultRoleID": "4459ee6c-2f76-11e7-93ae-92361f002671",
  "authenticatedUserDefaultRoleID": "4459ee6c-2f76-11e7-93ae-92361f002671",
  "cpNonAuthenticatedPolicyName": null,
  "aaaPolicyId": null,
  "mbatimeoutRoleId": null,
  "roamingAssistPolicy": null,
  "features": ["CENTRALIZED-SITE"],
  "vendorSpecificAttributes": ["apName", "vnsName", "ssid"],
  "hotspotType": "Disabled",
  "hotspot": null,
  "dscp": {
    "codePoints": [2,0,0,0,0,0,0,0,0,0,2,0,2,0,2,0,1,0,3,0,3,0,3,0,3,0,4,0,4,0,4,0,4,0,5,0,5,0,5,0,5,0,0,0,0,0,6,0,6,0,0,0,0,0,0,0,7,0,0,0,0,0,0,0]
  }
}
```

#### 3. AAA Policy Element

**Endpoint:** `POST /v1/aaapolicy`

**✅ CORRECT Field Names:**
```json
{
  "id": "uuid",
  "name": "XIQ_RADIUS_Policy",
  "authenticationRadiusServers": [
    {
      "id": "uuid",
      "ipAddress": "192.168.1.10",
      "sharedSecret": "secret123",
      "port": 1813,
      "timeout": 5,
      "totalRetries": 3,
      "pollInterval": 60
    }
  ],
  "accountingRadiusServers": [],
  "authenticationType": "PAP",
  "serverPoolingMode": "failover",
  "features": ["CENTRALIZED-SITE"]
}
```

**❌ INCORRECT Field Names (OLD - DO NOT USE):**
- `policyName` → Use `name`
- `radiusServers` → Use `authenticationRadiusServers`
- `authenticationProtocol` → Use `authenticationType`

#### 4. RADIUS Server Element

**✅ CORRECT Field Names:**
```json
{
  "id": "uuid",
  "ipAddress": "192.168.1.10",
  "sharedSecret": "secret123",
  "port": 1813,
  "timeout": 5,
  "totalRetries": 3,
  "pollInterval": 60
}
```

**❌ INVALID FIELDS (DO NOT USE):**
- `serverName` - Not in API spec
- `enabled` - Not in API spec
- `authenticationPort` - Deprecated
- `accountingPort` - Deprecated
- `retries` → Use `totalRetries`

#### 5. CoS (Class of Service) Element

**Endpoint:** `POST /v1/cos`

**✅ CORRECT Schema:**
```json
{
  "id": "uuid",
  "cosName": "Gold_CoS",
  "cosQos": {
    "priority": 5,
    "tosDscp": 46,
    "mask": 0,
    "useLegacyMarking": null
  },
  "transmitQueue": 0,
  "predefined": false,
  "inboundRateLimiterId": "rate-limiter-uuid",
  "outboundRateLimiterId": "rate-limiter-uuid",
  "features": ["CENTRALIZED-SITE"]
}
```

**❌ INCORRECT (OLD - DO NOT USE):**
- Flat structure with `name`, `dscp`, `dot1p` fields
- `ingressRateLimiterId` → Use `inboundRateLimiterId`
- `egressRateLimiterId` → Use `outboundRateLimiterId`

---

## Field Validation Requirements

### Name Fields

**Rules:**
- Length: 1-255 characters (topology/service names)
- SSID: 1-32 characters specifically
- Service Name: 1-64 characters specifically
- **Invalid Characters:** Semicolon (;), Colon (:), Ampersand (&)
- Valid: Alphanumeric + most special characters

**Python Validation:**
```python
def validate_name(name: str, min_len: int = 1, max_len: int = 255) -> bool:
    if not name or not isinstance(name, str):
        return False
    if len(name) < min_len or len(name) > max_len:
        return False
    invalid_chars = [';', ':', '&']
    return not any(char in name for char in invalid_chars)
```

### IP Address Fields

**Rules:**
- Format: IPv4 (e.g., 192.168.1.1)
- Range: 0.0.0.0 to 255.255.255.255
- Special: 0.0.0.0 used for "not configured"

**Python Validation:**
```python
def validate_ip_address(ip: str) -> bool:
    if not ip or not isinstance(ip, str):
        return False
    parts = ip.split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(part) <= 255 for part in parts)
    except (ValueError, TypeError):
        return False
```

### Numeric Field Ranges

| Field | Min | Max | Default | Description |
|-------|-----|-----|---------|-------------|
| `vlanid` | 1 | 4094 | - | VLAN ID (IEEE 802.1Q) |
| `cidr` | 0 | 32 | 0 | CIDR notation for IPv4 |
| `dhcpDefaultLease` | - | - | 36000 | DHCP lease time (seconds) |
| `dhcpMaxLease` | - | - | 2592000 | Max DHCP lease (30 days) |
| `timeout` | 1 | 360 | 5 | RADIUS timeout (seconds) |
| `totalRetries` | 1 | 32 | 3 | RADIUS retry count |
| `pollInterval` | 30 | 300 | 60 | RADIUS poll interval (seconds) |
| `port` | 1 | 65535 | 1813 | Port number |
| `mtu` | - | - | 1500 | Maximum Transmission Unit |
| `preAuthenticatedIdleTimeout` | 5 | 999999 | 300 | Pre-auth idle (seconds) |
| `postAuthenticatedIdleTimeout` | 0 | 999999 | 1800 | Post-auth idle (seconds) |
| `sessionTimeout` | 0 | 999999 | 0 | Session timeout (0=unlimited) |

---

## Network/Topology Best Practices

### 1. VLAN ID Assignment

**Best Practices:**
- Use VLAN IDs 1-4094 (IEEE 802.1Q standard)
- Avoid VLAN 1 (default VLAN)
- Reserve VLANs 1002-1005 (Token Ring/FDDI)
- Plan VLAN ranges:
  - 10-99: Infrastructure
  - 100-199: User networks
  - 200-299: Guest networks
  - 300-399: IoT/Management

### 2. L3 Configuration

**When to set `l3Presence: true`:**
- Subnet is configured (valid IP/CIDR)
- Gateway is configured
- DHCP server mode is enabled

**Best Practice:**
```json
{
  "l3Presence": true,
  "ipAddress": "192.168.100.1",
  "cidr": 24,
  "gateway": "192.168.100.1",
  "dhcpMode": "DHCPServer",
  "dhcpStartIpRange": "192.168.100.10",
  "dhcpEndIpRange": "192.168.100.250"
}
```

### 3. DHCP Configuration

**Modes:**
- `DHCPServer`: Full DHCP server (requires start/end range)
- `DHCPRelay`: Forward to external DHCP server
- `DHCPNone`: No DHCP

**DHCPServer Requirements:**
```python
if dhcp_start and dhcp_end and dhcp_start != "0.0.0.0":
    dhcp_mode = "DHCPServer"
    # Also configure:
    # - dhcpDomain
    # - dhcpDnsServers (comma-separated)
    # - dhcpDefaultLease
```

**DNS Server Format:**
```json
{
  "dhcpDnsServers": "8.8.8.8,8.8.4.4"
}
```

### 4. Features Array

**REQUIRED for all topologies:**
```json
{
  "features": ["CENTRALIZED-SITE"]
}
```

---

## Service/SSID Best Practices

### 1. Security Configuration

#### PSK (Personal)
```json
{
  "privacy": {
    "WpaPskElement": {
      "mode": "auto",
      "pmfMode": "enabled",
      "keyHexEncoded": false,
      "presharedKey": "SecurePassword123"
    }
  }
}
```

**PMF (Protected Management Frames):**
- `disabled`: PMF off
- `enabled`: PMF optional (WPA2 compatibility)
- `required`: PMF mandatory (WPA3)

#### Enterprise (802.1X)
```json
{
  "privacy": {
    "WpaEnterpriseElement": {
      "mode": "auto",
      "pmfMode": "enabled"
    }
  },
  "aaaPolicyId": "aaa-policy-uuid"
}
```

#### Open Network
```json
{
  "privacy": null
}
```

### 2. Role Assignment

**Default Role UUID:**
```
4459ee6c-2f76-11e7-93ae-92361f002671  // Enterprise User role
```

**Always set both roles:**
```json
{
  "unAuthenticatedUserDefaultRoleID": "4459ee6c-2f76-11e7-93ae-92361f002671",
  "authenticatedUserDefaultRoleID": "4459ee6c-2f76-11e7-93ae-92361f002671"
}
```

### 3. Topology Reference

**Critical:** SSID must reference a valid topology UUID
```json
{
  "defaultTopology": "topology-uuid-here"
}
```

**How to get topology UUIDs:**
```bash
GET /v1/topologies
```

### 4. Initial Status

**Best Practice:** Create SSIDs as `disabled`
```json
{
  "status": "disabled"
}
```

**Reason:** Allows configuration verification before enabling

### 5. Features Array

**REQUIRED:**
```json
{
  "features": ["CENTRALIZED-SITE"]
}
```

---

## AAA Policy Best Practices

### 1. Server Pooling

**Modes:**
- `failover`: Try servers in order
- `loadBalance`: Distribute requests

**Recommended:** Use `failover` for reliability

### 2. Multiple RADIUS Servers

**Best Practice:** Configure at least 2 servers
```json
{
  "authenticationRadiusServers": [
    {
      "ipAddress": "192.168.1.10",
      "sharedSecret": "secret1",
      "port": 1813,
      "timeout": 5,
      "totalRetries": 3
    },
    {
      "ipAddress": "192.168.1.11",
      "sharedSecret": "secret2",
      "port": 1813,
      "timeout": 5,
      "totalRetries": 3
    }
  ]
}
```

### 3. Timeout Configuration

**Recommendations:**
- `timeout`: 5 seconds (responsive)
- `totalRetries`: 3 (balance availability/speed)
- `pollInterval`: 60 seconds (health check)

### 4. Authentication Type

**Options:**
- `PAP`: Password Authentication Protocol (default)
- `CHAP`: Challenge-Handshake
- `MSCHAP`: Microsoft CHAP
- `MSCHAP2`: Microsoft CHAP v2 (recommended for Windows)

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Action |
|------|---------|--------|
| 200 | Success | Process response |
| 201 | Created | Object created successfully |
| 204 | No Content | Success, no response body |
| 400 | Bad Request | Check schema/validation |
| 401 | Unauthorized | Re-authenticate |
| 404 | Not Found | Check endpoint/ID |
| 405 | Method Not Allowed | Check HTTP method |

### Retry Logic

**Recommended Strategy:**
```python
max_retries = 3
for attempt in range(max_retries):
    try:
        response = make_request()
        if response.status_code == 401:
            re_authenticate()
            continue
        return response
    except Timeout:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        continue
```

### Validation Errors (400)

**Common Causes:**
1. Invalid field names (e.g., `policyName` vs `name`)
2. Missing required fields
3. Invalid data types
4. Out-of-range values
5. Invalid UUID format
6. Invalid character in name field

**Debugging:**
- Check swagger.json for exact field names
- Verify all required fields present
- Validate field data types
- Check numeric ranges
- Ensure UUID format

---

## Performance Optimization

### 1. Dependency Ordering

**Post objects in this order:**
1. Rate Limiters (no dependencies)
2. CoS Policies (depend on rate limiters)
3. Topologies (no dependencies)
4. AAA Policies (no dependencies)
5. Services (depend on topologies, AAA policies)

### 2. Batch Operations

**For large migrations:**
- Check for existing objects before creating
- Use `/v1/{resource}/nametoidmap` endpoints
- Skip duplicates gracefully

### 3. Token Refresh

**Pro-active refresh:**
```python
if datetime.now() >= token_expiry - timedelta(minutes=5):
    refresh_token()
```

---

## Migration Workflow

### Step 1: Authentication
```python
token = authenticate(username, password)
```

### Step 2: Export from Source
```python
xiq_config = xiq_client.get_configuration()
```

### Step 3: Get Existing Objects
```python
existing_topologies = cc_client.get_existing_topologies()
existing_services = cc_client.get_existing_services()
```

### Step 4: Convert Configuration
```python
cc_config = converter.convert(xiq_config, existing_topologies)
```

### Step 5: Post in Order
```python
# 1. Rate Limiters
post_rate_limiters(cc_config['rate_limiters'])

# 2. CoS Policies
post_cos_policies(cc_config['cos_policies'])

# 3. Topologies
post_topologies(cc_config['topologies'])

# 4. AAA Policies
post_aaa_policies(cc_config['aaa_policies'])

# 5. Services
post_services(cc_config['services'])
```

### Step 6: Verification
```python
verify_all_objects_created()
verify_ssid_topology_mappings()
verify_aaa_policy_links()
```

### Step 7: Enable Services
```python
# Enable SSIDs after verification
for service in services:
    update_service_status(service['id'], "enabled")
```

---

## Common Pitfalls

### 1. ❌ Using Wrong Field Names

**Problem:**
```json
{
  "policyName": "MyPolicy"  // WRONG
}
```

**Solution:**
```json
{
  "name": "MyPolicy"  // CORRECT
}
```

### 2. ❌ Missing Required Fields

**Problem:**
```json
{
  "serviceName": "WiFi",
  "ssid": "WiFi"
  // Missing: status, enableCaptivePortal, mbaAuthorization, etc.
}
```

**Solution:** Include ALL required fields per swagger.json

### 3. ❌ Invalid Characters in Names

**Problem:**
```json
{
  "name": "Network:VLAN;100"  // Contains : and ;
}
```

**Solution:**
```json
{
  "name": "Network-VLAN-100"  // Use dashes
}
```

### 4. ❌ Invalid VLAN ID

**Problem:**
```json
{
  "vlanid": 5000  // Out of range
}
```

**Solution:**
```json
{
  "vlanid": 100  // 1-4094
}
```

### 5. ❌ Missing Topology UUID

**Problem:**
```json
{
  "defaultTopology": null
}
```

**Solution:**
```json
{
  "defaultTopology": "valid-uuid-here"
}
```

### 6. ❌ Wrong Endpoint

**Problem:**
```
POST /v1/policyClassOfService  // WRONG
```

**Solution:**
```
POST /v1/cos  // CORRECT
```

### 7. ❌ Missing Features Array

**Problem:**
```json
{
  "name": "VLAN100"
  // Missing features
}
```

**Solution:**
```json
{
  "name": "VLAN100",
  "features": ["CENTRALIZED-SITE"]
}
```

---

## Validation Checklist

### Before Posting Topologies:
- [ ] VLAN ID is 1-4094
- [ ] No duplicate VLAN IDs
- [ ] Name is 1-255 chars, no ;:&
- [ ] IP addresses are valid format
- [ ] CIDR is 0-32
- [ ] DHCP mode matches configuration
- [ ] Features array includes "CENTRALIZED-SITE"

### Before Posting Services:
- [ ] SSID is 1-32 chars
- [ ] Service name is 1-64 chars
- [ ] Topology UUID is valid
- [ ] Role UUIDs are valid
- [ ] Privacy object is correct schema
- [ ] Status is "enabled" or "disabled"
- [ ] All required fields present
- [ ] Features array includes "CENTRALIZED-SITE"

### Before Posting AAA Policies:
- [ ] Using `name` not `policyName`
- [ ] Using `authenticationRadiusServers` not `radiusServers`
- [ ] Using `authenticationType` not `authenticationProtocol`
- [ ] RADIUS IPs are valid
- [ ] Timeout is 1-360
- [ ] Total retries is 1-32
- [ ] Features array included

---

## Quick Reference

### Endpoints

| Resource | GET | POST | PUT | DELETE |
|----------|-----|------|-----|--------|
| Topologies | `/v1/topologies` | `/v1/topologies` | `/v1/topologies/{id}` | `/v1/topologies/{id}` |
| Services | `/v1/services` | `/v1/services` | `/v1/services/{id}` | `/v1/services/{id}` |
| AAA Policies | `/v1/aaapolicy` | `/v1/aaapolicy` | `/v1/aaapolicy/{id}` | `/v1/aaapolicy/{id}` |
| CoS | `/v1/cos` | `/v1/cos` | `/v1/cos/{id}` | `/v1/cos/{id}` |
| Rate Limiters | `/v1/ratelimiters` | `/v1/ratelimiters` | `/v1/ratelimiters/{id}` | `/v1/ratelimiters/{id}` |
| Profiles | `/v3/profiles` | - | `/v3/profiles/{id}` | - |
| Roles | `/v3/roles` | `/v3/roles` | `/v3/roles/{id}` | `/v3/roles/{id}` |

### Useful Utility Endpoints

- Get defaults: `GET /v1/{resource}/default`
- Name to ID map: `GET /v1/{resource}/nametoidmap`

---

## Additional Resources

- **Swagger Spec:** `swagger.json` (OpenAPI 3.0)
- **API Version:** 1.25.1
- **Base URL:** `https://{IP}:5825/management`
- **Official Docs:** https://www.extremenetworks.com/support/documentation/

---

**Last Updated:** 2025-11-27
**Maintainer:** Claude Code Optimization
**Status:** Production Ready ✅
