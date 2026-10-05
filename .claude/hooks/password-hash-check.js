#!/usr/bin/env node
'use strict';

/**
 * Hook: password-hash-check.js
 * Invariant: NFR-03 (Passwords stored using strong KDF; plaintext credentials never logged)
 */

const fs = require('fs');
const path = require('path');

let input = {};
try {
  const raw = fs.readFileSync(0, 'utf8');
  if (raw) input = JSON.parse(raw);
} catch (e) {
  // Graceful fallback if no JSON stdin
}

const filePath = (input.tool_input && input.tool_input.file_path) || process.argv[2];
if (!filePath) process.exit(0);

const resolved = path.resolve(filePath).replace(/\\/g, '/');

// Only check source code files in backend/src
if (!resolved.includes('/src/') && !resolved.includes('/backend/')) process.exit(0);
if (!/\.(py|ts|js)$/.test(resolved)) process.exit(0);

try {
  const content = fs.readFileSync(filePath, 'utf8');

  // Check for dangerous logging of passwords
  const passwordLoggingPattern = /logger\.(info|debug|warn|error)\(.*password.*=.*\{/i;
  if (passwordLoggingPattern.test(content)) {
    console.error(`[HOOK ERROR - NFR-03] Potential plaintext password logging detected in ${filePath}`);
    process.exit(1);
  }

  // Check for MD5 or SHA1 password hashing
  const weakHashPattern = /hashlib\.(md5|sha1)\(/i;
  if (weakHashPattern.test(content) && content.toLowerCase().includes('password')) {
    console.error(`[HOOK ERROR - NFR-03] Weak hash (MD5/SHA1) detected for credentials in ${filePath}. Use bcrypt or argon2.`);
    process.exit(1);
  }

  process.exit(0);
} catch (err) {
  process.exit(0);
}
