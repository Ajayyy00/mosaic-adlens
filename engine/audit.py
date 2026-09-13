"""Deterministic ad-spend audit. No binary floating-point monetary arithmetic."""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = Decimal
TEXT = ('ad_id','platform','ad_type','brand','category','target_audience','creative_theme','status','start_date')
INTEGER = ('days_running','impressions','clicks','conversions')
NUMERIC = ('spend','revenue','roas','ctr','cpc','cpa','creative_score','landing_page_score','frequency')
FIELDS = set(TEXT + INTEGER + NUMERIC + ('video_completion_rate',))
PLATFORMS = ('Google','Instagram','Meta','YouTube')
PINNED_SHA = '75560e463afcec73fed96bd4c3a4105ef1772f0f3d7c50a43572e6953e752474'

def money(value):
    return str(D(value).quantize(D('0.01'), rounding=ROUND_HALF_UP))

def encode(value):
    if isinstance(value, D):
        return str(value)
    raise TypeError(type(value).__name__)

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, default=encode, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')

def read(path):
    return json.loads(path.read_text(encoding='utf-8'), parse_float=D,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))

def validate(row):
    if not isinstance(row, dict):
        return ['Record must be an object']
    errors = [f'Missing field: {key}' for key in sorted(FIELDS - row.keys())]
    for key in TEXT:
        if key in row and (not isinstance(row[key], str) or not row[key].strip()):
            errors.append(f'{key}: nonempty text required')
    for key in INTEGER:
        if key in row and (type(row[key]) is not int or row[key] < 0):
            errors.append(f'{key}: nonnegative integer required')
    for key in NUMERIC + ('video_completion_rate',):
        if key not in row or (key == 'video_completion_rate' and row[key] is None):
            continue
        value = row[key]
        if isinstance(value, bool) or not isinstance(value, (int,D)) or not D(value).is_finite() or value < 0:
            errors.append(f'{key}: finite nonnegative exact number required')
    if row.get('platform') not in PLATFORMS:
        errors.append('Unknown platform')
    try:
        date.fromisoformat(row.get('start_date',''))
    except (ValueError,TypeError):
        errors.append('start_date: ISO date required')
    return errors

def rules(row):
    return {'roas_below_one': row['roas'] < 1,
            'spend_above_5000': row['spend'] > 5000,
            'running_over_14_days': row['days_running'] > 14}

def aggregate(rows, keys):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[k] for k in keys)].append(row)
    result = []
    for group, items in groups.items():
        spend = sum((D(x['spend']) for x in items), D(0))
        revenue = sum((D(x['revenue']) for x in items), D(0))
        waste = sum((D(x['spend']) for x in items if x['contributes']), D(0))
        result.append({**dict(zip(keys,group)), 'count':len(items), 'spend':money(spend),
                       'revenue':money(revenue), 'wasted_spend':money(waste),
                       'flagged_count':sum(x['contributes'] for x in items),
                       'weighted_roas':str(revenue/spend) if spend else None})
    return result

def audit(source):
    if not isinstance(source,list):
        raise ValueError('Root must be an array')
    malformed, duplicates, output, warnings = [], [], [], []
    fingerprints, ids = {}, defaultdict(list)
    for index, row in enumerate(source):
        errors = validate(row)
        if errors:
            malformed.append({'source_index':index,'errors':errors,'source':row})
            continue
        fingerprint = json.dumps(row,sort_keys=True,default=encode)
        ids[row['ad_id']].append((index,fingerprint))
        if fingerprint in fingerprints:
            duplicates.append({'source_index':index,'ad_id':row['ad_id'],
                               'kind':'identical','original_index':fingerprints[fingerprint]})
        else:
            fingerprints[fingerprint]=index
    conflicts = {key for key, group in ids.items() if len({x[1] for x in group}) > 1}
    for key in sorted(conflicts):
        duplicates.append({'ad_id':key,'kind':'conflicting_id','source_indices':[x[0] for x in ids[key]]})
    # No official duplicate/malformed policy exists: fail the final-result gate, rather than invent one.
    bad_indices = {x['source_index'] for x in malformed}
    repeat_indices = {x['source_index'] for x in duplicates if x['kind']=='identical'}
    for index,row in enumerate(source):
        if index in bad_indices:
            continue
        checks = rules(row)
        eligible = all(checks.values())
        excluded = index in repeat_indices or row['ad_id'] in conflicts
        contributes = eligible and not excluded
        if row['spend'] and (row['roas'] < 1) != (row['revenue'] < row['spend']):
            warnings.append({'ad_id':row['ad_id'],'kind':'roas_threshold_rounding',
                             'reported_roas':row['roas'], 'computed_roas':D(row['revenue'])/D(row['spend']),
                             'changes_final_classification':bool(row['spend']>5000 and row['days_running']>14)})
        if row['spend'] and abs(D(row['roas'])-D(row['revenue'])/D(row['spend'])) > D('.005'):
            warnings.append({'ad_id':row['ad_id'],'kind':'inconsistent_reported_roas'})
        failed = [key for key,value in checks.items() if not value]
        reason = ('All three strict thresholds pass; full spend counts once in '+row['platform']+'.') if contributes else (
            'Duplicate or conflicting ID quarantined; final answer blocked.' if excluded else 'Excluded: '+', '.join(failed)+'.')
        output.append({**row, 'source_index':index,'source_pointer':f'/'+str(index),
                       'checks':checks,'contributes':contributes,
                       'audit_status':'Quarantined' if excluded else 'Wasted spend' if contributes else 'Not flagged',
                       'contribution':money(row['spend'] if contributes else 0),
                       'exact_contribution':str(row['spend']) if contributes else '0',
                       'explanation':reason,'reconciliation_category':row['platform'] if contributes else None,
                       'billed_amount':None,'expected_amount':None,
                       'metric_note':'Invoice fields do not apply. Contribution is full qualifying ad spend, not spend minus revenue.'})
    # Official money values have <=2 decimals. Retain exact spend for general precision tests.
    exact = sum((D(row['spend']) for row in output if row['contributes']),D(0))
    categories = []
    for platform in PLATFORMS:
        subset=[x for x in output if x['contributes'] and x['platform']==platform]
        subtotal=sum((D(x['spend']) for x in subset),D(0))
        categories.append({'category':platform,'count':len(subset),'amount':money(subtotal),'exact_amount':str(subtotal),
                           'record_ids':[x['ad_id'] for x in subset],
                           'description':'Qualifying wasted spend on '+platform})
    # Report separate applicability counts; never add overlapping threshold totals.
    combinations=Counter(''.join('1' if value else '0' for value in x['checks'].values()) for x in output)
    rounding_residual=D(money(exact))-sum((D(c['amount']) for c in categories),D(0))
    valid=not malformed and not duplicates and rounding_residual==0
    reconciliation={'status':'PASS' if valid else 'BLOCKED', 'official_category':'Wasted spend',
        'presentation_partition':'Platform (mutually exclusive)', 'exact_total':str(exact),'total':money(exact),
        'category_sum':money(sum((D(c['amount']) for c in categories),D(0))),
        'rounding_residual':str(rounding_residual),'count':sum(x['contributes'] for x in output),
        'threshold_order':['roas_below_one','spend_above_5000','running_over_14_days'],
        'threshold_combinations':dict(sorted(combinations.items())),
        'rounding':'Decimal ROUND_HALF_UP at final reporting. Official inputs use at most two decimal places.',
        'duplicate_policy':'Quarantine repeats/conflicting IDs and block final answer; official page supplies no resolution policy.',
        'record_contributions':[{'ad_id':x['ad_id'],'category':x['reconciliation_category'],'amount':str(x['spend']),
                                 'why':x['explanation'],'source_pointer':x['source_pointer']} for x in output if x['contributes']]}
    audiences=aggregate(output,['platform','target_audience'])
    themes=aggregate(output,['creative_theme'])
    rank=lambda x: D(x['weighted_roas']) if x['weighted_roas'] is not None else D('Infinity')
    result={'status':reconciliation['status'],'answer':money(exact) if valid else None,
        'exact_answer':str(exact) if valid else None,'currency':'INR','records_processed':len(source),
        'valid_records':len(output),'flagged_records':sum(x['contributes'] for x in output),
        'malformed_count':len(malformed),'duplicate_count':len(duplicates),
        'total_spend':money(sum((D(x['spend']) for x in output),D(0))),
        'total_revenue':money(sum((D(x['revenue']) for x in output),D(0))),
        'categories':categories, 'rule':'roas < 1.0 AND spend > 5000 AND days_running > 14',
        'rank_method':'Weighted ROAS = sum(revenue) / sum(spend); worst ascending, best descending; labels break ties.',
        'worst_audiences':sorted(audiences,key=lambda x:(rank(x),x['platform'],x['target_audience']))[:3],
        'best_themes':sorted(themes,key=lambda x:(-rank(x),x['creative_theme']))[:3],
        'audience_groups':sorted(audiences,key=lambda x:(rank(x),x['platform'],x['target_audience'])),
        'theme_groups':sorted(themes,key=lambda x:(-rank(x),x['creative_theme'])), 'warnings':warnings}
    return result, output, reconciliation, malformed, duplicates

def main():
    raw=ROOT/'data/content_ads.json'
    digest=hashlib.sha256(raw.read_bytes()).hexdigest()
    if digest != PINNED_SHA:
        raise ValueError('Dataset integrity mismatch. Review official download.')
    with localcontext() as ctx:
        ctx.prec=40
        source=read(raw)
        if len(source)!=800:
            raise ValueError('Dataset incomplete')
        result,records,recon,malformed,duplicates=audit(source)
    manifest=read(ROOT/'data/manifest.json')
    result['dataset']=manifest
    result['generated_at']=datetime.now(timezone.utc).isoformat()
    outputs={'final-result':result,'category-breakdown':result['categories'],'record-results':records,
             'reconciliation':recon,'malformed-records':malformed,'duplicate-records':duplicates}
    for name,value in outputs.items():
        save(ROOT/f'artifacts/results/{name}.json',value)
        save(ROOT/f'public/reports/{name}.json',value)
    csv_fields=['ad_id','platform','target_audience','creative_theme','status','start_date','days_running',
                'spend','revenue','roas','audit_status','contribution','explanation','source_pointer']
    for folder in ('artifacts/results','public/reports'):
        with (ROOT/folder/'record-results.csv').open('w',newline='',encoding='utf-8') as file:
            writer=csv.DictWriter(file,fieldnames=csv_fields,extrasaction='ignore')
            writer.writeheader(); writer.writerows(records)
    print(json.dumps({'answer':result['answer'],'flagged':result['flagged_records'],'categories':result['categories'],
                      'worst':result['worst_audiences'],'best':result['best_themes'],'status':result['status']},default=encode,indent=2))

if __name__=='__main__':
    main()
