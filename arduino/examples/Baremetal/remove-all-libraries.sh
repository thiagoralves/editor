#!/bin/sh
# remove-all-libraries.sh
# Removes all installed Arduino libraries

# Source the script that finds arduino-cli
. "`dirname \"$0\"`/find-arduino-cli.sh"

# List all installed libraries and extract their names using jq
# The library names are in the "name" field of each library object
libraries="`\"$ARDUINO_CLI\" lib list --json | jq -r '.installed_libraries[].library.name'`"

# Iterate through each library and uninstall it
echo "$libraries" | while read -r lib; do
    echo "Removing library: $lib"
    "$ARDUINO_CLI" lib uninstall "$lib"
done
