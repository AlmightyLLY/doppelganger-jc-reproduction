"""B65 post-run analysis. Requires complete preserved natural outputs; no model calls."""
from pathlib import Path
import json,collections,itertools
from score_adapter import score_record
from background_bounds import bounds
from analysis_core import all_strata
P=Path(__file__).resolve().parent
def analyze(refs,outputs,pairs):
 raw={r['call_id']:r for r in outputs};assert len(raw)==len(outputs)==len(refs)==1312
 scored=[];scores={}
 for r in refs:
  out=raw[r['call_id']];assert out['messages']==r['messages']
  s=score_record(out['generated_text'],r);a=s['answer'];gold=r['gold'];bg=r.get('background_gold');rev=lambda x:dict(actor=x['undergoer'],undergoer=x['actor'])
  kind='C' if s['score']=='C' else 'R1_REVERSE' if a==rev(gold) else 'U' if s['score']=='U' else 'BG_C' if bg and a==bg else 'BG_R' if bg and a==rev(bg) else 'MIXED_OTHER_W'
  row=dict(r);row.update(out);row.update(assessment=s,detail=kind,background_evidence=bounds(out['generated_text'],r));scored.append(row);scores[r['call_id']]=s
 statistics=all_strata(pairs,scores);index={r['call_id']:r for r in scored};transitions=[]
 for pair in pairs:
  a,b=index[pair['mismatched']],index[pair['matched']]
  transitions.append(dict(pair,before=a['detail'],after=b['detail'],rescue_known_wrong=a['assessment']['score']=='W' and b['detail']=='C',harm_known_wrong=a['detail']=='C' and b['assessment']['score']=='W',lost_complete=a['detail']=='C' and b['detail']!='C',gained_complete=a['detail']!='C' and b['detail']=='C',unknown_involved='U' in [a['detail'],b['detail']]))
 new=[r for r in scored if r['stage']!='BRIDGE']
 # Raw stage A is transport metadata, so scientific bridge identity uses references.
 new=[r for r in scored if r['material_set']!='BRIDGE'];assert len(new)==1280
 counts=[]
 for model in ['qwen','apertus']:
  for frame in ['ALL','DIRECT','QUOTED']:
   for layer in ['ALL','BA_AU','BA_UA','BEI_AU','BEI_UA']:
    for material in ['ALL','MAIN_BACKGROUND','NONE_ORIGINAL','NONE_SWAPPED']:
     rr=[r for r in new if r['model']==model and (frame=='ALL' or r['frame']==frame) and (layer=='ALL' or r['construction']+'_'+r['schema']==layer) and (material=='ALL' or r['material_set']==material)]
     counts.append(dict(model=model,frame=frame,layer=layer,material=material,n=len(rr),counts=dict(collections.Counter(r['detail'] for r in rr)),format_ok_n=sum(r['assessment']['format_ok'] for r in rr)))
 none=[]
 for r in new:
  if r['material_set']!='NONE_SWAPPED':continue
  original=index[r['call_id'].removesuffix('-SWAPPED')];a,b=original['assessment'],r['assessment']
  none.append(dict(model=r['model'],group_id=r['group_id'],frame=r['frame'],construction=r['construction'],schema=r['schema'],original_id=original['call_id'],swapped_id=r['call_id'],original_detail=original['detail'],swapped_detail=r['detail'],joint_correct=int(a['score']=='C' and b['score']=='C'),joint_upper=int(a['score']!='W' and b['score']!='W'),mapping_equal=a['answer'] is not None and a['answer']==b['answer'],both_known_wrong=a['score']=='W' and b['score']=='W'))
 assert len(none)==128
 summary=dict(status='COMPLETE_NATURAL_ANALYSIS',natural_outputs=1312,new_outputs=1280,models={m:{k:v for k,v in statistics[m]['overall'].items() if k not in ['pairs','group_contributions','leave_one']} for m in statistics},two_model_direction_replication=all(statistics[m]['overall']['label']=='SUPPORTED' for m in statistics),independent_human_gold=0,independent_material_review='NOT_COMPLETED_AT_RELEASE',evidence_identity='development prospective replication; not independent confirmation')
 return dict(SUMMARY=summary,SCORED_RESULTS=scored,STATISTICS=statistics,TRANSITIONS=transitions,COUNTS=counts,NONE_PAIRS=none)
if __name__=='__main__':
 refs=json.loads((P/'AUTHOR-REFERENCES.json').read_text());pairs=json.loads((P/'PAIR-MAP.json').read_text());outs=[]
 for m in ['qwen','apertus']:
  path=P/f'retrieved/run_{m}/ROWS.partial.jsonl';outs.extend(json.loads(line) for line in path.read_text().splitlines())
 for n,x in analyze(refs,outs,pairs).items():(P/(n.replace('_','-')+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2))
