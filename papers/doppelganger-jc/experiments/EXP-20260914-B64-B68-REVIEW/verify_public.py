"""Verify this public export offline. Requires Python 3 and NumPy; no model calls.

This verifies the stated scope, not human semantic validity, GPU numerical
reproduction, private Office contents, or unexported full-vocabulary logits.
"""
from pathlib import Path
from collections import Counter
import gzip, hashlib, importlib.util, json, math, numbers, sys
import numpy as np

ROOT=Path(__file__).resolve().parent
EXPECTED={64:3120,65:1312,66:4640,67:3872,68:4640}
def read(p): return json.loads(p.read_text())
def rows(p): return [json.loads(x) for x in gzip.decompress(p.read_bytes()).splitlines()]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b,path='root'):
    if isinstance(a,dict):
        assert isinstance(b,dict) and set(a)==set(b), (path,'keys')
        for k in a: close(a[k],b[k],path+'.'+k)
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b),(path,'length')
        for i,(x,y) in enumerate(zip(a,b)):close(x,y,f'{path}[{i}]')
    elif isinstance(a,numbers.Real) and not isinstance(a,(bool,np.bool_)):
        assert math.isclose(a,b,rel_tol=0,abs_tol=1e-12),(path,a,b)
    else: assert a==b,(path,a,b)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def reverse(a):return {'actor':a['undergoer'],'undergoer':a['actor']}
def inspect_pairs(obj,refs,scores):
    total=0
    if isinstance(obj,list):
        return sum(inspect_pairs(x,refs,scores) for x in obj)
    if not isinstance(obj,dict):return 0
    for left,right in [('before_id','after_id'),('left_id','right_id'),('mismatched','matched'),('mismatched_id','matched_id')]:
        if left not in obj or right not in obj:continue
        a,b=obj[left],obj[right];assert a in refs and b in refs
        assert refs[a]['model']==refs[b]['model']
        aa,bb=scores[a]['assessment'],scores[b]['assessment'];ac,bc=int(aa['score']=='C'),int(bb['score']=='C')
        values={'before_C':ac,'after_C':bc,'delta_C':bc-ac,'D':bc-ac,'both_C':ac*bc,
                'mapping_equal':int(aa['answer']==bb['answer']),
                'both_wrong':int(aa['score']==bb['score']=='W'),
                'both_known_wrong':int(aa['score']==bb['score']=='W'),
                'rescue':int(not ac and bc),'harm':int(ac and not bc),
                'U_involved':int('U' in (aa['score'],bb['score']))}
        for k,v in values.items():
            if k in obj: assert obj[k]==v,(left,k,a,b,obj[k],v)
        if 'before' in obj: assert obj['before']==scores[a]['detail']
        if 'after' in obj: assert obj['after']==scores[b]['detail']
        if 'matched_C' in obj: assert obj['matched_C']==bc and obj['mismatched_C']==ac
        return 1
    return sum(inspect_pairs(v,refs,scores) for v in obj.values())

def component_statistics(n,p,refs,scores):
    core=load(f'analysis_core_b{n}',p/'analysis_core.py')
    transitions=read(p/'TRANSITIONS.json')['BACKGROUND']
    assert len(transitions)==1536
    assert len({(x['before_id'],x['after_id']) for x in transitions})==1536
    pairs=[]
    for t in transitions:
        a,b=refs[t['before_id']],refs[t['after_id']]
        assert a['R1']==b['R1'] and a['gold']==b['gold'] and a['background_gold']==b['background_gold']
        assert a['background']!=a['construction'] and b['background']==b['construction']
        pairs.append((a,b,int(scores[b['call_id']]['assessment']['score']=='C')-int(scores[a['call_id']]['assessment']['score']=='C')))
    axes=('target_render','background_render') if n==67 else ('frame_render','local_render')
    frozen=read(p/'STATISTICS.json');strata=read(p/'STRATA.json')
    for model in ('qwen','apertus'):
        for layer in (None,'BA_AU','BA_UA','BEI_AU','BEI_UA'):
            arrays=[]
            for cohort in ('M63','M65'):
                table=[]
                for g in range(1,25):
                    row=[]
                    for f,l in [('O','O'),('O','N'),('N','O'),('N','N')]:
                        vals=[d for a,b,d in pairs if a['model']==model and a['unit_id']==f'{cohort}-G{g:02d}' and a[axes[0]]==f and a[axes[1]]==l and (layer is None or a['construction']+'_'+a['schema']==layer)]
                        assert len(vals)==(4 if layer is None else 1)
                        row.append(np.mean(vals))
                    table.append(row)
                arrays.append(np.array(table))
            actual=core.summarize(*arrays)
            close(actual,frozen[model] if layer is None else strata[model][layer],f'B{n}.{model}.{layer}')
    return 'All group contrasts, bootstrap intervals, leave-one summaries, flags and four strata reproduced'

def main():
    manifest=read(ROOT/'PUBLIC-FILES-SHA256.json')
    actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='PUBLIC-FILES-SHA256.json'}
    assert actual==set(manifest),'Public file set differs from manifest'
    for name,info in manifest.items():
        p=ROOT/name;assert sha(p)==info['sha256'] and p.stat().st_size==info['bytes'],name
    report={};previous=None
    for n,total in EXPECTED.items():
        p=ROOT/f'B{n}'
        refs_list=rows(p/'REFERENCES.jsonl.gz');raw_list=rows(p/'RAW-OUTPUTS.jsonl.gz');sc_list=rows(p/'SCORES.jsonl.gz')
        refs={r['call_id']:r for r in refs_list};raw={r['call_id']:r for r in raw_list};scores={r['call_id']:r for r in sc_list}
        assert len(refs_list)==len(raw_list)==len(sc_list)==len(refs)==len(raw)==len(scores)==total
        assert set(refs)==set(raw)==set(scores)
        for mod in ['scoring_b62','scoring_b61','scoring_b39_frozen','parse_readout','background_bounds']:
            sys.modules.pop(mod,None)
        sys.path.insert(0,str(p));scorer=load(f'score_adapter_b{n}',p/'score_adapter.py')
        kinds=Counter()
        for cid,r in refs.items():
            o,s=raw[cid],scores[cid];a=scorer.score_record(o['generated_text'],r)
            close(a,s['assessment'],cid+'.assessment')
            ans=a['answer'];label=a['score'];bg=r.get('background_gold')
            detail=('C' if label=='C' else ('R' if n==64 else 'R1_REVERSE') if ans==reverse(r['gold']) else 'U' if label=='U' else 'BG_C' if bg and ans==bg else 'BG_R' if bg and ans==reverse(bg) else 'MIXED_OTHER_W')
            assert detail==s['detail'],(cid,detail,s['detail'])
            if 'input_token_n' in o: assert len(o['input_ids'])==o['input_token_n']
            if 'generated_token_n' in o: assert len(o['generated_token_ids'])==o['generated_token_n']
            if 'row_forward_n' in o: assert len(o['generated_token_ids'])==o['row_forward_n']
            if r['material_set']!='BRIDGE': kinds[r['model']+':'+detail]+=1
        sys.path.pop(0)
        npairs=0
        for name in ['TRANSITIONS','ALL-PAIRS','PAIR-MAP','PAIR-MAPS','PAIRS','NONE-PAIRS','ALL-HARMS']:
            if (p/(name+'.json')).exists():npairs+=inspect_pairs(read(p/(name+'.json')),refs,scores)
        bridges=read(p/'BRIDGE-EXPECTED.json')
        for cid,v in bridges.items():
            assert cid in raw
            for k in ('generated_text','generated_token_ids'):
                if k in v:assert raw[cid][k]==v[k],(n,cid,k)
        replay_n=0
        if previous:
            old_refs,old_raw=previous
            for cid,r in refs.items():
                source=r.get('historical_reference_id') or (r.get(f'source_b{n-1}_id') if r['material_set']=='BRIDGE' else None)
                if source and source in old_raw:
                    assert r['messages']==old_refs[source]['messages']
                    for k in ('generated_text','generated_token_ids'): assert raw[cid][k]==old_raw[source][k]
                    replay_n+=1
        extra={}
        if n==65:
            pairmap=read(p/'PAIR-MAP.json');stats=read(p/'STATISTICS.json')
            for model in ('qwen','apertus'):
                ps=[x for x in pairmap if x['model']==model];assert len(ps)==192
                d=np.mean([int(scores[x['matched']]['assessment']['score']=='C')-int(scores[x['mismatched']]['assessment']['score']=='C') for x in ps])
                close(float(d),stats[model]['overall']['D'])
                extra[model+'_D']=float(d)
        if n in (67,68):extra['full_component_statistics']=component_statistics(n,p,refs,scores)
        report[f'B{n}']={'natural_outputs':total,'scientific_error_counts':dict(kinds),'paired_records_checked_including_repeated_views':npairs,'bridge_count':len(bridges),'exact_prior_replays_checked':replay_n,**extra}
        previous=(refs,raw)
    print(json.dumps({'status':'PASS','public_files_hashed':len(manifest),'natural_outputs':sum(EXPECTED.values()),'batches':report,'limits':'No model rerun, independent human validation, private Office inspection or full-vocabulary/hidden-state reproduction.'},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
