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
- Public GitHub: authenticated browser session verified as Ajayyy00; import preparation underway. Local Git credentials remain unavailable; no new token is created
- Video: validated local MP4, 115.84 seconds, 1920×1080, 30 fps, H.264/AAC, male neural narration and 43 caption cues; public video publication underway

Source publishing uses a short-lived Sites credential as a per-command HTTP header, never saved to source/configuration. The read-only Git export contains only reviewed commit objects, refs and HEAD, with no repository configuration or hooks. No CV, private files or fellowship application is published.
