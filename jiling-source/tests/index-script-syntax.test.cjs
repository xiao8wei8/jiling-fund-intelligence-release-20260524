const fs = require('fs');
const path = require('path');
const assert = require('assert');

const htmlPath = path.join(__dirname, '..', 'frontend', 'index.html');
const html = fs.readFileSync(htmlPath, 'utf8');
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1].trim())
  .filter(Boolean);

assert(scripts.length > 0, 'expected at least one inline script in frontend/index.html');

for (const [index, script] of scripts.entries()) {
  try {
    new Function(script);
  } catch (error) {
    error.message = `inline script ${index + 1} has invalid syntax: ${error.message}`;
    throw error;
  }
}

console.log('inline script syntax checks passed');
