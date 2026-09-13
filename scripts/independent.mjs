// Independent raw-source calculation: preserve JSON numeric lexemes, then use BigInt cents.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import assert from "node:assert/strict";
import crypto from "node:crypto";
export function parseExact(text) {
  return JSON.parse(
    text.replace(
      /"(?:\\.|[^"\\])*"|-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?/g,
      (token) => (token.startsWith('"') ? token : JSON.stringify(token)),
    ),
  );
}
export function scaled(value, places = 2) {
  const match = /^(-?)(\d+)(?:\.(\d+))?$/.exec(value);
  if (!match || (match[3] || "").length > places)
    throw new Error(`Invalid precision: ${value}`);
  return (
    (match[1] ? -1n : 1n) *
    BigInt(match[2] + (match[3] || "").padEnd(places, "0"))
  );
}
export function format(cents) {
  const sign = cents < 0n ? "-" : "";
  const absolute = cents < 0n ? -cents : cents;
  return (
    sign + absolute / 100n + "." + (absolute % 100n).toString().padStart(2, "0")
  );
}
export function calculate(rows) {
  let total = 0n,
    count = 0,
    recomputed = 0n;
  const categories = Object.fromEntries(
    ["Google", "Instagram", "Meta", "YouTube"].map((p) => [
      p,
      { count: 0, cents: 0n, ids: [] },
    ]),
  );
  const ids = new Set();
  const signatures = new Set();
  let repeats = 0,
    duplicateIds = 0;
  for (const ad of rows) {
    if (ids.has(ad.ad_id)) duplicateIds++;
    ids.add(ad.ad_id);
    const signature = JSON.stringify(
      Object.fromEntries(
        Object.entries(ad).sort(([a], [b]) => a.localeCompare(b)),
      ),
    );
    if (signatures.has(signature)) repeats++;
    signatures.add(signature);
    const spend = scaled(ad.spend),
      revenue = scaled(ad.revenue),
      roas = scaled(ad.roas),
      days = BigInt(ad.days_running);
    if (revenue < spend && spend > 500000n && days > 14n) recomputed += spend;
    if (roas >= 100n || spend <= 500000n || days <= 14n) continue;
    total += spend;
    count++;
    categories[ad.platform].count++;
    categories[ad.platform].cents += spend;
    categories[ad.platform].ids.push(ad.ad_id);
  }
  return {
    records: rows.length,
    count,
    total: format(total),
    recomputed_ratio_total: format(recomputed),
    duplicate_ids: duplicateIds,
    identical_repeats: repeats,
    categories: Object.entries(categories).map(([category, x]) => ({
      category,
      count: x.count,
      amount: format(x.cents),
      record_ids: x.ids,
    })),
  };
}
export function main() {
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
  const raw = fs.readFileSync(path.join(root, "data/content_ads.json"), "utf8");
  const actual = calculate(parseExact(raw));
  const primary = JSON.parse(
    fs.readFileSync(
      path.join(root, "artifacts/results/final-result.json"),
      "utf8",
    ),
  );
  assert.equal(actual.records, 800);
  assert.equal(actual.records, primary.records_processed);
  assert.equal(actual.count, primary.flagged_records);
  assert.equal(actual.total, primary.answer);
  assert.equal(actual.duplicate_ids, 0);
  assert.equal(actual.identical_repeats, 0);
  for (const category of actual.categories) {
    const other = primary.categories.find(
      (x) => x.category === category.category,
    );
    assert.equal(category.amount, other.amount);
    assert.equal(category.count, other.count);
    assert.deepEqual(category.record_ids, other.record_ids);
  }
  const report = {
    implementation:
      "Node.js BigInt, raw official JSON, independent predicates and grouping",
    status: "PASS",
    source_sha256: crypto.createHash("sha256").update(raw).digest("hex"),
    ...actual,
    comparisons: [
      "record count",
      "flagged count",
      "all platform counts",
      "all platform amounts",
      "all flagged IDs",
      "grand total",
    ],
    rounding:
      "All monetary inputs verified to <=2 decimal places; integer cents require no rounding.",
  };
  fs.writeFileSync(
    path.join(root, "artifacts/results/independent-validation.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  fs.writeFileSync(
    path.join(root, "public/reports/independent-validation.json"),
    JSON.stringify(report, null, 2) + "\n",
  );
  console.log(JSON.stringify(report, null, 2));
}
if (
  process.argv[1] &&
  path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)
)
  main();
