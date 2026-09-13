# Validation evidence

## Computation

- Original official file: 800 records, 486217 bytes; SHA-256 matches pinned acquisition manifest.
- Python Decimal: 13 flagged ads, 1475731.79 INR.
- Independent JavaScript BigInt: starts from original JSON; same 13 IDs, same platform counts/totals, same grand total.
- Recomputed revenue/spend predicate: same final answer. AD-0207 boundary discrepancy has no final effect.
- No malformed rows, missing required fields, repeated identical records, or conflicting IDs found.
- Platform sum minus answer: 0.00.
- Actual `npm run check`: 21 Python tests and 3 Node tests passed; ESLint passed; TypeScript and Vite production build passed.
- Clean checkout at deployed commit `8dc74df87eaeb5ccf0e4a8257ba2c94dcfd43a86`: `npm ci` completed with zero reported vulnerabilities; all stages of `npm run check` passed again on 2026-09-13. Anonymous GitHub refs matched that source commit.

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

Screenshots are in artifacts/qa/.

## Public production verification

Verified https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site on 2026-09-13. Independent requests supplied no authentication or cookies. Homepage, both JS/CSS assets, all seven JSON reports, the CSV and favicon returned HTTP 200. JSON contents and the full 800-row CSV were parsed and checked. The missing-report request returns a static SPA HTML fallback, not report JSON; this hosting behavior is explicitly retained in `artifacts/qa/http-checks.json`.

Real browser production actions verified every major view, Instagram + wasted-spend filtering (5 records), AD-0029 search/details, pagination and sorting. Ascending ID began at AD-0001 and page 2 at AD-0013; descending spend began at AD-0072 (199998.91); newest start date began at AD-0395. Mobile 390×844 was rechecked with actual screenshot and document client/scroll width both 375 (15 pixels used by the browser scrollbar). No production-origin warning/error logs were recorded. Two earlier localhost-only createRoot warnings occurred during source-formatting hot reloads; they are not production failures.

## Video verification

`artifacts/demo/validation.json` records an actually decoded 115.84-second MP4: H.264, 1920×1080, 30 fps, AAC audio. It contains 43 valid, nonoverlapping subtitle cues, matching the narration transcript after punctuation normalization. Word-boundary timings come from the actual synthesis, and scene durations are aligned to 30 fps. The final overview shot repeats the exact answer. Authentic public browser screenshot provenance is saved beside the demo. Representative decoded frames were visually inspected; captions were resized and recolored for readability before final rendering. Voice: en-US-AndrewNeural, disclosed neural male narration. A human realism assessment is subjective; no human voice recording is claimed.

An independent local faster-whisper tiny.en transcription recovered the audio's core content, all thresholds, the AD-0029 example and final amount. ASR spelling errors include the product name and paise; the canonical transcript and on-screen exact figures are authoritative. Audio was processed locally, not uploaded to an external transcription API.

Anonymous HTTP verification also checked the public MP4, SRT and transcript byte for byte against local artifacts. The MP4 SHA-256 is `2ec56503d093bd26ce4ab299867a57bef95e6bd78322508018335d6c7422314d`. The HTTP checker pins media hashes so it also runs from a clean checkout without the ignored MP4.

