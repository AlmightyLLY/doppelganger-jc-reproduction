"""Offline verification of the B69/B70 additions; Python 3 + NumPy, zero model calls.

Audits scores, all paired behavioral quantities and frozen group statistics.
Does not certify human material validity, rerun models, or inspect private Office.
Historical B63-B68 packages have separate supported verifiers.
"""
from pathlib import Path
import gzip,hashlib,json,runpy,sys
ROOT=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
read=lambda p:json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in gzip.decompress(p.read_bytes()).splitlines()]
manifest=read(ROOT/'PUBLIC-FILES-SHA256.json')
actual={str(p.relative_to(ROOT)) for p in ROOT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='PUBLIC-FILES-SHA256.json'}
assert actual==set(manifest),'File set differs from manifest'
for name,info in manifest.items():
 p=ROOT/name;assert p.stat().st_size==info['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==info['sha256'],name
batches={}
for b,n in [(69,3104),(70,6176)]:
 p=ROOT/f'B{b}'
 refs=rows(p/'REFERENCES.jsonl.gz');raw=rows(p/'RAW-OUTPUTS.jsonl.gz');scores=rows(p/'SCORES.jsonl.gz')
 assert len(refs)==len(raw)==len(scores)==n
 assert len({x['call_id'] for x in refs})==n
 assert {x['call_id'] for x in refs}=={x['call_id'] for x in raw}=={x['call_id'] for x in scores}
 batches[b]={x['call_id']:x for x in raw}
 runpy.run_path(str(p/'audit_public.py'),run_name='__main__')
cross={**read(ROOT/'B70/BRIDGE-CROSSWALK.json'),**read(ROOT/'B70/ENDPOINT-CROSSWALK.json')}
assert len(cross)==3104
for cid,hid in cross.items():
 for k in ['messages','source_text','rendered_prefix','input_ids','generated_text','generated_token_ids']:
  assert batches[70][cid][k]==batches[69][hid][k],(cid,k)
print(json.dumps(dict(status='PASS',public_files=len(manifest),natural_outputs=9280,B70_exact_B69_bridges_and_endpoints=len(cross),model_calls=0,human_gold=0,scope='New B69/B70 public files, all scores and paired contrasts, cluster statistics, historical endpoint equality. Existing snapshots unchanged; not GPU or human semantic validation.')))
