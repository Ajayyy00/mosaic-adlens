# Validation evidence

## Computation

- Original official file: 800 records, 486217 bytes; SHA-256 matches pinned acquisition manifest.
- Python Decimal: 13 flagged ads, 1475731.79 INR.
- Independent JavaScript BigInt: starts from original JSON; same 13 IDs, same platform counts/totals, same grand total.
- Recomputed revenue/spend predicate: same final answer. AD-0207 boundary discrepancy has no final effect.
- No malformed rows, missing required fields, repeated identical records, or conflicting IDs found.
- Platform sum minus answer: 0.00.
- Actual `npm run check`: 21 Python tests and 3 Node tests passed; ESLint passed; TypeScript and Vite production build passed.

## Browser QA (local working app)

Real browser actions were performed against http://127.0.0.1:5173/.

- Dashboard displayed 1475731.79 and the complete platform reconciliation.
- Flagged-ad action selected exactly 13 ads; page 2 displayed AD-0214.
- Search AD-0029 returned one row; opening it showed spend 139192.58, revenue 95216.60, ROAS 0.68, 65 days, contribution 139192.58, source index 28.
- Combined filters Instagram + M 35-44 + Lifestyle returned five records. ROAS ascending sorted 0.68, 2.48, 3.77, 27.36, 61.60.
- A nonexistent search produced the explicit empty state.
- Methodology page displayed reconciliation and source provenance.
- Downloads view exposed eight actual report links.
- Desktop screenshots captured; mobile 390×844 viewport tested, including record dialog. An initial screen-reader table label caused horizontal page overflow; adding a containing block fixed it. Recheck: document width 375 and scroll width 375, with table overflow confined to its own scroll area.
- Browser error/warning log check returned no entries during these checks.

Screenshots are in artifacts/qa/. Public production HTTP/browser checks and final video validation are recorded after deployment.
