"""B09 lossless JSON field grading. Reference never used to decode identity."""
import json,re
from collections import Counter
class ObjectPairs(list):pass
def combine(*xs):return 'W' if 'W' in xs else 'U' if 'U' in xs else 'C'
def candidates(text):
    decoder=json.JSONDecoder(object_pairs_hook=ObjectPairs);out=[];i=0
    while i<len(text):
        if text[i] not in '{[':i+=1;continue
        try:v,end=decoder.raw_decode(text,i)
        except ValueError:return []  # Fail closed rather than extracting a nested fragment.
        out.append((i,end,v));i=end
    return out

def score(text,call,ref):
    spans=candidates(text);unique_obj=len(spans)==1 and isinstance(spans[0][2],ObjectPairs)
    obj=spans[0][2] if unique_obj else None
    # A successfully decoded outer array remains an array, never its nested object.
    keys=[k for k,v in obj] if obj is not None else []
    expected=['occurred',*call['role_keys']];duplicates=[k for k,n in Counter(keys).items() if n>1]
    vals={};reasons={}
    for key in expected:
        vv=[v for k,v in obj if k==key] if obj is not None else []
        vals[key]=vv[0] if len(vv)==1 else None
        reasons[key]='UNIQUE' if len(vv)==1 else 'DUPLICATE_KEY' if len(vv)>1 else 'MISSING_OR_AMBIGUOUS_OBJECT'
    occurrence=vals['occurred'];unsupported=False;contradiction=False
    if occurrence in ('YES','NO','UNKNOWN'):
        if occurrence==ref['occurred']:ol='C'
        elif occurrence=='UNKNOWN':ol='U'
        else:
            ol='W';unsupported=ref['occurred']=='UNKNOWN';contradiction=ref['occurred'] in ('YES','NO')
    else:ol='U'
    decoded={};labels={};noncanonical=[]
    for component,key in zip(['role_a','role_b'],call['role_keys']):
        value=vals[key]
        if call['representation']=='IDS':person=call['entity_map'].get(value) if isinstance(value,str) else None
        else:person=value if isinstance(value,str) and value in call['entity_map'].values() else None
        decoded[component]=person;labels[component]='U' if person is None else ('C' if person==ref[component] else 'W')
        if value is not None and person is None:noncanonical.append({'field':key,'raw_value':value,'representation':call['representation'],'reason':'UNLISTED_OR_INVALID_REPRESENTATION'})
    labels['occurrence']=ol;labels['participant']=combine(labels['role_a'],labels['role_b']);labels['record']=combine(ol,labels['participant'])
    direct=unique_obj and text.strip()==text[spans[0][0]:spans[0][1]]
    extras=[k for k in keys if k not in expected]
    type_ok=occurrence in ('YES','NO','UNKNOWN') and all(vals[k] is None or isinstance(vals[k],str) for k in call['role_keys'])
    fmt=direct and sorted(keys)==sorted(expected) and type_ok
    return {'labels':labels,'occurred_asserted':occurrence,'decoded_names':decoded,'raw_fields':vals,'field_identity_reasons':reasons,'occurrence_reason':('CORRECT' if ol=='C' else 'UNSUPPORTED_ASSERTION' if unsupported else 'EXPLICIT_CONTRADICTION' if contradiction else 'UNKNOWN_ABSTENTION' if occurrence=='UNKNOWN' else 'MISSING_NULL_OR_INVALID'), 'entity_reasons':{component:('CORRECT' if labels[component]=='C' else 'OTHER_LISTED_PERSON' if labels[component]=='W' else reasons[key] if reasons[key]!='UNIQUE' else 'NULL_OMISSION' if vals[key] is None else 'UNLISTED_OR_INVALID_REPRESENTATION') for component,key in zip(['role_a','role_b'],call['role_keys'])},'unsupported_assertion':unsupported,'explicit_occurrence_contradiction':contradiction,'format_compliance':'PASS' if fmt else 'FAIL','unique_readable_object':unique_obj,'object_or_array_count':len(spans),'raw_object_pairs':obj,'duplicate_keys':duplicates,'extra_keys':extras,'noncanonical_entities':noncanonical,'outside_json_text':text[:spans[0][0]]+text[spans[0][1]:] if unique_obj else text,'language_status':'CANONICAL_SCHEMA_VALUES' if fmt and not noncanonical else 'REQUIRES_FULL_RESPONSE_LANGUAGE_REVIEW','identity':'AI_SCORING_NOT_HUMAN_GOLD','full_response_read':False}

def semantic_pair_pass(old,new,variant):
    # Inputs must already be scored against their own reference, after per-input map decoding.
    if old['labels']['record']!='C' or new['labels']['record']!='C':return False
    a,b=old['decoded_names'],new['decoded_names'];x,y=old['occurred_asserted'],new['occurred_asserted']
    if variant=='PARAPHRASE':return x==y and a==b
    if variant=='ROLE_SWAP':return x==y=='YES' and a['role_a']==b['role_b'] and a['role_b']==b['role_a']
    if variant=='NEGATED':return x=='YES' and y=='NO' and a==b
    if variant=='UNRESOLVED':return x=='YES' and y=='UNKNOWN' and a==b
    raise ValueError(variant)

def mapping_signal(rows):
    """rows: one source per representation, with MAP12/MAP21 scored observations."""
    cells=[]
    for representation in ('NAMES','IDS'):
        subset=[r for r in rows if r['representation']==representation]
        for oldmap,newmap in [('MAP12','MAP21'),('MAP21','MAP12')]:
            harms=set();definite=set();record_harms=set();details=[]
            for r in subset:
                old,new=r[oldmap]['labels'],r[newmap]['labels']
                components=[k for k in ['occurrence','role_a','role_b'] if old[k]=='C' and new[k] in ('W','U')]
                if components:harms.add(r['source_id']);details.append({'source_id':r['source_id'],'components':components})
                if any(old[k]=='C' and new[k]=='W' for k in ['occurrence','role_a','role_b']):definite.add(r['source_id'])
                if old['record']=='C' and new['record'] in ('W','U'):record_harms.add(r['source_id'])
            cells.append({'representation':representation,'direction':oldmap+'->'+newmap,'source_ids_any_component_new_harm':sorted(harms),'n_sources':len(harms),'source_ids_definite_C_to_W':sorted(definite),'source_ids_complete_C_to_WU':sorted(record_harms),'component_details':details,'supported':len(harms)>=3})
    return cells
