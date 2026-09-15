"""Offline audit of released model outputs. Requires numpy, performs no model calls."""
import json,gzip,collections,hashlib
from pathlib import Path
import numpy as np
from score_public import score
P=Path(__file__).resolve().parent
load=lambda n:json.loads((P/n).read_text())
def rows(n):return [json.loads(l) for l in gzip.decompress((P/n).read_bytes()).splitlines()]
def audit():
 allrows=[]
 for batch in ['B71','B72']:
  refs={x['call_id']:x for x in rows(batch+'/REFERENCES.jsonl.gz')};raw=rows(batch+'/RAW-OUTPUTS.jsonl.gz');saved={x['call_id']:x for x in rows(batch+'/SCORES.jsonl.gz')}
  assert len(refs)==len(raw)==len(saved)==len({x['call_id'] for x in raw})
  for r in raw:
   ref=refs[r['call_id']];s=score(r['generated_text'],ref)
   assert all(s[k]==v for k,v in saved[r['call_id']].items() if k!='call_id')
   assert r['generated_token_ids'] and r['finish_reason']=='EOS'
   first,second=sorted(ref['gold'].values(),key=ref['R1'].index)
   mid=ref['R1'].split(first,1)[1].split(second,1)[0]
   assert mid==('把' if ref['construction']=='BA' else '被')
   derived={'actor':first,'undergoer':second} if mid=='把' else {'actor':second,'undergoer':first};assert derived==ref['gold']
   allrows.append({**ref,**s})
 expected=load('SUMMARY.json');strata=load('STRATA.json');effects=load('BACKGROUND-EFFECTS.json');group_saved=load('GROUP-CONTRIBUTIONS.json')
 for e in expected:
  key='|'.join(e[k] for k in ['batch','contract','model']);rs=[x for x in allrows if all(x[k]==e[k] for k in ['batch','contract','model'])]
  assert len(rs)==e['n']==576
  for k in ['C','R','U','format_ok']:assert sum(x[k] for x in rs)==e[k]
  assert sum(x['C'] and x['format_ok'] for x in rs)==e['C_and_format']
  for co,sc,bg in sorted({(x['construction'],x['schema'],x['background']) for x in rs}):
   ss=[x for x in rs if (x['construction'],x['schema'],x['background'])==(co,sc,bg)];v=strata[key+'|'+co+'|'+sc+'|'+bg];assert len(ss)==v['n']==48
   for k in ['C','R','U','format_ok']:assert sum(x[k] for x in ss)==v[k]
   assert sum(x['C'] and x['format_ok'] for x in ss)==v['C_and_format']
  target=[x for x in rs if x['construction']=='BEI' and x['schema']=='AU'];units=sorted({x['unit_id'] for x in target});v=[]
  for u in units:
   b=[x for x in target if x['unit_id']==u and x['background']!='NONE'];n=[x for x in target if x['unit_id']==u and x['background']=='NONE'];assert len(b)==4 and len(n)==2
   v.append(np.mean([x['R'] for x in b])-np.mean([x['R'] for x in n]))
  assert dict(zip(units,v))==group_saved[key];v=np.array(v);ef=effects[key];assert len(v)==24
  boot=np.random.default_rng(ef['seed']).integers(0,24,size=(10000,24));assert np.allclose(np.quantile(v[boot].mean(1),[.025,.975]),ef['ci95']);assert np.isclose(v.mean(),ef['mean']);assert np.allclose([(v.sum()-z)/23 for z in v],ef['loo'])
 idx={x['call_id']:x for x in allrows}
 for p in load('K0-K1-TRANSITIONS.json'):
  a,b=idx[p['before']],idx[p['after']];assert bool(not a['C'] and b['C'])==p['rescue'];assert bool(a['C'] and not b['C'])==p['harm'];assert a['answer']==p['old_answer'] and b['answer']==p['new_answer']
 q=[x for x in allrows if x['batch']=='B72' and x['contract']=='K1' and x['model']=='qwen'];target=[x for x in q if x['construction']=='BEI' and x['schema']=='AU' and x['background']!='NONE'];others=[x for x in q if not(x['construction']=='BEI' and x['schema']=='AU')];none=[x for x in q if x['background']=='NONE']
 cells=collections.defaultdict(list)
 for x in others:cells[x['construction'],x['schema'],x['background']].append(x)
 checks={'reverse_compatible':abs(sum(x['R'] for x in target)/96-21/96)<=.1,'other_cells':all(sum(x['C'] for x in rs)>=46 for rs in cells.values()),'NONE':sum(x['C'] for x in none)/192>=.9,'U':sum(x['U'] for x in q)/576<=.02}
 assert checks==load('B72/P0-GATE.json')['checks'];assert all(checks.values())==load('B72/P0-GATE.json')['behavior_pass']==False
 return {'science_outputs':len(allrows),'score_strata_cluster_CI_LOO_and_K0_K1_transitions':'PASS','P0_gate':'FAILED_AS_FROZEN','human_validation':False}
if __name__=='__main__':print(json.dumps(audit(),indent=2))
