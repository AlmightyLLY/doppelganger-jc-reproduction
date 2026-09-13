import json,re
def parse(text):
 raw=text.strip();s=raw;fenced=False
 m=re.fullmatch(r'```(?:json|text)?\s*\n(.*?)\n```',s,re.S)
 if m:s=m.group(1).strip();fenced=True
 def obj(ps):
  if len(dict(ps))!=len(ps):raise ValueError('duplicate keys')
  return dict(ps)
 try:
  d=json.loads(s,object_pairs_hook=obj)
  if not isinstance(d,dict) or set(d)!={'actor','undergoer'} or not all(v is None or isinstance(v,str) for v in d.values()):raise ValueError('not a role pair')
  return {'mapping':d,'form':'JSON','bare':not fenced,'order':list(d),'error':None}
 except (ValueError,TypeError):pass
 # Recognize the whole response, never extract a convenient substring from prose.
 parts=re.split(r'[;；,，\n]+',s.strip().rstrip(';；,，'));d={};delims_semicolon_or_newline=not bool(re.search(r'[,，]',s))
 try:
  if len(parts)!=2:raise ValueError('requires two fields')
  for part in parts:
   mm=re.fullmatch(r'\s*(actor|undergoer)\s*[=:：]\s*(.*?)\s*',part)
   if not mm:raise ValueError('label or syntax')
   key,val=mm.groups()
   if key in d:raise ValueError('duplicate field')
   if val.startswith(('"',"'")):
    if len(val)<2 or val[-1]!=val[0]:raise ValueError('unmatched quote')
    val=val[1:-1]
   if not val or any(c in val for c in '={}[];；,，\n"\''):raise ValueError('extra syntax')
   d[key]=None if val=='null' else val
  if set(d)!={'actor','undergoer'}:raise ValueError('keys')
  return {'mapping':d,'form':'KV','bare':not fenced,'order':list(d),'requested_KV_separator':delims_semicolon_or_newline,'error':None}
 except ValueError as e:return {'mapping':None,'form':'UNPARSED','bare':not fenced,'order':[],'error':str(e)}
def format_ok(parsed,arm,schema):
 return parsed['mapping'] is not None and parsed['form']==arm and parsed['bare'] and parsed['order']==(['actor','undergoer'] if schema=='AU' else ['undergoer','actor']) and (arm!='KV' or parsed['requested_KV_separator'])
def walkthrough():
 good={'actor':'林舟','undergoer':'陈宁'}
 cases=[('{"actor":"林舟","undergoer":"陈宁"}',good,'JSON'),('actor=林舟；undergoer=陈宁',good,'KV'),('undergoer=陈宁\nactor=林舟',{'undergoer':'陈宁','actor':'林舟'},'KV'),('actor:林舟,undergoer:陈宁',good,'KV'),('actor="林舟"；undergoer="陈宁"',good,'KV'),('actor=陈宁；undergoer=林舟',{'actor':'陈宁','undergoer':'林舟'},'KV'),('actor=周岚；undergoer=吴桐',{'actor':'周岚','undergoer':'吴桐'},'KV'),('actor=null；undergoer=陈宁',{'actor':None,'undergoer':'陈宁'},'KV'),('actor=赵清；undergoer=陈宁',{'actor':'赵清','undergoer':'陈宁'},'KV'),('actor=林舟',None,'UNPARSED'),('actor=林舟；actor=陈宁',None,'UNPARSED'),('{"actor":"林舟","actor":"周岚","undergoer":"陈宁"}',None,'UNPARSED'),('答案是 actor=林舟；undergoer=陈宁',None,'UNPARSED'),('actor=林舟；undergoer=陈宁；理由=材料',None,'UNPARSED'),('```json\n{"actor":"林舟","undergoer":"陈宁"}\n```',good,'JSON')]
 out=[]
 for text,m,f in cases:
  p=parse(text);assert p['mapping']==m and p['form']==f,(text,p);out.append({'synthetic_text':text,'expected_mapping':m,'parsed':p,'JSON_AU_format':format_ok(p,'JSON','AU'),'KV_AU_format':format_ok(p,'KV','AU')})
 return out
if __name__=='__main__':print(json.dumps(walkthrough(),ensure_ascii=False,indent=2))
