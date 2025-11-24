# Changelog

All notable changes to the XIQ to Edge Services Migration Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-01-23

### Added - Web User Interface

#### Browser-Based Migration Interface
- **Complete Web UI** for the migration tool using Flask
- Point-and-click interface requiring no command-line knowledge
- Accessible via web browser at `http://localhost:5000`
- Launch with simple command: `./start_ui.sh`

#### User Interface Features
- **Step-by-Step Workflow** - Visual progression through 6 migration steps
- **Real-Time Progress Bar** - Visual progress indicator showing migration status
- **Interactive Object Selection** - Checkbox-based selection for SSIDs, VLANs, RADIUS servers
- **Visual Profile Assignment** - Grid-based interface for assigning SSIDs to profiles
- **Live Migration Logs** - Real-time log display with color-coded severity levels
- **Migration Summary** - Visual summary displaying all object counts
- **Responsive Design** - Works on desktop, tablet, and mobile devices

#### New Files
- `web_ui.py` - Flask application backend (380 lines)
- `templates/index.html` - Main UI template (280 lines)
- `static/css/style.css` - Modern CSS styling (680 lines)
- `static/js/app.js` - Frontend JavaScript logic (870 lines)
- `start_ui.sh` - Web UI launcher script
- `WEB_UI_GUIDE.md` - Comprehensive Web UI documentation (1,000+ lines)

#### REST API Endpoints
- `POST /api/connect_xiq` - Connect to ExtremeCloud IQ
- `POST /api/connect_edge` - Connect to Edge Services
- `POST /api/convert` - Convert configuration
- `POST /api/migrate` - Execute migration
- `GET /api/status` - Get migration status and logs
- `POST /api/reset` - Reset migration state

#### UI Workflow
1. **Connect to XIQ** - Form-based authentication with region selection
2. **Select Objects** - Tabbed interface (SSIDs, VLANs, RADIUS) with checkboxes
3. **Connect to Edge** - Form-based Edge Services authentication
4. **Assign Profiles** - Visual grid for SSID-to-profile assignments with radio selection
5. **Review & Execute** - Migration summary with dry-run option
6. **View Results** - Visual display of migration results

#### Quick Actions
- "Select All" / "Select None" buttons for bulk object selection
- "Assign All to All Profiles" - One-click assignment of all SSIDs to all profiles
- "Assign All to Custom Profiles" - One-click assignment to custom profiles only
- "Start Over" button to reset and begin new migration

#### Visual Elements
- Gradient background with modern design
- Color-coded profile badges (CUSTOM in blue, DEFAULT in gray)
- Real-time progress bar with percentage
- Live log panel with syntax highlighting
- Responsive card-based layout
- Smooth animations and transitions

#### Technical Details
- Flask web framework for backend
- Flask-CORS for cross-origin support
- RESTful API architecture
- Session-based state management
- Automatic log polling (1-second intervals)
- Support for concurrent migrations
- Mobile-responsive CSS grid layout

### Changed
- Updated `requirements.txt` to include Flask and Flask-CORS
- Updated README.md with Web UI quick start section
- CLI interface remains fully functional (both interfaces available)

### Documentation
- Created `WEB_UI_GUIDE.md` with comprehensive Web UI documentation including:
  - Step-by-step usage instructions
  - Common workflow scenarios
  - Troubleshooting guide
  - Security considerations
  - Browser compatibility matrix
  - CLI vs Web UI comparison
  - Advanced configuration options

### Performance
- Web UI adds negligible overhead (~1-2 seconds for UI rendering)
- Backend migration speed identical to CLI
- Supports environments with 50+ SSIDs
- Real-time log updates every second

## [1.3.0] - 2025-01-23

### Added - Associated Profile Assignment

#### Automated SSID-to-Profile Association
- **Interactive profile selection** for each SSID during migration
- Fetches all Associated Profiles from Edge Services (`/v3/profiles`)
- Sorts profiles with custom profiles first, default profiles last
- For each SSID, prompts:
  - Which profiles to associate with (numbers, 'all', 'custom', 'none')
  - Which radios to use (0=all radios, 1=2.4GHz, 2=5GHz, 3=6GHz)
- Applies assignments automatically via `PUT /v3/profiles/{id}`

#### New Methods
- `get_profiles()` in Edge Services client - Fetches Associated Profiles
- `update_profile_ssid_assignments()` - Updates profile with SSID assignments
- `sort_profiles()` - Sorts custom profiles first, then defaults
- `select_profile_assignments()` - Interactive profile selection UI

#### Features
- **Profile Sorting:** Custom (non-default) profiles shown first
- **Radio Selection:** Per-profile radio targeting (all, 2.4GHz, 5GHz, 6GHz)
- **Bulk Options:** 'all' applies to all profiles, 'custom' for custom only
- **Skip Option:** 'none' skips profile assignment for manual setup later
- **Duplicate Prevention:** Merges with existing assignments
- **--select-all Support:** Applies all SSIDs to all profiles on all radios

#### Documentation
- Created `PROFILE_ASSIGNMENT_GUIDE.md` with comprehensive documentation
- Updated README.md with profile assignment workflow
- Includes troubleshooting, best practices, and examples

### Changed
- Migration workflow now includes STEP 4: Associate SSIDs with Profiles
- Profile assignment happens automatically after services are posted
- Assignment summary shows all SSID-to-profile mappings

### Technical Details
- Uses Edge Services v3 API for profiles
- InterfaceAssignmentElement schema: `{serviceId, index}`
- Radio index mapping: 0=all, 1=radio1, 2=radio2, 3=radio3
- Returns JSON format: `{service_id: [{profile_id, profile_name, radio_index}]}`

## [1.2.0] - 2025-01-22

### Added - Quick Wins Phase 1

#### DNS Servers in VLANs
- Extract DNS server configurations from XIQ VLANs
- Convert to Edge Services topology `dhcpDnsServers` (comma-separated)
- Include DNS domain in `dhcpDomain` field
- Automatic fallback to Google DNS (8.8.8.8, 8.8.4.4)

#### AP Names and Locations
- New `get_devices()` method in XIQ API client
- Filter and normalize Access Point information
- Migrate AP names and physical locations
- Respect 32-character location limit
- Update via `PUT /v1/aps/{serial}` endpoint

#### Rate Limiter Support
- New `_convert_to_rate_limiters()` converter method
- Support bandwidth in Kbps or Mbps (auto-converts)
- Use `cirKbps` field per Edge Services v5.26 schema
- Post to `/v1/ratelimiters` endpoint
- New `_post_rate_limiters()` in Edge Services client

#### Class of Service (CoS) Policies
- New `_convert_to_cos_policies()` converter method
- Map rate limiter names to UUIDs
- Support DSCP (0-63) and 802.1p (0-7) values
- Reference ingress/egress rate limiters
- Post to `/v1/policyClassOfService` endpoint
- New `_post_cos_policies()` in Edge Services client

### Changed
- Updated migration dependency order:
  1. Rate Limiters
  2. Class of Service
  3. Topologies/VLANs
  4. AAA Policies
  5. Services/SSIDs
  6. AP Configurations

- Expanded conversion output to show:
  - Rate Limiters count
  - CoS Policies count
  - AP Configurations count

- Updated main.py to fetch devices during XIQ retrieval

### Documentation
- Updated README.md with new features
- Updated FEATURES.md with detailed feature documentation
- Added migration coverage metrics (30% → 55%)
- Added dependency order explanation

## [1.1.0] - 2025-01-20

### Added - Interactive Selection
- Interactive object selection for SSIDs, VLANs, and RADIUS servers
- Smart VLAN auto-detection (`auto` option)
- Ability to skip specific object types
- Selection summary with confirmation prompt
- `--select-all` flag for non-interactive mode

### Changed
- Renamed "Campus Controller" to "Edge Services" throughout codebase
- Updated all documentation and docstrings
- Improved user experience with detailed selection prompts

## [1.0.0] - 2025-01-15

### Added - Initial Release

#### Core Features
- XIQ API integration with username/password authentication
- XIQ API token authentication support
- Multi-region support (Global, EU, APAC, California)
- Edge Services v5.26 OAuth 2.0 authentication
- Configuration extraction from XIQ
- Configuration conversion to Edge Services format
- Automated posting to Edge Services

#### Object Support
- SSIDs (Wireless Services)
- VLANs (Network Topologies)
- RADIUS Servers (AAA Policies)

#### Security Support
- Open networks
- WPA-PSK (WPA2/WPA3)
- WPA-Enterprise (802.1X)
- Protected Management Frames (PMF)

#### Operational Features
- Dry-run mode for testing
- Verbose logging mode
- JSON export of configurations
- CSV export of XIQ data
- Existing topology detection and reuse
- Duplicate VLAN prevention

#### Quality of Life
- Services created in "disabled" state for review
- Comprehensive error handling
- Progress indicators
- Result summaries
- Setup and migration launcher scripts

### Fixed
- XIQ API pagination handling
- Topology UUID mapping
- Role ID requirements
- Captive portal settings
- VLAN conflict prevention

---

## Migration Coverage History

| Version | Objects Supported | Coverage |
|---------|------------------|----------|
| 1.0.0   | SSIDs, VLANs, RADIUS | ~30% |
| 1.1.0   | + Interactive Selection | ~30% |
| 1.2.0   | + DNS, APs, Rate Limiters, CoS | ~55% |

## Upcoming Features

### Planned for Future Releases

#### Phase 2 (Medium Priority)
- User Profiles/Roles migration
- L3 Roaming support
- Firewall rules migration
- Application visibility settings

#### Phase 3 (Nice to Have)
- Radio profiles optimization
- Advanced QoS mappings
- Custom attributes migration
- Bulk AP group assignments

See `MIGRATION_ENHANCEMENT_PLAN.md` for detailed roadmap.
