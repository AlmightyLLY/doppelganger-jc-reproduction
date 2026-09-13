"""Offline reproduction only. No network, model loading, or B64 execution."""
import gzip,json,hashlib,sys
from pathlib import Path
P=Path(__file__).resolve().parent
def load(rel):return json.loads((P/rel).read_text())
def rows(rel):return [json.loads(x) for x in gzip.decompress((P/rel).read_bytes()).decode().splitlines()]
def verify():
 manifest=load('PUBLIC-FILES-SHA256.json')
 for rel,v in manifest['files'].items():
  raw=(P/rel).read_bytes()
  assert len(raw)==v['bytes'] and hashlib.sha256(raw).hexdigest()==v['sha256'],rel
 sys.path.insert(0,str(P/'B63'))
 from analyze_b63_v2 import analyze
 from analyze_b63 import analyze as original_analyze
 refs=rows('B63/REFERENCES.jsonl.gz');raw=rows('B63/RAW-OUTPUTS.jsonl.gz');scores=rows('B63/SCORES.jsonl.gz')
 assert len(refs)==len(raw)==len(scores)==4656
 assert sum(r['row_forward_n'] for r in raw)==78721
 computed=analyze(refs,raw)
 for name in ['ALL-PAIRS','STATISTICS','E-STATISTICS','TRANSITIONS','COUNTS']:
  assert computed[name]==load('B63/'+name+'.json'),name
 for k,v in computed['SUMMARY'].items():assert load('B63/SUMMARY.json')[k]==v,k
 index={r['call_id']:r for r in computed['SCORED-RESULTS']}
 for r in scores:
  for k,v in r.items():assert index[r['call_id']][k]==v,(r['call_id'],k)
 original=original_analyze(refs,raw)
 assert original['SUMMARY']==load('B63/SUMMARY-V1.json')
 assert original['E-STATISTICS']==load('B63/E-STATISTICS-V1.json')
 proposed=rows('B64/PROPOSED-INPUTS.jsonl.gz');status=load('B64/STATUS.json')
 assert len(proposed)==len({r['call_id'] for r in proposed})==3120
 assert status['actual_model_calls']==0 and not status['execution_authorized'] and not status['dispatch_authorized']
 assert all(r['run_status']=='NOT_RUN' for r in proposed)
 print(json.dumps({'status':'PASS','hashes':len(manifest['files']),'recomputed_b63_outputs':len(raw),'recomputed_pairs':len(computed['ALL-PAIRS']),'b64_proposed_inputs':len(proposed),'b64_actual_calls':0,'independent_human_gold':0},indent=2))
if __name__=='__main__':verify()
