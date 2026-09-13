import json,itertools,collections
from pathlib import Path
import numpy as np
from scoring_b62 import score
P=Path(__file__).resolve().parent;GROUPS=[f'G{i:02}' for i in range(1,25)];DRAWS=np.random.default_rng(630913).integers(0,24,(10000,24))
def metric(values):
 a=np.array(values,dtype=float);assert a.shape==(24,2);mid=a.mean(axis=0);boot=a[DRAWS].mean(axis=1);loo=np.array([np.delete(a,i,axis=0).mean(axis=0) for i in range(24)])
 return dict(lower=float(mid[0]),upper=float(mid[1]),ci_lower=float(np.quantile(boot[:,0],.025)),ci_upper=float(np.quantile(boot[:,1],.975)),loo_lower_min=float(loo[:,0].min()),loo_upper_min=float(loo[:,1].min()),groups=[dict(group_id=g,lower=float(v[0]),upper=float(v[1])) for g,v in zip(GROUPS,a)],leave_one=[dict(omitted=g,lower=float(v[0]),upper=float(v[1])) for g,v in zip(GROUPS,loo)])
def analyze(refs,outputs):
 results={r['call_id']:r for r in outputs};assert len(results)==len(outputs)==len(refs)==4656;sc=[]
 for r in refs:
  raw=results[r['call_id']];s=score(raw['generated_text'],dict(r,arm='J_UA',format_arm='JSON'));a=s['answer'];c='C' if s['score']=='C' else 'R' if a=={'actor':r['gold']['undergoer'],'undergoer':r['gold']['actor']} else 'U' if s['score']=='U' else 'OTHER_W';bg=r.get('background_gold');detail=c
  if c=='OTHER_W':detail='BG_C' if bg and a==bg else 'BG_R' if bg and a=={'actor':bg['undergoer'],'undergoer':bg['actor']} else 'MIXED_OTHER_W'
  sc.append(dict(**r,**{k:v for k,v in raw.items() if k not in r},assessment=s,content=c,detail=detail,answer=a,C_lower=int(c=='C'),C_upper=int(c in ['C','U']),E_lower=int(detail in ['BG_C','BG_R']),E_upper=int(detail in ['BG_C','BG_R','U'])))
 new=[r for r in sc if r['material_set']!='BRIDGE'];idx={(r['model'],r['group_id'],r['R1_frame'],r['construction'],r['schema'],r['background'],r['material_set'],r['condition']):r for r in new};assert len(idx)==4608
 pairs=[]
 for m,g,f,t,s,c in itertools.product(['qwen','apertus'],GROUPS,['A','B'],['BA','BEI'],['AU','UA'],['ZERO','ORIGINAL_A','ABLATION_B']):
  for kind in ['BACKGROUND','NONE']:
   keys=[(bg,'MAIN_BACKGROUND') for bg in ['BA','BEI']] if kind=='BACKGROUND' else [('NONE',k) for k in ['NONE_ORIGINAL','NONE_SWAPPED']];a,b=[idx[m,g,f,t,s,bg,k,c] for bg,k in keys];same=a['answer'] is not None and a['answer']==b['answer'];pairs.append(dict(model=m,group_id=g,frame=f,construction=t,schema=s,condition=c,kind=kind,left_id=a['call_id'],right_id=b['call_id'],lower=a['C_lower']*b['C_lower'],upper=a['C_upper']*b['C_upper'],mapping_equal=same,both_known_wrong=a['content'] not in ['C','U'] and b['content'] not in ['C','U']))
 stats=[];primaryA={};pvalues={}
 for m,f,c,kind in itertools.product(['qwen','apertus'],['A','B'],['ZERO','ORIGINAL_A','ABLATION_B'],['BACKGROUND','NONE']):
  for layer in ['MAIN','BA_AU','BA_UA','BEI_AU','BEI_UA']:
   rr=[r for r in pairs if (r['model'],r['frame'],r['condition'],r['kind'])==(m,f,c,kind) and ((r['construction'],r['schema']) in [('BA','UA'),('BEI','AU')] if layer=='MAIN' else r['construction']+'_'+r['schema']==layer)];v=np.array([[np.mean([r[k] for r in rr if r['group_id']==g]) for k in ['lower','upper']] for g in GROUPS]);pvalues[m,f,c,kind,layer]=v;stats.append(dict(model=m,frame=f,condition=c,kind=kind,layer=layer,n_pairs=len(rr),**metric(v)))
 for f in ['A','B']:
  z=pvalues['qwen',f,'ZERO','BACKGROUND','MAIN'];d=pvalues['qwen',f,'ORIGINAL_A','BACKGROUND','MAIN'];v=np.column_stack([d[:,0]-z[:,1],d[:,1]-z[:,0]]);st=metric(v);st['ceiling_limited']=float(z[:,0].mean())>.95;st['passes']=st['lower']>=.05 and st['loo_lower_min']>0 and st['ci_lower']>0 and not st['ceiling_limited'];primaryA[f]=st
 def ev(m,c,f):return np.array([[np.mean([r[k] for r in new if r['model']==m and r['group_id']==g and r['condition']==c and r['R1_frame']==f and r['material_set']=='MAIN_BACKGROUND']) for k in ['E_lower','E_upper']] for g in GROUPS])
 def sub(a,b):return np.column_stack([a[:,0]-b[:,1],a[:,1]-b[:,0]])
 interactions={};E=[]
 for m in ['qwen','apertus']:
  v={(c,f):ev(m,c,f) for c,f in itertools.product(['ZERO','ORIGINAL_A','ABLATION_B'],['A','B'])}
  for (c,f),a in v.items():E.append(dict(model=m,condition=c,R1_frame=f,R2_frame='B' if f=='A' else 'A',**metric(a)))
  da=sub(sub(v['ORIGINAL_A','B'],v['ZERO','B']),sub(v['ORIGINAL_A','A'],v['ZERO','A']));db=sub(sub(v['ABLATION_B','A'],v['ZERO','A']),sub(v['ABLATION_B','B'],v['ZERO','B']));F=.5*(sub(v['ORIGINAL_A','B'],v['ORIGINAL_A','A'])+sub(v['ABLATION_B','A'],v['ABLATION_B','B']));st=metric(F);st.update(direction_A=metric(da),direction_B=metric(db));st['label']='FRAME_MATCH_PATTERN' if st['lower']>=.05 and st['ci_lower']>0 and st['loo_lower_min']>0 and st['direction_A']['lower']>0 and st['direction_B']['lower']>0 else 'INCONCLUSIVE';interactions[m]=st
 transitions=[]
 for r in new:
  if r['condition']=='ZERO':continue
  z=idx[r['model'],r['group_id'],r['R1_frame'],r['construction'],r['schema'],r['background'],r['material_set'],'ZERO'];transitions.append(dict(model=r['model'],condition=r['condition'],group_id=r['group_id'],left_id=z['call_id'],right_id=r['call_id'],before=z['detail'],after=r['detail'],rescue=z['content'] not in ['C','U'] and r['content']=='C',harm=z['content']=='C' and r['content'] not in ['C','U'],unresolved='U' in [z['content'],r['content']]))
 counts=[]
 for m,c,f,kind in itertools.product(['qwen','apertus'],['ZERO','ORIGINAL_A','ABLATION_B'],['A','B'],['MAIN_BACKGROUND','NONE_ORIGINAL','NONE_SWAPPED']):
  rr=[r for r in new if (r['model'],r['condition'],r['R1_frame'],r['material_set'])==(m,c,f,kind)];ct=collections.Counter(r['detail'] for r in rr);den=ct['C']+ct['R'];counts.append(dict(model=m,condition=c,frame=f,kind=kind,n=len(rr),counts=dict(ct),target_pair_subset_n=den,C_over_target_subset=ct['C']/den if den else None))
 summary=dict(status='COMPLETE_ANALYSIS',started=4656,outputs=4656,primary_A=primaryA,primary_A_label='LOCAL_CROSS_PACKAGE_TRANSFER' if all(x['passes'] for x in primaryA.values()) else 'CEILING_LIMITED' if any(x['ceiling_limited'] for x in primaryA.values()) else 'PARTIAL_OR_INCONCLUSIVE',primary_B=interactions['apertus'],qwen_interaction_boundary=interactions['qwen'],harm_flag='OBSERVED_NEW_HARM' if any(r['harm'] for r in transitions) else 'NO_KNOWN_NEW_HARM',transitions=[dict(model=m,condition=c,rescues=sum(r['rescue'] for r in transitions if r['model']==m and r['condition']==c),harms=sum(r['harm'] for r in transitions if r['model']==m and r['condition']==c),unresolved=sum(r['unresolved'] for r in transitions if r['model']==m and r['condition']==c)) for m,c in itertools.product(['qwen','apertus'],['ORIGINAL_A','ABLATION_B'])],human_review='PENDING',independent_human_gold=0)
 return {'SUMMARY':summary,'SCORED-RESULTS':sc,'ALL-PAIRS':pairs,'STATISTICS':stats,'E-STATISTICS':E,'TRANSITIONS':transitions,'COUNTS':counts}
if __name__=='__main__':
 refs=json.loads((P/'AUTHOR-REFERENCES.json').read_text());outputs=[r for m in ['qwen','apertus'] for r in json.loads((P/f'retrieved/run_{m}/RESULTS.json').read_text())['rows']]
 for n,d in analyze(refs,outputs).items():(P/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2))
