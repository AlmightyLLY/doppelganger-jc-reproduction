import copy,json
from scoring_b61 import score as common_score
def score(text,m):
 n=copy.deepcopy(m)
 # Only names actually presented in this task are known distractors. No change to old batch scores.
 names={v for v in m['entity_map'].values() if v in m['source_text']}|set(m.get('demo_names_present',[]))
 n['entity_map']={str(i):v for i,v in enumerate(sorted(names))}
 r=common_score(text,n);a=r['answer']
 r['demo_name_selected']=bool(a and any(v in set(m.get('demo_names_present',[])) for v in a.values()))
 return r
def synthetic():
 m={'arm':'J_UA','format_arm':'JSON','schema':'AU','entity_map':{'A':'林舟','B':'陈宁','C':'周岚','D':'吴桐'},'source_text':'林舟确实把陈宁扶稳了。','gold':{'actor':'林舟','undergoer':'陈宁'},'demo_names_present':['周映川','谢知遥']}
 out=[]
 for a,e in [({'actor':'林舟','undergoer':'陈宁'},'C'),({'actor':'陈宁','undergoer':'林舟'},'W'),({'actor':'周映川','undergoer':'谢知遥'},'W'),({'actor':None,'undergoer':'林舟'},'W'),({'actor':'赵清','undergoer':'陈宁'},'U'),({'actor':'周岚','undergoer':'陈宁'},'U')]:
  s=score(json.dumps(a,ensure_ascii=False),m);assert s['score']==e;(out.append({'text':a,'expected':e,'actual':s}))
 # Same unpresented demonstration names in ZERO are unknown; do not silently add them there.
 z=dict(m,demo_names_present=[]);assert score('{"actor":"周映川","undergoer":"谢知遥"}',z)['score']=='U'
 return {'status':'PASS','cases':out,'ZERO_demo_names_not_present_control':'PASS','model_calls':0,'full_analyzer_headroom_and_U_tests':'executor required'}
if __name__=='__main__':print(json.dumps(synthetic(),ensure_ascii=False,indent=2))
