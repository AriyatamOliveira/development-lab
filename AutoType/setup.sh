#!/bin/bash

# AutoType Setup Script

echo "Setting up AutoType..."

# Check if we're in the AutoType directory
if [[ ! -f "autotyper.py" ]]; then
    echo "Error: Please run this script from the AutoType directory"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip3.11 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Dependencies installed successfully!"
else
    echo "Failed to install dependencies. Please check your internet connection and try again."
    exit 1
fi

echo ""
echo "Setup complete!"
echo "To run AutoType:"
echo "1. Open System Settings > Privacy & Security > Accessibility and Automation"
echo "2. Add your terminal app (Terminal.app, etc.) to the list"
echo "3. Run: python3.11 autotyper.py"