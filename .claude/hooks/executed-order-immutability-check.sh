#!/bin/bash
# Hook: executed-order-immutability-check.sh
# Invariant: NFR-02 (Append-only trade records)

TARGET_FILE="$1"
if [ -z "$TARGET_FILE" ]; then
  exit 0
fi

if [[ "$TARGET_FILE" =~ (repositories|services) ]] && [[ "$TARGET_FILE" =~ \.(py|ts|js|sql)$ ]]; then
  if grep -inE "(DELETE FROM trade_executions|UPDATE trade_executions)" "$TARGET_FILE"; then
    echo "[HOOK ERROR - NFR-02] Forbidden UPDATE/DELETE statement targeting trade_executions in $TARGET_FILE"
    exit 1
  fi
fi
exit 0
