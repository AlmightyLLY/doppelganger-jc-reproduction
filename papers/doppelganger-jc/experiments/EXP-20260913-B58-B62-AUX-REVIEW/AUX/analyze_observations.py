"""CPU-only frozen probe analysis. No model calls or parameter selection."""
from pathlib import Path
import json,os,itertools,warnings
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.exceptions import ConvergenceWarning
P=Path(__file__).resolve().parent;R=P/'results_continuation';A=P/'analysis';A.mkdir(exist_ok=True)
load=lambda n:json.loads((P/n).read_text())
refs=load('AUTHOR-REFERENCES.json');by={r['call_id']:r for r in refs};ids=list(by);idx={x:i for i,x in enumerate(ids)};t={r['input_id']:r for r in load('TOKEN-MANIFEST.json')['rows']};folds=load('PROBE-FOLDS.json')
states=np.load(P/'results/REPRESENTATIONS-PORTABLE.npz');qs=np.load(R/'QUERY-PORTABLE.npz');q=np.stack([qs[i] for i in ids]).astype(np.float64)
y=np.array([by[i]['y_A_actor'] for i in ids]);rng=np.random.default_rng(130913);proj=rng.normal(0,1/8,(4096,64));np.save(A/'projection.npy',proj)
raw=[json.loads(l) for l in (R/'GENERATIONS.jsonl').read_text().splitlines()];base={r['input_id']:r for r in raw if r['task']=='BASELINE_OBSERVE'};assert len(base)==48
outputs=[];controls=[];fits=[];warn=[]
def fit(train,test,X,labels,meta):
 scaler=StandardScaler().fit(X[train]);tr=scaler.transform(X[train]);te=scaler.transform(X[test]);clf=LogisticRegression(C=1,solver='lbfgs',max_iter=2000)
 with warnings.catch_warnings(record=True) as caught:
  warnings.simplefilter('always');clf.fit(tr,labels)
 for w in caught:warn.append(dict(meta,message=str(w.message)))
 fits.append(dict(meta,n_train=len(train),n_test=len(test),iterations=int(clf.n_iter_[0])))
 return clf.predict(te),clf.predict_proba(te)[:,1]
def emit(pred,prob,test,meta):
 for i,a,b in zip(test,pred,prob):
  r=by[ids[i]];outputs.append(dict(meta,input_id=ids[i],group_id=r['group_id'],construction=r['construction'],schema=r['schema'],background=r['background'],fact_variant=r['fact_variant'],label=int(y[i]),prediction=int(a),probability=float(b),correct=int(a==y[i]),new_native_score=base.get(ids[i],{}).get('score'),new_native_observed=ids[i] in base))
for f in folds:
 tr=[idx[i] for i in f['train_ids']];te=[idx[i] for i in f['test_ids']]
 pred,prob=fit(tr,te,q,y[tr],dict(kind='Q_ONLY',fold=f['test_group']));emit(pred,prob,te,dict(kind='Q_ONLY',anchor='NAME_EMBEDDING',layer=None,permutation=None,fold=f['test_group']))
for r in refs:
 a=r['entity_map']['A'];first=int(r['R1_first_person']==a);grammar=first if r['construction']=='BA' else 1-first;assert grammar==r['y_A_actor']
 controls.append(dict(input_id=r['call_id'],first_mentioned_prediction=first,grammar_prediction=grammar,label=r['y_A_actor']))
for anchor in ['R1_END','NATIVE_PROMPT_END']:
 h=np.stack([states[i+'__'+anchor] for i in ids]).astype(np.float64);h/=np.linalg.norm(h,axis=-1,keepdims=True)
 features=np.einsum('ild,id,dk->ilk',h,q,proj,optimize=True)
 for layer in range(33):
  X=features[:,layer]
  for f in folds:
   train=f['train_ids'];test=[idx[i] for i in f['test_ids']]
   if anchor=='R1_END':
    unique={}
    for i in train:unique.setdefault(t[i]['anchors'][anchor]['prefix_ids_sha256'],i)
    train=list(unique.values())
   train=[idx[i] for i in train]
   meta=dict(kind='PROBE',anchor=anchor,layer=layer,permutation=None,fold=f['test_group']);pred,prob=fit(train,test,X,y[train],meta);emit(pred,prob,test,meta)
   units=sorted(set((by[ids[i]]['group_id'],by[ids[i]]['construction'],by[ids[i]]['fact_variant']) for i in train))
   unitlabels=[next(y[i] for i in train if (by[ids[i]]['group_id'],by[ids[i]]['construction'],by[ids[i]]['fact_variant'])==u) for u in units]
   for k in range(20):
    shuffled=dict(zip(units,np.random.default_rng(130913+k).permutation(unitlabels)));labels=np.array([shuffled[(by[ids[i]]['group_id'],by[ids[i]]['construction'],by[ids[i]]['fact_variant'])] for i in train]);meta=dict(kind='PERMUTATION',anchor=anchor,layer=layer,permutation=k,fold=f['test_group']);pred,prob=fit(train,test,X,labels,meta);emit(pred,prob,test,meta)
   for source,target in [('BA','BEI'),('BEI','BA')]:
    tr=[i for i in train if by[ids[i]]['construction']==source];te=[i for i in test if by[ids[i]]['construction']==target];meta=dict(kind='CROSS_'+source+'_TO_'+target,anchor=anchor,layer=layer,permutation=None,fold=f['test_group']);pred,prob=fit(tr,te,X,y[tr],meta);emit(pred,prob,te,meta)
  (A/'PROGRESS.json').write_text(json.dumps({'anchor':anchor,'layer':layer,'fits':len(fits)}))
with (A/'PROBE-PREDICTIONS.jsonl').open('w') as f:
 for r in outputs:f.write(json.dumps(r)+'\n')
(A/'PROBE-FITS.json').write_text(json.dumps(fits));(A/'PROBE-WARNINGS.json').write_text(json.dumps(warn));(A/'RULE-CONTROLS.json').write_text(json.dumps(controls));(A/'PROBE-STATUS.json').write_text(json.dumps({'status':'COMPLETE','fits':len(fits),'predictions':len(outputs),'warnings':len(warn),'R2_END':'NOT_APPLICABLE_NO_R2_ANCHOR_IN_FROZEN_NONE_TRAINING; pretarget control represented by distance/lens only','random_projection':'numpy default_rng130913 Gaussian sd1/8','Q_ONLY':'4096-dimensional q; same L2 logistic; no layer selection','human_gold':0}))
print('PROBES COMPLETE',len(fits),len(outputs),len(warn),flush=True)
