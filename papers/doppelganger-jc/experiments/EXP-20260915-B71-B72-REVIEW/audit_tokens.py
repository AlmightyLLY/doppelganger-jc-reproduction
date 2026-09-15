"""Replay the recorded token decisions offline; does not reload model weights."""
import json,gzip,collections,math
from pathlib import Path
P=Path(__file__).resolve().parent
def rd(n):return [json.loads(l) for l in gzip.decompress((P/n).read_bytes()).splitlines()]
def audit():
 counts={}
 for batch in ['B71','B72']:
  raw=rd(batch+'/RAW-OUTPUTS.jsonl.gz');steps=collections.defaultdict(list)
  for s in rd(batch+'/NATURAL-STEPS.jsonl.gz'):steps[s.get('id',s.get('call_id'))].append(s)
  for r in raw:
   ss=steps[r['call_id']];ids=r['generated_token_ids'];prefix=r['input_ids'];assert len(ids)<=128 and r['finish_reason']=='EOS';assert ids[-1] in ([2,68,72] if r['model']=='apertus' else [151643,151645])
   if batch=='B71':
    before=[s for s in ss if s['phase']=='BEFORE'];after=[s for s in ss if s['phase']!='BEFORE'];assert len(before)==len(after)==len(ids)
    for i,(b,a) in enumerate(zip(before,after)):
     assert a['step']==b['step']==i and b['input_ids']==prefix+ids[:i] and a['generated_token_ids']==ids[:i+1];assert a['argmax']==ids[i] and a['finite'];assert math.isfinite(a['chosen_logit']) and math.isfinite(a['top1_top2_margin']) and a['top1_top2_margin']>=0
   else:
    assert len(ss)==len(ids)
    for i,s in enumerate(ss):assert s['step']==i and s['input_ids']==prefix+ids[:i] and s['token']==s['argmax']==ids[i] and s['finite'] and math.isfinite(s['top2_margin']) and s['top2_margin']>=0
  counts[batch]={'outputs':len(raw),'natural_forwards':sum(len(r['generated_token_ids']) for r in raw),'all_recorded_prefixes_argmax_finite_EOS':'PASS'}
 return counts
if __name__=='__main__':print(json.dumps(audit(),indent=2))
