#!/usr/bin/env node
'use strict';

/**
 * Hook: role-boundary-check.js
 * Invariant: NFR-04 (Role boundary enforcement on admin controllers)
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

if (!resolved.includes('/controllers/') || !/\.(py|ts|js)$/.test(resolved)) {
  process.exit(0);
}

try {
  const content = fs.readFileSync(filePath, 'utf8');

  // If this controller declares an admin prefix or admin route
  if (content.includes('/api/admin') || resolved.includes('admin')) {
    const hasAdminGuard = /require_role\(.*ADMIN.*\)|HasRole\(.*ADMIN.*\)|@roles_required\(.*ADMIN.*\)/i.test(content);
    if (!hasAdminGuard) {
      console.error(`[HOOK ERROR - NFR-04] Admin controller ${filePath} missing explicit ADMIN role guard dependency.`);
      process.exit(1);
    }
  }

  process.exit(0);
} catch (err) {
  process.exit(0);
}
