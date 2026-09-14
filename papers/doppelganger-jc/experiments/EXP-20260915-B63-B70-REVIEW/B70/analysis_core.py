"""B70 pre-output factorial arithmetic, 16 predicate clusters, fixed primary T."""
import numpy as np
VARIANTS=['C0A0','C0A1','C1A0','C1A1']
NAMES=['D00','D01','D10','D11','T','S0','S1','T1','J','PACKAGE','COMMA_MEAN','ALREADY_MEAN']
COEF=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[-1,1,0,0],[-1,0,1,0],[0,-1,0,1],[0,0,-1,1],[1,-1,-1,1],[-1,0,0,1],[-.5,-.5,.5,.5],[-.5,.5,-.5,.5]])
ALL_NAMES=NAMES+['B00','B01','B10','B11','B01_MINUS_B00']
def summarize(d,burden,direction,scenario):
 d=np.asarray(d,float);burden=np.asarray(burden,float);assert d.shape==burden.shape==(16,4)
 a=np.column_stack((d@COEF.T,burden,burden[:,1]-burden[:,0]));indices=np.random.default_rng(700915).integers(0,16,(10000,16));boot=a[indices].mean(1)
 lo,hi=np.quantile(boot,[.025,.975],axis=0);point=a.mean(0);est={n:dict(value=float(point[i]),low=float(lo[i]),high=float(hi[i])) for i,n in enumerate(ALL_NAMES)}
 loo=[dict(omitted_group=f'V{i+1:02d}',**dict(zip(ALL_NAMES,np.delete(a,i,axis=0).mean(0).tolist()))) for i in range(16)]
 v=est['T'];passed=v['value']>=.05 and v['low']>0 and all(x>0 for x in direction.values()) and all(x>0 for x in scenario.values()) and all(x['T']>0 for x in loo)
 label='NONCOMMA_MODULATION_SUPPORTED_IN_DEVELOPMENT' if passed else 'REVERSED_NONCOMMA_MODULATION' if v['high']<0 else 'NOT_MET_OR_UNCERTAIN'
 return dict(estimates=est,leave_one=loo,direction_points=direction,scenario_points=scenario,label=label,PRACTICALLY_SMALL_UNDER_THIS_DESIGN=v['low']>=-.025 and v['high']<=.025,seed=700915,bootstrap_n=10000,independent_units=16)
def low_headroom(counts):
 assert len(counts)==4 and all(0<=n<=64 for n in counts)
 return all(n>=63 for n in counts)
def synthetic():
 cases=[]
 for name,row,t,j in [('already',[0,1,0,1],1,0),('comma',[0,0,1,1],0,0),('joint',[0,0,0,1],0,1),('reverse',[1,0,1,0],-1,0),('null',[0,0,0,0],0,0)]:
  s=summarize(np.tile(row,(16,1)),np.zeros((16,4)),dict(AB=t,BA=t),dict(S1=t,S2=t));assert s['estimates']['T']['value']==t and s['estimates']['J']['value']==j
  assert s['label']==('NONCOMMA_MODULATION_SUPPORTED_IN_DEVELOPMENT' if t>0 else 'REVERSED_NONCOMMA_MODULATION' if t<0 else 'NOT_MET_OR_UNCERTAIN')
  assert s['PRACTICALLY_SMALL_UNDER_THIS_DESIGN']==(t==0);cases.append(dict(case=name,T=t,J=j,label=s['label']))
 s=summarize(np.tile([0,.25,0,.25],(16,1)),np.tile([-.5,-.25,0,0],(16,1)),dict(AB=0,BA=.5),dict(S1=.25,S2=.25));assert s['label']=='NOT_MET_OR_UNCERTAIN' and s['estimates']['B01_MINUS_B00']['value']==.25
 assert low_headroom([63,64,64,63]) and not low_headroom([62,64,64,64])
 return dict(status='PASS',cases=cases,zero_direction_blocks_gate=True,burden_sign_checked=True,headroom_boundary_checked=True,model_calls=0)
