#!/bin/bash

file1=$1
file2=$2

# Extract the cipher suites block from file1.yml
CIPHER_BLOCK=$(awk '/tls_cipher_suites:/ {print; flag=1; next} flag && /^  -/ {print} flag && !/^  -/ {exit}' $file1)

echo $CIPHER_BLOCK

# Escape newlines and slashes for sed
CIPHER_BLOCK_ESCAPED=$(echo "$CIPHER_BLOCK" | sed ':a;N;$!ba;s/\n/\\n/g;s/\//\\\//g')
echo $CIPHER_BLOCK_ESCAPED

# Replace the placeholder in file2.yml
sed -i "s/# INSERT_CIPHER_SUITES_HERE/$CIPHER_BLOCK_ESCAPED/" $file2
