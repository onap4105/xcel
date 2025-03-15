#!/bin/bash

# Two files, update the 2nd file based on the 1st file
#  case 1: file1 has a variable/value pair like "variableName1:false", and file2 has "variableName1:true" or "# variableName1:false"
#  case 2: a variable is in file1 but it is not in file2, add the variable at the bottom of file2
#  case 3: insert a configuration block from file1 to file2, see below block sample
#        tls_cipher_suites:
#           - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256   # ECDSA auth, AES-GCM
#           - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256     # RSA auth, AES-GCM
#           - TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256  # ECDSA auth, ChaCha20

# placeholder in file2
# INSERT_TLS_CIPHER_SUITES

# test files
# test file1
##############################################
# variableName1: false
# tls_cipher_suites:
#  - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
#  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
# new_variable: value
###############################################
# test file2 before update
##############################################
# # INSERT_TLS_CIPHER_SUITES
# variableName1: true
# # legacy_variable: old_value
##############################################
# test file2 after update
#############################################
# tls_cipher_suites:
#  - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
#  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
# variableName1: false
# # legacy_variable: old_value
# new_variable: value
##############################################

 FILE1="file1.yml"
FILE2="file2.yml"
TEMP_FILE="$(mktemp)"
BACKUP_FILE="$FILE2.bak"

# Create backup
cp "$FILE2" "$BACKUP_FILE"

# Extract cipher block with strict 2-space indentation
CIPHER_BLOCK=$(awk '
    /^tls_cipher_suites:/ {
        print $0
        while ((getline line) > 0) {
            if (line ~ /^  - /) {  # Must have exactly 2 spaces
                print line
            } else {
                break
            }
        }
    }
' "$FILE1")

# Process file2 with atomic replacement
awk -v cipher_block="$CIPHER_BLOCK" '
    BEGIN { cipher_inserted = 0 }

    # Replace existing cipher block or placeholder
    /^(# INSERT_TLS_CIPHER_SUITES|tls_cipher_suites:)/ {
        if (!cipher_inserted) {
            print cipher_block
            cipher_inserted = 1
        }
        # Skip existing list items
        while ((getline line) > 0) {
            if (line ~ /^  - /) continue
            print line
            break
        }
        next
    }

    # Process variables from FILE1
    FILENAME == ARGV[1] && /^[^#]/ && !/tls_cipher_suites/ {
        key = $0; sub(/:.*/, "", key); gsub(/ /, "", key)
        vars[key] = $0
        next
    }

    # Update existing variables
    FILENAME == ARGV[2] {
        if (match($0, /^[[:space:]]*#?[[:space:]]*([^:]+):/, groups)) {
            current_key = groups[1]
            if (current_key in vars) {
                print vars[current_key]
                delete vars[current_key]
                  next
            }
        }
        print
    }

    # Add remaining elements
    END {
        if (!cipher_inserted) print cipher_block
        for (key in vars) print vars[key]
    }
' "$FILE1" "$FILE2" > "$TEMP_FILE"

# Final indentation enforcement
sed -i '
    s/^\( *\)-/\1  -/  # Force 2-space indent before hyphen
    s/   /  /g          # Replace triple spaces with double
    /^$/d               # Remove empty lines
' "$TEMP_FILE"

# Validate YAML
cp "$TEMP_FILE" "./updated.yml"
if yq eval '.' "./updated.yml" >/dev/null 2>&1; then
    mv "./updated.yml" "$FILE2"
    echo "Update successful! Backup: $BACKUP_FILE"
else
    echo "YAML Error. Inspect failed_update.yml"
    cp "$TEMP_FILE" "failed_update.yml"
    mv "$BACKUP_FILE" "$FILE2"
    exit 1
fi  
