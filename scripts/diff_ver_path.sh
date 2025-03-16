#!/bin/bash

# Side-by-side file comparison script
# Usage: ./compare_files.sh file1 file2

file1="$1"
file2="$2"

# Use temporary file descriptors
exec 3<"$file1"
exec 4<"$file2"

# Set column widths
left_width=80
right_width=80

# Print header
printf "%-${left_width}s | %-${right_width}s\n" "File1: $file1" "File2: $file2"
printf "%-${left_width}s | %-${right_width}s\n" "$(printf '%.0s-' {1..80})" "$(printf '%.0s-' {1..80})"

# Initialize counters
line_num=1
eof1=false
eof2=false

# Compare line by line
while true; do
    # Read lines from both files
    read -r line1 <&3 || eof1=true
    read -r line2 <&4 || eof2=true

    # Break loop if both files are exhausted
    $eof1 && $eof2 && break

    # Color differences red
    if [ "$line1" != "$line2" ]; then
        color=$'\033[31m'
        reset=$'\033[0m'
    else
        color=""
        reset=""
    fi

    # Print line numbers and lines
    printf "${color}%4d %-${left_width}s | %4d %-${right_width}s${reset}\n" \
        "$line_num" "${line1:-}" \
        "$line_num" "${line2:-}"

    ((line_num++))
done

# Close file descriptors
exec 3<&-
exec 4<&-
