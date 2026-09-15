import json
from parse_readout import parse,format_ok,walkthrough
from scoring_b39_frozen import score as frozen_score
def score(text,m):
 p=parse(text);derived=json.dumps(p['mapping'],ensure_ascii=False) if p['mapping'] is not None else ''
 r=frozen_score(derived,m);r['format_ok']=format_ok(p,m['format_arm'],m['schema']);r['parse_form']=p['form'];r['parse_error']=p['error'];r['emitted_order']=p['order'];r['bare_response']=p['bare'];r['allowed_name_values']=p['mapping'] is not None and all(v is None or v in set(m['entity_map'].values()) for v in p['mapping'].values());return r
def synthetic():
 m={'arm':'J_UA','format_arm':'KV','schema':'AU','entity_map':{'A':'林舟','B':'陈宁','C':'周岚','D':'吴桐'},'gold':{'actor':'林舟','undergoer':'陈宁'}}
 cases=[('actor=林舟；undergoer=陈宁','C',True),('undergoer=陈宁；actor=林舟','C',False),('{"actor":"林舟","undergoer":"陈宁"}','C',False),('actor=陈宁；undergoer=林舟','W',True),('actor=周岚；undergoer=吴桐','W',True),('actor=赵清；undergoer=陈宁','U',True),('actor=null；undergoer=林舟','W',True),('actor=null；undergoer=陈宁','U',True),('actor=林舟；actor=陈宁','U',False),('actor=林舟','U',False),('答案是 actor=林舟；undergoer=陈宁','U',False),('actor=林舟,undergoer=陈宁','C',False),('```json\n{"actor":"林舟","undergoer":"陈宁"}\n```','C',False)]
 out=[]
 for text,s,f in cases:
  r=score(text,m);assert r['score']==s and r['format_ok']==f,(text,r);out.append({'synthetic_text':text,'expected_score':s,'expected_format':f,'actual':r})
 # The executor must additionally verify full analyzer U bounds on synthetic paired inputs.
 return {'parser_cases':walkthrough(),'scoring_cases':out,'model_calls':0,'identity':'synthetic scoring walkthrough; not empirical results'}
if __name__=='__main__':print(json.dumps(synthetic(),ensure_ascii=False,indent=2))
