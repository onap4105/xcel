#!/bin/bash

# Configuration
ROOT_DIR=$1       # Directory to process
HEADER_TEXT="# ---------------------------------------------------------------------------- #
# Copyright (c) 2025 AT&T Inc. All Rights Reserved.                            #
# ---------------------------------------------------------------------------- #"

HEADER_TEXT1="// ----------------------------------------------------------------------------
// Copyright (c) 2025 AT&T Inc. All Rights Reserved.
// ---------------------------------------------------------------------------- "

DRY_RUN="dryrun"           # Set to false to actually write changes
EXCLUDE_DIRS="emptystate|build|Example|example"  # Directories to exclude

# Check for command-line argument and set DRY_RUN if provided
if [ -n "$2" ]; then
    DRY_RUN="$2"
fi

# Function to display the help message
usage() {
    echo "Usage: $0 [DIRECTORY] [RUN_MODE]"
    echo ""
    echo "Arguments:"
    echo "  DIRECTORY  The directory to operate on."
    echo "  RUN_MODE   The mode of operation. Can be 'dryrun' or 'update'."
    echo ""
    echo "Example:"
    echo "  $0 /path/to/directory dryrun"
    echo "  $0 /path/to/directory update"
}

# Function to get appropriate comment format
get_comment_format() {
    case "$1" in
        py|tf|sh|tpl) echo "$HEADER_TEXT" ;;
        java)         echo "$HEADER_TEXT1" ;;
        *)            echo "" ;;  # Unknown format
    esac
}

# Check if the user requested help
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    usage
    exit 0
fi

# Construct the exclude argument for the find command
exclude=""
for dir in $(echo $EXCLUDE_DIRS | tr "|" "\n"); do
    exclude="$exclude -o -path '*/$dir/*'"
done

# Construct the find command with exclusions
find_cmd="find \"$ROOT_DIR\" -type f \
    -not \( -path '*/.git/*' -o -path '*/venv/*' -o -path '*/node_modules/*' $exclude \) \
    -print0"

# Main processing
eval "$find_cmd" | while IFS= read -r -d $'\0' file; do

    # Get file extension
    ext="${file##*.}"

    # Get appropriate comment format
    comment=$(get_comment_format "$ext")
    [ -z "$comment" ] && continue  # Skip unknown formats

    # Check if text file
    file -b --mime-type "$file" | grep -q 'text/' || continue

    # Check if header already exists
    if grep -qF "$comment" "$file"; then
        echo "✓ Header exists: $file"
        continue
    fi

    # Add header (with dry-run support)
    echo "→ ${DRY_RUN} Adding Copyright: $file"
    if [ "$DRY_RUN" = "update" ]; then
        temp_file=$(mktemp)
        # Check if the first line is '#!/bin/bash'
        if head -n 1 "$file" | grep -qE "^#! ?/bin/bash"; then
            # Add the '#!/bin/bash' line and the comment, then the rest of the file
            {
                head -n 1 "$file"
                echo ""
                echo "$comment"
                echo ""
                tail -n +2 "$file"
            } > "$temp_file"
        else
            # Add the comment at the top if '#!/bin/bash' is not present
            {
                echo "$comment"
                echo ""
                cat "$file"
            } > "$temp_file"
        fi
        mv "$temp_file" "$file"
    fi
done

echo "Process complete!"

comments from Tony
the notion of get_comment_format() and #! processing should be separated out as two parts:
 
check for existing copyright (no need to do anything further)
determine the language:
look first for a #! line and grab the language from there
if not, THEN look at the extension and grab the language from there
if there is a configurations for the extensions, use that
otherwise use the list of "known" extensions
otherwise the language is "unknown"
keep a separate log of these so that the user can easily grab the list of files that need further viewing
Once the language is decided, determine the comment convention for use with that language
if the language is unknown, then use a default comment convention
I suggest using a default of # instead of an empty string
at some point, you will probably running to a language that requires both a comment prefix and suffix
check for #! (any #!, not just /bin/bash lines)
if it exists, preserve the #! line
add the appropriate copyright line with the language-appropriate comment prefix/suffix

your mv command does not preserve file permissions
 
you could use a yaml configuration file like this:
 
 
# language to comment convention. Use [str1,str2] for prefix and suffix
comments:
    python: '# '
    c: '// '
    c++: '// '
    shell: '# '
    terraform: '# '
    template: '# '
    perl: '# '
# filename extensions to look for
extensions:
    py: python
    sh: shell
    bash: shell
    ksh: shell
    eksh: shell
    tf: terraform
    tpl: template
    tmpl: template
    template: template
# #! mappings. Strings found in #! headers
shbang:
    python: python
    perl: perl
    bash: shell
    sh: shell
    ksh: shell
    eksh: shell
    dash: shell
 
 
 
you COULD rewrite it into python -- might make a bunch of the processing easier, especially after adding support for a configuration file
 
