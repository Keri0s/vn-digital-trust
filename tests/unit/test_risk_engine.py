"""Production RM module against frozen synthetic expectations, not CRM evidence."""
import json,unittest
from pathlib import Path
from dataclasses import replace
from vdt.risk import FactorInput,PathInput,RiskInput,evaluate_risk,compare_impact,ImpactSnapshot,ComparisonContext,IMPACTS
BASE=Path(__file__).resolve().parents[2]/'docs/planning/verification'
MF=json.loads((BASE/'risk-method-fixtures-v0.4.json').read_text(encoding='utf-8-sig'))
IP=json.loads((BASE/'impact-progress-fixtures-v0.1.json').read_text(encoding='utf-8-sig'))
def norm(v):
 if isinstance(v,tuple):return [norm(x) for x in v]
 if hasattr(v,'items'):return {k:norm(x) for k,x in v.items()}
 return v
def make_risk(c):
 bounds=c.get('evidence_bound_constraints',{})
 factors={k:FactorInput(v,tuple(bounds.get(k,(1,5))),k not in c.get('unconfirmed_factors',[]),k in bounds and k not in c.get('unconfirmed_bounds',[])) for k,v in c['factors'].items()}
 paths=None
 if 'paths' in c:
  paths=tuple(PathInput(p['path_id'],p['coverage'],p.get('g'),tuple(p.get('bounds',(1,5))),p['coverage']!='UNKNOWN',p.get('bounds_confirmed',False)) for p in c['paths'])
 return evaluate_risk(RiskInput(factors,paths,essential_context_complete=c.get('essential_context_complete',True),path_inventory_complete=c.get('path_inventory_complete',True)))
class RiskFixtureTests(unittest.TestCase):
 def test_bool_is_not_an_ordinal(self):
  c=dict(MF['cases'][0]);c['factors']=dict(c['factors'],E=True)
  r=make_risk(c);self.assertIsNone(r.R25_range);self.assertEqual(r.status,'NEEDS_REVIEW')
 def test_disagreement_preserves_determined_score_and_review(self):
  f={k:FactorInput(v,confirmed=True) for k,v in zip(('E','F','G')+IMPACTS,(1,1,2,3,2,1,1))}
  r=evaluate_risk(RiskInput(f,unresolved_reviewer_disagreement=True))
  self.assertTrue(r.score_determined);self.assertEqual(r.score,'3');self.assertEqual(r.status,'NEEDS_REVIEW')
def risk_case(c):
 def test(self):
  r=make_risk(c)
  for k in ['status','score','score_range','R25','R25_range','raw_level','risk_level','level_range','raw_level_range','impact_gate_reason','score_determined','display_score','display_score_range']:
   if k in c['expected']:self.assertEqual(norm(getattr(r,k)),c['expected'][k],c['id']+'.'+k)
  for k in ['missing_factors','missing_paths']:
   if k in c['expected']:self.assertEqual(sorted(getattr(r,k)),sorted(c['expected'][k]),c['id']+'.'+k)
 return test
for c in MF['cases']:setattr(RiskFixtureTests,'test_'+c['id'].replace('-','_'),risk_case(c))
def impact_case(raw):
 def test(self):
  c=dict(IP['case_defaults'],**raw);b=IP['baseline'];beforevalues=c.get('before_impact_override',b['impact'])
  beforeverified=c.get('before_verified_dimensions_override',b['verified_dimensions'])
  def snap(sid,context,values,verified,disputed,efg,status):
   impacts={k:FactorInput(v,confirmed=k in verified,disputed=k in disputed) for k,v in zip(IMPACTS,values)}
   f=dict(impacts,**{k:FactorInput(v,confirmed=v is not None) for k,v in zip(('E','F','G'),efg)})
   risk=evaluate_risk(RiskInput(f))
   return ImpactSnapshot(sid,ComparisonContext(**context),impacts,risk,status)
  before=snap(b['snapshot_id'],b['context'],beforevalues,beforeverified,[],b['EFG'],c['assessment_status_before'])
  after=snap(c['snapshot_id'],dict(b['context'],**c['context_overrides']),c['after_impact'],c['after_verified_dimensions'],c['after_disputed_dimensions'],c.get('EFG_override',b['EFG']),c['assessment_status_after'])
  r=compare_impact(before,after,treatment_link_confirmed=c['treatment_link_confirmed'],treatment_evidence_ids=[c['treatment_evidence_id']] if c.get('treatment_evidence_id') else [])
  for k,v in c['expected'].items():
   attr={'overall':'impact_progress','score_change':'R_progress'}.get(k,k)
   actual=getattr(r,attr)
   if k.startswith('impact_summary_'):
    actual={field:norm(getattr(actual,field)) for field in v}
   # Legacy score_change conflates incompatible context with unresolved score.
   # OpenAPI R_progress explicitly distinguishes UNDETERMINED for comparable ranges.
   if k=='score_change' and v=='NOT_COMPARABLE' and r.comparability=='COMPARABLE':
    self.assertEqual(actual,'UNDETERMINED',c['id']);continue
   self.assertEqual(norm(actual),v,c['id']+'.'+k)
  self.assertEqual(r.assessment_status_before,c['assessment_status_before'])
  self.assertEqual(r.assessment_status_after,c['assessment_status_after'])
 return test
for c in IP['cases']:setattr(RiskFixtureTests,'test_'+c['id'].replace('-','_'),impact_case(c))
