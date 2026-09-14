import json
def combine(ss):
 return 'MISSING' if 'MISSING'in ss else 'W'if'W'in ss else'U'if'U'in ss else'C'
def normalize(s):
 s=s.strip().strip('"\'“”‘’')
 if s.endswith(('。','.','!','！')):s=s[:-1]
 return s.strip().strip('"\'“”‘’')
def score(text,m):
 raw=text.strip();arm=m['arm'];names=set(m['entity_map'].values())
 if arm!='J_UA':
  choices={'是','否'}if arm=='F'else names;v=normalize(raw)
  return dict(score='C'if v==m['gold']else'W'if v in choices else'U',answer=v if v in choices else None,format_ok=raw in choices|{'null'},raw_null=raw=='null')
 try:
  def obj(ps):
   if len(dict(ps))!=len(ps):raise ValueError('duplicate keys')
   return dict(ps)
  d=json.loads(raw,object_pairs_hook=obj)
  if not isinstance(d,dict)or set(d)!={'actor','undergoer'}:raise ValueError('keys')
  scores={k:'C'if d[k]==m['gold'][k]else'W'if isinstance(d[k],str)and d[k]in names else'U'for k in d}
  fmt=list(d)==['undergoer','actor']and all(v is None or isinstance(v,str)and v in names for v in d.values())
  return dict(score=combine(list(scores.values())),answer=d,field_scores=scores,format_ok=fmt,raw_null=any(v is None for v in d.values()))
 except (ValueError,TypeError):return dict(score='U',answer=None,field_scores={'actor':'U','undergoer':'U'},format_ok=False,raw_null=raw=='null')
def synthetic():
 m=dict(arm='L_A',gold='林舟',entity_map=dict(A='林舟',B='陈宁',C='周岚',D='吴桐'))
 cases=[('林舟','C',True),('陈宁','W',True),('null','U',True),('林舟。','C',False),('','U',False),('林舟或陈宁','U',False)]
 for t,s,f in cases:assert (score(t,m)['score'],score(t,m)['format_ok'])==(s,f)
 for pol,g in [('POS','是'),('NEG','否')]:
  mm=dict(m,arm='F',gold=g);assert score(g,mm)['score']=='C'and score('null',mm)['format_ok'];assert score('否'if g=='是'else'是',mm)['score']=='W'
  assert score('林舟',m)['score']=='C' # polarity never changes role reference
 jm=dict(m,arm='J_UA',gold=dict(undergoer='陈宁',actor='林舟'))
 for t,s,f in [(' {"undergoer":"陈宁","actor":"林舟"} ','C',True),('{"actor":"林舟","undergoer":"陈宁"}','C',False),('{"undergoer":null,"actor":"林舟"}','U',True),('{"undergoer":"林舟","actor":null}','W',True),('{"undergoer":"陈宁","actor":"林舟","extra":1}','U',False),('{"actor":"林舟","actor":"陈宁","undergoer":"陈宁"}','U',False)]:assert (score(t,jm)['score'],score(t,jm)['format_ok'])==(s,f)
 for ss,s in [(['C','C'],'C'),(['C','U'],'U'),(['C','W'],'W'),(['W','U'],'W'),(['C','MISSING'],'MISSING')]:assert combine(ss)==s
 assert ('W','C')!=('C','W') # rescue and harm kept directionally distinct
 return dict(status='PASS',model_calls=0,synthetic_only=True,cases=24)
