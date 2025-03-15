#!/bin/bash

# Find all unique file extensions in a directory hierarchy
find . -type f -print0 | while IFS= read -r -d '' file; do
    # Get just the filename without path
    filename=$(basename -- "$file")
    # Extract extension (everything after last dot)
    ext="${filename##*.}"
    # Check if the extension is different from the filename (i.e., has an extension)
    if [[ "$filename" != "$ext" ]]; then
        echo "$ext"
    fi
done | sort -fu | awk 'NF'  # Sort and get unique results, filtering empty lines

# Explanation of components:
# - find . -type f: searches for all files in current directory and subdirectories
# - -print0 with read -d '': handles filenames with spaces and special characters
# - basename -- "$file": gets just the filename without path
# - ${filename##*.}: removes longest prefix ending with '.', leaving extension
# - if [[ "$filename" != "$ext" ]]: filters out files without extensions
# - sort -fu: shows unique sorted results (case-insensitive)
# - awk 'NF': removes empty lines
