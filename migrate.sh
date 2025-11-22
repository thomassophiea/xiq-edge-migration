#!/bin/bash
# Launcher script for XIQ to Edge Services Migration Tool
# This script can be run from anywhere

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Change to the migration directory
cd "$SCRIPT_DIR" || exit 1

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Please run setup.sh first:"
    echo "  cd $SCRIPT_DIR"
    echo "  ./setup.sh"
    exit 1
fi

# Activate virtual environment and run the migration tool
source venv/bin/activate
python main.py "$@"
deactivate
