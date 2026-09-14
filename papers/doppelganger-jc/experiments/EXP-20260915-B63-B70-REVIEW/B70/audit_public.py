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
assert len(raw)==len(idx)==len(refs)==6176
audit={}
for r in refs:
    o=idx[r['call_id']]
    assert o['messages']==r['messages'] and o['source_text']==r['source_text']
    a=json.loads(o['generated_text'],object_pairs_hook=unique_object)
    assert isinstance(a,dict) and set(a)=={'actor','undergoer'}
    names={n for n in r['entity_map'].values() if n in r['source_text']}
    fs={k:'C' if a[k]==r['gold'][k] else 'W' if isinstance(a[k],str) and a[k] in names else 'U' for k in a}
    score='W' if 'W' in fs.values() else 'U' if 'U' in fs.values() else 'C'
    detail='C' if score=='C' else 'R1_REVERSE' if a==rev(r['gold']) else 'U' if score=='U' else 'BG_C' if r['background_gold'] and a==r['background_gold'] else 'BG_R' if r['background_gold'] and a==rev(r['background_gold']) else 'MIXED_OTHER_W'
    assert len(o['input_ids'])==o['input_token_n']<=2048
    assert len(o['generated_token_ids'])==o['generated_token_n']==o['row_forward_n']<=128 and o['stopped_on_eos']
    if r['material_set']=='SCIENCE':
        wanted={'actor':r['entity_map']['A' if r['direction']=='AB' else 'B'],'undergoer':r['entity_map']['B' if r['direction']=='AB' else 'A']}
        assert r['gold']==wanted
        mention=sorted(wanted.values(),key=r['R1'].index)
        assert r['H_COPY']==dict(zip(['actor','undergoer'] if r['schema']=='AU' else ['undergoer','actor'],mention))
        assert r['local_render']==f"C{r['comma']}A{r['already']}"
    audit[r['call_id']]=dict(r,answer=a,score=score,detail=detail,field_scores=fs)

# Independently rebuild every pair without importing the execution pair maps.
science=[r for r in audit.values() if r['material_set']=='SCIENCE'];assert len(science)==6144
fields=['model','unit_id','scenario_id','direction','construction','schema','local_render','background']
lookup={key(r,fields):r for r in science};assert len(lookup)==6144
def alt(r,**kw):return lookup[key(dict(r,**kw),fields)]
trans={k:[] for k in ['BACKGROUND','COMMA','ALREADY','PACKAGE','NONE','SAME_FACT','FIXED_ORDER_FACT_CHANGE']};g4=[]
for r in science:
    if r['background']!='NONE' and r['background']!=r['construction']:trans['BACKGROUND'].append((r,alt(r,background=r['construction'])))
    if r['comma']==0:trans['COMMA'].append((r,alt(r,local_render=f"C1A{r['already']}")))
    if r['already']==0:trans['ALREADY'].append((r,alt(r,local_render=f"C{r['comma']}A1")))
    if r['local_render']=='C0A0':trans['PACKAGE'].append((r,alt(r,local_render='C1A1')))
    if r['background']!='NONE':trans['NONE'].append((alt(r,background='NONE'),r))
    if r['construction']=='BA':
        trans['SAME_FACT'].append((r,alt(r,construction='BEI')))
        trans['FIXED_ORDER_FACT_CHANGE'].append((r,alt(r,construction='BEI',direction='BA' if r['direction']=='AB' else 'AB')))
        if r['direction']=='AB':g4.append([alt(r,direction=d,construction=c) for d,c in itertools.product(['AB','BA'],['BA','BEI'])])
assert [len(trans[k]) for k in trans]==[2048,3072,3072,1536,4096,3072,3072] and len(g4)==1536
# Public saved rows are reconstructed above.
for cid,r in audit.items():
    e=saved[cid]
    assert (r['answer'],r['score'],r['field_scores'],r['detail'])==(e['assessment']['answer'],e['assessment']['score'],e['assessment']['field_scores'],e['detail'])
    assert e['assessment']['format_ok']==(list(r['answer'])==(['actor','undergoer'] if r['schema']=='AU' else ['undergoer','actor']))
    assert e['field_U']==('U' in r['field_scores'].values())
    assert e['string_null']==any(v=='null' for v in r['answer'].values())
    assert e['true_null']==any(v is None for v in r['answer'].values())
expected=read(E/'TRANSITIONS.json');harms=read(E/'ALL-HARMS.json');totals={}
for kind,pairs in trans.items():
    ee={(p['before_id'],p['after_id']):p for p in expected[kind]};assert len(ee)==len(pairs)
    for a,b in pairs:
        if kind=='FIXED_ORDER_FACT_CHANGE':
            assert b['gold']==rev(a['gold']) and sorted(a['gold'].values(),key=a['R1'].index)==sorted(b['gold'].values(),key=b['R1'].index)
        else:assert a['gold']==b['gold']
        if kind=='BACKGROUND':assert a['R1']==b['R1'] and a['background_gold']==b['background_gold']
        if kind in ['COMMA','ALREADY','PACKAGE','SAME_FACT','FIXED_ORDER_FACT_CHANGE']:assert a['R2']==b['R2']
        ac,bc=int(a['score']=='C'),int(b['score']=='C')
        vals=dict(before_C=ac,after_C=bc,delta_C=bc-ac,both_C=ac*bc,mapping_equal=int(a['answer']==b['answer']),both_wrong=int(a['score']==b['score']=='W'),U_involved=int(a['score']=='U' or b['score']=='U'))
        if kind=='FIXED_ORDER_FACT_CHANGE':vals['correct_swap']=ac*bc
        else:vals.update(rescue=int(not ac and bc),harm=int(ac and not bc))
        assert all(ee[a['call_id'],b['call_id']][k]==v for k,v in vals.items())
    assert {(a['call_id'],b['call_id']) for a,b in pairs if kind!='FIXED_ORDER_FACT_CHANGE' and a['score']=='C' and b['score']!='C'}=={(p['before_id'],p['after_id']) for p in harms[kind]}
    totals[kind]={m:{'n':sum(a['model']==m for a,b in pairs),'before_C':sum(a['model']==m and a['score']=='C' for a,b in pairs),'after_C':sum(a['model']==m and b['score']=='C' for a,b in pairs),'both_C':sum(a['model']==m and a['score']==b['score']=='C' for a,b in pairs),'same_mapping':sum(a['model']==m and a['answer']==b['answer'] for a,b in pairs),'both_wrong':sum(a['model']==m and a['score']==b['score']=='W' for a,b in pairs),'rescues':sum(a['model']==m and a['score']!='C' and b['score']=='C' for a,b in pairs) if kind!='FIXED_ORDER_FACT_CHANGE' else None,'harms':sum(a['model']==m and a['score']=='C' and b['score']!='C' for a,b in pairs) if kind!='FIXED_ORDER_FACT_CHANGE' else None} for m in ['qwen','apertus']}
eg={tuple(x['member_ids']):x for x in read(E/'FOUR-MEMBER-RESULTS.json')};assert len(eg)==1536
for rr in g4:
    x=eg[tuple(r['call_id'] for r in rr)];assert x['all_four_correct']==int(all(r['score']=='C' for r in rr)) and x['details']==[r['detail'] for r in rr] and x['raw_outputs']==[idx[r['call_id']]['generated_text'] for r in rr]

# Seventeen prespecified quantities from explicit arithmetic, fixed resampling.
group_saved={(r['model'],r['unit_id']):r for r in read(E/'GROUP-CONTRIBUTIONS.json')}
stats=read(E/'STATISTICS.json');variants=['C0A0','C0A1','C1A0','C1A1']
for m in ['qwen','apertus']:
    def delta(pairs,**filters):
        pp=[(a,b) for a,b in pairs if a['model']==m and all(a[k]==v for k,v in filters.items())];assert pp
        return sum(int(b['score']=='C')-int(a['score']=='C') for a,b in pp)/len(pp)
    vv=[]
    for i in range(1,17):
        uid=f'V{i:02d}';d00,d01,d10,d11=[delta(trans['BACKGROUND'],unit_id=uid,local_render=l) for l in variants]
        b00,b01,b10,b11=[delta(trans['NONE'],unit_id=uid,local_render=l) for l in variants]
        v=dict(D00=d00,D01=d01,D10=d10,D11=d11,T=d01-d00,S0=d10-d00,S1=d11-d01,T1=d11-d10,J=(d11-d10)-(d01-d00),PACKAGE=d11-d00,COMMA_MEAN=((d10-d00)+(d11-d01))/2,ALREADY_MEAN=((d01-d00)+(d11-d10))/2,B00=b00,B01=b01,B10=b10,B11=b11,B01_MINUS_B00=b01-b00)
        for k,value in v.items():assert math.isclose(group_saved[m,uid][k],value,abs_tol=1e-12)
        vv.append(v)
    names=list(vv[0]);a=np.array([[v[k] for k in names] for v in vv]);draw=np.random.default_rng(700915).integers(0,16,(10000,16));bs=a[draw].mean(1);ci=np.quantile(bs,[.025,.975],axis=0);point=a.mean(0);e=stats[m]
    for j,k in enumerate(names):
        assert np.allclose([point[j],ci[0,j],ci[1,j]],[e['estimates'][k][v] for v in ['value','low','high']],atol=1e-12,rtol=0)
        for i in range(16):assert math.isclose(np.delete(a,i,axis=0)[:,j].mean(),e['leave_one'][i][k],abs_tol=1e-12)
    for field,out,values in [('direction','direction_points',['AB','BA']),('scenario_fold','scenario_points',['S1','S2'])]:
        for v in values:
            val=delta(trans['BACKGROUND'],**{field:v,'local_render':'C0A1'})-delta(trans['BACKGROUND'],**{field:v,'local_render':'C0A0'})
            assert math.isclose(val,e[out][v],abs_tol=1e-12)
    t=e['estimates']['T'];passed=t['value']>=.05 and t['low']>0 and all(v>0 for v in e['direction_points'].values()) and all(v>0 for v in e['scenario_points'].values()) and all(v['T']>0 for v in e['leave_one'])
    label='NONCOMMA_MODULATION_SUPPORTED_IN_DEVELOPMENT' if passed else 'REVERSED_NONCOMMA_MODULATION' if t['high']<0 else 'NOT_MET_OR_UNCERTAIN'
    assert e['label']==label and e['PRACTICALLY_SMALL_UNDER_THIS_DESIGN']==(t['low']>=-.025 and t['high']<=.025)
strata=read(E/'STRATA.json')
for x in strata:
    rr=[r for r in science if all(r[k]==x[k] for k in ['model','construction','schema','local_render','background'])]
    assert len(rr)==x['n']==64 and dict(Counter(r['detail'] for r in rr))==x['counts']
    assert sum(r['score']=='C' for r in rr)==x['C']==x['H_ROLE_fit'] and sum(r['answer']==r['H_COPY'] for r in rr)==x['H_COPY_fit']
for m in stats:
    hc=[x['C'] for x in strata if x['model']==m and x['construction']=='BEI' and x['schema']=='AU' and x['background']!='NONE' and x['local_render'] in ['C0A0','C0A1']]
    assert len(hc)==4 and stats[m]['headroom_C_counts']==hc and stats[m]['LOW_HEADROOM']==all(v>=63 for v in hc)
for x in read(E/'COPY-FIT.json'):
    rr=[r for r in science if r['model']==x['model'] and (r['gold']!=r['H_COPY'])==x['copy_role_conflict'] and (x['detail']=='ALL' or r['detail']==x['detail'])]
    assert len(rr)==x['n'] and sum(r['answer']==r['gold'] for r in rr)==x['H_ROLE_fit'] and sum(r['answer']==r['H_COPY'] for r in rr)==x['H_COPY_fit']
assert {r['call_id'] for r in read(E/'ALL-UNRESOLVED.json')}=={r['call_id'] for r in science if r['score']=='U'}
assert {r['call_id'] for r in read(E/'ALL-FIELD-UNRESOLVED.json')}=={r['call_id'] for r in science if 'U' in r['field_scores'].values()}
field_summary={m:dict(rows_with_field_U=sum('U' in r['field_scores'].values() for r in science if r['model']==m),aggregate_W_with_field_U=sum('U' in r['field_scores'].values() and r['score']=='W' for r in science if r['model']==m),string_null=sum(any(v=='null' for v in r['answer'].values()) for r in science if r['model']==m),true_null=sum(any(v is None for v in r['answer'].values()) for r in science if r['model']==m)) for m in stats}
assert field_summary==read(E/'FIELD-UNRESOLVED-SUMMARY.json')

print('B70 public score, all seven pair sets, G4, seventeen estimates, bootstrap, LOO and strata PASS')
