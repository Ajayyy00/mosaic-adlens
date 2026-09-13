import { test } from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {
  parseExact,
  scaled,
  format,
  calculate,
} from "../scripts/independent.mjs";
test("JSON numeric lexemes and strings remain exact", () => {
  const rows = parseExact(fs.readFileSync("data/content_ads.json", "utf8"));
  assert.equal(typeof rows[0].spend, "string");
  assert.equal(rows[0].ad_id, "AD-0001");
  assert.equal(calculate(rows).total, "1475731.79");
});
test("integer cents arithmetic, signs and precision rejection", () => {
  assert.equal(format(scaled("0.1") + scaled("0.2")), "0.30");
  assert.equal(format(scaled("-1.23")), "-1.23");
  assert.throws(() => scaled("1.005"));
  assert.equal(format(0n), "0.00");
});
test("strict boundary changes on official record copies", () => {
  const rows = parseExact(fs.readFileSync("data/content_ads.json", "utf8"));
  const original = rows.find((x) => x.ad_id === "AD-0029");
  for (const [field, value] of [
    ["spend", "5000"],
    ["roas", "1"],
    ["days_running", "14"],
  ]) {
    assert.equal(calculate([{ ...original, [field]: value }]).total, "0.00");
  }
});
