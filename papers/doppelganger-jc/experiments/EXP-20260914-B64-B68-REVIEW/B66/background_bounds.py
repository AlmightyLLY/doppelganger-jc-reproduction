import json,re,itertools
from parse_readout import parse
def bounds(text,m):
 bg=m.get('background_gold')
 if not bg:return dict(lower=0,upper=0,observed_complete=0,reason='NO_BACKGROUND',fields={},compatible=[])
 parsed=parse(text);mapping=parsed['mapping'];basis='FROZEN_FULL_RESPONSE_PARSE'
 if mapping is None:
  # Partial valid JSON object is used only to establish known fields for bounds, never as a scored answer.
  try:
   def obj(ps):
    if len(dict(ps))!=len(ps):raise ValueError('duplicate keys')
    return dict(ps)
   d=json.loads(text.strip(),object_pairs_hook=obj)
   if not isinstance(d,dict) or not set(d)<= {'actor','undergoer'}:raise ValueError('not partial role object')
   mapping=d;basis='WHOLE_VALID_PARTIAL_JSON_FIELDS_ONLY'
  except (ValueError,TypeError):mapping={};basis='UNPARSED_OR_CONFLICTING_OBJECT_ALL_FIELDS_UNRESOLVED'
 known_names={v for v in m['entity_map'].values() if v in m['source_text']}|set(m.get('demo_names_present',[]));fields={}
 for key in ['actor','undergoer']:
  value=mapping.get(key)
  if key not in mapping:fields[key]={'known':False,'reason':'MISSING_OR_UNPARSED'}
  elif value is None:fields[key]={'known':False,'reason':'NULL'}
  elif isinstance(value,str) and value in known_names:fields[key]={'known':True,'value':value,'reason':'EXACT_PRESENTED_NAME'}
  elif isinstance(value,str) and re.fullmatch(r'[\u3400-\u9fff]{3}',value):fields[key]={'known':True,'value':value,'reason':'LITERAL_COMPLETE_THREE_CHARACTER_NAME_NOT_ALIAS'}
  else:fields[key]={'known':False,'value':value,'reason':'UNRESOLVED_VALUE_NO_COMPLETION_OR_ALIAS'}
 candidates=[bg,{'actor':bg['undergoer'],'undergoer':bg['actor']}];compatible=[c for c in candidates if all(not f['known'] or f['value']==c[k] for k,f in fields.items())];observed=int(parsed['mapping'] in candidates);return dict(lower=observed,upper=int(bool(compatible)),observed_complete=observed,reason=basis,fields=fields,compatible=compatible)
def synthetic():
 m={'entity_map':{'A':'赵知远','B':'郑若辰','C':'蒋若桐','D':'尤书桐'},'source_text':'赵知远郑若辰蒋若桐尤书桐','background_gold':{'actor':'蒋若桐','undergoer':'尤书桐'},'demo_names_present':[]};cases=[({'actor':'蒋若桐','undergoer':'尤书桐'},(1,1)),({'actor':'赵知远','undergoer':'郑若辰'},(0,0)),({'actor':'蒋若桐','undergoer':'蒋若桐'},(0,0)),({'actor':'蒋若桐','undergoer':None},(0,1)),({'actor':'赵知远','undergoer':None},(0,0)),({'actor':'蒋若桐','undergoer':'别姓名'},(0,0)),({'actor':None,'undergoer':None},(0,1)),({'actor':'蒋若'},(0,1)),({'actor':'赵知远'},(0,0))];out=[]
 for value,expected in cases:
  b=bounds(json.dumps(value,ensure_ascii=False),m);assert (b['lower'],b['upper'])==expected;(out.append({'input':value,'bounds':b}))
 for text in ['not a JSON object','{"actor":"蒋若桐","actor":"赵知远","undergoer":null}','{"actor":"蒋若']:
  b=bounds(text,m);assert (b['lower'],b['upper'])==(0,1);out.append({'input':text,'bounds':b})
 # Additional determined fields can only shrink compatible mapping sets.
 vals=[None,'赵知远','蒋若桐','尤书桐','别姓名']
 for a,u in itertools.product(vals,repeat=2):
  x=bounds(json.dumps({'actor':a,'undergoer':None},ensure_ascii=False),m);y=bounds(json.dumps({'actor':a,'undergoer':u},ensure_ascii=False),m);assert y['lower']<=y['upper'];assert all(c in x['compatible'] for c in y['compatible'])
 return {'status':'PASS','cases':out,'monotonic_cases':25,'model_calls':0}
