import json,collections,itertools,numpy as np
from pathlib import Path
from score_adapter import score_record
from analysis_core import summarize,low_headroom
P=Path(__file__).resolve().parent
read=lambda n:json.loads((P/(n+'.json')).read_text())
def save(n,x):(P/(n+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def classify(text,r):
 s=score_record(text,r);a=s['answer'];g=r['gold'];b=r['background_gold'];rev=lambda x:dict(actor=x['undergoer'],undergoer=x['actor'])
 detail='C' if s['score']=='C' else 'R1_REVERSE' if a==rev(g) else 'U' if s['score']=='U' else 'BG_C' if b and a==b else 'BG_R' if b and a==rev(b) else 'MIXED_OTHER_W'
 return dict(assessment=s,detail=detail,H_ROLE_fit=int(a==g),H_COPY_fit=int(a==r.get('H_COPY')) if r.get('H_COPY') else None,copy_role_conflict=r.get('H_COPY')!=g if r.get('H_COPY') else None)
def analyze(scored):
 idx={r['call_id']:r for r in scored};science=[r for r in scored if r['material_set']=='SCIENCE'];assert len(science)==3072
 trans={}
 for kind,ps in read('PAIR-MAPS').items():
  ts=[]
  for p in ps:
   a,b=idx[p['before_id']],idx[p['after_id']];aa,bb=a['assessment'],b['assessment'];ca,cb=int(a['detail']=='C'),int(b['detail']=='C')
   rec=dict(p,before_detail=a['detail'],after_detail=b['detail'],before_C=ca,after_C=cb,delta_C=cb-ca,both_C=ca*cb,mapping_equal=int(aa['answer'] is not None and aa['answer']==bb['answer']),both_wrong=int(aa['score']==bb['score']=='W'),U_involved=int(a['detail']=='U' or b['detail']=='U'))
   if kind=='FIXED_ORDER_FACT_CHANGE':rec['correct_swap']=ca*cb
   else:rec.update(rescue=int(not ca and cb),harm=int(ca and not cb))
   ts.append(rec)
  trans[kind]=ts
 g4=[]
 for g in read('FOUR-MEMBER-MAPS'):
  rr=[idx[c] for c in g['member_ids']];g4.append(dict(g,all_four_correct=int(all(r['detail']=='C' for r in rr)),details=[r['detail'] for r in rr],raw_outputs=[r.get('raw_output',{}).get('generated_text','SYNTHETIC') for r in rr]))
 stats={};group_rows=[];strata=[];copy=[]
 for model in ['qwen','apertus']:
  bg=[p for p in trans['BACKGROUND'] if p['model']==model];none=[p for p in trans['NONE'] if p['model']==model]
  def ds(ps):
   vals=[]
   for local in ['O','N']:
    pp=[p for p in ps if p['local_render']==local];assert pp;vals.append(sum(p['delta_C'] for p in pp)/len(pp))
   return vals
  dd=[];bb=[]
  for i in range(1,17):
   unit=f'V{i:02d}';d=ds([p for p in bg if p['unit_id']==unit]);b=ds([p for p in none if p['unit_id']==unit]);dd.append(d);bb.append(b)
   group_rows.append(dict(model=model,unit_id=unit,D_O=d[0],D_N=d[1],Lambda=d[0]-d[1],background_burden_O=b[0],background_burden_N=b[1],burden_interaction=b[0]-b[1]))
  points={}
  for field,vals in [('direction',['AB','BA']),('scenario_fold',['S1','S2'])]:
   points[field]={}
   for v in vals:
    d=ds([p for p in bg if p[field]==v]);points[field][v]=d[0]-d[1]
  stats[model]=summarize(dd,bb,points['direction'],points['scenario_fold'])
  for ct,sc,lo,bgval in itertools.product(['BA','BEI'],['AU','UA'],['O','N'],['BA','BEI','NONE']):
   rr=[r for r in science if (r['model'],r['construction'],r['schema'],r['local_render'],r['background'])==(model,ct,sc,lo,bgval)];assert len(rr)==64
   strata.append(dict(model=model,construction=ct,schema=sc,local_render=lo,background=bgval,n=64,counts=dict(collections.Counter(r['detail'] for r in rr)),C=sum(r['detail']=='C' for r in rr),H_COPY_fit=sum(r['H_COPY_fit'] for r in rr),H_ROLE_fit=sum(r['H_ROLE_fit'] for r in rr)))
  hc=[x['C'] for x in strata if x['model']==model and x['construction']=='BEI' and x['schema']=='AU' and x['background']!='NONE'];stats[model]['LOW_HEADROOM']=low_headroom(hc);stats[model]['headroom_C_counts']=hc
  for conflict,detail in itertools.product([False,True],['ALL','C','R1_REVERSE','BG_C','BG_R','MIXED_OTHER_W','U']):
   rr=[r for r in science if r['model']==model and r['copy_role_conflict']==conflict and (detail=='ALL' or r['detail']==detail)]
   copy.append(dict(model=model,copy_role_conflict=conflict,detail=detail,n=len(rr),H_COPY_fit=sum(r['H_COPY_fit'] for r in rr),H_ROLE_fit=sum(r['H_ROLE_fit'] for r in rr)))
 return dict(STATISTICS=stats,GROUP_CONTRIBUTIONS=group_rows,STRATA=strata,COPY_FIT=copy,TRANSITIONS=trans,FOUR_MEMBER_RESULTS=g4,ALL_HARMS={k:[p for p in ps if p.get('harm')] for k,ps in trans.items()},ALL_UNRESOLVED=[r for r in science if r['detail']=='U'])
def synthetic():
 refs=[r for r in read('AUTHOR-REFERENCES') if r['material_set']=='SCIENCE'];cases=[]
 for label,pred in [('ROLE','gold'),('COPY','H_COPY')]:
  rows=[dict(r,**classify(json.dumps(r[pred],ensure_ascii=False),r)) for r in refs];a=analyze(rows)
  assert all(s['estimates']['Lambda']['value']==0 for s in a['STATISTICS'].values())
  assert sum(x['all_four_correct'] for x in a['FOUR_MEMBER_RESULTS'])==(768 if pred=='gold' else 0)
  assert sum(x['correct_swap'] for x in a['TRANSITIONS']['FIXED_ORDER_FACT_CHANGE'])==(1536 if pred=='gold' else 0)
  cases.append(dict(case=label,G4_correct=sum(x['all_four_correct'] for x in a['FOUR_MEMBER_RESULTS'])))
 return dict(status='PASS',cases=cases,model_calls=0,synthetic_not_model_outputs=True)
def main():
 refs=read('AUTHOR-REFERENCES');out=[]
 for m in ['qwen','apertus']:out+=read(f'retrieved/run_{m}/RESULTS')['rows']
 raw={r['call_id']:r for r in out};assert len(raw)==len(out)==len(refs)==3104
 scored=[]
 for r in refs:
  o=raw[r['call_id']];assert o['messages']==r['messages'];scored.append(dict(r,raw_output=o,**classify(o['generated_text'],r)))
 result=analyze(scored)
 for n,x in result.items():save(n.replace('_','-'),x)
 save('SCORED-RESULTS',scored);save('SUMMARY',dict(status='COMPLETE_ANALYSIS',outputs=3104,science=3072,candidate_forwards=0,statistics=result['STATISTICS'],independent_human_gold=0,personal_review='PENDING',identity='new event bindings within shared template family; developmental prospective validation'))
 print(json.dumps(result['STATISTICS'],ensure_ascii=False))
if __name__=='__main__':main()
