# Adlens — Mosaic Ad Performance Intelligence

A reproducible, auditable solution to the Mosaic Fellowship **Content & Creative** Builder Challenge. Explore all 800 official ads, inspect each threshold and trace the exact answer to 13 qualifying records.

**[Open the verified public application](https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site)** — no login required. **[Watch the 115.84-second demo](https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site/demo/demo.mp4)**. **[Public GitHub source](https://github.com/Ajayyy00/mosaic-adlens)**.

**Computed answer: ₹14,75,731.79 (1475731.79).** Python Decimal and an independent JavaScript BigInt implementation agree on every qualifying ID, count and platform subtotal. No private answer-key match is claimed.

## Challenge and source

[Official challenge](https://mosaicfellowship.in/challenge) → Content & Creative → Ad Performance Intelligence.

Sum full ad spend when **roas < 1.0 AND spend > 5000 AND days_running > 14**. The official file is [content_ads.json](https://mosaicfellowship.in/data/content_ads.json). This is the supplied synthetic challenge dataset, not live advertising performance. No replacement dataset was created.

The complete requirement register, scope resolution, observed schema and submission constraints are in [docs/official-requirements.md](docs/official-requirements.md). Invoice/GST checks in the supplied project brief do not apply to this challenge.

## Result and reconciliation

| Platform partition | Qualifying ads | Contribution (₹) |
|---|---:|---:|
| Google | 5 | 429321.93 |
| Instagram | 5 | 576898.53 |
| Meta | 1 | 143760.62 |
| YouTube | 2 | 325750.71 |
| **Total** | **13** | **1475731.79** |

The only official scored category is **wasted spend**. Platforms partition it without overlap. All three checks can pass for one ad, but its full spend is added once. The total is not spend minus revenue. Active, paused and completed ads all qualify when the numerical conditions pass (5 active, 5 paused and 3 completed flagged ads).

Total dataset spend is ₹78,036,687.57. Flagged spend is approximately 1.89% of that total.

## Requirements and setup

- Python 3.11+ (standard library only for processing and tests)
- Node.js 22+ and npm

```bash
npm ci
python scripts/download.py
python engine/audit.py
node scripts/independent.mjs
npm test
npm run lint
npm run typecheck
npm run build
npm run dev
```

Open the URL printed by Vite. Routes use URL fragments (`#overview`, `#explorer`, `#insights`, `#methodology`, `#downloads`), so any static host can serve them without SPA rewrites. The initial page fetches generated static JSON reports; no runtime backend, database, API keys or login is needed. `npm run preview` serves the production build locally.

`npm run check` runs tests, independent reconciliation, lint, typecheck and production build. For a clean checkout, generated reports and the official source are committed; downloading is also independently reproducible.

## Acquisition and completeness

`scripts/download.py` downloads from the exact official link, verifies 800 records and the pinned SHA-256 before saving, and writes `data/manifest.json` with source URL, UTC timestamp, bytes, checksum and fields. A changed source hash fails closed for review. Original JSON bytes are preserved.

- Filename: `content_ads.json`
- Bytes: 486,217
- SHA-256: `75560e463afcec73fed96bd4c3a4105ef1772f0f3d7c50a43572e6953e752474`
- Rows: 800; unique ad IDs: 800
- Schema: 23 fields; 9 descriptive/date strings, 4 integer counts, 9 numeric metrics and nullable video completion
- Essential fields: `ad_id`, `platform`, `target_audience`, `creative_theme`, `ad_type`, `spend`, `revenue`, `roas`, `days_running`

All fields are validated by the engine. There are no missing required fields, malformed rows or duplicates in this pinned dataset. The 488 null `video_completion_rate` fields are permitted and irrelevant to the decision.

## Audit methodology and numerical discipline

`engine/audit.py` parses raw JSON numbers directly as `Decimal`. Monetary addition and comparisons never use binary floating point. It retains exact spend and exact contributions; formatted output uses `ROUND_HALF_UP` to two decimal places only for reporting. The official page specifies two decimals but no tie-breaking mode. Because every supplied money value is already in cents, half-up, half-even and per-record rounding give the same final answer. A category rounding residual blocks the final result rather than silently adjusting a category.

The primary filter uses the supplied ROAS. `AD-0207` is reported as 1.00 although revenue/spend is slightly below one; its eight running days exclude it under both interpretations. A complete independent recomputed-ROAS filter agrees with the final total. All reported ROAS values are within 0.005 of revenue/spend.

The official page does not prescribe policies for malformed rows or duplicate IDs. The engine preserves evidence, quarantines invalid rows and all conflicting-ID rows, and quarantines identical repeats after the first. Any such anomaly **blocks publication of a final answer**. Distinct legitimate IDs are not deduplicated just because some metrics coincide. This is an explicit implementation safeguard, not a fabricated official rule.

`scripts/independent.mjs` starts again from the original JSON, preserves numeric lexemes as strings and independently evaluates predicates using BigInt integer cents. It compares record count, duplicate counts, qualifying IDs, per-platform counts and amounts, and grand total with the Python calculation. It rejects more than two decimal places in monetary inputs rather than silently rounding.

## Evidence and exports

`artifacts/results/` and `public/reports/` contain the summary, category breakdown, all 800 record results, reconciliation ledger, malformed and duplicate reports, independent validation, and CSV export. Every record preserves its original source fields, source array index/JSON pointer, all three boolean checks, exact contribution, display contribution and inclusion/exclusion explanation. Invoice-only fields are null with an explicit applicability note.

The app provides a searchable, filterable, sortable and paginated explorer, keyboard-accessible record dialogs, platform breakdown, methodology, dataset provenance, creative insights and downloadable evidence. Global totals remain unchanged when explorer filters change.

## Creative insights

Rank by weighted ROAS = aggregate revenue / aggregate spend (not average ad ROAS), with deterministic label tie breaks. This ranking definition is an implementation choice; the official page does not specify one.

- Lowest platform-audience groups: Meta / M 18–24 (66.64×), YouTube / M 18–24 (67.17×), Google / F 25–34 (67.85×).
- Highest creative themes: Doctor Trust (122.51×), Lifestyle (110.08×), Product Demo (105.95×).

The synthetic dataset has unusually high aggregate returns. Relative low ranking is not equivalent to loss-making. Review still-active flagged ads first and test incremental budget in stronger themes; do not assume historical waste is recoverable or that average ROAS guarantees causal lift.

## Tests

`npm test` runs Python unit/regression tests and Node tests. Edge tests use deliberately mutated copies of official records, isolated from the production pipeline. They cover all eight threshold combinations, strict boundaries, each platform partition, repeated identical records, conflicting IDs, every missing field, malformed/non-finite/negative values, nullable video completion, zero spend/revenue, break-even, exact decimals, rounding, reconciliation and official-file integrity.

Real browser and HTTP evidence is recorded in `artifacts/qa/`; the final status and remaining limitations are documented in `artifacts/submission/deployment-notes.md` and `docs/validation.md`. Do not interpret configuration files or an expected URL as proof of a deployment.

## Deployment

The build is a static `dist/` directory. Vercel and Netlify configuration files are included; Cloudflare Pages can use `npm run build` and output directory `dist`. These deployment targets require an authenticated account. No secrets belong in this repository.

Sites hosting is prepared with `.openai/hosting.json`. `python scripts/prepare_deployment.py` packages only validated build output and its hosting manifest into `artifacts/deploy/site.tar.gz`, without destructive cleanup. A source commit must be pushed to the registered Sites repository before saving and publishing that exact version. Public access and HTTP checks are required before reporting success. The actual URL and hosting result are recorded in deployment notes.

The public GitHub repository is [Ajayyy00/mosaic-adlens](https://github.com/Ajayyy00/mosaic-adlens). Anonymous Git access verified the deployed source commit, and `npm ci` followed by `npm run check` passed in a clean checkout. No application is submitted by any script.

## Demo

The narrated demo artifacts are in `artifacts/demo/`: `demo.mp4`, `demo.srt`, and `transcript.txt`. The MP4 is publicly hosted at the demo link above; [captions](https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site/demo/demo.srt) and [transcript](https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site/demo/transcript.txt) are also public. Video rendering additionally needs `edge-tts`, `Pillow`, and `imageio-ffmpeg`. Real browser screenshots are the visual source and must be recaptured to render from a fresh checkout. See `scripts/make_demo.py` and `artifacts/demo/validation.json` for actual validation results. Generated audio/video and temporary capture files are ignored by Git. `python scripts/http_check.py` verifies deployed reports and pinned media hashes without requiring a local MP4.

## Project structure

```text
frontend/           React + TypeScript application and CSS
engine/             Python Decimal audit engine
data/               Original official JSON and provenance manifest
tests/              Python and JavaScript validation tests
scripts/            Acquisition, independent verification, packaging, demo
public/reports/     Static downloadable reports consumed by the UI
artifacts/results/  Machine-readable processing outputs
artifacts/qa/       Browser screenshots and verification evidence
artifacts/demo/     Narrated video, captions, transcript, validation
artifacts/submission/ Written submission materials (no personal information)
docs/               Official requirements and validation record
```

## Limits

This is an offline analysis of a fixed official synthetic dataset, not a live ad account integration. The ROAS interpretation, unspecified ranking metric, and anomaly safeguards are disclosed above. The private answer key is unavailable. Deployment/GitHub status must be taken from verified deployment notes, not inferred. No CV, credentials, private files or application submission is included.
