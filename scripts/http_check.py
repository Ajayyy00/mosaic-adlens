"""Anonymous production checks: no cookies, credentials or browser session."""
import csv
import io
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
BASE=sys.argv[1] if len(sys.argv)>1 else 'https://mosaic-adlens-audit.ochre-deer-1487.chatgpt.site'
checks=[]
def get(path):
    try:
        with urlopen(Request(BASE+path,headers={'User-Agent':'Adlens-Anonymous-Verification/1.0'}),timeout=45) as response:
            body=response.read()
            item={'path':path,'status':response.status,'bytes':len(body),'content_type':response.headers.get('Content-Type'),
                  'final_url':response.url,'anonymous':True}
    except HTTPError as error:
        body=error.read(); item={'path':path,'status':error.code,'bytes':len(body),'anonymous':True}
    checks.append(item)
    return item,body

home,html=get('/')
assert home['status']==200 and b'id="root"' in html
assert 'auth' not in home['final_url']
for asset in re.findall(r'(?:src|href)="(/assets/[^\"]+)"',html.decode()):
    status,_=get(asset); assert status['status']==200
for filename in ['final-result.json','record-results.json','category-breakdown.json','reconciliation.json',
                 'independent-validation.json','malformed-records.json','duplicate-records.json']:
    status,body=get('/reports/'+filename); assert status['status']==200
    data=json.loads(body)
    if filename=='final-result.json':assert data['answer']=='1475731.79' and data['records_processed']==800
    if filename=='record-results.json':assert len(data)==800 and sum(x['contributes'] for x in data)==13
    if filename=='reconciliation.json':assert data['status']=='PASS' and data['total']=='1475731.79'
status,body=get('/reports/record-results.csv'); assert status['status']==200
assert len(list(csv.DictReader(io.StringIO(body.decode()))))==800
status,_=get('/favicon.svg'); assert status['status']==200
missing,missing_body=get('/reports/nonexistent-report.json')
assert missing['status']==404 or (missing['status']==200 and b'id="root"' in missing_body), 'Unknown path returned unexpected content'
missing['behavior']='HTTP 404' if missing['status']==404 else 'Static host SPA fallback: HTML app shell, not a JSON report'
media_hashes={
    'demo.mp4':'2ec56503d093bd26ce4ab299867a57bef95e6bd78322508018335d6c7422314d',
    'demo.srt':'60a5afee5ec6141141db80168ff8a8df5061b5c6e50f322edf1200bc47f73443',
    'transcript.txt':'22a1ef5a4034f775ed44f8aff3084a9d48ab9097de9261ec28237fd80ee954ea',
}
for media,expected_hash in media_hashes.items():
    status,body=get('/demo/'+media)
    status['sha256']=hashlib.sha256(body).hexdigest()
    assert status['status']==200 and status['sha256']==expected_hash
    status['matches_pinned_hash']=True
    local=ROOT/'public/demo'/media
    if local.exists():
        assert body==local.read_bytes()
        status['matches_local']=True
report={'checked_at':datetime.now(timezone.utc).isoformat(),'base_url':BASE,'status':'PASS','checks':checks,
        'routes':'The five UI views use URL fragments and are verified in real browser QA.'}
(ROOT/'artifacts/qa').mkdir(exist_ok=True,parents=True)
(ROOT/'artifacts/qa/http-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
