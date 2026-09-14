"""B66 fixed independent-cohort group bootstrap; no selection of groups."""
import numpy as np
def estimates(a,b):
 return np.stack([a[...,0],a[...,1],b[...,0],b[...,1],a[...,0]-a[...,1],b[...,0]-b[...,1],a[...,0]-b[...,0],a[...,1]-b[...,1],(a[...,0]-a[...,1])-(b[...,0]-b[...,1])],axis=-1)
NAMES=['D63OLD','D63NEW','D65OLD','D65NEW','E63','E65','M_OLD','M_NEW','I']
def summarize(a,b):
 a=np.asarray(a,dtype=float);b=np.asarray(b,dtype=float);assert a.shape==b.shape==(24,2)
 rng=np.random.default_rng(660914);ia=rng.integers(0,24,size=(10000,24));ib=rng.integers(0,24,size=(10000,24))
 point=estimates(a.mean(0),b.mean(0));boot=estimates(a[ia].mean(1),b[ib].mean(1));ci=np.quantile(boot,[.025,.975],axis=0)
 loo={cohort:[estimates(np.delete(a,i,0).mean(0) if cohort=='M63' else a.mean(0),np.delete(b,i,0).mean(0) if cohort=='M65' else b.mean(0)).tolist() for i in range(24)] for cohort in ['M63','M65']}
 return {'estimates':{n:{'value':float(point[i]),'low':float(ci[0,i]),'high':float(ci[1,i])} for i,n in enumerate(NAMES)},'leave_one':loo,'seed':660914,'bootstrap_n':10000,'independent_cohorts':True}
def synthetic():
 a=np.ones((24,2));a[:,1]=0;b=np.zeros((24,2));s=summarize(a,b)['estimates'];assert s['E63']==dict(value=1.,low=1.,high=1.);assert s['I']['value']==1 and s['M_NEW']['value']==0
 z=summarize(np.zeros((24,2)),np.zeros((24,2)));assert all(v==0 for e in z['estimates'].values() for v in e.values());return {'status':'PASS','tests':['constant contrasts and interaction','all-zero null','cohort resampling independently implemented'],'model_calls':0}
