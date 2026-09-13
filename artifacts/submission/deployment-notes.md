# Deployment notes

The application is publicly deployed and anonymously verified.

- Actual host: OpenAI Sites, with Cloudflare-managed static hosting
- Production URL: https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site
- Initial successful deployment: 2026-09-13 09:25 UTC
- Public access: verified via independent HTTP requests without credentials/cookies and real browser navigation
- Major views: overview, explorer, insights, methodology and downloads; fragment routes on one static entrypoint
- Reports: all seven JSON files and the complete 800-record CSV returned HTTP 200 and correct content
- Missing-path behavior: this static host serves the HTML application shell with HTTP 200; it does not return fabricated report JSON. The application catches failed JSON loads and displays an error state

- Build: `npm run build`
- Output: `dist/`
- Local preview: `npm run dev`
- Package: `python scripts/prepare_deployment.py`
- Runtime environment variables: none
- Public GitHub: https://github.com/Ajayyy00/mosaic-adlens — repository is Public; anonymous Git access confirmed deployed commit `8dc74df87eaeb5ccf0e4a8257ba2c94dcfd43a86`. Default branch: `codex/mosaic-adlens`. Later documentation-only updates do not change the deployed frontend.
- Video: https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site/demo/demo.mp4 — validated MP4, 115.84 seconds, 1920×1080, 30 fps, H.264/AAC, male neural narration and 43 caption cues. Public MP4, SRT and transcript match the local artifacts byte for byte.
- Final app deployment: succeeded 2026-09-13 09:39 UTC, source commit `8dc74df87eaeb5ccf0e4a8257ba2c94dcfd43a86`.
- Clean checkout: `npm ci` and `npm run check` passed on 2026-09-13; 24 tests, independent reconciliation, lint, typecheck and production build succeeded.

Source publishing uses a short-lived Sites credential as a per-command HTTP header, never saved to source/configuration. The read-only Git export contains only reviewed commit objects, refs and HEAD, with no repository configuration or hooks. No CV, private files or fellowship application is published.
