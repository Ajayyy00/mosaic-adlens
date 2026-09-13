"""Edge tests mutate copies of official rows only; no replacement dataset is created."""
import copy
import hashlib
import unittest
from decimal import Decimal as D
from engine.audit import ROOT, PINNED_SHA, read, audit, rules, validate, money

class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read(ROOT/'data/content_ads.json')
        cls.flagged=next(x for x in cls.rows if all(rules(x).values()))
    def variant(self, **changes):
        row=copy.deepcopy(self.flagged); row.update(changes); return row
    def test_official_completeness(self):
        self.assertEqual(len(self.rows),800)
        self.assertEqual(hashlib.sha256((ROOT/'data/content_ads.json').read_bytes()).hexdigest(),PINNED_SHA)
        self.assertEqual(len({x['ad_id'] for x in self.rows}),800)
    def test_official_schema(self):
        self.assertTrue(all(not validate(x) for x in self.rows))
    def test_official_regression(self):
        result,_,recon,bad,dup=audit(self.rows)
        self.assertEqual(result['answer'],'1475731.79'); self.assertEqual(result['flagged_records'],13)
        self.assertEqual(recon['status'],'PASS'); self.assertEqual(bad,[]); self.assertEqual(dup,[])
    def test_every_platform(self):
        for platform in ('Meta','Google','YouTube','Instagram'):
            result,_,_,_,_=audit([self.variant(platform=platform)])
            category=next(x for x in result['categories'] if x['category']==platform)
            self.assertEqual(category['count'],1); self.assertEqual(category['amount'],money(self.flagged['spend']))
    def test_and_all_eight_combinations(self):
        for roas in (D('.99'),D('1')):
            for spend in (D('5000'),D('5000.01')):
                for days in (14,15):
                    row=self.variant(roas=roas,spend=spend,days_running=days)
                    result,_,_,_,_=audit([row])
                    self.assertEqual(result['flagged_records'],int(roas<1 and spend>5000 and days>14))
    def test_overlap_counts_once_full_spend(self):
        result,records,recon,_,_=audit([self.flagged])
        self.assertEqual(sum(records[0]['checks'].values()),3)
        self.assertEqual(result['answer'],money(self.flagged['spend']))
        self.assertEqual(len(recon['record_contributions']),1)
    def test_identical_repeated_three_times(self):
        result,records,_,_,dup=audit([self.flagged]*3)
        self.assertEqual(result['status'],'BLOCKED'); self.assertIsNone(result['answer'])
        self.assertEqual(len(dup),2); self.assertEqual(sum(x['contributes'] for x in records),1)
    def test_conflicting_id(self):
        result,records,_,_,dup=audit([self.flagged,self.variant(spend=D('7000'))])
        self.assertIsNone(result['answer']); self.assertEqual(sum(x['contributes'] for x in records),0)
        self.assertEqual(dup[0]['kind'],'conflicting_id')
    def test_missing_every_field(self):
        for field in self.flagged:
            row=copy.deepcopy(self.flagged); del row[field]
            result,_,_,bad,_=audit([row]); self.assertIsNone(result['answer']); self.assertEqual(len(bad),1)
    def test_malformed_values(self):
        for field,value in [('spend','oops'),('spend',D('NaN')),('spend',D('Infinity')),('roas',None),
                            ('days_running',D('14.5')),('spend',True),('start_date','2025-02-30'),('ad_id','')]:
            self.assertTrue(validate(self.variant(**{field:value})),(field,value))
        self.assertTrue(validate(None))
    def test_negative_values(self):
        for key in ('spend','revenue','roas','days_running'):
            self.assertTrue(validate(self.variant(**{key:-1})))
    def test_zero_revenue_qualifies(self):
        self.assertEqual(audit([self.variant(revenue=D('0'),roas=D('0'))])[0]['flagged_records'],1)
    def test_break_even_zero_difference(self):
        self.assertEqual(audit([self.variant(revenue=self.flagged['spend'],roas=D('1'))])[0]['flagged_records'],0)
    def test_zero_spend(self):
        self.assertEqual(audit([self.variant(spend=0)])[0]['answer'],'0.00')
    def test_decimal_exact(self):
        self.assertEqual(D('.1')+D('.2'),D('.3'))
        self.assertEqual(audit([self.variant(spend=D('5000.01'))])[0]['answer'],'5000.01')
    def test_half_up_rounding(self):
        self.assertEqual(money(D('1.005')),'1.01'); self.assertEqual(money(D('1.0049')),'1.00')
        self.assertEqual(money(D('-1.005')),'-1.01')
    def test_precision_no_early_total_rounding(self):
        rows=[self.variant(spend=D('5000.004'),ad_id='precision-a'),self.variant(spend=D('5000.004'),ad_id='precision-b')]
        result,_,recon,_,_=audit(rows)
        self.assertEqual(result['exact_answer'],'10000.008'); self.assertEqual(result['answer'],'10000.01')
        self.assertEqual(recon['exact_total'],'10000.008')
    def test_reconciliation_categories_records(self):
        result,records,recon,_,_=audit(self.rows)
        self.assertEqual(sum(D(c['amount']) for c in result['categories']),D(result['answer']))
        self.assertEqual(sum(D(r['contribution']) for r in records),D(result['answer']))
        self.assertEqual(len({x['ad_id'] for x in recon['record_contributions']}),13)
    def test_rounding_boundary_warning(self):
        warnings=audit(self.rows)[0]['warnings']
        warning=next(x for x in warnings if x['ad_id']=='AD-0207')
        self.assertFalse(warning['changes_final_classification'])
    def test_nullable_video(self):
        self.assertEqual(validate(self.variant(video_completion_rate=None)),[])
    def test_status_not_an_extra_filter(self):
        for status in ('Active','Paused','Completed'):
            self.assertEqual(audit([self.variant(status=status)])[0]['flagged_records'],1)

if __name__=='__main__': unittest.main()
