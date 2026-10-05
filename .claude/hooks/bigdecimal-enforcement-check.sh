#!/bin/bash
# Hook: bigdecimal-enforcement-check.sh
# Invariant: NFR-01 (Fixed-point Decimal math)

TARGET_FILE="$1"
if [ -z "$TARGET_FILE" ]; then
  exit 0
fi

if [[ "$TARGET_FILE" =~ (domain|services) ]] && [[ "$TARGET_FILE" =~ \.(py|ts|js)$ ]]; then
  if grep -inE "(pnl|price|valuation|balance|cost|gain|loss).*float\(" "$TARGET_FILE"; then
    echo "[HOOK ERROR - NFR-01] Prohibited floating-point operation in financial calculation in $TARGET_FILE"
    exit 1
  fi
fi
exit 0
