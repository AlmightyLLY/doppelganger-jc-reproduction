"""Reference-free first-mention normalization, inversion and two-map consensus.

This module never accepts or reads scoring references. It returns a derived answer
or the exact baseline string. Scoring is a separate downstream operation.
"""
import json,re
import score_b09 as parser
NORMAL_NAMES=['山田','鈴木']
def transform(call,orientation):
 assert orientation in ['FIRST_YAMADA','FIRST_SUZUKI']
 names=list(call['entity_map'].values());pattern='|'.join(re.escape(n) for n in sorted(names,key=len,reverse=True))
 mentions=list(dict.fromkeys(re.findall(pattern,call['source_text'])))
 assert len(mentions)==2 and all(call['source_text'].count(n)==1 for n in mentions)
 assigned=NORMAL_NAMES if orientation=='FIRST_YAMADA' else list(reversed(NORMAL_NAMES))
 forward=dict(zip(mentions,assigned));inverse={v:k for k,v in forward.items()}
 source=re.sub(pattern,lambda m:forward[m[0]],call['source_text'])
 oldrecord='记录：'+json.dumps(call['source_text'],ensure_ascii=False);newrecord='记录：'+json.dumps(source,ensure_ascii=False)
 oldinventory='实体表：'+'；'.join(names);newinventory='实体表：'+'；'.join(NORMAL_NAMES)
 text=call['messages'][0]['content'];assert text.count(oldrecord)==text.count(oldinventory)==1
 text=text.replace(oldrecord,newrecord,1).replace(oldinventory,newinventory,1)
 return {'orientation':orientation,'first_mentions':mentions,'forward_map':forward,'inverse_map':inverse,'source_text':source,'messages':[{'role':'user','content':text}]}

def invert(text,role_keys,inverse_map):
 assert set(inverse_map)==set(NORMAL_NAMES) and len(set(inverse_map.values()))==2
 spans=parser.candidates(text);obj=spans[0][2] if len(spans)==1 and isinstance(spans[0][2],parser.ObjectPairs) else None
 expected=['occurred',*role_keys];keys=[k for k,v in obj] if obj is not None else []
 unique=obj is not None and len(keys)==len(set(keys))
 fields={k:next((v for kk,v in obj if kk==k),None) for k in expected} if unique else dict.fromkeys(expected)
 outside=text[:spans[0][0]]+text[spans[0][1]:] if obj is not None else text
 wrapper=re.sub(r'\s+','',outside).lower() in ['','```json```','``````']
 structural=unique and sorted(keys)==sorted(expected) and wrapper
 occurrence=fields['occurred'] if structural and fields['occurred'] in ['YES','NO'] else None
 roles={k:inverse_map.get(fields[k]) if structural and isinstance(fields[k],str) else None for k in role_keys}
 answer={'occurred':occurrence,**roles};eligible=occurrence is not None and all(roles[k] is not None for k in role_keys)
 reasons=[]
 if not structural:reasons.append('INVALID_OBJECT_EXTRA_ASSERTION_OR_FIELDS')
 if occurrence is None:reasons.append('OCCURRENCE_UNDETERMINED')
 if any(v is None for v in roles.values()):reasons.append('UNLISTED_NULL_OR_NONINVERTIBLE_NAME')
 return {'answer':answer,'consensus_eligible':eligible,'raw_fields':fields,'raw_occurrence':fields['occurred'],'structural_content_allowed':structural,'outside_json_text':outside,'reasons':reasons,'inverse_map':inverse_map,'derived_output':json.dumps(answer,ensure_ascii=False,separators=(',',':'))}

def choose(baseline_raw,first_inverse,second_inverse):
 agreed=first_inverse['consensus_eligible'] and second_inverse['consensus_eligible'] and first_inverse['answer']==second_inverse['answer']
 return {'used_consensus':agreed,'choice':'TWO_MAP_CONSENSUS' if agreed else 'EXACT_BASELINE_FALLBACK','output':first_inverse['derived_output'] if agreed else baseline_raw,'reason':'BOTH_COMPLETE_DETERMINATE_AND_EQUAL' if agreed else 'DISAGREEMENT_OR_UNDETERMINED','identity':'RULE_DERIVED_NOT_ADDITIONAL_MODEL_GENERATION'}
