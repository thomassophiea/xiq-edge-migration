#!/bin/bash
# Setup script for XIQ to Edge Services Migration Tool

echo "=========================================="
echo "XIQ to Edge Services Migration Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies into virtual environment..."
source venv/bin/activate
pip install -r requirements.txt
deactivate

echo ""
echo "✓ Setup complete!"
echo ""
echo "To test the installation, run:"
echo "  cd /Users/thomassophieaii/Documents/Claude/migration"
echo "  ./migrate.sh --help"
echo ""
echo "To run a migration:"
echo "  cd /Users/thomassophieaii/Documents/Claude/migration"
echo "  ./migrate.sh --xiq-username tsophiea@extremenetworks.com --xiq-password 'TSts1232!!*7' --controller-url https://tsophiea.ddns.net --username admin --password 'TSts1232!!*7' --verbose"
echo ""
