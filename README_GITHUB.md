# XIQ to Edge Services Migration Tool

Automated migration tool to convert Extreme Cloud IQ (XIQ) wireless configurations to Extreme Edge Services (formerly Campus Controller).

## 🚀 Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd migration

# Run setup
./setup.sh

# Run migration (interactive mode)
./migrate.sh

# Or with command-line arguments
./migrate.sh \
  --xiq-username your@email.com \
  --xiq-password 'yourpassword' \
  --controller-url https://edge-services.example.com \
  --username admin \
  --password 'password' \
  --verbose
```

## 📋 What Gets Migrated

### Currently Supported (v1.0)
- ✅ **Wireless Services (SSIDs)** - Complete SSID configuration including security, VLANs, QoS
- ✅ **Network Topologies (VLANs)** - VLAN configuration with DHCP and DNS settings
- ✅ **AAA Policies (RADIUS)** - RADIUS server configuration for authentication

### Enhanced Features (Planned)
- 🔄 **Rate Limiters** - Bandwidth policies for QoS
- 🔄 **Class of Service** - QoS marking and prioritization
- 🔄 **AP Configuration** - Preserve AP names and locations
- 🔄 **User Profiles/Roles** - Access control policies and firewall rules
- 🔄 **Guest Portals** - Captive portal and eGuest configuration

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Usage Guide](USAGE_GUIDE.md)** - Complete command reference
- **[Features](FEATURES.md)** - Interactive object selection
- **[Field Mapping](FIELD_MAPPING.md)** - XIQ → Edge Services field mappings
- **[API Reference](EDGE_SERVICES_API_REFERENCE.md)** - Complete Edge Services API documentation
- **[Enhancement Plan](MIGRATION_ENHANCEMENT_PLAN.md)** - Roadmap for future features
- **[Quick Wins Implementation](QUICK_WINS_IMPLEMENTATION.md)** - High-value enhancements
- **[Endpoint Verification](ENDPOINT_VERIFICATION_REPORT.md)** - Verified API endpoints

## 🛠️ Requirements

- Python 3.7+
- Network access to XIQ and Edge Services
- Valid credentials for both systems

## 📖 How It Works

1. **Extract** - Pulls configuration from XIQ via REST API
2. **Transform** - Converts XIQ format to Edge Services format
3. **Select** - Interactive selection of objects to migrate
4. **Validate** - Checks for conflicts and dependencies
5. **Load** - Posts configuration to Edge Services via REST API

## 🔒 Security

- Never stores passwords in files
- Uses OAuth 2.0 for Edge Services authentication
- Supports XIQ token-based authentication
- SSL/TLS verification configurable

## 🤝 Contributing

This tool was developed to streamline XIQ to Edge Services migrations. Contributions welcome!

## 📝 License

[Add your license here]

## 📧 Support

[Add support contact here]

## 🎯 Project Status

**Current Version:** 1.0 (Production)
**API Compatibility:** Edge Services v5.26
**XIQ API:** v2 (2025)

---

Generated with detailed analysis and verification of Edge Services v5.26 REST API Gateway
