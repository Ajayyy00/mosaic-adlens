# Official requirements and scope resolution

Verified 2026-09-13 by reading https://mosaicfellowship.in/challenge in a browser, selecting **Content & Creative**, and reading https://mosaicfellowship.in/submit without entering information or submitting anything.

## Authoritative problem

**Content & Creative — Ad Performance Intelligence.** The dataset contains 800 ads across Meta, Google, YouTube and Instagram. Identify every ad satisfying **ROAS < 1.0 AND spend > ₹5,000 AND days_running > 14**. Sum the **full spend** on qualifying ads. Report total wasted spend in rupees to two decimal places.

The monetary quantity is neither invoice overcharge nor spend minus revenue. All three conditions are necessary, and their boundaries are strict. The page supplies no status restriction. Completed and paused ads remain eligible. This is a historical dataset; days_running is used as supplied, not recomputed from today's date.

The user's long brief also contains finance-specific requirements. Those are inapplicable to the selected problem: there are no invoices, billed/expected amounts, HSN codes, GST reference, rate card, surcharges, subtotal checks or finance error categories. No finance dataset has been substituted or downloaded.

## Requirement register

| Topic | Verified official requirement or explicit absence |
|---|---|
| Dataset | One JSON file, 800 ad records |
| Exact URL | https://mosaicfellowship.in/data/content_ads.json |
| Download source | Dataset link on selected Content & Creative tab |
| Scored answer | Sum of spend where all three strict predicates pass; 2 decimal places |
| Required checks | ROAS < 1, spend > 5000, days_running > 14 |
| Categories | One scored category: wasted spend; no official mutually exclusive error taxonomy |
| Overlap | Three conjunctive predicates identify a single ad; spend added once. No other precedence rule is published |
| Malformed / missing / duplicate / conflicting rows | No official resolution rule specified; implementation blocks final answer when such records are encountered |
| ROAS recomputation | Page explains revenue/spend and supplies a ROAS field; does not specify handling rounded boundary disagreement. Both interpretations are independently compared |
| Money arithmetic | Page does not mandate an arithmetic library; exact arithmetic is a user requirement and implemented |
| Rounding | Two decimal places; no tie-breaking convention or per-line rounding is specified |
| Optional insight description | Narrative calls worst platform-audience and best theme insights a non-scored bonus |
| Submission checklist | Explicitly asks for top 3 worst platform-audience combinations and top 3 best creative themes; included despite the non-scored label |
| Insight ranking metric | Not specified; aggregate weighted ROAS chosen and disclosed |
| UI | Working app showing ad performance, filterable by platform, audience and creative type |
| Deployment | Live internet app, publicly accessible without sign-up/login, plus public GitHub repository |
| Allowed hosts | Vercel, Netlify, Cloudflare Pages listed as examples of instantly loading hosts |
| Prohibited hosts/tools | Streamlit, Render, Lovable, Emergent |
| AI usage | AI-assisted coding encouraged; process the supplied dataset in code, do not paste it into an LLM to obtain the answer |
| Dataset restrictions | Do not invent replacement/sample data. No explicit raw-file redistribution condition appears on the inspected challenge page; only the challenge synthetic data is included |
| Write-up | Maximum 500 words; explain patterns, approach, design and budget reallocation |
| Form description | Maximum 500 characters |
| Other text limits | No other limits visible in form labels; see captured input attributes below |
| Submission/application | Reviewed on a rolling basis; no fixed deadline shown. Never submit in this task |
| Evaluation | Numerical answer checked programmatically; GitHub/code quality, system design and product thinking reviewed |
| Application timing inconsistency | Page says Fellowship 2026 but its explanatory copy says cohort starts July 2025. Preserve as a page inconsistency; do not infer a current deadline |

## Submission form fields (viewed, never filled)

Full Name; Email; Phone; College; Graduation Year (select); Problem Statement (select); Solution Name; Deployed App URL; Public GitHub Repo URL; Your Numerical Answer (two decimals); Tech Stack; Brief Description (max 500 chars); Demo Video (optional); Notes (optional); CV upload (PDF, DOC, DOCX; max 5MB, marked required); original-work confirmation checkbox; Submit Solution button.

This project contains no personal form responses or CV. The 90–120 second male-narrated, captioned video and the elaborate audit test suite are user requirements, not stated official challenge requirements.

## Observed schema

Root: array of 800 objects, each with 23 fields.

| Fields | Observed type / meaning |
|---|---|
| ad_id | Unique string, AD-0001 through AD-0800 |
| platform | Google, Instagram, Meta, YouTube |
| ad_type | Creative format string |
| brand, category | Brand and product category strings |
| target_audience | Gender and age-band label |
| creative_theme | Theme string |
| status | Active, Paused, Completed |
| start_date | ISO YYYY-MM-DD string |
| days_running | Nonnegative integer, used directly in official predicate |
| impressions, clicks, conversions | Nonnegative integer counts |
| spend, revenue | Nonnegative decimal rupee amounts, at most two decimal places |
| roas | Supplied decimal ratio, at most two decimal places |
| ctr, cpc, cpa | Decimal metrics (CTR is a percentage; CPC/CPA in rupees) |
| creative_score, landing_page_score, frequency | Decimal metrics |
| video_completion_rate | Decimal percentage or null (488 nulls) |

The exact byte count, SHA-256, download timestamp and field names are recorded in `data/manifest.json`. Schema details are observed from the official file, not a separately published formal schema.

## Implementation choices and safeguards

Use supplied ROAS for the official classification. Compare revenue < spend as an independent alternate interpretation. AD-0207 is the sole ROAS boundary disagreement, but its eight days exclude it under either interpretation. All supplied ROAS values agree with revenue/spend within 0.005.

Partition qualifying spend by platform for a disjoint reconciliation. Preserve all three predicate values per row. Quarantine identical repeated rows after the first; quarantine every row of a conflicting ID; block final result for any duplicates or malformed rows because no official resolution policy exists. Do not infer duplicates from two different legitimate ad IDs sharing metrics. Official data has none of these problems.

Retain exact Decimal spend; round only at reporting with ROUND_HALF_UP. Record both exact and formatted contributions. A nonzero category rounding residual blocks the answer rather than concealing it. No residual occurs on the official data. Rank audiences and themes by total revenue / total spend, with deterministic label tie breaks. Rankings are descriptive and do not prove a causal improvement from budget reallocation.

## Additional form inspection
The graduation-year dropdown offers 2025, 2026, 2027 and 2028. The inspected text controls expose no HTML maxlength/min/max attributes; the visible 500-character label remains authoritative. The file input accept attribute lists PDF/DOC/DOCX MIME types. No form values were entered and no original-work checkbox was selected.

