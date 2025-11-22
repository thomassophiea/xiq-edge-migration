# Edge Services v5.26 REST API Gateway - Complete Reference

**API Version:** 1.25.1
**Base URL:** `https://{IP_Address}:5825/management`
**Protocol:** OAuth 2.0 Bearer Token Authentication

---

## Authentication

### OAuth 2.0 Token Endpoint
**Endpoint:** `POST /v1/oauth2/token`

**Request:**
```json
{
  "grantType": "password",
  "userId": "adminUserId",
  "password": "adminPassword",
  "scope": "..."
}
```

**Response:**
```json
{
  "access_token": "f06f6f285e364e59fd317bd74da9e837",
  "token_type": "Bearer",
  "expires_in": 7200,
  "idle_timeout": 604800,
  "refresh_token": "3e33d8f724e69024811f1cf5869dbaf7",
  "adminRole": "FULL"
}
```

**Token Usage:**
- Add to all API requests: `Authorization: Bearer {access_token}`
- Default expiration: 7200 seconds (2 hours)
- Idle timeout: 604800 seconds (7 days)

**Refresh Token:**
- **Endpoint:** `POST /v1/oauth2/refreshToken`
- **Endpoint:** `DELETE /v1/oauth2/token/{token}` - Revoke token

---

## HTTP Response Codes

| Code | Description |
|------|-------------|
| 200 OK | Request successful |
| 201 Created | Resource created successfully |
| 204 No Content | Success with no response body |
| 400 Bad Request | Syntactically incorrect or schema violation |
| 401 Unauthorized | Invalid credentials or unauthorized |
| 404 Not Found | Resource not found |
| 405 Method Not Allowed | HTTP method not supported |

---

## Core API Endpoints

### Services (Wireless SSIDs)

**Manager:** ServiceManager

#### List All Services
- **GET** `/v1/services`
- Returns: Array of `ServiceElement`

#### Create Service
- **POST** `/v1/services`
- Body: `ServiceElement`
- Returns: 201 with created `ServiceElement`

#### Get Service by ID
- **GET** `/v1/services/{serviceId}`
- Returns: `ServiceElement`

#### Update Service
- **PUT** `/v1/services/{serviceId}`
- Body: `ServiceElement`
- Returns: Updated `ServiceElement`

#### Delete Service
- **DELETE** `/v1/services/{serviceId}`
- Returns: 204 No Content

#### Additional Service Endpoints
- **GET** `/v1/services/default` - Get default service template
- **GET** `/v1/services/nametoidmap` - Map service names to IDs
- **GET** `/v1/services/{serviceId}/deviceids` - Get devices for service
- **GET** `/v1/services/{serviceId}/siteids` - Get sites for service
- **GET** `/v1/services/{serviceId}/stations` - Get connected clients
- **GET** `/v1/services/{serviceId}/report` - Service analytics report

---

### Topologies (VLANs)

**Manager:** TopologyManager

#### List All Topologies
- **GET** `/v1/topologies`
- Returns: Array of `TopologyElement`

#### Create Topology
- **POST** `/v1/topologies`
- Body: `TopologyElement`
- Returns: 201 with created `TopologyElement`

#### Get Topology by ID
- **GET** `/v1/topologies/{topologyId}`
- Returns: `TopologyElement`

#### Update Topology
- **PUT** `/v1/topologies/{topologyId}`
- Body: `TopologyElement`
- Returns: Updated `TopologyElement`

#### Delete Topology
- **DELETE** `/v1/topologies/{topologyId}`
- Returns: 204 No Content

#### Additional Topology Endpoints
- **GET** `/v1/topologies/default` - Get default topology template
- **GET** `/v1/topologies/nametoidmap` - Map topology names to IDs
- **GET** `/v3/topologies` - V3 topology endpoint

---

### AAA Policies (RADIUS)

**Manager:** AAAPolicyManager

#### List All AAA Policies
- **GET** `/v1/aaapolicy`
- Returns: Array of `AAAPolicyElement`

#### Create AAA Policy
- **POST** `/v1/aaapolicy`
- Body: `AAAPolicyElement`
- Returns: 201 with created `AAAPolicyElement`

#### Get AAA Policy by ID
- **GET** `/v1/aaapolicy/{id}`
- Returns: `AAAPolicyElement`

#### Update AAA Policy
- **PUT** `/v1/aaapolicy/{id}`
- Body: `AAAPolicyElement`
- Returns: Updated `AAAPolicyElement`

#### Delete AAA Policy
- **DELETE** `/v1/aaapolicy/{id}`
- Returns: 204 No Content

#### Additional AAA Endpoints
- **GET** `/v1/aaapolicy/default` - Get default AAA policy template
- **GET** `/v1/aaapolicy/nametoidmap` - Map AAA policy names to IDs

---

### Roles (Access Control Policies)

**Manager:** RoleManager (v3 API)

#### List All Roles
- **GET** `/v3/roles`
- Returns: Array of `RoleElement`

#### Create Role
- **POST** `/v3/roles`
- Body: `RoleElement`
- Returns: 201 with created `RoleElement`

#### Get Role by ID
- **GET** `/v3/roles/{roleId}`
- Returns: `RoleElement`

#### Update Role
- **PUT** `/v3/roles/{roleId}`
- Body: `RoleElement`
- Returns: Updated `RoleElement`

#### Delete Role
- **DELETE** `/v3/roles/{roleId}`
- Returns: 204 No Content

#### Additional Role Endpoints
- **GET** `/v3/roles/default` - Get default role template
- **GET** `/v3/roles/nametoidmap` - Map role names to IDs
- **GET** `/v3/roles/{roleId}/rulestats` - Role rule statistics
- **GET** `/v1/roles/{roleId}/stations` - Clients with this role
- **GET** `/v1/roles/{roleId}/report` - Role analytics report

---

## Data Models

### ServiceElement (SSID)

**Required Fields:**
- `serviceName` (string, 1-64 chars) - Unique service name
- `ssid` (string, 1-32 chars) - SSID broadcast name
- `status` (enum) - "enabled" or "disabled"
- `enableCaptivePortal` (boolean) - Captive portal enabled
- `mbaAuthorization` (boolean) - MAC-based authentication
- `authenticatedUserDefaultRoleID` (UUID) - Role for authenticated users
- `defaultTopology` (UUID) - Default VLAN/topology

**Important Fields:**
```json
{
  "id": "uuid",
  "serviceName": "Corporate-WiFi",
  "ssid": "Corporate-WiFi",
  "status": "enabled|disabled",
  "suppressSsid": false,

  "privacy": {
    "WpaPskElement": {
      "mode": "auto",
      "pmfMode": "enabled|disabled|required",
      "keyHexEncoded": false,
      "presharedKey": "password"
    },
    "WpaEnterpriseElement": {
      "mode": "auto",
      "pmfMode": "enabled|disabled|required"
    },
    "WpaSaeElement": {},
    "WpaSaePskElement": {},
    "OweElement": {},
    "WepElement": {}
  },

  "defaultTopology": "topology-uuid",
  "defaultCoS": "cos-uuid",
  "authenticatedUserDefaultRoleID": "role-uuid",
  "unAuthenticatedUserDefaultRoleID": "role-uuid",
  "aaaPolicyId": "aaa-policy-uuid",

  "enableCaptivePortal": true,
  "captivePortalType": "Internal|External",
  "eGuestPortalId": "eguest-uuid",
  "cpNonAuthenticatedPolicyName": "string",

  "proxied": "Local|Centralized",
  "shutdownOnMeshpointLoss": false,
  "flexibleClientAccess": false,

  "enabled11kSupport": false,
  "rm11kBeaconReport": false,
  "rm11kQuietIe": false,
  "enable11mcSupport": true,

  "uapsdEnabled": true,
  "admissionControlVideo": false,
  "admissionControlVoice": false,
  "admissionControlBestEffort": false,
  "admissionControlBackgroundTraffic": false,

  "preAuthenticatedIdleTimeout": 300,
  "postAuthenticatedIdleTimeout": 1800,
  "sessionTimeout": 0,

  "clientToClientCommunication": true,
  "includeHostname": false,
  "mbo": true,
  "beaconProtection": false,

  "vendorSpecificAttributes": ["apName", "vnsName", "ssid"],

  "hotspotType": "Disabled",
  "hotspot": null,

  "dot1dPortNumber": 101,
  "accountingEnabled": false,
  "mbatimeoutRoleId": null,
  "roamingAssistPolicy": null,

  "features": ["CENTRALIZED-SITE"],

  "dscp": {
    "codePoints": [...]
  }
}
```

---

### TopologyElement (VLAN)

**Required Fields:**
- `name` (string, 1-255 chars) - Unique topology name
- `vlanid` (number, 1-4094) - VLAN ID
- `mode` (enum) - "BridgedAtAc" or "BridgedAtAp"

**Important Fields:**
```json
{
  "id": "uuid",
  "name": "Corporate-VLAN",
  "vlanid": 100,
  "tagged": false,
  "mode": "BridgedAtAc|BridgedAtAp",

  "l3Presence": true,
  "ipAddress": "192.168.100.1",
  "cidr": 24,
  "gateway": "192.168.100.1",

  "dhcpMode": "DHCPNone|DHCPRelay|DHCPServer",
  "dhcpStartIpRange": "192.168.100.10",
  "dhcpEndIpRange": "192.168.100.254",
  "dhcpDefaultLease": 36000,
  "dhcpMaxLease": 2592000,
  "dhcpDnsServers": "8.8.8.8,8.8.4.4",
  "dhcpDomain": "example.com",
  "dhcpServers": "",
  "dhcpExclusions": [],

  "multicastFilters": [],
  "multicastBridging": false,

  "group": 0,
  "members": [],
  "mtu": 1500,
  "enableMgmtTraffic": false,

  "portName": "vlan100",
  "vlanMapToEsa": -1,
  "foreignIpAddress": "0.0.0.0",
  "apRegistration": false,
  "fqdn": "",
  "isid": 0,

  "pool": [],
  "proxied": "Local",
  "features": ["CENTRALIZED-SITE"],

  "vni": 10001,
  "remoteVtepIp": "10.0.0.1",
  "wins": ""
}
```

---

### AAAPolicyElement

**Schema:**
```json
{
  "id": "uuid",
  "policyName": "Corporate-RADIUS",

  "radiusServers": [
    {
      "id": "uuid",
      "serverName": "RADIUS-Primary",
      "ipAddress": "192.168.1.10",
      "authenticationPort": 1812,
      "accountingPort": 1813,
      "sharedSecret": "secret123",
      "timeout": 5,
      "retries": 3,
      "enabled": true
    }
  ],

  "authenticationProtocol": "PAP|CHAP",
  "accountingEnabled": false,
  "features": ["CENTRALIZED-SITE"]
}
```

---

### RoleElement (Access Control Policy)

**Required Fields:**
- `name` (string, 1-64 chars, pattern: `^[a-zA-Z0-9._ -]{1,64}$`)
- `defaultAction` (enum) - "allow", "deny", or "containToVlan"
- `defaultCos` (UUID) - Default Class of Service

**Important Fields:**
```json
{
  "id": "uuid",
  "name": "Enterprise User",

  "defaultAction": "allow|deny|containToVlan",
  "topology": "topology-uuid",
  "defaultCos": "cos-uuid",

  "l2Filters": [
    {
      "name": "Allow IPv4",
      "intoNetwork": "destAddr",
      "outFromNetwork": "sourceAddr",
      "action": "FILTERACTION_ALLOW|FILTERACTION_DENY",
      "topologyId": "topology-uuid",
      "cosId": "cos-uuid",
      "ethertype": "ipv4|ipv6|arp",
      "macAddrType": "any|unicast|multicast",
      "userPriority": "notApplicable|0|1|2|3|4|5|6|7"
    }
  ],

  "l3Filters": [],
  "l7Filters": [],

  "profiles": ["profile-uuid"],

  "cpRedirect": "https://portal.example.com",
  "cpIdentity": "controller-id",
  "cpSharedKey": "shared-secret-16-chars",
  "cpDefaultRedirectUrl": "https://success.example.com",

  "features": ["CENTRALIZED-SITE"],
  "predefined": false
}
```

---

## Additional Endpoints by Category

### Access Points
- `/v1/aps` - List all APs
- `/v1/aps/{apSerialNumber}` - Get AP details
- `/v1/aps/reboot` - Reboot APs
- `/v1/aps/upgrade` - Upgrade AP firmware
- `/v1/aps/{apSerialNumber}/stations` - Get connected clients

### Administrators
- `/v1/administrators` - Manage admin accounts
- `/v1/administrators/{userId}` - User details
- `/v1/administrators/adminpassword` - Change password

### Audit Logs
- `/v1/auditlogs` - Retrieve audit logs

### Class of Service (CoS)
- `/v1/cos` - List all CoS policies
- `/v1/cos/{cosId}` - CoS details

### Rate Limiters
- `/v1/ratelimiters` - List rate limiters
- `/v1/ratelimiters/{rateLimiterId}` - Rate limiter details

### Global Settings
- `/v1/globalsettings` - Get/update global settings

### NSight Configuration
- `/v1/nsightconfig` - NSight server configuration

### Notifications
- `/v1/notifications` - Manage notifications
- `/v1/notifications/regional` - Regional notifications

### Reports & Analytics
- `/v1/report/services/{serviceId}` - Service reports
- `/v1/report/aps/{apSerialNumber}` - AP reports
- `/v1/report/roles/{roleId}` - Role reports
- `/v1/report/sites` - Site reports

### Entity State
- `/v1/entitystate` - Get AP, switch, site states

---

## Best Practices

### 1. Role Management
- Always specify both `authenticatedUserDefaultRoleID` and `unAuthenticatedUserDefaultRoleID`
- Use predefined role: `4459ee6c-2f76-11e7-93ae-92361f002671` (Enterprise User)
- Don't delete predefined roles (`predefined: true`)

### 2. Topology References
- Services reference topologies by UUID, not VLAN ID
- Always fetch existing topologies before creating services
- Check for duplicate VLAN IDs before creating topologies

### 3. Service Creation
- Create topologies first
- Create AAA policies (if needed)
- Create services last (they depend on topologies and AAA)
- Set initial `status: "disabled"` for manual review

### 4. Features Array
- Always include `"features": ["CENTRALIZED-SITE"]` for centralized deployment
- Required for most objects (services, topologies, AAA policies, roles)

### 5. Authentication
- Token expires in 2 hours (7200 seconds)
- Use refresh token for long-running operations
- Handle 401 responses by re-authenticating

### 6. Error Handling
- Check for duplicate resources (VLAN conflicts)
- Validate UUIDs before using as references
- Handle schema validation errors (400 Bad Request)

---

## Common Patterns

### Creating a Complete SSID Setup

```python
# 1. Create Topology
topology = {
    "name": "Corporate-VLAN",
    "vlanid": 100,
    "mode": "BridgedAtAc",
    "l3Presence": True,
    "ipAddress": "192.168.100.1",
    "cidr": 24,
    "gateway": "192.168.100.1",
    "dhcpMode": "DHCPRelay",
    "features": ["CENTRALIZED-SITE"]
}
POST /v1/topologies

# 2. Create AAA Policy (optional)
aaa_policy = {
    "policyName": "Corporate-RADIUS",
    "radiusServers": [...],
    "features": ["CENTRALIZED-SITE"]
}
POST /v1/aaapolicy

# 3. Create Service
service = {
    "serviceName": "Corporate-WiFi",
    "ssid": "Corporate-WiFi",
    "status": "disabled",
    "defaultTopology": "{topology-uuid}",
    "authenticatedUserDefaultRoleID": "4459ee6c-2f76-11e7-93ae-92361f002671",
    "unAuthenticatedUserDefaultRoleID": "4459ee6c-2f76-11e7-93ae-92361f002671",
    "aaaPolicyId": "{aaa-policy-uuid}",
    "enableCaptivePortal": False,
    "mbaAuthorization": False,
    "privacy": {
        "WpaPskElement": {
            "mode": "auto",
            "pmfMode": "enabled",
            "presharedKey": "password123"
        }
    },
    "features": ["CENTRALIZED-SITE"]
}
POST /v1/services
```

---

## Migration Considerations

### XIQ to Edge Services Mapping

| XIQ Object | Edge Services Object |
|------------|---------------------|
| SSID | ServiceElement |
| VLAN | TopologyElement |
| RADIUS Server | AAAPolicyElement.radiusServers[] |
| User Profile | RoleElement |
| Network Policy | Profile (multiple services) |

### Key Differences
1. **Role IDs**: Edge Services requires explicit role assignments
2. **Topology UUIDs**: Services reference topologies by UUID, not VLAN ID
3. **Features Array**: Required for centralized deployments
4. **Privacy Objects**: Nested structure vs flat XIQ structure
5. **Status**: Services default to "disabled" for safety

---

## Versioning

**Current Version:** 1.25.1

- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

**Semantic Versioning:** https://semver.org/
