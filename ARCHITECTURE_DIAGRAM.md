# Edge Services Migration Tool - Architecture Diagram

## Migration Flow Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     EDGE SERVICES MIGRATION TOOL                                 │
│                          Web-Based Migration Interface                           │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              6-STEP MIGRATION WIZARD                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐    │
│  │   STEP 1     │   │   STEP 2     │   │   STEP 3     │   │   STEP 4     │    │
│  │  Connect to  │ → │    Select    │ → │  Connect to  │ → │    Assign    │    │
│  │     XIQ      │   │   Objects    │   │     Edge     │   │   Profiles   │    │
│  └──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘    │
│         │                   │                   │                   │            │
│         ▼                   ▼                   ▼                   ▼            │
│  ┌──────────────┐   ┌──────────────┐                                            │
│  │   STEP 5     │   │   STEP 6     │                                            │
│  │   Review &   │ → │   Results &  │                                            │
│  │   Execute    │   │   PDF Report │                                            │
│  └──────────────┘   └──────────────┘                                            │
│                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────┘


## Data Flow Architecture

┌─────────────────────────┐                    ┌─────────────────────────┐
│                         │                    │                         │
│   EXTREMECLOUD IQ       │                    │   EXTREME EDGE SERVICES │
│   (Source Platform)     │                    │   (Target Platform)     │
│                         │                    │                         │
│  ┌───────────────────┐  │                    │  ┌───────────────────┐  │
│  │ SSIDs             │  │                    │  │ Services          │  │
│  │ - Guest-WiFi      │  │                    │  │ - Guest-WiFi      │  │
│  │ - Corporate       │  │                    │  │ - Corporate       │  │
│  │ - IoT             │  │                    │  │ - IoT             │  │
│  └───────────────────┘  │                    │  └───────────────────┘  │
│                         │                    │                         │
│  ┌───────────────────┐  │                    │  ┌───────────────────┐  │
│  │ VLANs             │  │   ┌─────────┐      │  │ Topologies        │  │
│  │ - VLAN 10         │  │   │         │      │  │ - VLAN 10         │  │
│  │ - VLAN 20         │  ├───┤  TOOL   ├──────┤  │ - VLAN 20         │  │
│  │ - VLAN 30         │  │   │         │      │  │ - VLAN 30         │  │
│  └───────────────────┘  │   └─────────┘      │  └───────────────────┘  │
│                         │                    │                         │
│  ┌───────────────────┐  │                    │  ┌───────────────────┐  │
│  │ RADIUS Servers    │  │                    │  │ AAA Policies      │  │
│  │ - 192.168.1.10    │  │                    │  │ - RADIUS Config   │  │
│  │ - 192.168.1.11    │  │                    │  │ - Auth Settings   │  │
│  └───────────────────┘  │                    │  └───────────────────┘  │
│                         │                    │                         │
│  ┌───────────────────┐  │                    │  ┌───────────────────┐  │
│  │ Access Points     │  │                    │  │ AP Configs        │  │
│  │ - AP-Floor1-01    │  │                    │  │ - AP-Floor1-01    │  │
│  │ - AP-Floor2-01    │  │                    │  │ - AP-Floor2-01    │  │
│  └───────────────────┘  │                    │  └───────────────────┘  │
│                         │                    │                         │
└─────────────────────────┘                    └─────────────────────────┘
         ▲                                                  │
         │                                                  │
         │                                                  ▼
         │                                     ┌─────────────────────────┐
         │                                     │                         │
         │                                     │   ASSOCIATED PROFILES   │
         │                                     │   (SSID Assignments)    │
         │                                     │                         │
         │                                     │  ┌──────────────────┐   │
         │                                     │  │ AP3000/default   │   │
         │                                     │  │  - Guest-WiFi    │   │
         │                                     │  │  - Corporate     │   │
         │                                     │  └──────────────────┘   │
         │                                     │                         │
         │                                     │  ┌──────────────────┐   │
         │                                     │  │ AP3000/custom    │   │
         │                                     │  │  - IoT           │   │
         └─────────────────────────────────────┤  └──────────────────┘   │
           PDF DOCUMENTATION                   │                         │
           - Full Audit Trail                  └─────────────────────────┘
           - Object Mappings
           - Migration Timeline


## Component Architecture

┌────────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND (Browser)                                │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   HTML5      │  │     CSS3     │  │  JavaScript  │  │  Material    │   │
│  │   Templates  │  │   AURA Theme │  │  (Vanilla)   │  │   Design     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘   │
│                                                                              │
│  Features: Real-time logs, Progress tracking, Theme switching, DOM caching  │
│                                                                              │
└───────────────────────────────────┬────────────────────────────────────────┘
                                    │
                              REST API (JSON)
                                    │
┌───────────────────────────────────▼────────────────────────────────────────┐
│                        BACKEND (Python/Flask)                               │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                          web_ui.py                                    │  │
│  │  - Flask Routes         - Session Management    - Thread Safety      │  │
│  │  - State Management     - Progress Tracking     - Auto-push to GitHub│  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐     │
│  │ xiq_api_client   │  │ campus_controller│  │ config_converter     │     │
│  │                  │  │     _client      │  │                      │     │
│  │ - OAuth 2.0 Auth │  │ - OAuth 2.0 Auth │  │ - XIQ→Edge Mapping   │     │
│  │ - Pagination     │  │ - Token Refresh  │  │ - Security Settings  │     │
│  │ - Error Handling │  │ - Retry Logic    │  │ - VLAN Mapping       │     │
│  │ - Data Extraction│  │ - SSID Enable    │  │ - UUID Generation    │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘     │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    pdf_report_generator.py                            │  │
│  │  - 17+ Page Reports    - Object Mappings      - API Documentation    │  │
│  │  - Timeline Generation - Text Wrapping        - Material Design      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                           config.py                                   │  │
│  │  Centralized Configuration Constants                                  │  │
│  │  - API Timeouts  - Pagination Limits  - Security Settings            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└────────────────────────────────────────────────────────────────────────────┘
                        ▲                               ▲
                        │                               │
          ┌─────────────┴──────────┐      ┌────────────┴─────────────┐
          │                        │      │                          │
          │  XIQ REST API          │      │  Edge Services REST API  │
          │  api.extremecloudiq... │      │  https://controller:5825 │
          │                        │      │                          │
          └────────────────────────┘      └──────────────────────────┘


## Key Features Visual

┌─────────────────────────────────────────────────────────────────────────────┐
│                         USER-FACING FEATURES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  📻 SSID BROADCAST CONTROL          📄 AUTO PDF REPORTS                      │
│  ┌──────────────────────────┐       ┌──────────────────────────┐            │
│  │ ○ Import as Disabled     │       │ ☑ Download PDF Summary   │            │
│  │ ● Start Broadcasting     │       │                           │            │
│  └──────────────────────────┘       │ - Full Audit Trail        │            │
│                                      │ - Object Mappings         │            │
│  🌓 THEME SWITCHING                 │ - Migration Timeline      │            │
│  ┌──────────────────────────┐       │ - 17+ Pages               │            │
│  │ ● Dark  ○ Light  ○ Auto  │       └──────────────────────────┘            │
│  └──────────────────────────┘                                                │
│                                      ⚡ PERFORMANCE                            │
│  🔒 DRY RUN MODE                     ┌──────────────────────────┐            │
│  ┌──────────────────────────┐       │ - Thread-Safe Operations │            │
│  │ ☐ Test without changes   │       │ - DOM Caching            │            │
│  └──────────────────────────┘       │ - Reduced API Polling    │            │
│                                      │ - Memory Optimized       │            │
│                                      └──────────────────────────┘            │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘


## Security & Reliability Features

┌───────────────────────────────────────────────────────────────┐
│                    ENTERPRISE-GRADE FEATURES                   │
├───────────────────────────────────────────────────────────────┤
│                                                                 │
│  🔐 OAuth 2.0 Authentication    ⏱️  Auto Token Refresh         │
│  🔁 Automatic Retry Logic       📊 Real-time Progress          │
│  🧵 Thread-Safe Operations      🔒 Session Security            │
│  📝 Comprehensive Logging       ⚠️  Error Handling             │
│  💾 Memory Management           🚀 Production Ready            │
│                                                                 │
└───────────────────────────────────────────────────────────────┘


## Deployment Architecture

┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│                         GitHub Repository                        │
│              https://github.com/.../xiq-edge-migration           │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │   Source   │  │   Tests    │  │    Docs    │               │
│  │    Code    │  │  (Future)  │  │   README   │               │
│  └────────────┘  └────────────┘  └────────────┘               │
│                                                                  │
└────────────────────────┬───────────────────────────────────────┘
                         │
                   Auto-Deploy
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                                                                  │
│                         Railway.app                              │
│                    Production Deployment                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Flask Application                       │  │
│  │  - HTTPS Enabled                                          │  │
│  │  - Environment Variables (SECRET_KEY)                     │  │
│  │  - Auto-scaling                                           │  │
│  │  - Health Monitoring                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└────────────────────────────────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
                  ┌─────────────┐
                  │   End Users │
                  │  (Admins)   │
                  └─────────────┘
```

---

**Legend:**
- `→` Flow direction
- `┌─┐` Component boundary
- `│` Connection/relationship
- `▼` Data flow direction
- `○` Radio button (unselected)
- `●` Radio button (selected)
- `☐` Checkbox (unchecked)
- `☑` Checkbox (checked)
