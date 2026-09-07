import json,sys,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
import remote_batch as core
rows=[json.loads(s) for s in (R/'OUTPUTS.jsonl').read_text().splitlines()]
seen=set();verified=[]
for info in core.E['models']:
 tok,expected,_=core.inputs(info);mapping={p['prompt_id']:p for p in expected}
 for row in [r for r in rows if r['model']==info['key']]:
  assert row['trace_id'] not in seen;seen.add(row['trace_id'])
  for k,v in mapping[row['prompt_id']].items():assert row[k]==v,(row['trace_id'],k)
  out=row['output_token_ids'];ids=row['input_token_ids']
  assert tok.decode(out,skip_special_tokens=True)==row['raw_output']
  assert tok.decode(out,skip_special_tokens=False)==row['output_full_decode']
  assert tok.decode(ids+out,skip_special_tokens=False)==row['full_sequence_decode']
  assert len(out)==row['output_token_n']<=256
  verified.append(row['trace_id'])
complete=core.read(R/'COMPLETE.json')
assert len(rows)==144==complete['outputs'] and complete['attempts']<=156 and complete['wall_seconds']<=3600
events=[json.loads(s) for s in (R/'ATTEMPTS.jsonl').read_text().splitlines()]
assert len([e for e in events if e['event']=='START'])==complete['attempts']
assert len([e for e in events if e['event']=='SUCCESS'])==144
assert core.read(R/'PREGENERATION-GATE.json')['at']<core.read(R/'INFERENCE-START.json')['at']
core.save('CPU-REPLAY-VERIFICATION.json',dict(status='PASS',at=core.now(),verified_outputs=len(verified),all_input_messages_native_render_token_ids_and_decodes=True,attempts=complete['attempts'],new_generation_calls=0,outputs_sha256=core.sha(R/'OUTPUTS.jsonl')))
core.save('RESOURCE-RELEASE.json',dict(at=core.now(),gpu=core.gpu(),processes=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],text=True)))
print(json.dumps(dict(status='PASS',outputs=len(verified),new_generation_calls=0)))
