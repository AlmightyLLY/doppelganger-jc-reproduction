import json,hashlib,collections,itertools
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent; D=R/'download_070900'
raw=[json.loads(s) for s in (D/'OUTPUTS.jsonl').read_text().splitlines()]
old=[json.loads(s) for s in (R/'download_070531/OUTPUTS.jsonl').read_text().splitlines()]
assert raw[:48]==old
assert len(raw)==144 and len({r['trace_id'] for r in raw})==144
plans={r['trace_id']:r for r in json.loads((R/'PLANNED-RESULTS.json').read_text())}
core_reasons={
'B01':'书信及已寄给妹妹的事件正确。',
'B02':'书信及尚未寄给妹妹的事件正确。',
'B03':'学习数学两小时及自愿性保留。',
'B04':'原计划学习数学，发烧后取消并未开始学习。',
'B05':'已决定录用，工作从下个月开始，未写成已经上岗。',
'B06':'最终取消录用且从未在该公司工作。',
'B07':'预订已完成且房费尚未支付。',
'B08':'客满导致未订成，房费尚未支付。'}
overrides={}
def put(ids,**v):
 for i in ids:overrides[i]=v.copy()
put(['qwen-B02-K-TRANSLATE','qwen-B02-H-TRANSLATE'],ai_provisional='W',full_translation='W',ai_reason='“还没有装进信封寄出”按通常读法否定已装入信封，与原文已装好相冲突。未寄出的核心状态仍正确。连动否定的附着范围列入人审复核。',addition='未装入信封的否定状态',review_flag='否定范围需人审；完整译文事实错误候选')
put(['qwen-B01-P-EVENT_QA'],ai_provisional='U',lexical='U',ai_reason='保留日语“便り”而未给出可确认的中文物品意义；寄出状态正确。不能因原词复制直接判错义。',language='中日混合',review_flag='词义未决；非中文目标词')
put(['llmjp-B02-P-TRANSLATE'],ai_provisional='U',full_translation='U',ai_reason='“把信封放进了桌子上”搭配不清，未明确保留信已装入信封的关系；未寄出正确。语义可修复但不足以直接判完整正确或明确相反。',omission='信在信封内的关系不清',fluency='介词搭配异常',review_flag='完整译文未决；P相对K损害候选')
put([f'llmjp-B04-{c}-{t}' for c in ['K','H','P'] for t in ['TRANSLATE','EVENT_QA']],ai_provisional='W',ai_reason='原文只说发烧，输出增加“高烧”的程度，属于未获原文支持的具体信息。学习计划未实现的核心事件正确；该严格语义保真判断需人审确认。',addition='高烧程度，原文仅发烧',review_flag='额外具体信息；核心事件仍正确；需人审尺度复核')
put(['apertus-B02-K-TRANSLATE','apertus-B02-P-TRANSLATE'],ai_provisional='W',full_translation='W',ai_reason='保留写信、装在信封内及未寄出，但完整翻译遗漏“放在桌上”。词义及寄信状态正确。',omission='放在桌上',review_flag='完整翻译遗漏')
put(['apertus-B02-H-TRANSLATE'],ai_provisional='W',full_translation='W',ai_reason='明确说“没有把它放进信封里，而是放在桌子上”，与原文信已装入信封相反；“妹妹的信”也弱化了收信人方向。未寄出状态仍正确。',addition='未装入信封，与原文相反',review_flag='明确事实矛盾；K/H均非完整正确')
put(['apertus-B03-H-TRANSLATE'],ai_provisional='U',event='U',full_translation='U',ai_reason='“自己走到桌前”可指独自行动，也可语境理解为主动；不足以明确保留自分から的自愿性，但并未明确写成被迫。学习内容及时长正确，保留U。',omission='主动性保留不明确',review_flag='自愿性未决；H相对K损害候选')
put(['apertus-B05-H-TRANSLATE'],ai_provisional='W',full_translation='W',ai_reason='聘请工程师及下月付薪工作正确，但完整翻译遗漏此人前来应聘的身份信息；不因工程师这一合义表述机械判错。',omission='前来应聘',review_flag='完整翻译遗漏；H相对K新增损害')
put([f'apertus-B05-{c}-EVENT_QA' for c in ['K','H','P']],ai_provisional='W',event='W',ai_reason='把下个月开始付薪工作的安排推成“已经开始上班”，与尚未上岗的状态相反。',addition='已经开始上班',review_flag='明确事件错误；与翻译不一致')
put([f'apertus-B06-{c}-EVENT_QA' for c in ['K','H','P']],ai_provisional='W',event='W',ai_reason='说公司最后决定让技术人员来工作，违反签约前取消录用；未上班这一子答案正确。',addition='最后仍录用，与取消录用相反',review_flag='明确事件错误；与翻译不一致')
results=[]
for row in raw:
 p=plans[row['trace_id']]; answer=row['raw_output'];channel=None
 if row['model']=='llmjp':
  full=row['output_full_decode'];assert full.startswith('<|channel|> final<|message|>') and full.endswith('<|return|>')
  answer=full.split('<|message|>',1)[1].removesuffix('<|return|>').strip();channel='final'
 r={**p,**row,'status':'GENERATED','answer_text':answer,'native_output_channel':channel,'ai_provisional':'C','lexical':'C','event':'C','full_translation':'C' if p['task']=='TRANSLATE' else None,'language':'中文','format':'符合任务格式','omission':'未见实质遗漏','addition':'未见无依据添加','fluency':'可理解','ai_reason':core_reasons[p['base_id']]+('完整译文按全句语义保留事实，接受合义措辞。' if p['task']=='TRANSLATE' else '回答覆盖题目要求；不要求复述所有原文细节。'),'review_flag':'','pi_review':None,'pi_understanding':None,'independent_review':None,'intermediate_output_note':'两个任务各次独立，没有多步轨迹；原生channel为序列格式，不是额外实验步骤。'}
 r.update(overrides.get(r['trace_id'],{}))
 if r['task']=='TRANSLATE':r['full_translation']=r['ai_provisional']
 if row['model']=='llmjp' and p['base_id']=='B03':r['fluency']='“去面对桌子”生硬；自学按本句语境接受，不据不自然直接判错'
 if row['model']=='llmjp' and p['base_id']=='B05' and p['task']=='TRANSLATE' and p['condition'] in ['K','P']:r['fluency']='“以工资形式工作”生硬，但保留付薪工作关系'
 if row['model']=='apertus' and p['base_id']=='B02' and p['condition']=='K' and p['task']=='EVENT_QA':r['language']='中文主体含日语词“封筒”';r['review_flag']='语言混用；不改变题目所问书信及未寄出正确性'
 results.append(r)
def counts(rr,field='ai_provisional'):return dict(collections.Counter(r[field] for r in rr))
aggregate=[]
for model in ['qwen','llmjp','apertus','ALL']:
 for task in ['TRANSLATE','EVENT_QA']:
  for c in ['K','H','P']:
   rr=[r for r in results if (model=='ALL' or r['model']==model) and r['task']==task and r['condition']==c]
   aggregate.append(dict(model=model,task=task,condition=c,n=len(rr),**{k:counts(rr).get(k,0) for k in ['C','W','U']}))
lookup={(r['model'],r['base_id'],r['task'],r['condition']):r for r in results}
pairs=[]
for model,base,task,other in itertools.product(['qwen','llmjp','apertus'],[f'B{i:02d}' for i in range(1,9)],['TRANSLATE','EVENT_QA'],['H','P']):
 a=lookup[model,base,task,'K'];b=lookup[model,base,task,other]
 pairs.append(dict(model=model,base_id=base,family=a['family_id'],relation=a['relation'],task=task,comparison='K-'+other,K=a['ai_provisional'],other=b['ai_provisional'],transition=a['ai_provisional']+'->'+b['ai_provisional'],K_id=a['trace_id'],other_id=b['trace_id']))
cross=[]
for model,base,c in itertools.product(['qwen','llmjp','apertus'],[f'B{i:02d}' for i in range(1,9)],['K','H','P']):
 t=lookup[model,base,'TRANSLATE',c];q=lookup[model,base,'EVENT_QA',c]
 cross.append(dict(model=model,base_id=base,condition=c,translate=t['ai_provisional'],qa=q['ai_provisional'],translate_event=t['event'],qa_event=q['event'],translation_id=t['trace_id'],qa_id=q['trace_id']))
analysis=dict(at=datetime.now(timezone.utc).isoformat(),evidence='AI provisional full-response semantic review; not human gold',scoring_note='C/W/U separate from language/format; full translation omissions and unsupported additions can be W despite correct lexical/event core; ambiguous preservation remains U. Borderline judgments explicitly marked for human review.',native_channel_handling='LLM-jp generated final channel markers are parsed structurally from complete native decode; raw skip-special decode and full decode retained unchanged, final is not scored as added prose.',aggregate=aggregate,pairs=pairs,cross_task=cross,reviewed_outputs=144,independent_gold=0)
for n,v in [('RESULTS-SCORED-v1.json',results),('ANALYSIS-v1.json',analysis)]:
 with (R/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2)
validation=dict(outputs=144,all_trace_ids_unique=True,first48_exactly_unchanged=raw[:48]==old,attempts=144,generation_errors=0,technical_resource_gate_stops=1,wall_seconds=json.loads((D/'COMPLETE.json').read_text())['wall_seconds'],all_eos=all(r['stop_reason']=='eos' for r in raw),native_cpu_replay=json.loads((D/'CPU-REPLAY-VERIFICATION.json').read_text()),human_fields_all_blank=all(r['pi_review'] is None and r['independent_review'] is None for r in results),paid_usd=0)
(R/'FINAL-VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2))
print(json.dumps(aggregate,ensure_ascii=False));print(json.dumps(validation,ensure_ascii=False))
