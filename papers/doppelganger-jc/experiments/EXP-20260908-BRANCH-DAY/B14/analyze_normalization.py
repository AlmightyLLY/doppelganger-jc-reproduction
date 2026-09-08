"""Frozen normalization analysis. Construct outputs first without reference access."""
from pathlib import Path
from collections import Counter
import json,argparse,hashlib,datetime
import pure_method
from score_b13_v2 import score
P=Path(__file__).resolve().parent
def rd(n):return json.loads((P/n).read_text())
def tally(rows):return {k:dict(Counter(r['observation']['content']['labels'][k] for r in rows)) for k in ['record','occurrence','role_a','role_b']}
def compute(raw,all_read=False):
 spec=rd('RUN-SPEC.json');new=rd('CALL-PLAN.json')['A'];assert len(raw)==len(new)==len({r['call_id'] for r in raw})==spec['new_calls_limit']
 rx={r['call_id']:r for r in raw};assert set(rx)=={c['call_id'] for c in new}
 for c in new:assert rx[c['call_id']]['messages']==c['messages'] and rx[c['call_id']]['source_text']==c['source_text']
 cache={r['position_id']:r for r in rd('BASELINE-CACHE.json')};refs=rd('SCORING-REFERENCE.json');position_refs={r['position_id']:r for r in refs['positions']};normrefs={r['call_id']:r for r in refs['normalized_calls']}
 bases=rd('BASELINE-CALLS.json');normcalls={c['call_id']:c for c in rd('NORMALIZED-CALLS.json')};trans=rd('TRANSFORM-PLAN.json');tx={x['position_id']:x for x in trans};method=rd('METHOD-PLAN.json');outputs=[];inverse_rows=[];base_rows=[];method_rows=[];norm_scores=[]
 for c in normcalls.values():
  r=rx[c['call_id']];obs=score(r['generated_text'],c,normrefs[c['call_id']]);obs['full_response_read']=all_read
  norm_scores.append({'call':c,'reference':normrefs[c['call_id']],'raw_output':r['generated_text'],'observation':obs,'new_forwards':r['row_forward_n']})
 # Output construction depends on raw strings and input-derived maps only.
 bx={c['position_id']:c for c in bases}
 for c in bases:
  r=cache[c['position_id']]['prior_raw'] if c['execution_origin']=='EXACT_OLD_CACHE' else rx[c['call_id']]
  assert r['messages']==c['messages'] and r['source_text']==c['source_text']
  base_rows.append({**c,'raw_output':r['generated_text'],'actual_generation_call_id':r['call_id'],'new_forwards':0 if c['execution_origin']=='EXACT_OLD_CACHE' else r['row_forward_n']})
 brx={r['position_id']:r for r in base_rows}
 for t in trans:
  rawout=rx[t['normalized_call_id']]['generated_text'];c=bx[t['baseline_position_id']]
  inverse=pure_method.invert(rawout,c['role_keys'],t['inverse_map'])
  inverse_rows.append({**t,'raw_normalized_output':rawout,'inverse':inverse,'raw_output':inverse['derived_output'],'actual_generation_call_id':t['normalized_call_id'],'new_forwards':0,'forward_accounting':'Shared unique generation counted only in normalized call ledger'})
 irx={r['position_id']:r for r in inverse_rows}
 for m in method:
  b=brx[m['baseline_position_id']];a,z=[irx[k] for k in m['mapping_position_ids']];chosen=pure_method.choose(b['raw_output'],a['inverse'],z['inverse'])
  method_rows.append({**m,'raw_output':chosen['output'],'decision':chosen,'new_forwards':0,'identity':'RULE_DERIVED_NOT_MODEL_OUTPUT'})
 # Reference-dependent scoring starts only after all method answers are fixed.
 for group in [base_rows,inverse_rows,method_rows]:
  for r in group:
   c=bx[r['position_id'] if r['kind']=='BASELINE' else r['baseline_position_id']];ref=position_refs[r['position_id']];obs=score(r['raw_output'],c,ref);obs['full_response_read']=all_read
   r.update(model=c['model'],source_id=c['source_id'],source_form=c['source_form'],domain=c['domain'],fact=c['fact'],pair_names=c['pair_names'],source_text=c['source_text'],reference=ref,observation=obs)
  outputs+=group
 ox={r['position_id']:r for r in outputs};pp=[]
 for p in rd('PAIRED-PLAN.json'):
  a,b=ox[p['old_position_id']],ox[p['new_position_id']]
  tr={z:{k:a['observation'][z]['labels'][k]+'->'+b['observation'][z]['labels'][k] for k in ['record','occurrence','role_a','role_b']} for z in ['strict','content']}
  harm=[k for k in ['occurrence','role_a','role_b'] if a['observation']['content']['labels'][k]=='C' and b['observation']['content']['labels'][k]!='C']
  pp.append({**p,'model':a['model'],'domain':a['domain'],'source_form':a['source_form'],'source_id':a['source_id'],'old_source_text':a['source_text'],'new_source_text':b['source_text'],'old_answer':a['raw_output'],'new_answer':b['raw_output'],'transitions':tr,'any_new_component_harm':harm,'hidden_harm_record_WW':tr['content']['record']=='W->W' and bool(harm)})
 grids=[];signals=[];orient=[]
 for model in ['qwen','llama']:
  for kind in ['BASELINE','FIRST_YAMADA','FIRST_SUZUKI','METHOD']:
   for form in ['JA_ACTIVE','JA_PASSIVE','ZH_ACTIVE']:
    rr=[r for r in outputs if r['model']==model and r['kind']==kind and r['source_form']==form];assert len(rr)==32
    yes=sum(r['fact']=='YES' and r['observation']['content']['labels']['record']=='C' for r in rr);no=sum(r['fact']=='NO' and r['observation']['content']['labels']['record']=='C' for r in rr)
    grids.append({'model':model,'kind':kind,'source_form':form,'n':32,'content':tally(rr),'strict_record':dict(Counter(r['observation']['strict']['labels']['record'] for r in rr)),'floor':{'C':yes+no,'positive_C':yes,'negative_C':no,'pass_floor':yes+no>=30 and yes>=15 and no>=15},'format':dict(Counter(r['observation']['strict']['format_compliance'] for r in rr)),'format_identity':'ACTUAL_BASELINE_OUTPUT' if kind=='BASELINE' else 'DERIVED_OUTPUT_NOT_RAW_MODEL_FORMAT'})
  changes=[p for p in pp if p['model']==model and p['pair_type']=='BASELINE_TO_METHOD'];resc=[p for p in changes if p['transitions']['content']['record'] in ['W->C','U->C']];harms=[p for p in changes if p['any_new_component_harm']]
  used=sum(r['model']==model and r['decision']['used_consensus'] for r in method_rows);domains=sorted({p['domain'] for p in resc});floor=all(g['floor']['pass_floor'] for g in grids if g['model']==model and g['kind']=='METHOD')
  signals.append({'model':model,'rescues':len(resc),'rescue_domains':domains,'rescue_pair_ids':[p['pair_id'] for p in resc],'new_component_harm_pair_ids':[p['pair_id'] for p in harms],'consensus_n':used,'consensus_denominator':96,'consensus_coverage':used/96,'fallback_n':96-used,'all_method_floors_pass':floor,'pass_signal':len(resc)>=3 and len(domains)>=2 and not harms and floor and used/96>=0.90,'independent_confirmation':False})
  correct=[sum(r['model']==model and r['kind']==kind and r['observation']['content']['labels']['record']=='C' for r in inverse_rows) for kind in ['FIRST_YAMADA','FIRST_SUZUKI']]
  orient.append({'model':model,'first_yamada_C':correct[0],'first_suzuki_C':correct[1],'each_n':96,'mean_C_across_fixed_maps':sum(correct)/2,'worst_fixed_map_C':min(correct),'method_worst_source_form_C':min(g['floor']['C'] for g in grids if g['model']==model and g['kind']=='METHOD'),'source_form_denominator':32})
 bad=[r for r in outputs if r['observation']['content']['labels']['record']!='C' or r['observation']['strict']['labels']['record']!='C' or r['observation']['strict']['format_compliance']!='PASS']
 summary={'experiment_id':spec['experiment_id'],'new_calls':len(raw),'new_forwards':sum(r['row_forward_n'] for r in raw),'old_cache':len(cache),'baseline_positions':192,'mapped_positions':384,'method_positions':192,'unique_normalized_calls':len(normcalls),'related_positions_not_independent_n':768,'grids':grids,'signals':signals,'shared_signal':all(s['pass_signal'] for s in signals),'fixed_mapping_average_and_worst':orient,'all_raw_reviewed':all_read,'automatic_B16':False,'paid_usd':0,'independent_human_gold':0}
 summary['actual_normalized_raw_format']=dict(Counter(r['observation']['strict']['format_compliance'] for r in norm_scores))
 summary['actual_normalized_raw_name_compliant']=sum(r['observation']['name_representation_compliant'] for r in norm_scores)
 normbad=[r for r in norm_scores if r['observation']['content']['labels']['record']!='C' or r['observation']['strict']['format_compliance']!='PASS' or not r['observation']['name_representation_compliant']]
 return {'SUMMARY.json':summary,'BASELINES.AI.json':base_rows,'MAPPED.AI.json':inverse_rows,'METHOD.AI.json':method_rows,'NORMALIZED-UNIQUE.AI.json':norm_scores,'NORMALIZED-NONC-OR-NONCOMPLIANT.json':normbad,'ALL-POSITIONS.AI.json':outputs,'PAIRS.json':pp,'ALL-NONC-OR-NONCOMPLIANT.json':bad}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--raw',required=True);ap.add_argument('--output-dir',required=True);ap.add_argument('--all-raw-reviewed',action='store_true');a=ap.parse_args();raw=json.loads(Path(a.raw).read_text());raw=raw['rows'] if isinstance(raw,dict) else raw
 result=compute(raw,a.all_raw_reviewed);result['SUMMARY.json'].update(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),raw_sha256=hashlib.sha256(Path(a.raw).read_bytes()).hexdigest());out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
 for name,d in result.items():
  p=out/name;assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result['SUMMARY.json']['signals']))
if __name__=='__main__':main()
