"""Frozen descriptive paired analysis; AI labels are explicitly not human gold."""
import json,collections
from pathlib import Path
import numpy as np
from measurement import form_hits,error_bounds,pair_bounds
W=Path(__file__).resolve().parent
SEED=20260917;B=10000
def rankdata(a,axis=-1):
 def one(v):
  _,inverse,counts=np.unique(v,return_inverse=True,return_counts=True)
  average=np.cumsum(counts)-(counts-1)/2
  return average[inverse]
 return np.apply_along_axis(one,axis,np.asarray(a,float))
def paired_summary(values):
 a=np.asarray(values,dtype=float);assert len(a)>0
 rng=np.random.default_rng(SEED);idx=rng.integers(0,len(a),(B,len(a)))
 if a.ndim==1:
  samples=a[idx].mean(axis=1)
  return dict(n=len(a),mean=float(a.mean()),ci95=np.quantile(samples,[.025,.975]).tolist())
 assert a.shape[1]==2 and np.all(a[:,0]<=a[:,1])
 samples=a[idx].mean(axis=1)
 return dict(n=len(a),identification_interval=a.mean(axis=0).tolist(),sampling_envelope95=[float(np.quantile(samples[:,0],.025)),float(np.quantile(samples[:,1],.975))])
def spearman_summary(x,y):
 x=np.asarray(x,float);y=np.asarray(y,float);n=len(x)
 if n<3 or np.ptp(x)==0 or np.ptp(y)==0:return dict(n=n,rho=None,ci95=None,reason='NO_VARIATION_OR_TOO_FEW')
 def corr(a,b):
  a=rankdata(a,axis=-1);b=rankdata(b,axis=-1);a-=a.mean(axis=-1,keepdims=True);b-=b.mean(axis=-1,keepdims=True)
  den=np.sqrt((a*a).sum(axis=-1)*(b*b).sum(axis=-1))
  return np.divide((a*b).sum(axis=-1),den,out=np.full_like(den,np.nan),where=den>0)
 rho=float(corr(x,y));rng=np.random.default_rng(SEED);boot=[]
 for _ in range(B//500):
  idx=rng.integers(0,n,(500,n));boot.extend(corr(x[idx],y[idx]).tolist())
 a=np.array(boot);valid=a[np.isfinite(a)]
 return dict(n=n,rho=rho,ci95=np.quantile(valid,[.025,.975]).tolist() if len(valid) else None,degenerate_bootstrap_fraction=float(1-len(valid)/B))
def analyze(materials,outputs,labels):
 ids=sorted(m['item_index'] for m in materials);mmap={m['item_index']:m for m in materials}
 assert len(outputs)==len(ids)*3 and len(labels)==len(outputs)
 for i in ids:
  for c in 'OTU':assert labels[i,c]['label'] in ('C','W','U')
 subsets=dict(all=ids,source_unflagged=[i for i in ids if not mmap[i]['source_issue']],strict_unchanged=[i for i in ids if not mmap[i]['revised']],strict_unflagged=[i for i in ids if not mmap[i]['revised'] and not mmap[i]['source_issue']],guard=[i for i in ids if mmap[i]['guard_proxy']])
 result=dict(status='DEVELOPMENT_AI_LABELS_NOT_HUMAN_GOLD',human_gold=0,bootstrap_replicates=B,seed=SEED,subsets={})
 for name,ss in subsets.items():
  z=dict(n=len(ss),E1={},E2={},E3={})
  for language,key in [('chinese','word'),('japanese','japanese_word')]:
   hits={(i,c):int(bool(form_hits(outputs[i,c],mmap[i][key]))) for i in ss for c in 'OTU'}
   z['E1'][language]={'counts':{c:sum(hits[i,c] for i in ss) for c in 'OTU'},'rates':{c:sum(hits[i,c] for i in ss)/len(ss) for c in 'OTU'},'contrasts':{a+'-'+b:paired_summary([hits[i,a]-hits[i,b] for i in ss]) for a,b in [('O','U'),('O','T'),('U','T')]}}
  z['E2']['label_counts']={c:dict(collections.Counter(labels[i,c]['label'] for i in ss)) for c in 'OTU'}
  z['E2']['pairs']={}
  for a,b in [('O','T'),('U','T'),('O','U')]:
   transitions=collections.Counter(labels[i,a]['label']+'->'+labels[i,b]['label'] for i in ss)
   clear=[i for i in ss if labels[i,a]['label']!='U' and labels[i,b]['label']!='U']
   differences=[int(labels[i,a]['label']=='W')-int(labels[i,b]['label']=='W') for i in clear]
   z['E2']['pairs'][a+'-'+b]=dict(transitions=dict(transitions),rescue=transitions['W->C'],new_harm=transitions['C->W'],uncertainty=paired_summary([pair_bounds(labels[i,a]['label'],labels[i,b]['label']) for i in ss]),clear_subset=paired_summary(differences) if differences else None,clear_fraction=len(clear)/len(ss))
  x=[mmap[i]['fixed_six_model_mean'] for i in ss]
  z['E3']['old_effect_to_O_form']=spearman_summary(x,[int(bool(form_hits(outputs[i,'O'],mmap[i]['word']))) for i in ss])
  for a,b in [('U','T'),('O','T')]:
   clear=[i for i in ss if labels[i,a]['label']!='U' and labels[i,b]['label']!='U']
   z['E3']['old_effect_to_'+a+'-'+b]=spearman_summary([mmap[i]['fixed_six_model_mean'] for i in clear],[int(labels[i,a]['label']=='W')-int(labels[i,b]['label']=='W') for i in clear])
   z['E3']['old_effect_to_'+a+'-'+b]['coverage']=len(clear)/len(ss)
  result['subsets'][name]=z
 return result
if __name__=='__main__':
 materials=json.loads((W/'MATERIALS.json').read_text());raw=[json.loads(p.read_text()) for p in sorted((W/'results').glob('R1P-*.json'))]
 outputs={(r['item_index'],r['condition']):r['output'] for r in raw}
 lab=json.loads((W/'AI-SEMANTIC-LABELS.json').read_text());labels={(r['item_index'],r['condition']):r for r in lab}
 result=analyze(materials,outputs,labels);(W/'ANALYSIS.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result['subsets']['all'],ensure_ascii=False))
