"""Acquire only the dataset linked by the official Content & Creative challenge."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://mosaicfellowship.in/data/content_ads.json'
EXPECTED_SHA = '75560e463afcec73fed96bd4c3a4105ef1772f0f3d7c50a43572e6953e752474'

def main():
    with urlopen(Request(URL, headers={'User-Agent':'Mozilla/5.0 MosaicAudit/1.0'}), timeout=60) as response:
        content = response.read()
    rows = json.loads(content)
    digest = hashlib.sha256(content).hexdigest()
    if not isinstance(rows, list) or len(rows) != 800:
        raise ValueError('Official dataset must contain 800 records; download not saved.')
    if digest != EXPECTED_SHA:
        raise ValueError('Official source changed. Review the new version before updating the pinned hash.')
    target = ROOT / 'data'
    target.mkdir(exist_ok=True)
    (target / 'content_ads.json').write_bytes(content)
    manifest = dict(filename='content_ads.json', source_url=URL,
                    downloaded_at=datetime.now(timezone.utc).isoformat(),
                    bytes=len(content), sha256=digest, row_count=len(rows),
                    fields=list(rows[0]), official_synthetic_data=True)
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
