"""Prospective visible-map content and strict-name analysis for B13."""
from pathlib import Path
from collections import Counter
import json,re,copy,argparse,datetime,hashlib
import score_b09 as frozen
P=Path(__file__).resolve().parent
COMP=['occurrence','role_a','role_b'];FORMS=['JA_ACTIVE','JA_PASSIVE','ZH_ACTIVE']
def rd(n):return json.loads((P/n).read_text())
def score(text,c,ref):
 strict=frozen.score(text,c,ref);content=copy.deepcopy(strict)
 for comp,k in zip(['role_a','role_b'],c['role_keys']):
  v=strict['raw_fields'][k];person=c['visible_id_map'].get(v,v) if isinstance(v,str) else None
  person=person if person in c['entity_map'].values() else None
  content['decoded_names'][comp]=person
  content['labels'][comp]='U' if person is None else 'C' if person==ref[comp] else 'W'
 outside=re.sub(r'\s+','',strict['outside_json_text']).lower()
 wrapper_ok=outside in ('','```json```','``````') and not strict['extra_keys']
 if not wrapper_ok:
  # Do not silently ignore semantic assertions outside the complete object.
  for k in COMP:
   if content['labels'][k]=='C':content['labels'][k]='U'
 content['labels']['participant']=frozen.combine(*(content['labels'][k] for k in ['role_a','role_b']))
 content['labels']['record']=frozen.combine(content['labels']['occurrence'],content['labels']['participant'])
 return dict(strict=strict,content=content,visible_map_used=c['visible_id_map'],outside_wrapper_allowed=wrapper_ok,
  name_representation_compliant=all(strict['raw_fields'][k] is None or strict['raw_fields'][k] in c['entity_map'].values() for k in c['role_keys']))
def tally(rr,key):return {k:dict(Counter(r['observation'][key]['labels'][k] for r in rr)) for k in ['record',*COMP]}
def compute(rows):
 ix={r['call_id']:r for r in rows};assert len(ix)==len(rows)==384
 pp=[]
 for p in rd('PAIRED-PLAN.json'):
  a,b=ix[p['old_call_id']],ix[p['new_call_id']];oa,ob=a['observation'],b['observation']
  transitions={z:{k:oa[z]['labels'][k]+'->'+ob[z]['labels'][k] for k in ['record',*COMP]} for z in ['strict','content']}
  harms=[k for k in COMP if oa['content']['labels'][k]=='C' and ob['content']['labels'][k]!='C']
  both=oa['content']['labels']['record']==ob['content']['labels']['record']=='C'
  pp.append({**p,'model':a['model'],'domain':a['domain'],'source_form':a['source_form'],'inventory':a['inventory'],'pair_names':a['pair_names'],
   'old_source_text':a['source_text'],'new_source_text':b['source_text'],'old_raw_output':a['raw_output'],'new_raw_output':b['raw_output'],
   'transitions':transitions,'any_new_component_harm':harms,'both_correct_to_own_reference':both,
   'hidden_harm_record_WW':transitions['content']['record']=='W->W' and bool(harms)})
 grids=[]
 for m in ['qwen','llama']:
  for f in FORMS:
   for inv in ['ID_TABLE','NAME_ONLY']:
    rr=[r for r in rows if (r['model'],r['source_form'],r['inventory'])==(m,f,inv)];assert len(rr)==32
    pos=sum(r['fact']=='YES' and r['observation']['content']['labels']['record']=='C' for r in rr)
    neg=sum(r['fact']=='NO' and r['observation']['content']['labels']['record']=='C' for r in rr)
    grids.append(dict(model=m,source_form=f,inventory=inv,n=32,strict=tally(rr,'strict'),content=tally(rr,'content'),
     floor=dict(C=pos+neg,positive_C=pos,negative_C=neg,pass_floor=pos+neg>=30 and pos>=15 and neg>=15),
     name_representation_compliant=sum(r['observation']['name_representation_compliant'] for r in rr),format=dict(Counter(r['observation']['strict']['format_compliance'] for r in rr))))
 signals=[]
 for m in ['qwen','llama']:
  sub=[p for p in pp if p['model']==m and p['pair_type']=='INVENTORY'];assert len(sub)==96
  resc=[p for p in sub if p['transitions']['content']['record'] in ('W->C','U->C')]
  domains=sorted({p['domain'] for p in resc});names=sorted({tuple(p['pair_names']) for p in resc});harms=[p for p in sub if p['any_new_component_harm']]
  floor=all(g['floor']['pass_floor'] for g in grids if g['model']==m and g['inventory']=='NAME_ONLY')
  signals.append(dict(model=m,all_name_only_floors_pass=floor,rescue_pairs=[p['pair_id'] for p in resc],rescue_domains=domains,rescue_directed_names=names,
   harm_pairs=[p['pair_id'] for p in harms],pass_signal=floor and len(domains)==2 and len(names)>=2 and not harms,independent_confirmation=False))
 pairsummary=[]
 for kind in sorted({p['pair_type'] for p in pp}):
  for m in ['qwen','llama']:
   sub=[p for p in pp if p['pair_type']==kind and p['model']==m]
   if sub:pairsummary.append(dict(pair_type=kind,model=m,n=len(sub),both_correct=sum(p['both_correct_to_own_reference'] for p in sub),strict_transitions=dict(Counter(p['transitions']['strict']['record'] for p in sub)),content_transitions=dict(Counter(p['transitions']['content']['record'] for p in sub)),any_component_harm=sum(bool(p['any_new_component_harm']) for p in sub),hidden_harm=[p['pair_id'] for p in sub if p['hidden_harm_record_WW']]))
 bad=[r for r in rows if r['observation']['content']['labels']['record']!='C' or r['observation']['strict']['labels']['record']!='C' or r['observation']['strict']['format_compliance']!='PASS' or not r['observation']['name_representation_compliant']]
 return {'SUMMARY.json':dict(experiment_id='EXP-20260908-B13',positions=384,new_starts=360,old_cache=24,grids=grids,pair_summary=pairsummary,signals=signals,shared_signal=all(s['pass_signal'] for s in signals),all_content=tally(rows,'content'),all_strict=tally(rows,'strict'),nonC_or_noncompliant=len(bad),independent_human_gold=0,independent_confirmation=False,automatic_B14=False),
  'SCORES.AI.json':rows,'PAIRS.json':pp,'ALL-NONC-OR-NONCOMPLIANT.json':bad}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--raw',required=True);ap.add_argument('--output-dir',required=True);ap.add_argument('--all-raw-reviewed',action='store_true');args=ap.parse_args()
 raw=json.loads(Path(args.raw).read_text());raw=raw['rows'] if isinstance(raw,dict) else raw
 calls=rd('ALL-POSITIONS.json')['A'];new=rd('CALL-PLAN.json')['A'];refs={r['call_id']:r for r in rd('SCORING-REFERENCE.json')};cache=rd('CACHE24.json')
 assert len(raw)==len({r['call_id'] for r in raw})==360 and {r['call_id'] for r in raw}=={r['call_id'] for r in new}
 rawix={r['call_id']:r for r in raw};ci={r['call_id']:r for r in cache};out=[]
 for c in calls:
  r=rawix[c['call_id']] if c['execution_origin']=='NEW' else ci[c['call_id']]['prior_raw']
  assert r['messages']==c['messages'] and r['source_text']==c['source_text']
  obs=score(r['generated_text'],c,refs[c['call_id']]);obs['full_response_read']=args.all_raw_reviewed
  out.append({**c,'reference':refs[c['call_id']],'raw_output':r['generated_text'],'observation':obs,'actual_generation_call_id':r['call_id'],'new_forwards':r['row_forward_n'] if c['execution_origin']=='NEW' else 0})
 result=compute(out);result['SUMMARY.json'].update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),new_forwards=sum(r['row_forward_n'] for r in raw),all_raw_reviewed=args.all_raw_reviewed,new_raw_sha256=hashlib.sha256(Path(args.raw).read_bytes()).hexdigest(),cache_sha256=hashlib.sha256((P/'CACHE24.json').read_bytes()).hexdigest())
 op=Path(args.output_dir);op.mkdir(exist_ok=True,parents=True)
 for n,d in result.items():
  f=op/n;assert not f.exists();f.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['SUMMARY.json']['all_content'],ensure_ascii=False))
if __name__=='__main__':main()
