#!/bin/bash

# check for correct number of arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 file1.json file2.json"
    exit 1
fi

# Check for the existence of the input files
if [ ! -f "$1" ]; then
    echo "Error: could not find file '$1'"
    exit 1
fi

if [ ! -f "$2" ]; then
    echo "Error: could not find file '$2'"
    exit 1
fi

# create temporary files
TEMP1=$(mktemp)
TEMP2=$(mktemp)

# cleanup on exit
trap 'rm -f "$TEMP1" "$TEMP2"' EXIT

# sort JSON files
jq --sort-keys 'walk(if type == "object" then . else . end)' "$1" > "$TEMP1"
jq --sort-keys 'walk(if type == "object" then . else . end)' "$2" > "$TEMP2"

# check for success of jq tool
if [ $? -ne 0 ]; then
    echo "Fehler: Probleme beim Parsen der JSON-Dateien"
    exit 1
fi

# check for colordiff
if command -v colordiff >/dev/null 2>&1; then
    DIFF_CMD="colordiff"
else
    DIFF_CMD="diff"
fi

# execute comparison
$DIFF_CMD "$TEMP1" "$TEMP2"

# forward exit code of diff
exit $?
