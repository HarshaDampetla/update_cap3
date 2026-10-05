#!/usr/bin/env node
'use strict';

/**
 * Hook: bigdecimal-enforcement-check.js
 * Invariant: NFR-01 (Price, quantity, and P&L values computed in fixed-point Decimal, never float)
 */

const fs = require('fs');
const path = require('path');

let input = {};
try {
  const raw = fs.readFileSync(0, 'utf8');
  if (raw) input = JSON.parse(raw);
} catch (e) {}

const filePath = (input.tool_input && input.tool_input.file_path) || process.argv[2];
if (!filePath) process.exit(0);

const resolved = path.resolve(filePath).replace(/\\/g, '/');

if ((!resolved.includes('/domain/') && !resolved.includes('/services/')) || !/\.(py|ts|js)$/.test(resolved)) {
  process.exit(0);
}

try {
  const content = fs.readFileSync(filePath, 'utf8');

  // Check for float() casting in financial computation functions
  const floatPattern = /(pnl|price|valuation|balance|cost|gain|loss).*\bfloat\(/i;
  if (floatPattern.test(content)) {
    console.error(`[HOOK ERROR - NFR-01] Floating-point cast detected in financial logic in ${filePath}. Use Decimal.`);
    process.exit(1);
  }

  process.exit(0);
} catch (err) {
  process.exit(0);
}
