from pathlib import Path
import json,csv,collections,itertools
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;R=P/'results_continuation';A=P/'analysis';F=A/'figures';F.mkdir(exist_ok=True)
load=lambda n:json.loads((P/n).read_text())
readlines=lambda p:[json.loads(l) for l in p.read_text().splitlines()]
refs=load('AUTHOR-REFERENCES.json');by={r['call_id']:r for r in refs};states=np.load(P/'results/REPRESENTATIONS-PORTABLE.npz');groups=sorted(set(r['group_id'] for r in refs))
def csvsave(n,rows):
 with (F/n).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def finish(fig,name):
 fig.tight_layout(rect=[0,.05,1,.96])
 for ext in ['png','pdf']:fig.savefig(F/(name+'.'+ext),dpi=180)
 plt.close(fig)
def boot(x):
 means=x.mean(0);ix=np.random.default_rng(130913).integers(0,len(x),(10000,len(x)));v=x[ix].mean(1);return means,np.quantile(v,.025,axis=0),np.quantile(v,.975,axis=0)
raw=readlines(R/'GENERATIONS.jsonl');baselines=[r for r in raw if r['task']=='BASELINE_OBSERVE'];base={r['input_id']:r for r in baselines}
for r in baselines:
 ref=by[r['input_id']];ans=r['answer'];rev={'actor':ref['gold']['undergoer'],'undergoer':ref['gold']['actor']};r['category']='C' if r['score']=='C' else 'R' if ans==rev else 'OTHER_W' if r['score']=='W' else 'U';r['target_person_set_correct']=isinstance(ans,dict) and set(ans.values())==set(ref['gold'].values());r['group_id']=ref['group_id'];r['background']=ref['background'];r['fact_variant']=ref['fact_variant'];r['construction']=ref['construction'];r['schema']=ref['schema']
(A/'BASELINE-RESULTS.json').write_text(json.dumps(baselines,ensure_ascii=False,indent=2))
lens=readlines(R/'LENS.jsonl');tf=[r for r in lens if r['kind']=='TEACHER_FORCED'];fig,axes=plt.subplots(1,3,figsize=(15,5));lensdata=[]
for j,ax in enumerate(axes,1):
 mat=np.zeros((12,33))
 for gi,g in enumerate(groups):
  for l in range(33):
   x=[r['margin'] for r in tf if by[r['input_id']]['group_id']==g and r['opponent'].endswith('C'+str(j)) and r['layer']==l];mat[gi,l]=np.mean(x);lensdata.append({'group':g,'layer':l,'opponent':'C'+str(j),'n_inputs':len(x),'mean_logp_margin':float(mat[gi,l])})
 vmax=max(abs(mat.min()),abs(mat.max()));im=ax.imshow(mat,aspect='auto',cmap='RdBu',vmin=-vmax,vmax=vmax);ax.set_title(['Target vs reversed','Target vs background/null','Target vs reversed background/both A'][j-1]);ax.set(xlabel='Residual layer',yticks=range(12),yticklabels=groups);fig.colorbar(im,ax=ax,label='log p(correct token) - log p(other token)')
fig.suptitle('Conditional token readout: all 192 inputs, 33 layers');fig.text(.03,.015,'Each comparison uses its own shared completion prefix. These are not one normalized four-answer distribution.',fontsize=10);finish(fig,'01_candidate_lens');csvsave('01_candidate_lens.csv',lensdata)
# Probe: group is unit; all layer curves and permutation bands shown, no best-layer selection.
probes=readlines(A/'PROBE-PREDICTIONS.jsonl');rules=load('analysis/RULE-CONTROLS.json');probeagg=[]
for anchor in ['R1_END','NATIVE_PROMPT_END']:
 for kind in ['PROBE','PERMUTATION','CROSS_BA_TO_BEI','CROSS_BEI_TO_BA']:
  for subset in ['NONE','BACKGROUND','NATIVE_W']:
   for l in range(33):
    z=[r for r in probes if r['anchor']==anchor and r['kind']==kind and r['layer']==l and ((r['background']=='NONE') if subset=='NONE' else (r['background']!='NONE') if subset=='BACKGROUND' else r['new_native_score']=='W')]
    if not z:continue
    vals=[np.mean([r['correct'] for r in z if r['group_id']==g]) for g in groups if any(r['group_id']==g for r in z)];m,lo,hi=boot(np.array(vals)[:,None]);probeagg.append({'anchor':anchor,'kind':kind,'subset':subset,'layer':l,'group_mean_accuracy':float(m[0]),'low':float(lo[0]),'high':float(hi[0]),'groups':len(vals),'rows':len(z)})
qacc=np.mean([r['correct'] for r in probes if r['kind']=='Q_ONLY']);posacc=np.mean([r['first_mentioned_prediction']==r['label'] for r in rules]);fig,axes=plt.subplots(2,2,figsize=(12,8))
for row,anchor in enumerate(['R1_END','NATIVE_PROMPT_END']):
 for col,subset in enumerate(['NONE','BACKGROUND']):
  ax=axes[row,col]
  for kind in ['PROBE','PERMUTATION','CROSS_BA_TO_BEI','CROSS_BEI_TO_BA']:
   z=[r for r in probeagg if r['anchor']==anchor and r['subset']==subset and r['kind']==kind];ax.plot([r['layer'] for r in z],[r['group_mean_accuracy'] for r in z],label=kind)
   if kind=='PROBE':ax.fill_between([r['layer'] for r in z],[r['low'] for r in z],[r['high'] for r in z],alpha=.15)
  ax.axhline(qacc,color='black',ls=':',label='Q-only / first-position = %.2f'%qacc);ax.axhline(1,color='gray',ls='--',label='Explicit grammar = 1.00');ax.set(title=anchor+' / '+subset,xlabel='Residual layer',ylabel='Held-out accuracy',ylim=(-.03,1.08));ax.legend(fontsize=7)
fig.suptitle('Fixed bilinear features, 64-D linear classifier, 12 held-out groups');fig.text(.03,.012,'Training uses other groups NONE only; R1 duplicate prefixes merged. Shading: group bootstrap. No independent human gold.',fontsize=9);finish(fig,'02_probe_holdout');csvsave('02_probe_holdout.csv',probeagg)
# Representational distances: same-fact background pairs and actual role swaps.
distance=[]
for r in refs:
 if r['background']=='BA_TOPIC':
  mate=next(z for z in refs if z['group_id']==r['group_id'] and z['construction']==r['construction'] and z['schema']==r['schema'] and z['background']=='BEI_TOPIC');family='SAME_FACT_BACKGROUND'
 elif r['background']=='NONE' and r['fact_variant']=='ORIGINAL':
  mate=next(z for z in refs if z['group_id']==r['group_id'] and z['construction']==r['construction'] and z['schema']==r['schema'] and z['background']=='NONE' and z['fact_variant']!='ORIGINAL');family='FACT_SWAP'
 else:continue
 for anchor in ['COMMON_HEADER_END','R2_END','R1_END','NATIVE_PROMPT_END']:
  ka=r['call_id']+'__'+anchor;kb=mate['call_id']+'__'+anchor
  if ka not in states or kb not in states:continue
  x=states[ka].astype(float);y=states[kb].astype(float)
  for l in range(33):
   cos=1-np.dot(x[l],y[l])/(np.linalg.norm(x[l])*np.linalg.norm(y[l]));norm=np.linalg.norm(x[l]-y[l])/np.sqrt((np.dot(x[l],x[l])+np.dot(y[l],y[l]))/2)
   distance.append({'family':family,'group':r['group_id'],'left':r['call_id'],'right':mate['call_id'],'anchor':anchor,'layer':l,'cosine_distance':float(cos),'rms_normalized_l2':float(norm)})
csvsave('03_distances.csv',distance);fig,axes=plt.subplots(2,3,figsize=(13,7))
for col,anchor in enumerate(['R2_END','R1_END','NATIVE_PROMPT_END']):
 for row,metric in enumerate(['cosine_distance','rms_normalized_l2']):
  ax=axes[row,col]
  for family in ['SAME_FACT_BACKGROUND','FACT_SWAP']:
   vals=[]
   for g in groups:
    z=[r for r in distance if r['anchor']==anchor and r['family']==family and r['group']==g]
    if z:vals.append([np.mean([r[metric] for r in z if r['layer']==l]) for l in range(33)])
   if vals:
    m,lo,hi=boot(np.array(vals));ax.plot(m,label=family);ax.fill_between(range(33),lo,hi,alpha=.15)
  ax.set(title=anchor+(' (before target)' if anchor=='R2_END' else ''),xlabel='Residual layer',ylabel=metric);ax.legend(fontsize=7)
fig.suptitle('Paired representation differences: 48 background pairs, 48 fact swaps');fig.text(.03,.01,'R2 precedes R1. Distances do not measure binding strength. Curves weight 12 author groups equally.',fontsize=9);finish(fig,'03_representation_distances')
# Actual self failure, no fabricated donor heatmap.
sc=readlines(R/'CANDIDATE-SCORES.jsonl');selfrows=[r for r in sc if r['setting_id'] is not None];sd=readlines(R/'SELF-STATE-DIFFERENCES.jsonl');deltas=[]
fig,ax=plt.subplots(figsize=(9,4.5))
for r in selfrows:
 b=next(z for z in sc if z['candidate_id']==r['candidate_id'] and z['setting_id'] is None)
 for i,(a,c) in enumerate(zip(r['token_logps'],b['token_logps'])):deltas.append({'setting_id':r['setting_id'],'candidate_id':r['candidate_id'],'token_position':i,'self_logp':a,'baseline_logp':c,'delta':a-c})
 ax.plot([x['delta'] for x in deltas],marker='o');ax.set(title='Stored-recipient SELF calibration failed',xlabel='Candidate token position',ylabel='Self minus unpatched log probability')
fig.text(.07,.01,'One completed SELF candidate forward. Donor/sham interventions NOT_RUN; no causal heatmap is available.',fontsize=9);finish(fig,'04_self_calibration_failure');csvsave('04_self_calibration_failure.csv',deltas)
counts=collections.Counter(r['category'] for r in baselines);fig,axes=plt.subplots(1,2,figsize=(11,4.5));cats=['C','R','OTHER_W','U'];axes[0].bar(cats,[counts[k] for k in cats]);axes[0].set(title='48 new native observation outputs',ylabel='Outputs');axes[1].barh(['Native observations','No-hook repeats','Intervention generations'],[48,4,0]);axes[1].set(xlabel='Completed generations',title='Actual generation coverage');axes[1].text(1,2,'NOT_RUN: SELF score gate failed',va='center',fontsize=9);fig.text(.04,.01,'Rescue and new-harm transitions are unavailable: no intervention free generation started. Zero is coverage, not effect.',fontsize=9);finish(fig,'05_generation_coverage');csvsave('05_generation_coverage.csv',[{'type':k,'completed':v} for k,v in [('native_observations',48),('nohook_repeats',4),('intervention_generations',0)]])
summary={'native_counts':dict(counts),'native_n':48,'format_ok':sum(r['format_ok'] for r in baselines),'person_set_correct':sum(r['target_person_set_correct'] for r in baselines),'q_only_accuracy':float(qacc),'position_accuracy':float(posacc),'grammar_accuracy':1,'candidate_sequences':len(sc),'self_completed_candidates':len(selfrows),'self_state_differences':sd,'self_max_token_logp_delta':max(abs(x['delta']) for x in deltas),'self_sum_delta':sum(x['delta'] for x in deltas),'native_lens_rows':sum(r['kind']=='NATIVE' for r in lens),'tf_lens_rows':len(tf),'distance_pairs_background':48,'distance_pairs_factswap':48,'human_gold':0}
(A/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));(A/'REBUILD.md').write_text('Run analyze_observations.py in pinned cpu-env; then run make_figures.py with existing system Python matplotlib. All inputs are saved arrays/JSON. No model calls. Each figure has CSV data and vector PDF. Figures04/05 report calibration/coverage because donor interventions did not run. Full teacher-forced prefixes and native token traces are in results_continuation/LENS.jsonl and GENERATIONS.jsonl. RMS-normalized L2 = norm(x-y)/sqrt((norm(x)^2+norm(y)^2)/2). Bootstrap10000, seed130913, equal author-group weighting. R2_END probe has no NONE training anchor, so no R2 classifier is fit.\n')
print(json.dumps(summary,ensure_ascii=False))
