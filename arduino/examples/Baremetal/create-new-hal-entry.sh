#!/bin/bash

# Check if jq is available
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed"
    echo "Please install jq using your package manager:"
    echo "  For Gentoo: emerge -av app-misc/jq"
    echo "  For Debian/Ubuntu: apt-get install jq"
    echo "  For Fedora: dnf install jq"
    exit 1
fi

# Create backup of original file
cp hals.json hals.json.bak

# Apply jq filter to add new template object
jq '
. + {
  "New Board Template": {
    "aliases": [],
    "core": "vendor:architecture",
    "default_ain": "A0, A1, A2, A3",
    "default_aout": "DAC0, DAC1",
    "default_din": "D2, D3, D4, D5, D6, D7, D8, D9",
    "default_dout": "D10, D11, D12, D13, D14, D15, D16, D17",
    "define": "BOARD_TEMPLATE",
    "last_update": 0,
    "platform": "vendor:architecture:board:upload_speed=115200",
    "source": "template.cpp",
    "version": "0",
    "board_manager_url": "https://example.com/package_vendor_index.json"
  }
}
' hals.json > hals.json.tmp

# On success, replace original file with updated version and clean up
if [ $? -eq 0 ]; then
    mv hals.json.tmp hals.json
    rm hals.json.bak
    echo "New template object successfully added to JSON file"
else
    rm hals.json.tmp
    echo "Error adding template object to JSON file"
    echo "Backup preserved as hals.json.bak"
    exit 1
fi