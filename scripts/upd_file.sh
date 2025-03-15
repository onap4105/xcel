#!/bin/bash

if [ $# -ne 2 ]; then
    echo "Usage: $0 <file1> <file2>"
    exit 1
fi

file1="$1"
file2="$2"

awk '
    NR == FNR {
        if ($0 ~ /^[[:space:]]*#/ || $0 ~ /^[[:space:]]*$/) next
        colon_pos = index($0, ":")
        if (colon_pos == 0) next
        var = substr($0, 1, colon_pos - 1)
        value = substr($0, colon_pos + 1)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", var)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", value)
        vars[var] = value
        next
    }
    {
        original_line = $0
        is_comment = 0
        if (match($0, /^[[:space:]]*#/)) {
            is_comment = 1
            content = substr($0, RSTART + RLENGTH)
            sub(/^[[:space:]]+/, "", content)
        } else {
            content = $0
        }
        colon_pos = index(content, ":")
        if (colon_pos == 0) {
            print original_line
            next
        }
        var = substr(content, 1, colon_pos - 1)
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", var)

        if (var in vars) {
            print var ":" vars[var]
            seen_vars[var] = 1
        } else {
            print original_line
        }
    }
    END {
        for (var in vars) {
            if (!(var in seen_vars)) {
                print var ":" vars[var]
            }
        }
    }
' "$file1" "$file2" > "$file2.tmp" && mv "$file2.tmp" "$file2"
