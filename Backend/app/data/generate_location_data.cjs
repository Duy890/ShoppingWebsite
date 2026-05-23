/**
 * Fetches full Vietnamese administrative data from the DVHCVN public API
 * (based on Resolution 202/2025/QH15 — 34 provinces effective July 1, 2025)
 * and writes three JSON files:
 *   - provinces.json   → array of province objects
 *   - districts.json   → dict keyed by province_code
 *   - wards.json       → dict keyed by district_code
 *
 * Usage: node generate_location_data.js
 * Requires: Node.js 18+ (built-in fetch)
 */

const fs = require('fs');
const path = require('path');

const BASE_URL = 'https://provinces.open-api.vn/api';

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.json();
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function main() {
  console.log('Fetching provinces...');
  const provinces = await fetchJSON(`${BASE_URL}/p/`);

  const provincesOut = provinces.map(p => ({
    code: String(p.code).padStart(2, '0'),
    name: p.name,
    type: p.division_type,
  }));

  const districtsOut = {};
  const wardsOut = {};

  for (let i = 0; i < provinces.length; i++) {
    const province = provinces[i];
    const pCode = String(province.code).padStart(2, '0');

    console.log(`[${i + 1}/${provinces.length}] Fetching districts for ${province.name}...`);

    let provinceDetail;
    try {
      provinceDetail = await fetchJSON(`${BASE_URL}/p/${province.code}?depth=3`);
    } catch (err) {
      console.warn(`  WARNING: failed to fetch ${province.name}:`, err.message);
      districtsOut[pCode] = [];
      continue;
    }

    const districtList = provinceDetail.districts || [];
    districtsOut[pCode] = districtList.map(d => ({
      code: String(d.code).padStart(3, '0'),
      name: d.name,
      type: d.division_type,
    }));

    for (const district of districtList) {
      const dCode = String(district.code).padStart(3, '0');
      const wardList = district.wards || [];
      wardsOut[dCode] = wardList.map(w => ({
        code: String(w.code).padStart(5, '0'),
        name: w.name,
        type: w.division_type,
      }));
    }

    // Be polite to the public API — 300ms between requests
    await sleep(300);
  }

  const outDir = path.dirname(__filename);
  fs.writeFileSync(path.join(outDir, 'provinces.json'), JSON.stringify(provincesOut, null, 2), 'utf8');
  fs.writeFileSync(path.join(outDir, 'districts.json'), JSON.stringify(districtsOut, null, 2), 'utf8');
  fs.writeFileSync(path.join(outDir, 'wards.json'), JSON.stringify(wardsOut, null, 2), 'utf8');

  const totalDistricts = Object.values(districtsOut).reduce((s, v) => s + v.length, 0);
  const totalWards = Object.values(wardsOut).reduce((s, v) => s + v.length, 0);

  console.log('\n✓ Done!');
  console.log(`  Provinces : ${provincesOut.length}`);
  console.log(`  Districts : ${totalDistricts}`);
  console.log(`  Wards     : ${totalWards}`);
  console.log('\nFiles written to:', outDir);
}

main().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
