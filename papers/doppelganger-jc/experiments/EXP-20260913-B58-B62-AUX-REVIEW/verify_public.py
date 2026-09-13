"""Recompute public headline counts and B62 paired response; no model calls.

Run with Python 3 from any working directory. Optional NumPy is not required.
This checks public-data consistency, not semantic validity or independent human gold.
"""
from pathlib import Path
from collections import Counter,defaultdict
import json,gzip,hashlib
P=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text())
rows={}
for b,n in [('B58',1152),('B59',1088),('B60',1296),('B61',384),('B62',600)]:
    idx=load(P/b/'INDEX.json');data=[]
    for f in idx['files']:
        d=load(P/b/f['path']);assert len(d['rows'])==f['rows'];data+=d['rows']
    assert len(data)==n==idx['rows'] and len({r['call_id'] for r in data})==n
    assert Counter(r['content'] for r in data)==idx['content_counts']
    assert all(r['reference_status']=='AI_AUTHOR_REFERENCE_NOT_INDEPENDENT_HUMAN_GOLD' and r['human_review']=='PENDING' for r in data)
    rows[b]=data
assert sum(map(len,rows.values()))==4520
r62=[r for r in rows['B62'] if r['b62_kind']!='BRIDGE'];assert len(r62)==576
base=defaultdict(dict);bg=defaultdict(dict);none=defaultdict(dict)
for r in r62:
    ans=json.loads(r['generated_text']);correct=ans==r['gold'];assert correct==(r['content']=='C')
    base[r['base_test_id']][r['condition']]=r
    k=(r['condition'],r['group_id'],r['construction'],r['schema'])
    if r['b62_kind']=='MAIN_BACKGROUND':bg[k][r['background']]=r
    else:none[k][r['b62_kind']]=r
assert len(base)==192
primary={};cal={};trans={}
for c in ['ZERO','DEMO_F','DEMO_R']:
    primary[c]=sum(all(r['content']=='C' for r in v.values()) for k,v in bg.items() if k[0]==c and (k[2],k[3]) in [('BA','UA'),('BEI','AU')])
    cal[c]=sum(all(r['content']=='C' for r in v.values()) for k,v in none.items() if k[0]==c)
for c in ['DEMO_F','DEMO_R']:
    trans[c]={'rescue':sum(v['ZERO']['content']!='C' and v[c]['content']=='C' for v in base.values()),'harm':sum(v['ZERO']['content']=='C' and v[c]['content']!='C' for v in base.values())}
assert primary=={'ZERO':19,'DEMO_F':24,'DEMO_R':24}
assert cal=={'ZERO':47,'DEMO_F':48,'DEMO_R':48}
assert all(v=={'rescue':10,'harm':0} for v in trans.values())
r60={r['call_id']:r for r in rows['B60']}
bridges=[r for r in rows['B62'] if r['b62_kind']=='BRIDGE'];assert len(bridges)==24
for r in bridges:
    o=r60[r['parent_b60_call_id']]
    for k in ['messages','input_ids','generated_text','generated_token_ids']:assert r[k]==o[k]
a=P/'AUX';native=load(a/'BASELINE-RESULTS.json');assert Counter(r['category'] for r in native)=={'C':30,'R':18}
refs={r['call_id']:r for r in load(a/'inputs.json')['rows']};r61={r['call_id']:r for r in rows['B61']}
for r in native:
    assert r['generated_ids']==r61[refs[r['input_id']]['parent_b61_id']]['generated_token_ids']
with gzip.open(a/'PROBE-PREDICTIONS.jsonl.gz','rt') as f:
    pred_n=0
    for line in f:
        r=json.loads(line);ref=refs[r['input_id']];assert r['label']==ref['y_A_actor']==int(ref['gold']['actor']==ref['entity_map']['A'])
        assert r['fold']==ref['group_id'] and r['correct']==int(r['prediction']==r['label']);pred_n+=1
assert pred_n==278976
with gzip.open(a/'LENS.jsonl.gz','rt') as f:assert Counter(json.loads(l)['kind'] for l in f)=={'TEACHER_FORCED':19008,'NATIVE':1584}
readlines=lambda p:[json.loads(x) for x in p.read_text().splitlines()]
caldir=a/'CAL02';scores=readlines(caldir/'SCORES.jsonl');bas={r['candidate_id']:r for r in scores if r['task']=='CANDIDATE_BASE'};sels=[r for r in scores if r['task']=='SELF_CANDIDATE']
assert len(bas)==16 and len(sels)==64
for r in sels:assert r['token_logps']==bas[r['candidate_id']]['token_logps'] and r['equal'] and r['max_logit_abs']==r['max_logp_abs']==0
gens=readlines(caldir/'GENERATIONS.jsonl');gbase={r['input_id']:r for r in gens if r['task']=='GEN_BASE'}
assert len(gens)==20 and len(gbase)==8
for r in gens:assert r['generated_ids']==gbase[r['input_id']]['generated_ids']
assert all(r['tokens_equal'] for r in load(caldir/'BEHAVIOR-COMPARISON.json'))
manifest=P/'PUBLIC-FILES-SHA256.json'
if manifest.exists():
    for f in load(manifest)['files']:
        b=(P/f['path']).read_bytes();assert len(b)==f['bytes'] and hashlib.sha256(b).hexdigest()==f['sha256']
print(json.dumps({'status':'PASS_PUBLIC_DATA_CONSISTENCY','formal_B_rows':4520,'B62_P':primary,'B62_NONE':cal,'B62_transitions':trans,'B62_exact_bridges':24,'AUX_native':48,'AUX_probe_predictions':pred_n,'CAL02_exact_SELF_candidates':64,'human_gold':0}))
