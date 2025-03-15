#!/bin/bash

# Configuration
ROOT_DIR="./testdir"              # Directory to process
HEADER_TEXT="Custom Header"       # Text for the comment
DRY_RUN=false                      # Set to false to actually write changes
EXCLUDE_DIRS=".git|venv|node_modules"  # Directories to exclude

# Comment format mapping
get_comment_format() {
  case "$1" in
    py|rb|sh|yaml|yml)    echo "# $HEADER_TEXT" ;;
    js|ts|java|c|cpp|h)   echo "// $HEADER_TEXT" ;;
    html)                echo "<!-- $HEADER_TEXT -->" ;;
    css)                 echo "/* $HEADER_TEXT */" ;;
    *)                   echo "" ;;  # Unknown format
  esac
}

# Main processing
find "$ROOT_DIR" -type d | grep -E "$EXCLUDE_DIRS" > /dev/null && exclude=" -not -path '*/"$(grep -E "$EXCLUDE_DIRS" <<<"{}")"/*'"
find "$ROOT_DIR" -type f \
  -not \( -path "*/.git/*" -o -path "*/venv/*" -o -path "*/node_modules/*" \) \
  -print0 | while IFS= read -r -d $'\0' file; do

    # Get file extension
    ext="${file##*.}"
    echo ${file}
    echo ${ext}

    # Get appropriate comment format
    comment=$(get_comment_format "$ext")
        [ -z "$comment" ] && continue  # Skip unknown formats
    echo ${comment}

    # Check if text file
    file -b --mime-type "$file" | grep -q 'text/' || continue

    # Check if header already exists
    if head -n 1 "$file" | grep -qF "$comment"; then
        echo "✓ Header exists: $file"
        continue
    fi

        # Add header (with dry-run support)
            echo "→ Modifying: $file"
                if [ "$DRY_RUN" = false ]; then
        temp_file=$(mktemp)
        (echo "$comment" ; cat "$file") > "$temp_file"
        mv "$temp_file" "$file"
    fi
done
echo "Process complete! (Set DRY_RUN=false to write changes)"
