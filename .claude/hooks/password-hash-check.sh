#!/bin/bash
# Hook: password-hash-check.sh
# Invariant: NFR-03 (Bcrypt/Argon2 enforcement; no plaintext logging)

TARGET_FILE="$1"
if [ -z "$TARGET_FILE" ]; then
  exit 0
fi

if [[ "$TARGET_FILE" =~ \.(py|ts|js)$ ]] && [[ "$TARGET_FILE" =~ (src|backend) ]]; then
  if grep -inE "logger\.(info|debug|warn|error).*password.*=" "$TARGET_FILE"; then
    echo "[HOOK ERROR - NFR-03] Plaintext password logging detected in $TARGET_FILE"
    exit 1
  fi
  if grep -inE "hashlib\.(md5|sha1)" "$TARGET_FILE" | grep -i "password"; then
    echo "[HOOK ERROR - NFR-03] Insecure hash (MD5/SHA1) used for password in $TARGET_FILE"
    exit 1
  fi
fi
exit 0
