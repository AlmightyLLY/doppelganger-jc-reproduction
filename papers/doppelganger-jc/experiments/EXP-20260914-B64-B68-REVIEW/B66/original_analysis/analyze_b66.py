"""Fixed B66 complete-data analysis. No model calls or data-dependent exclusions."""
from pathlib import Path
import json,collections,itertools,numpy as np
from score_adapter import score_record
from analysis_core import summarize
P=Path(__file__).resolve().parent;R=P.parents[2]
def read(p):return json.loads(p.read_text())
def save(n,x):(P/(n+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 refs=read(P/'AUTHOR-REFERENCES.json');outs=[]
 for m in ['qwen','apertus']:outs+=read(P/f'retrieved/run_{m}/RESULTS.json')['rows']
 raw={r['call_id']:r for r in outs};assert len(raw)==len(outs)==4640
 scored=[]
 for r in refs:
  o=raw[r['call_id']];assert o['messages']==r['messages'];s=score_record(o['generated_text'],r);a=s['answer'];g=r['gold'];b=r['background_gold'];rev=lambda x:{'actor':x['undergoer'],'undergoer':x['actor']}
  kind='C' if s['score']=='C' else 'R1_REVERSE' if a==rev(g) else 'U' if s['score']=='U' else 'BG_C' if b and a==b else 'BG_R' if b and a==rev(b) else 'MIXED_OTHER_W'
  scored.append(dict(r,raw_output=o,assessment=s,detail=kind,name_boundary=('罗蕾拉' in o['generated_text'] and r.get('unit_id')=='M65-G05')))
 science=[r for r in scored if r['material_set']=='SCIENCE'];assert len(science)==4608
 key=lambda r:tuple(r[k] for k in ['model','unit_id','variant','construction','schema'])
 bins=collections.defaultdict(dict)
 for r in science:bins[key(r)][r['background']]=r
 pairs=[];none=[]
 for k,rr in bins.items():
  assert set(rr)=={'BA','BEI','NONE'};t=k[3];ma=rr[t];mi=rr['BEI' if t=='BA' else 'BA'];base=rr['NONE'];a=ma['assessment'];b=mi['assessment'];meta={z:ma[z] for z in ['model','unit_id','material_cohort','source_group_id','package','variant','construction','schema']}
  assert ma['R1']==mi['R1']==base['R1'] and ma['gold']==mi['gold']==base['gold'] and ma['background_gold']==mi['background_gold']
  pairs.append(dict(meta,matched_id=ma['call_id'],mismatched_id=mi['call_id'],none_id=base['call_id'],matched_detail=ma['detail'],mismatched_detail=mi['detail'],matched_C=int(a['score']=='C'),mismatched_C=int(b['score']=='C'),D=int(a['score']=='C')-int(b['score']=='C'),both_C=int(a['score']==b['score']=='C'),mapping_equal=int(a['answer'] is not None and a['answer']==b['answer']),both_wrong=int(a['score']==b['score']=='W'),rescue=int(a['score']=='C' and b['score']!='C'),harm=int(a['score']!='C' and b['score']=='C'),U_involved=int(a['score']=='U' or b['score']=='U')))
  for bg in ['BA','BEI']:
   r=rr[bg];none.append(dict(meta,background=bg,background_id=r['call_id'],none_id=base['call_id'],background_detail=r['detail'],none_detail=base['detail'],delta_C=int(r['detail']=='C')-int(base['detail']=='C'),harm=int(r['detail']!='C' and base['detail']=='C'),rescue=int(r['detail']=='C' and base['detail']!='C')))
 assert len(pairs)==1536 and len(none)==3072
 statistics={};groups=[];cells=[];strata=[]
 for m in ['qwen','apertus']:
  arrays={}
  for co in ['M63','M65']:
   arr=[]
   for i in range(1,25):
    unit=f'{co}-G{i:02d}';v=[]
    for pack in ['OLD','NEW']:
     pp=[p for p in pairs if p['model']==m and p['unit_id']==unit and p['package']==pack];assert len(pp)==8
     d=float(np.mean([p['D'] for p in pp]));v.append(d);groups.append(dict(model=m,unit_id=unit,material_cohort=co,package=pack,D=d,rescue=sum(p['rescue'] for p in pp),harm=sum(p['harm'] for p in pp)))
    arr.append(v)
   arrays[co]=arr
   for pack in ['OLD','NEW']:
    pp=[p for p in pairs if p['model']==m and p['material_cohort']==co and p['package']==pack];assert len(pp)==192
    cells.append(dict(model=m,cohort=co,package=pack,n=192,**{f:sum(p[f] for p in pp) for f in ['matched_C','mismatched_C','both_C','mapping_equal','both_wrong','rescue','harm','U_involved']},D=float(np.mean([p['D'] for p in pp]))))
   for va,ct,sc in itertools.product(['OLD_AB','OLD_BA','NEW_DIRECT','NEW_QUOTED'],['BA','BEI'],['AU','UA']):
    pp=[p for p in pairs if p['model']==m and p['material_cohort']==co and p['variant']==va and p['construction']==ct and p['schema']==sc];assert len(pp)==24
    a=np.array([p['D'] for p in pp]);rng=np.random.default_rng(660914);boot=a[rng.integers(0,24,(10000,24))].mean(1);lo,hi=np.quantile(boot,[.025,.975]);strata.append(dict(model=m,cohort=co,variant=va,construction=ct,schema=sc,n=24,D=float(a.mean()),low=float(lo),high=float(hi),rescue=sum(p['rescue'] for p in pp),harm=sum(p['harm'] for p in pp)))
  statistics[m]=summarize(arrays['M63'],arrays['M65']);statistics[m]['both_expression_contrasts_supported']=all(statistics[m]['estimates'][k]['low']>0 for k in ['E63','E65'])
 history={}
 for co,path in [('M63',R/'research_notes/2026-09-13/b63_execution_v1'),('M65',P.parent/'b65_execution_v1')]:
  h={}
  for m in ['qwen','apertus']:
   f=path/f'retrieved/run_{m}/RESULTS.json'
   if f.exists():h.update({r['call_id']:r for r in read(f)['rows']})
  history[co]=h
 drift=[]
 for r in science:
  hid=r.get('historical_reference_id')
  if not hid:continue
  h=history[r['material_cohort']][hid];o=r['raw_output'];assert h['messages']==o['messages']
  drift.append(dict(call_id=r['call_id'],historical_id=hid,model=r['model'],cohort=r['material_cohort'],text_equal=h['generated_text']==o['generated_text'],tokens_equal=h['generated_token_ids']==o['generated_token_ids'],historical_text=h['generated_text'],current_text=o['generated_text']))
 assert len(drift)==2304
 for n,x in [('SCORED-RESULTS',scored),('PAIRS',pairs),('NONE-COMPARISONS',none),('STATISTICS',statistics),('GROUP-CONTRIBUTIONS',groups),('FOUR-CELLS',cells),('STRATA',strata),('HISTORY-DRIFT',drift),('ALL-HARMS',[p for p in pairs if p['harm']]),('ALL-UNRESOLVED',[r for r in science if r['detail']=='U'])]:save(n,x)
 save('SUMMARY',dict(status='COMPLETE_ANALYSIS',natural_outputs=4640,science_outputs=4608,bridge_outputs=32,candidate_forwards=0,statistics=statistics,cells=cells,history_drift=sum(not(r['text_equal'] and r['tokens_equal']) for r in drift),independent_human_gold=0,personal_review='PENDING',identity='exposed-material development diagnostic'))
 print(json.dumps({'cells':cells,'contrasts':{m:s['estimates'] for m,s in statistics.items()}},ensure_ascii=False))
if __name__=='__main__':main()
