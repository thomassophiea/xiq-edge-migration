#!/bin/bash
#
# Example Migration Script
# Demonstrates bulk extraction and migration from XIQ to Edge Services
#

set -e  # Exit on error

# Configuration
XIQ_TOKEN="${XIQ_API_TOKEN}"
CONTROLLER_URL="https://edge-services.example.com"
CONTROLLER_USER="admin"
CONTROLLER_PASS="${EDGE_SERVICES_PASSWORD}"
EXPORT_DIR="./migration_$(date +%Y%m%d_%H%M%S)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}XIQ to Edge Services Migration${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Extract from XIQ
echo -e "${GREEN}Step 1: Extracting configuration from XIQ...${NC}"
python main.py \
    --xiq-token "$XIQ_TOKEN" \
    --export-csv "$EXPORT_DIR/csv" \
    --export-json "$EXPORT_DIR/xiq_source.json" \
    --dry-run \
    --verbose

echo ""
echo -e "${GREEN}✓ Extraction complete${NC}"
echo ""
echo "Generated files:"
echo "  - $EXPORT_DIR/csv/vlans.csv (VLAN objects)"
echo "  - $EXPORT_DIR/csv/ssids.csv (SSID objects)"
echo "  - $EXPORT_DIR/csv/radius_servers.csv (RADIUS servers)"
echo "  - $EXPORT_DIR/xiq_source.json (Complete XIQ data)"
echo ""

# Step 2: Optional review pause
echo "Review exported CSV files for:"
echo "  - VLAN groups and classification rules"
echo "  - SSID security settings"
echo "  - RADIUS server configuration"
echo ""
read -p "Press Enter to continue with migration, or Ctrl+C to cancel..."

# Step 3: Migrate to Edge Services
echo ""
echo -e "${GREEN}Step 2: Migrating to Edge Services...${NC}"
python main.py \
    --input-file "$EXPORT_DIR/xiq_source.json" \
    --controller-url "$CONTROLLER_URL" \
    --username "$CONTROLLER_USER" \
    --password "$CONTROLLER_PASS" \
    --output "$EXPORT_DIR/campus_result.json" \
    --select-all \
    --verbose

echo ""
echo -e "${GREEN}✓ Migration complete!${NC}"
echo ""
echo "Migration results saved to:"
echo "  - $EXPORT_DIR/campus_result.json"
echo ""
echo "CSV exports available for documentation:"
echo "  - $EXPORT_DIR/csv/"
