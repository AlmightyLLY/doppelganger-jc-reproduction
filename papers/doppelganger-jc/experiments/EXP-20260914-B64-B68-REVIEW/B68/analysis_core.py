"""B68 pre-outcome contrasts: frame/local components, not B67's R1/R2 axes."""
import numpy as np
NAMES=['D_FO_LO','D_FO_LN','D_FN_LO','D_FN_LN','Theta','Frame','Local','Psi','Interaction']
COEF=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,-1],[.5,.5,-.5,-.5],[.5,-.5,.5,-.5],[0,-1,1,0],[1,-1,-1,1]],float)
def summarize(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);assert a.shape==b.shape==(24,4)
 rng=np.random.default_rng(680914)
 draws=[x[rng.integers(0,24,(10000,24))].mean(1)@COEF.T for x in [a,b]]
 points=[a.mean(0)@COEF.T,b.mean(0)@COEF.T]
 estimates={}
 for label,point,boot in zip(['M63','M65','pooled'],points+[(points[0]+points[1])/2],draws+[(draws[0]+draws[1])/2]):
  lo,hi=np.quantile(boot,[.025,.975],axis=0)
  estimates[label]={n:dict(value=float(point[i]),low=float(lo[i]),high=float(hi[i])) for i,n in enumerate(NAMES)}
 loo=[]
 for ci in range(2):
  for g in range(24):
   m=[np.delete(x,g,axis=0).mean(0) if j==ci else x.mean(0) for j,x in enumerate([a,b])]
   loo.append(dict(cohort=['M63','M65'][ci],group_id=f'G{g+1:02d}',pooled=dict(zip(NAMES,((m[0]+m[1])/2@COEF.T).tolist()))))
 p=estimates['pooled']
 flags=dict(local_component_dominant=p['Psi']['value']>=.05 and p['Psi']['low']>0 and p['Local']['low']>0 and all(estimates[c]['Psi']['value']>0 for c in ['M63','M65']),
  frame_component_dominant=p['Psi']['value']<=-.05 and p['Psi']['high']<0 and p['Frame']['low']>0 and all(estimates[c]['Psi']['value']<0 for c in ['M63','M65']),
  total_contrast_retained=p['Theta']['low']>0,
  positive_interaction=p['Interaction']['low']>0,negative_interaction=p['Interaction']['high']<0)
 return dict(estimates=estimates,leave_one=loo,flags=flags,bootstrap_n=10000,seed=680914,cohort_weights=[.5,.5])
def synthetic():
 cases=[]
 for label,row,expected in [('frame',[1,1,0,0],(1,0,-1,0)),('local',[1,0,1,0],(0,1,1,0)),('joint',[1,0,0,0],(.5,.5,0,1)),('null',[0,0,0,0],(0,0,0,0))]:
  x=np.tile(row,(24,1));s=summarize(x,x);v=s['estimates']['pooled']
  assert tuple(v[n]['value'] for n in ['Frame','Local','Psi','Interaction'])==expected
  assert all(v[n]['low']==v[n]['value']==v[n]['high'] for n in NAMES)
  cases.append(dict(case=label,expected=list(expected),flags=s['flags']))
 return dict(status='PASS',model_calls=0,cases=cases,notice='Synthetic arithmetic controls, not scientific results.')
if __name__=='__main__':
 import json
 print(json.dumps(synthetic(),ensure_ascii=False,indent=2))
