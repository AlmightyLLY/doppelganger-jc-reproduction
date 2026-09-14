import json,itertools,collections
from pathlib import Path
import numpy as np
from score_adapter import score_record
from background_bounds import bounds
P=Path(__file__).resolve().parent
GROUPS=[f'G{i:02}' for i in range(1,25)];NONE=GROUPS[::3];CONDS=['ZERO','PAIR_A','PAIR_B']
def metric(values,groups=GROUPS):
 a=np.array(values,float);assert a.shape==(len(groups),2);draw=np.random.default_rng(640914).integers(0,len(groups),(10000,len(groups)));boot=a[draw].mean(1);loo=np.array([np.delete(a,i,0).mean(0) for i in range(len(groups))]);mid=a.mean(0)
 return dict(lower=float(mid[0]),upper=float(mid[1]),ci_lower=float(np.quantile(boot[:,0],.025)),ci_upper=float(np.quantile(boot[:,1],.975)),loo_lower_min=float(loo[:,0].min()),groups=[dict(group_id=g,lower=float(v[0]),upper=float(v[1])) for g,v in zip(groups,a)],leave_one=[dict(omitted=g,lower=float(v[0]),upper=float(v[1])) for g,v in zip(groups,loo)])
def sub(a,b):return np.column_stack([a[:,0]-b[:,1],a[:,1]-b[:,0]])
def analyze(refs,outputs):
 result={x['call_id']:x for x in outputs};assert len(result)==len(outputs)==len(refs)==3120;sc=[]
 for r in refs:
  raw=result[r['call_id']];s=score_record(raw['generated_text'],r);a=s['answer'];c='C' if s['score']=='C' else 'R' if a==dict(actor=r['gold']['undergoer'],undergoer=r['gold']['actor']) else 'U' if s['score']=='U' else 'OTHER_W';bg=r.get('background_gold');detail=c
  if c=='OTHER_W':detail='BG_C' if bg and a==bg else 'BG_R' if bg and a==dict(actor=bg['undergoer'],undergoer=bg['actor']) else 'MIXED_OTHER_W'
  b=bounds(raw['generated_text'],r);sc.append(dict(**r,**{k:v for k,v in raw.items() if k not in r},assessment=s,content=c,detail=detail,answer=a,C_lower=int(c=='C'),C_upper=int(c in ['C','U']),E_observed=b['observed_complete'],E_lower=b['lower'],E_upper=b['upper'],background_evidence=b))
 new=[r for r in sc if r['material_set']!='BRIDGE'];assert len(new)==3072
 idx={(r['model'],r['group_id'],r['R1_frame'],r['construction'],r['schema'],r['background'],r['material_set'],r['condition']):r for r in new};assert len(idx)==3072
 pairs=[]
 for m,g,f,t,s,c in itertools.product(['qwen','apertus'],GROUPS,['A','B'],['BA','BEI'],['AU','UA'],CONDS):
  for kind in ['BACKGROUND','NONE']:
   if kind=='NONE' and g not in NONE:continue
   keys=[(bg,'MAIN_BACKGROUND') for bg in ['BA','BEI']] if kind=='BACKGROUND' else [('NONE',k) for k in ['NONE_ORIGINAL','NONE_SWAPPED']];a,b=[idx[m,g,f,t,s,bg,k,c] for bg,k in keys]
   pairs.append(dict(model=m,group_id=g,frame=f,construction=t,schema=s,condition=c,kind=kind,left_id=a['call_id'],right_id=b['call_id'],lower=a['C_lower']*b['C_lower'],upper=a['C_upper']*b['C_upper'],mapping_equal=a['answer'] is not None and a['answer']==b['answer'],both_known_wrong=a['content'] not in ['C','U'] and b['content'] not in ['C','U']))
 stats=[];E=[];interactions={}
 for m,f,c,kind,layer in itertools.product(['qwen','apertus'],['A','B'],CONDS,['BACKGROUND','NONE'],['ALL','BA_AU','BA_UA','BEI_AU','BEI_UA']):
  rr=[r for r in pairs if (r['model'],r['frame'],r['condition'],r['kind'])==(m,f,c,kind) and (layer=='ALL' or r['construction']+'_'+r['schema']==layer)];gs=GROUPS if kind=='BACKGROUND' else NONE
  stats.append(dict(model=m,frame=f,condition=c,kind=kind,layer=layer,n_pairs=len(rr),mapping_equal_n=sum(r['mapping_equal'] for r in rr),both_known_wrong_n=sum(r['both_known_wrong'] for r in rr),**metric([[np.mean([r[k] for r in rr if r['group_id']==g]) for k in ['lower','upper']] for g in gs],gs)))
 for m in ['qwen','apertus']:
  v={}
  for c,f in itertools.product(CONDS,['A','B']):
   rr=[r for r in new if r['model']==m and r['condition']==c and r['R1_frame']==f and r['material_set']=='MAIN_BACKGROUND'];a=np.array([[np.mean([r[k] for r in rr if r['group_id']==g]) for k in ['E_lower','E_upper']] for g in GROUPS]);v[c,f]=a;E.append(dict(model=m,condition=c,R1_frame=f,R2_frame='B' if f=='A' else 'A',n=len(rr),observed_n=sum(r['E_observed'] for r in rr),observed_rate=np.mean([r['E_observed'] for r in rr]),**metric(a)))
  da=sub(v['PAIR_A','B'],v['PAIR_B','B']);db=sub(v['PAIR_B','A'],v['PAIR_A','A']);d=metric((da+db)/2);d.update(direction_A=metric(da),direction_B=metric(db));d['label']='LOCAL_ASSOCIATION_PATTERN' if d['lower']>=.05 and d['ci_lower']>0 and d['loo_lower_min']>0 and d['direction_A']['lower']>0 and d['direction_B']['lower']>0 else 'INCONCLUSIVE_OR_NOT_SUPPORTED';d['observed_background_n']=sum(r['E_observed'] for r in new if r['model']==m and r['material_set']=='MAIN_BACKGROUND');d['zero_observed_background']=d['observed_background_n']==0;interactions[m]=d
 trans=[]
 for r in new:
  if r['condition']=='ZERO':continue
  z=idx[r['model'],r['group_id'],r['R1_frame'],r['construction'],r['schema'],r['background'],r['material_set'],'ZERO'];trans.append(dict(model=r['model'],condition=r['condition'],group_id=r['group_id'],left_id=z['call_id'],right_id=r['call_id'],before=z['detail'],after=r['detail'],rescue=z['content'] not in ['C','U'] and r['content']=='C',harm=z['content']=='C' and r['content'] not in ['C','U'],unresolved='U' in [z['content'],r['content']]))
 counts=[]
 for m,c,f,kind in itertools.product(['qwen','apertus'],CONDS,['A','B'],['MAIN_BACKGROUND','NONE_ORIGINAL','NONE_SWAPPED']):
  for layer in ['ALL','BA_AU','BA_UA','BEI_AU','BEI_UA']:
   rr=[r for r in new if (r['model'],r['condition'],r['R1_frame'],r['material_set'])==(m,c,f,kind) and (layer=='ALL' or r['construction']+'_'+r['schema']==layer)];ct=collections.Counter(r['detail'] for r in rr);den=ct['C']+ct['R'];counts.append(dict(model=m,condition=c,frame=f,kind=kind,layer=layer,n=len(rr),counts=dict(ct),target_pair_subset_n=den,C_over_target_subset=ct['C']/den if den else None))
 summary=dict(status='COMPLETE_ANALYSIS',outputs=3120,new_outputs=3072,primary_apertus=interactions['apertus'],qwen_boundary=interactions['qwen'],transitions=[dict(model=m,condition=c,rescues=sum(r['rescue'] for r in trans if r['model']==m and r['condition']==c),harms=sum(r['harm'] for r in trans if r['model']==m and r['condition']==c),unresolved=sum(r['unresolved'] for r in trans if r['model']==m and r['condition']==c)) for m,c in itertools.product(['qwen','apertus'],['PAIR_A','PAIR_B'])],human_review='PENDING',independent_human_gold=0)
 return dict(SUMMARY=summary,SCORED_RESULTS=sc,ALL_PAIRS=pairs,STATISTICS=stats,E_STATISTICS=E,TRANSITIONS=trans,COUNTS=counts)
if __name__=='__main__':
 refs=json.loads((P/'AUTHOR-REFERENCES.json').read_text());outs=[r for m in ['qwen','apertus'] for r in json.loads((P/f'retrieved/run_{m}/RESULTS.json').read_text())['rows']]
 for n,d in analyze(refs,outs).items():(P/(n.replace('_','-')+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
