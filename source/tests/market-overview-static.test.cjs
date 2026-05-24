const fs = require('fs');
const path = require('path');
const assert = require('assert');

const fundRoutePath = path.join(__dirname, '..', 'backend', 'routes', 'fund.py');
const source = fs.readFileSync(fundRoutePath, 'utf8');

for (const needle of [
  "MARKET_OVERVIEW_FALLBACK",
  "@fund_bp.route('/market-overview')",
  "'period': '2026年3月'",
  "'total_scale': 37.53",
  "'total_count': 13930",
  "'source': '中国证券投资基金业协会'",
  "'category_series'",
  "'company_ranking'",
  "'issuance'"
]) {
  assert(source.includes(needle), `expected fund.py to contain ${needle}`);
}

console.log('market overview static checks passed');
