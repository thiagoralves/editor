#!/bin/bash

# check arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 file.json" >&2
    exit 1
fi

# Check for existence of the input file
if [ ! -f "$1" ]; then
    echo "Error: Could not find file '$1'" >&2
    exit 1
fi

# do JSON formatting, sort objects by key, leave Arrays untouched
jq --sort-keys 'walk(if type == "object" then . else . end)' "$1" 2>/dev/null

# check for jq success
if [ $? -ne 0 ]; then
    # emit input file on errors
    cat "$1"
fi
