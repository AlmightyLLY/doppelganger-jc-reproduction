"""Frozen B69 pre-output arithmetic; all resampling units are 16 predicate groups."""
import numpy as np
NAMES=['D_O','D_N','Lambda','background_burden_O','background_burden_N','burden_interaction']
def summarize(d,burden,direction,scenario):
 d=np.asarray(d,float);burden=np.asarray(burden,float)
 assert d.shape==burden.shape==(16,2)
 a=np.column_stack((d[:,0],d[:,1],d[:,0]-d[:,1],burden[:,0],burden[:,1],burden[:,0]-burden[:,1]))
 indices=np.random.default_rng(690914).integers(0,16,(10000,16));boot=a[indices].mean(1)
 lo,hi=np.quantile(boot,[.025,.975],axis=0);mean=a.mean(0)
 est={n:dict(value=float(mean[i]),low=float(lo[i]),high=float(hi[i])) for i,n in enumerate(NAMES)}
 loo=[dict(omitted_group=f'V{i+1:02d}',**dict(zip(NAMES,np.delete(a,i,axis=0).mean(0).tolist()))) for i in range(16)]
 v=est['Lambda'];passed=v['value']>=.05 and v['low']>0 and all(x>0 for x in direction.values()) and all(x>0 for x in scenario.values()) and all(x['Lambda']>0 for x in loo)
 label='LOCAL_PACKAGE_PREDICTION_TRANSFER_WITHIN_TEMPLATE' if passed else 'REVERSED_LOCAL_PACKAGE_EFFECT' if v['high']<0 else 'NOT_MET_OR_UNCERTAIN'
 return dict(estimates=est,leave_one=loo,direction_points=direction,scenario_points=scenario,label=label,minimum_investment_effect_unsupported=v['high']<.05,seed=690914,bootstrap_n=10000,independent_units=16)
def low_headroom(counts):
 assert len(counts)==4 and all(0<=n<=64 for n in counts)
 return all(n>=63 for n in counts)
def synthetic():
 cases=[]
 for name,row,label in [('transfer',[.25,0],'LOCAL_PACKAGE_PREDICTION_TRANSFER_WITHIN_TEMPLATE'),('null',[0,0],'NOT_MET_OR_UNCERTAIN'),('reverse',[0,.25],'REVERSED_LOCAL_PACKAGE_EFFECT')]:
  delta=row[0]-row[1];s=summarize(np.tile(row,(16,1)),np.zeros((16,2)),dict(AB=delta,BA=delta),dict(S1=delta,S2=delta));assert s['label']==label and s['estimates']['Lambda']['value']==delta
  cases.append(dict(case=name,label=label))
 s=summarize(np.tile([.25,0],(16,1)),np.tile([-.5,-.25],(16,1)),dict(AB=0,BA=.5),dict(S1=.25,S2=.25));assert s['label']=='NOT_MET_OR_UNCERTAIN' and s['estimates']['burden_interaction']['value']==-.25
 assert low_headroom([63,64,64,63]) and not low_headroom([62,64,64,64])
 return dict(status='PASS',cases=cases,zero_direction_blocks_gate=True,burden_sign_checked=True,headroom_boundary_checked=True,model_calls=0)
if __name__=='__main__':
 import json
 print(json.dumps(synthetic(),indent=2))
