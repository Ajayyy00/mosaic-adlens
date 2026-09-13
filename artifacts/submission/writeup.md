# Adlens: making wasted ad spend auditable

Adlens solves Mosaic’s Content & Creative challenge by processing all 800 records in the official content_ads.json file. It identifies ads with ROAS below 1.0, spend above ₹5,000, and more than 14 running days, then sums their full spend exactly once.

The result is ₹14,75,731.79 across 13 ads. Instagram contributes ₹5,76,898.53; Google ₹4,29,321.93; YouTube ₹3,25,750.71; and Meta ₹1,43,760.62. These mutually exclusive platform totals reconcile exactly. Wasted spend is approximately 1.89% of total dataset spend.

Python parses monetary values directly into Decimal. A separate JavaScript implementation independently reads the original JSON and calculates with BigInt integer cents. Both implementations agree on all qualifying IDs, platform counts, amounts and the grand total. Automated tests cover strict boundaries, overlapping checks, duplicates, conflicting IDs, missing fields, malformed values, zero values, precision and rounding. The source is preserved with its URL, download timestamp and SHA-256.

There are no malformed records or duplicate IDs in the official file. One rounded ROAS value crosses the 1.0 boundary when recomputed, but that ad ran only eight days. Both interpretations therefore produce the same answer. The official page specifies two decimal places without a tie-breaking mode; all monetary inputs already use cents, so alternate rounding conventions agree here.

The React application makes the result reviewable: filter by platform, audience and creative theme, search an ad ID, sort performance, open record evidence, and download JSON or CSV. Each record explains all three threshold checks and why its spend does or does not contribute. Historical paused and completed ads remain eligible under the official rule.

For the requested insights, I rank groups by spend-weighted ROAS. Meta targeting men aged 18–24 ranks lowest, followed by YouTube targeting the same audience and Google targeting women aged 25–34. Doctor Trust, Lifestyle and Product Demo rank highest among creative themes. These are relative rankings: the synthetic data has unusually high aggregate returns, and strong themes still contain individual losing ads.

I would review the five still-active flagged ads first, revise or pause ineffective creatives, then test incremental budget in stronger themes. I would not treat historical waste as recoverable cash or assume group averages prove future lift. Separating the deterministic engine from the interface keeps the answer reproducible and every rupee traceable.
