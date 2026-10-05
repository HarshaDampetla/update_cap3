#!/usr/bin/env node
'use strict';

/**
 * Hook: executed-order-immutability-check.js
 * Invariant: NFR-02 (Trade records and executed orders are append-only)
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

if (!resolved.includes('/repositories/') && !resolved.includes('/services/')) {
  process.exit(0);
}
if (!/\.(py|ts|js|sql)$/.test(resolved)) {
  process.exit(0);
}

try {
  const content = fs.readFileSync(filePath, 'utf8');

  // Check for updates or deletes on executed trades or trade_executions
  const deleteTradeExecutionPattern = /(DELETE\s+FROM\s+trade_executions|delete.*trade_execution|UPDATE\s+trade_executions)/i;
  if (deleteTradeExecutionPattern.test(content)) {
    console.error(`[HOOK ERROR - NFR-02] Mutation or deletion detected on trade execution table in ${filePath}. Trades are strictly append-only.`);
    process.exit(1);
  }

  process.exit(0);
} catch (err) {
  process.exit(0);
}
