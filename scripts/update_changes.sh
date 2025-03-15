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
TEMP_FILE="temp.yml"

# Case 3: Insert TLS cipher block (preserve indentation)
# Extract cipher block from FILE1
CIPHER_BLOCK=$(awk '
    /^tls_cipher_suites:/ { block=1; print; next }
    block && /^  -/      { print; next }
    block                { block=0; exit }
' "$FILE1")

# Process variables and update FILE2
awk -v cipher_block="$CIPHER_BLOCK" '
    BEGIN { in_block = 0; inserted = 0 }
    
    # Insert cipher block at placeholder
    /# INSERT_TLS_CIPHER_SUITES/ {
        print cipher_block
        inserted = 1
        next
    }
    
    # Handle existing variables (Case 1)
    FNR==NR {
        if ($0 ~ /^[[:space:]]*#/ || $0 ~ /^$/) next
        if ($0 ~ /^tls_cipher_suites:/) next
        key = $0
        sub(/:.*/, "", key)
        gsub(/[[:space:]]/, "", key)
        vars[key] = $0
        next
    }
    
    # Process FILE2 lines
    {
        if ($0 ~ /^[[:space:]]*#?[[:space:]]*[^:]+:/) {
            key = $0
            sub(/:.*/, "", key)
            gsub(/[[:space:]#]/, "", key)
            
            if (key in vars) {
                print vars[key]
                delete vars[key]
                in_block = 0
                next
            }
        }
        print
    }
    
    # Add remaining variables at end (Case 2)
    END {
        if (!inserted) print cipher_block
        for (key in vars) print vars[key]
    }
' "$FILE1" "$FILE2" > "$TEMP_FILE"

# Replace original file
mv "$TEMP_FILE" "$FILE2"

echo "File update complete. Backup saved as $FILE2.bak"
