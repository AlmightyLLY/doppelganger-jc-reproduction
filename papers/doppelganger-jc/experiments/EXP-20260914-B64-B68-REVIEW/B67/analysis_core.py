"""Pre-outcome fixed B67 record-presentation contrasts and stratified group bootstrap."""
import numpy as np
NAMES=['D_OO','D_ON','D_NO','D_NN','Theta','T','B','Gamma','I']
COEF=np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1],[1,0,0,-1],[.5,.5,-.5,-.5],[.5,-.5,.5,-.5],[0,1,-1,0],[1,-1,-1,1]],float)
def summarize(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float);assert a.shape==b.shape==(24,4)
    rng=np.random.default_rng(670914)
    draws=[x[rng.integers(0,24,(10000,24))].mean(axis=1)@COEF.T for x in [a,b]]
    points=[a.mean(0)@COEF.T,b.mean(0)@COEF.T]
    out={}
    for label,point,boot in zip(['M63','M65','pooled'],points+[(points[0]+points[1])/2],draws+[(draws[0]+draws[1])/2]):
        ci=np.quantile(boot,[.025,.975],axis=0)
        out[label]={n:{'value':float(point[i]),'low':float(ci[0,i]),'high':float(ci[1,i])} for i,n in enumerate(NAMES)}
    loo=[]
    for ci in range(2):
        for g in range(24):
            means=[np.delete(x,g,0).mean(0) if j==ci else x.mean(0) for j,x in enumerate([a,b])]
            loo.append({'cohort':['M63','M65'][ci],'group_id':f'G{g+1:02d}','pooled':dict(zip(NAMES,((means[0]+means[1])/2@COEF.T).tolist()))})
    p=out['pooled'];same_positive=all(out[c]['Gamma']['value']>0 for c in ['M63','M65']);same_negative=all(out[c]['Gamma']['value']<0 for c in ['M63','M65'])
    flags={'target_dominant_local':p['Gamma']['value']>=.05 and p['Gamma']['low']>0 and same_positive and p['T']['low']>0,
           'background_dominant_local':p['Gamma']['value']<=-.05 and p['Gamma']['high']<0 and same_negative and p['B']['low']>0,
           'both_components_positive':p['T']['low']>0 and p['B']['low']>0,
           'canonical_total_positive':p['Theta']['low']>0,
           'positive_interaction':p['I']['low']>0}
    return dict(estimates=out,leave_one=loo,flags=flags,bootstrap_n=10000,seed=670914,cohort_weights=[.5,.5],independent_cohorts=True)
def synthetic():
    results=[]
    for label,row,expected in [('target',[1,1,0,0],(1,0,1,0)),('background',[1,0,1,0],(0,1,-1,0)),('joint',[1,0,0,0],(.5,.5,0,1)),('null',[0,0,0,0],(0,0,0,0))]:
        x=np.tile(row,(24,1));s=summarize(x,x);v=s['estimates']['pooled'];assert tuple(v[n]['value'] for n in ['T','B','Gamma','I'])==expected
        assert all(v[n]['low']==v[n]['value']==v[n]['high'] for n in NAMES)
        assert abs(v['T']['value']+v['B']['value']-v['Theta']['value'])<1e-12
        results.append({'synthetic_case':label,'expected_T_B_Gamma_I':list(expected),'flags':s['flags']})
    return {'status':'PASS','model_calls':0,'cases':results,'notice':'Synthetic arithmetic controls only, not empirical evidence.'}
if __name__=='__main__':
    import json
    print(json.dumps(synthetic(),ensure_ascii=False,indent=2))
