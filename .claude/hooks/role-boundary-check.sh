#!/bin/bash
# Hook: role-boundary-check.sh
# Invariant: NFR-04 (Role boundary check)

TARGET_FILE="$1"
if [ -z "$TARGET_FILE" ]; then
  exit 0
fi

if [[ "$TARGET_FILE" =~ controllers ]] && [[ "$TARGET_FILE" =~ \.(py|ts|js)$ ]]; then
  if grep -q "/api/admin" "$TARGET_FILE" || [[ "$TARGET_FILE" =~ admin ]]; then
    if ! grep -iqE "require_role.*ADMIN" "$TARGET_FILE"; then
      echo "[HOOK ERROR - NFR-04] Controller $TARGET_FILE has admin routes but lacks require_role(ADMIN) guard."
      exit 1
    fi
  fi
fi
exit 0
