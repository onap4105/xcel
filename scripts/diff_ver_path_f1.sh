#!/bin/bash

# Grouped comparison with sorted files
# Usage: ./sorted_compare.sh file1 file2

file1="$1"
file2="$2"

# Create temporary sorted files
sorted1=$(mktemp)
sorted2=$(mktemp)
sort "$file1" > "$sorted1"
sort "$file2" > "$sorted2"

# Color codes
color_red=$'\033[31m'
color_green=$'\033[32m'
color_reset=$'\033[0m'

# Cleanup temporary files on exit
trap 'rm -f "$sorted1" "$sorted2"' EXIT

# Read sorted files into arrays
mapfile -t file1_lines < "$sorted1"
mapfile -t file2_lines < "$sorted2"

# Version pattern (adjust as needed)
version_pattern='v[0-9]+\.[0-9]+\.[0-9]+'

highlight_diffs() {
    # Highlight version and path differences
    local line1="$1"
    local line2="$2"

    # Split into components
    IFS='/' read -ra parts1 <<< "$line1"
    IFS='/' read -ra parts2 <<< "$line2"

    # Find differing components
    output=""
    for ((i=0; i<${#parts1[@]} || i<${#parts2[@]}; i++)); do
        p1="${parts1[i]:-}"
        p2="${parts2[i]:-}"

        if [ "$p1" != "$p2" ]; then
            # Highlight version differences
            if [[ "$p1" =~ $version_pattern ]]; then
                output+="${color_red}$p1${color_reset}/"
                output+="${color_green}$p2${color_reset}/"
            else
                # Highlight path differences
                diff_chars=$(diff <(echo "$p1" | fold -w1) <(echo "$p2" | fold -w1) |
                            grep '^>' | sed 's/> //')
                highlighted=$(echo "$p2" |
                             sed -E "s/([$diff_chars])/${color_green}\1${color_reset}/g")
                output+="$p1/${highlighted}/"
            fi
        else
            output+="$p1/"
        fi
    done

    echo "${output%/}"
}

# Compare using comm for sorted files
comm_output=$(comm -3 "$sorted1" "$sorted2")

# Process comparison results
echo "╭────────────────────────────────────────────────────"
echo "│ Comparison between sorted files:"
echo "├────────────────────────────────────────────────────"
echo "│ ${color_red}Only in $file1${color_reset}"
echo "├────────────────────────────────────────────────────"
grep '^[^\t]' <<< "$comm_output" | while read -r line; do
    echo "│ ${color_red}$line${color_reset}"
done

echo "├────────────────────────────────────────────────────"
echo "│ ${color_green}Only in $file2${color_reset}"
echo "├────────────────────────────────────────────────────"
grep '^\t[^\t]' <<< "$comm_output" | cut -c2- | while read -r line; do
    echo "│ ${color_green}$line${color_reset}"
done

echo "├────────────────────────────────────────────────────"
echo "│ Common lines with differences:"
echo "├────────────────────────────────────────────────────"

# Find common lines that have differences
while IFS= read -r line; do
    [ -z "$line" ] && continue
    line1="$line"
    line2=$(grep -F -m1 "$(echo "$line" | cut -d/ -f1-3)" "$sorted2")

    echo "├┬─ Common Base: $(echo "$line" | cut -d/ -f1-3)"
    echo "│├─ ${color_red}Old: $(echo "$line" | cut -d/ -f4-)${color_reset}"
    echo "│└─ ${color_green}New: $(echo "$line2" | cut -d/ -f4-)${color_reset}"
done < <(comm -12 "$sorted1" "$sorted2" | while read -r line; do
    grep -vqF "$line" "$sorted2" || echo "$line"
done)

echo "╰────────────────────────────────────────────────────"
