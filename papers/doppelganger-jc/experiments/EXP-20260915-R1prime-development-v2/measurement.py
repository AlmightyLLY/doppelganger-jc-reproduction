"""Read-only measurement primitives. No automatic semantic labels or model calls."""
import unicodedata,random,statistics

def form_hits(output,word):
    text=unicodedata.normalize('NFC',output);word=unicodedata.normalize('NFC',word)
    if not word:raise ValueError('empty target')
    return [i for i in range(len(text)) if text.startswith(word,i)]

def error_bounds(label):
    return {'C':(0,0),'W':(1,1),'U':(0,1),'NOT_REVIEWED':(0,1)}[label]

def pair_bounds(a,b):
    al,au=error_bounds(a);bl,bu=error_bounds(b)
    return al-bu,au-bl

def select_review(materials,outputs):
    """Outputs is {(item_index, condition): raw full text}; includes whole triples."""
    assert len(outputs)==3*len(materials)
    ordered=sorted(materials,key=lambda x:(x['fixed_six_model_mean'],x['item_index']))
    strata={x['item_index']:min(3,4*j//len(ordered)) for j,x in enumerate(ordered)}
    mandatory={};pools={h:[] for h in range(4)}
    for m in materials:
        i=m['item_index'];out=[outputs[i,c] for c in 'OTU'];reasons=[]
        if len(set(out))>1:reasons.append('ANY_OUTPUT_DIFFERENT')
        if any(form_hits(s,m['word']) for s in out):reasons.append('ANY_FORM_HIT')
        if m['guard_proxy']:reasons.append('GUARD_PROXY')
        if reasons:mandatory[i]=reasons
        else:pools[strata[i]].append(i)
    # Allocate up to 60, balanced by stratum with unused capacity redistributed.
    allocations={h:0 for h in range(4)}
    for _ in range(min(60,sum(map(len,pools.values())))):
        h=min((h for h in range(4) if allocations[h]<len(pools[h])),key=lambda h:(allocations[h],h))
        allocations[h]+=1
    rng=random.Random(20260918);rows=[]
    for i,why in sorted(mandatory.items()):rows.append({'item_index':i,'reasons':why,'probability':1.0,'stratum':strata[i]})
    for h,pool in pools.items():
        n=allocations[h];N=len(pool)
        for i in sorted(rng.sample(sorted(pool),n)):
            rows.append({'item_index':i,'reasons':['IDENTICAL_RANDOM'],'probability':n/N,'stratum':h})
    return {'items':rows,'mandatory_items':len(mandatory),'random_items':sum(allocations.values()),'strata':{h:{'population':len(pools[h]),'sample':allocations[h]} for h in pools}}

def decision_candidate(delta,ci,guard_net,guard_unknown,rho,rho_ci,control_delta,complete):
    if not complete:return 'INCOMPLETE_REVIEW_NO_DECISION'
    if delta>=.08 and ci[0]>0 and control_delta>0 and guard_net<=0 and not guard_unknown and rho is not None and rho>0 and rho_ci[0]>0:
        return 'GO_CANDIDATE_REQUIRES_SCIENTIFIC_INTERPRETATION'
    if delta<.04 and ci[0]<=0<=ci[1]:return 'RESOURCE_NO_GO_CANDIDATE_NOT_PROOF_OF_NULL'
    return 'UNCERTAIN_OR_HARM_REVIEW'
