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
echo "  ./migrate.sh --help"
echo ""
echo "To run a migration:"
echo "  ./migrate.sh --xiq-username user@example.com --xiq-password 'your-xiq-password' --controller-url https://your-controller.example.com --username admin --password 'your-password' --verbose"
echo ""
