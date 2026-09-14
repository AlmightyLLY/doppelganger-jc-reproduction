import json,collections,numpy as np
from pathlib import Path
from score_adapter import score_record
from analysis_core import summarize
P=Path(__file__).resolve().parent
read=lambda n:json.loads((P/(n+'.json')).read_text())
def save(n,x):(P/(n+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 refs=read('AUTHOR-REFERENCES');out=[]
 for m in ['qwen','apertus']:out+=read(f'retrieved/run_{m}/RESULTS')['rows']
 raw={r['call_id']:r for r in out};assert len(raw)==len(out)==len(refs)==4640
 scored=[]
 for r in refs:
  o=raw[r['call_id']];assert o['messages']==r['messages'];s=score_record(o['generated_text'],r);a=s['answer'];g=r['gold'];b=r['background_gold'];rev=lambda x:{'actor':x['undergoer'],'undergoer':x['actor']}
  detail='C' if s['score']=='C' else 'R1_REVERSE' if a==rev(g) else 'U' if s['score']=='U' else 'BG_C' if b and a==b else 'BG_R' if b and a==rev(b) else 'MIXED_OTHER_W'
  scored.append(dict(r,raw_output=o,assessment=s,detail=detail,name_boundary=('罗蕾拉' in o['generated_text'] and r.get('unit_id')=='M65-G05')))
 idx={r['call_id']:r for r in scored};trans={}
 for kind,ps in read('PAIR-MAPS').items():
  ts=[]
  for p in ps:
   a,b=idx[p['before_id']],idx[p['after_id']];aa,bb=a['assessment'],b['assessment'];ts.append(dict(p,before_detail=a['detail'],after_detail=b['detail'],before_C=int(a['detail']=='C'),after_C=int(b['detail']=='C'),delta_C=int(b['detail']=='C')-int(a['detail']=='C'),both_C=int(a['detail']==b['detail']=='C'),mapping_equal=int(aa['answer'] is not None and aa['answer']==bb['answer']),both_wrong=int(aa['score']==bb['score']=='W'),rescue=int(a['detail']!='C' and b['detail']=='C'),harm=int(a['detail']=='C' and b['detail']!='C'),U_involved=int(a['detail']=='U' or b['detail']=='U')))
  trans[kind]=ts
 groups=[];stats={};cells=[];strata={}
 for model in ['qwen','apertus']:
  arrays={}
  for cohort in ['M63','M65']:
   arr=[]
   for i in range(1,25):
    unit=f'{cohort}-G{i:02d}';v=[]
    for pres in ['FO_LO','FO_LN','FN_LO','FN_LN']:
     pp=[p for p in trans['BACKGROUND'] if p['model']==model and p['unit_id']==unit and 'F'+p['frame_render']+'_L'+p['local_render']==pres];assert len(pp)==4
     d=sum(p['delta_C'] for p in pp)/4;v.append(d);groups.append(dict(model=model,cohort=cohort,unit_id=unit,presentation=pres,D=d,rescue=sum(p['rescue'] for p in pp),harm=sum(p['harm'] for p in pp)))
    arr.append(v)
   arrays[cohort]=arr
   for pres in ['FO_LO','FO_LN','FN_LO','FN_LN']:
    pp=[p for p in trans['BACKGROUND'] if p['model']==model and p['cohort']==cohort and 'F'+p['frame_render']+'_L'+p['local_render']==pres];assert len(pp)==96
    cells.append(dict(model=model,cohort=cohort,presentation=pres,n=96,**{f:sum(p[f] for p in pp) for f in ['before_C','after_C','both_C','mapping_equal','both_wrong','rescue','harm','U_involved']},D=sum(p['delta_C'] for p in pp)/96))
  stats[model]=summarize(arrays['M63'],arrays['M65'])
  strata[model]={}
  for ct in ['BA','BEI']:
   for schema in ['AU','UA']:
    aa=[]
    for co in ['M63','M65']:
     a=[]
     for i in range(1,25):
      row=[]
      for pr in ['FO_LO','FO_LN','FN_LO','FN_LN']:
       pp=[p for p in trans['BACKGROUND'] if p['model']==model and p['unit_id']==f'{co}-G{i:02d}' and 'F'+p['frame_render']+'_L'+p['local_render']==pr and p['construction']==ct and p['schema']==schema];assert len(pp)==1;row.append(pp[0]['delta_C'])
      a.append(row)
     aa.append(a)
    strata[model][ct+'_'+schema]=summarize(*aa)
 hist={}
 for m in ['qwen','apertus']:
  f=P.parent/f'b67_execution_v1/retrieved/run_{m}/RESULTS.json';hist.update({r['call_id']:r for r in json.loads(f.read_text())['rows']})
 drift=[]
 for r in scored:
  hid=r.get('historical_reference_id') if r['material_set']=='SCIENCE' else None
  if hid:
   h=hist[hid];o=r['raw_output'];assert h['messages']==o['messages'];drift.append(dict(call_id=r['call_id'],historical_id=hid,model=r['model'],text_equal=h['generated_text']==o['generated_text'],tokens_equal=h['generated_token_ids']==o['generated_token_ids'],historical_text=h['generated_text'],current_text=o['generated_text']))
 assert len(drift)==2304
 science=[r for r in scored if r['material_set']=='SCIENCE'];assert len(science)==4608
 summary=dict(status='COMPLETE_ANALYSIS',outputs=4640,science=4608,candidate_forwards=0,statistics=stats,cells=cells,history_drift=sum(not(x['text_equal'] and x['tokens_equal']) for x in drift),independent_human_gold=0,personal_review='PENDING',identity='exposed-material developmental record-presentation diagnostic')
 for n,x in [('SUMMARY',summary),('SCORED-RESULTS',scored),('TRANSITIONS',trans),('STATISTICS',stats),('GROUP-CONTRIBUTIONS',groups),('FOUR-CELLS',cells),('STRATA',strata),('HISTORY-DRIFT',drift),('ALL-HARMS',{k:[p for p in ps if p['harm']] for k,ps in trans.items()}),('ALL-UNRESOLVED',[r for r in science if r['detail']=='U'])]:save(n,x)
 print(json.dumps({m:s['estimates']['pooled'] for m,s in stats.items()},ensure_ascii=False))
if __name__=='__main__':main()
