"""CPU-only predeclared paired endpoint; caller supplies frozen scored outputs."""
import numpy as np
from collections import defaultdict
def summarize(pairs,scores):
 groups=defaultdict(list);detail=[]
 for p in pairs:
  a,b=(scores[p[k]] for k in ['matched','mismatched']);ca,cb=(int(s['score']=='C') for s in [a,b]);ua,ub=(int(s['score']=='U') for s in [a,b])
  d=dict(p,delta=ca-cb,lower=ca-(cb+ub),upper=ca+ua-cb,rescue=int(ca and not cb),harm=int(cb and not ca),both_correct=ca*cb,both_known_wrong=int(a['score']=='W' and b['score']=='W'),mapping_equal=a.get('answer') is not None and a.get('answer')==b.get('answer'),unknown=bool(ua or ub))
  groups[p['group_id']].append(d);detail.append(d)
 keys=['delta','lower','upper'];v=np.array([[np.mean([r[k] for r in g]) for k in keys] for _,g in sorted(groups.items())]);n=len(v);rng=np.random.default_rng(650914);boot=v[rng.integers(0,n,(10000,n))].mean(axis=1)
 ci=np.quantile(boot[:,0],[.025,.975]).tolist();bounds=[float(np.quantile(boot[:,1],.025)),float(np.quantile(boot[:,2],.975))]
 label=lambda c:'SUPPORTED' if c[0]>0 else 'REVERSED' if c[1]<0 else 'INCONCLUSIVE'
 return dict(pair_n=len(pairs),group_n=n,D=float(v[:,0].mean()),ci=ci,compatible_D_bounds=v[:,1:].mean(axis=0).tolist(),compatible_ci=bounds,label=label(ci),unknown_sensitive=label(ci)!=label(bounds),leave_one=[dict(omitted=k,D=float(np.delete(v,i,axis=0)[:,0].mean())) for i,k in enumerate(sorted(groups))] if n>1 else [],group_contributions=[dict(group_id=k,**{key:float(v[i,j]) for j,key in enumerate(keys)}) for i,k in enumerate(sorted(groups))],rescues=sum(r['rescue'] for r in detail),harms=sum(r['harm'] for r in detail),both_correct=sum(r['both_correct'] for r in detail),mapping_equal=sum(r['mapping_equal'] for r in detail),both_known_wrong=sum(r['both_known_wrong'] for r in detail),unknown_pairs=sum(r['unknown'] for r in detail),pairs=detail)
def all_strata(pairs,scores):
 out={}
 for model in ['qwen','apertus']:
  ps=[p for p in pairs if p['model']==model];out[model]={'overall':summarize(ps,scores),'strata':{}}
  for field,values in [('frame',['DIRECT','QUOTED'])]:
   for value in values:out[model]['strata'][value]=summarize([p for p in ps if p[field]==value],scores)
  for t in ['BA','BEI']:
   for s in ['AU','UA']:out[model]['strata'][t+'_'+s]=summarize([p for p in ps if p['construction']==t and p['schema']==s],scores)
 return out
