"""Primary development endpoints: no AI or human semantic labels required."""
import json
from pathlib import Path
from measurement import form_hits
from analyze import paired_summary,spearman_summary
W=Path(__file__).resolve().parent
def automatic_analysis(materials,raw):
 out={(r['item_index'],r['condition']):r['output'] for r in raw}
 assert len(out)==3*len(materials)
 mm={m['item_index']:m for m in materials};ids=sorted(mm)
 subsets={'all':ids,'strict_unchanged':[i for i in ids if not mm[i]['revised']],'source_unflagged':[i for i in ids if not mm[i]['source_issue']],'strict_unflagged':[i for i in ids if not mm[i]['revised'] and not mm[i]['source_issue']],'guard':[i for i in ids if mm[i]['guard_proxy']]}
 result={'status':'AUTOMATIC_BEHAVIOR_DESCRIPTION_NOT_SEMANTIC_VALIDATION','subsets':{},'new_logprob_calls':0,'human_gold':0,'semantic_labels_used':False}
 for name,ss in subsets.items():
  z={'n':len(ss),'form':{},'old_score_correlations':{}}
  for kind,key in [('chinese','word'),('japanese','japanese_word')]:
   h={(i,c):int(bool(form_hits(out[i,c],mm[i][key]))) for i in ss for c in 'OTU'}
   z['form'][kind]={'counts':{c:sum(h[i,c] for i in ss) for c in 'OTU'},'rates':{c:sum(h[i,c] for i in ss)/len(ss) for c in 'OTU'},'contrasts':{a+'-'+b:paired_summary([h[i,a]-h[i,b] for i in ss]) for a,b in [('O','U'),('U','T'),('O','T')]}}
   x=[mm[i]['fixed_six_model_mean'] for i in ss]
   z['old_score_correlations'][kind]={'O_form':spearman_summary(x,[h[i,'O'] for i in ss]),'U-T_form':spearman_summary(x,[h[i,'U']-h[i,'T'] for i in ss]),'O-T_form':spearman_summary(x,[h[i,'O']-h[i,'T'] for i in ss])}
  z['exact_output_identical_items']=sum(len({out[i,c] for c in 'OTU'})==1 for i in ss)
  result['subsets'][name]=z
 return result
if __name__=='__main__':
 m=json.loads((W/'MATERIALS.json').read_text());raw=[json.loads(p.read_text()) for p in sorted((W/'results').glob('R1P-*.json'))]
 q=automatic_analysis(m,raw);(W/'AUTOMATIC-ANALYSIS.json').write_text(json.dumps(q,ensure_ascii=False,indent=2));print(json.dumps(q['subsets']['all'],ensure_ascii=False))
