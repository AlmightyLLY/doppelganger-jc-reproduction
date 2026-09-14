from pathlib import Path
from collections import Counter
import json,hashlib,math,itertools,gzip
import numpy as np
HERE=Path(__file__).resolve().parent
E=HERE
read=lambda p:json.loads(p.read_text())
def readrows(p):return [json.loads(x) for x in gzip.decompress(p.read_bytes()).splitlines()]
RESULTS={}
def save(n,x):RESULTS[n]=x
def rev(g):return dict(actor=g['undergoer'],undergoer=g['actor'])
def key(r,ks):return tuple(r[k] for k in ks)
def unique_object(pairs):
 assert len(set(k for k,v in pairs))==len(pairs)
 return dict(pairs)
refs=readrows(E/'REFERENCES.jsonl.gz')
raw=readrows(E/'RAW-OUTPUTS.jsonl.gz')
idx={r['call_id']:r for r in raw}
refidx={r['call_id']:r for r in refs}
saved={r['call_id']:dict(refidx[r['call_id']],**r,raw_output=idx[r['call_id']]) for r in readrows(E/'SCORES.jsonl.gz')}
assert len(raw)==len(idx)==len(refs)==len(saved)==3104
audit={}
def unique_object(pairs):
    assert len(set(k for k,v in pairs))==len(pairs)
    return dict(pairs)
for r in refs:
    o=idx[r['call_id']]
    assert o['messages']==r['messages'] and o['source_text']==r['source_text']
    a=json.loads(o['generated_text'],object_pairs_hook=unique_object)
    assert isinstance(a,dict) and set(a)=={'actor','undergoer'}
    names={n for n in r['entity_map'].values() if n in r['source_text']}
    fs={k:'C' if a[k]==r['gold'][k] else 'W' if isinstance(a[k],str) and a[k] in names else 'U' for k in a}
    s='W' if 'W' in fs.values() else 'U' if 'U' in fs.values() else 'C'
    detail='C' if s=='C' else 'R1_REVERSE' if a==rev(r['gold']) else 'U' if s=='U' else 'BG_C' if r['background_gold'] and a==r['background_gold'] else 'BG_R' if r['background_gold'] and a==rev(r['background_gold']) else 'MIXED_OTHER_W'
    e=saved[r['call_id']]
    assert (a,s,fs,detail)==(e['assessment']['answer'],e['assessment']['score'],e['assessment']['field_scores'],e['detail'])
    assert e['assessment']['format_ok']==(list(a)==(['actor','undergoer'] if r['schema']=='AU' else ['undergoer','actor']))
    assert len(o['generated_token_ids'])==o['generated_token_n']==o['row_forward_n']
    assert len(o['input_ids'])==o['input_token_n']<=2048
    assert o['generated_token_n']<=128 and o['stopped_on_eos']
    if r['material_set']=='SCIENCE':
        assert r['frame_render']==r['background_render']=='N'
        wanted={'actor':r['entity_map']['A' if r['direction']=='AB' else 'B'],'undergoer':r['entity_map']['B' if r['direction']=='AB' else 'A']}
        assert r['gold']==wanted
        mention=sorted(wanted.values(),key=r['R1'].index)
        h=dict(zip(['actor','undergoer'] if r['schema']=='AU' else ['undergoer','actor'],mention))
        assert h==r['H_COPY'] and e['H_COPY_fit']==int(a==h) and e['H_ROLE_fit']==int(a==wanted)
    audit[r['call_id']]=dict(r,answer=a,score=s,detail=detail)
science=[r for r in audit.values() if r['material_set']=='SCIENCE']
assert len(science)==3072
base=['model','unit_id','scenario_id','direction','construction','schema','local_render','background']
lookup={key(r,base):r for r in science};assert len(lookup)==3072
def changed(r,**kw): return lookup[key(dict(r,**kw),base)]
trans={k:[] for k in ['BACKGROUND','LOCAL','NONE','SAME_FACT','FIXED_ORDER_FACT_CHANGE']}
g4=[]
for r in science:
    if r['background']!='NONE' and r['background']!=r['construction']:
        trans['BACKGROUND'].append((r,changed(r,background=r['construction'])))
    if r['local_render']=='O': trans['LOCAL'].append((r,changed(r,local_render='N')))
    if r['background']!='NONE': trans['NONE'].append((changed(r,background='NONE'),r))
    if r['construction']=='BA':
        trans['SAME_FACT'].append((r,changed(r,construction='BEI')))
        trans['FIXED_ORDER_FACT_CHANGE'].append((r,changed(r,construction='BEI',direction='BA' if r['direction']=='AB' else 'AB')))
        if r['direction']=='AB':
            g4.append([changed(r,direction=d,construction=c) for d,c in [('AB','BA'),('AB','BEI'),('BA','BA'),('BA','BEI')]])
expected=read(E/'TRANSITIONS.json');pair_totals={}
harms=read(E/'ALL-HARMS.json')
for kind,pairs in trans.items():
    ee={(p['before_id'],p['after_id']):p for p in expected[kind]}
    assert len(ee)==len(pairs)
    for a,b in pairs:
        if kind=='FIXED_ORDER_FACT_CHANGE':
            assert rev(a['gold'])==b['gold']
            assert sorted(a['gold'].values(),key=a['R1'].index)==sorted(b['gold'].values(),key=b['R1'].index)
        else: assert a['gold']==b['gold']
        if kind=='BACKGROUND': assert a['R1']==b['R1'] and a['background_gold']==b['background_gold']
        if kind in ['LOCAL','SAME_FACT','FIXED_ORDER_FACT_CHANGE']: assert a['R2']==b['R2']
        ac,bc=int(a['score']=='C'),int(b['score']=='C')
        vals=dict(before_C=ac,after_C=bc,delta_C=bc-ac,both_C=ac*bc,mapping_equal=int(a['answer']==b['answer']),both_wrong=int(a['score']==b['score']=='W'),U_involved=int(a['score']=='U' or b['score']=='U'))
        if kind=='FIXED_ORDER_FACT_CHANGE': vals['correct_swap']=ac*bc
        else: vals.update(rescue=int(not ac and bc),harm=int(ac and not bc))
        e=ee[a['call_id'],b['call_id']]
        assert all(e[k]==v for k,v in vals.items())
    assert {(a['call_id'],b['call_id']) for a,b in pairs if kind!='FIXED_ORDER_FACT_CHANGE' and a['score']=='C' and b['score']!='C'}=={(p['before_id'],p['after_id']) for p in harms[kind]}
    pair_totals[kind]={m:{'n':sum(a['model']==m for a,b in pairs),'both_C':sum(a['model']==m and a['score']==b['score']=='C' for a,b in pairs),'same_mapping':sum(a['model']==m and a['answer']==b['answer'] for a,b in pairs),'both_wrong':sum(a['model']==m and a['score']==b['score']=='W' for a,b in pairs),'rescues':sum(a['model']==m and a['score']!='C' and b['score']=='C' for a,b in pairs) if kind!='FIXED_ORDER_FACT_CHANGE' else None,'harms':sum(a['model']==m and a['score']=='C' and b['score']!='C' for a,b in pairs) if kind!='FIXED_ORDER_FACT_CHANGE' else None} for m in ['qwen','apertus']}
eg={tuple(g['member_ids']):g for g in read(E/'FOUR-MEMBER-RESULTS.json')}
assert len(g4)==len(eg)==768
for members in g4:
    x=eg[tuple(r['call_id'] for r in members)]
    assert x['all_four_correct']==int(all(r['score']=='C' for r in members))
    assert x['details']==[r['detail'] for r in members]
    assert x['raw_outputs']==[idx[r['call_id']]['generated_text'] for r in members]
NAMES=['D_O','D_N','Lambda','background_burden_O','background_burden_N','burden_interaction']
stats={};group_saved={(r['model'],r['unit_id']):r for r in read(E/'GROUP-CONTRIBUTIONS.json')}
for m in ['qwen','apertus']:
    groups=[]
    def delta(pairs,**filters):
        pp=[(a,b) for a,b in pairs if a['model']==m and all(a[k]==v for k,v in filters.items())]
        assert pp
        return sum(int(b['score']=='C')-int(a['score']=='C') for a,b in pp)/len(pp)
    for i in range(1,17):
        uid=f'V{i:02d}'
        old,new=[delta(trans['BACKGROUND'],unit_id=uid,local_render=l) for l in ['O','N']]
        bo,bn=[delta(trans['NONE'],unit_id=uid,local_render=l) for l in ['O','N']]
        row=[old,new,old-new,bo,bn,bo-bn];groups.append(row)
        assert np.allclose(row,[group_saved[m,uid][k] for k in NAMES],atol=1e-12)
    a=np.array(groups);draw=np.random.default_rng(690914).integers(0,16,(10000,16));bs=a[draw].mean(1)
    ci=np.quantile(bs,[.025,.975],axis=0);p=a.mean(0);e=read(E/'STATISTICS.json')[m]
    for i,n in enumerate(NAMES): assert np.allclose([p[i],ci[0,i],ci[1,i]],[e['estimates'][n][k] for k in ['value','low','high']],atol=1e-12)
    for i,x in enumerate(e['leave_one']): assert np.allclose(np.delete(a,i,axis=0).mean(0),[x[k] for k in NAMES],atol=1e-12)
    for f,out,values in [('direction','direction_points',['AB','BA']),('scenario_fold','scenario_points',['S1','S2'])]:
        for v in values:
            val=delta(trans['BACKGROUND'],**{f:v,'local_render':'O'})-delta(trans['BACKGROUND'],**{f:v,'local_render':'N'})
            assert math.isclose(val,e[out][v],abs_tol=1e-12)
    passed=p[2]>=.05 and ci[0,2]>0 and all(v>0 for v in e['direction_points'].values()) and all(v>0 for v in e['scenario_points'].values()) and all(x['Lambda']>0 for x in e['leave_one'])
    label='LOCAL_PACKAGE_PREDICTION_TRANSFER_WITHIN_TEMPLATE' if passed else 'REVERSED_LOCAL_PACKAGE_EFFECT' if ci[1,2]<0 else 'NOT_MET_OR_UNCERTAIN'
    assert e['label']==label
    stats[m]=e
strata=read(E/'STRATA.json')
for x in strata:
    rr=[r for r in science if all(r[k]==x[k] for k in ['model','construction','schema','local_render','background'])]
    assert len(rr)==x['n']==64 and dict(Counter(r['detail'] for r in rr))==x['counts']
    assert sum(r['score']=='C' for r in rr)==x['C']
    assert sum(r['answer']==r['H_COPY'] for r in rr)==x['H_COPY_fit']
for m in stats:
    hc=[x['C'] for x in strata if x['model']==m and x['construction']=='BEI' and x['schema']=='AU' and x['background']!='NONE']
    assert stats[m]['headroom_C_counts']==hc and stats[m]['LOW_HEADROOM']==all(v>=63 for v in hc)
for x in read(E/'COPY-FIT.json'):
    rr=[r for r in science if r['model']==x['model'] and (r['gold']!=r['H_COPY'])==x['copy_role_conflict'] and (x['detail']=='ALL' or r['detail']==x['detail'])]
    assert len(rr)==x['n'] and sum(r['answer']==r['gold'] for r in rr)==x['H_ROLE_fit'] and sum(r['answer']==r['H_COPY'] for r in rr)==x['H_COPY_fit']
assert read(E/'ALL-UNRESOLVED.json')==[] and all(r['detail']!='U' for r in science)

print('B69 public score, all five pair sets, G4, six estimates, bootstrap, LOO and strata PASS')
