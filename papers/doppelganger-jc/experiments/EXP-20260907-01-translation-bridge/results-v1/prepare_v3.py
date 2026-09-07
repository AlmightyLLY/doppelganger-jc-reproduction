import json,collections,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent
rows=json.loads((R/'RESULTS-SCORED-v1.json').read_text())
stats=[]
for scope in ['ALL','qwen','llmjp','apertus','F01','F02','F03','F04']:
 for task in ['TRANSLATE','EVENT_QA']:
  for cond in ['ALL','K','H','P']:
   rr=[r for r in rows if (scope=='ALL' or r['model']==scope or r['family_id']==scope) and r['task']==task and (cond=='ALL' or r['condition']==cond)]
   for field in ['lexical','event']:
    cc=collections.Counter(r[field] for r in rr)
    stats.append(dict(scope=scope,task=task,condition=cond,field=field,n=len(rr),**{k:cc[k] for k in ['C','W','U']}))
cases=[]
for r in rows:
 if r['ai_provisional']=='C':continue
 if r['trace_id'].startswith('llmjp-B04-'):kind='无依据具体添加';note='发烧不支持高烧程度，但不必然与原文矛盾；v1并入W偏离或超出已明定口径。'
 elif r['trace_id'] in ['apertus-B02-K-TRANSLATE','apertus-B02-P-TRANSLATE','apertus-B05-H-TRANSLATE']:kind='纯遗漏';note='桌上或应聘身份遗漏是全文保真问题；原约定另列遗漏，不能直接据此称明确矛盾W。'
 elif r['trace_id']=='apertus-B02-H-TRANSLATE' or (r['model']=='apertus' and r['base_id'] in ['B05','B06'] and r['task']=='EVENT_QA'):kind='明确矛盾候选';note='完整句含与源文冲突的状态；仍为AI判断，须PI检查。'
 else:kind='语义歧义';note='语义或否定附着范围待核对；尤其Qwen B02的v1 W不得称已确定反义。'
 cases.append(dict(trace_id=r['trace_id'],kind=kind,source=r['source'],task=r['task'],message=r['messages'][0]['content'],answer=r['answer_text'],v1_label=r['ai_provisional'],v1_reason=r['ai_reason'],disclosure=note,pi_review=None))
out=dict(status='AI_SCORING_SCOPE_REVIEW_REQUIRED',no_new_scoring=True,original_definition='C为目标事实正确，W为明确矛盾，U为不足以确定；遗漏与添加另列。',v1_deviation='AI v1把纯遗漏及无依据具体添加并入总W；该较严格全文保真层不能冒充预注册主分。',counts=stats,cases=cases,case_counts=dict(collections.Counter(x['kind'] for x in cases)),preserved_files={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in ['RESULTS-SCORED-v1.json','ANALYSIS-v1.json','05-实验结果总结-v2.docx','06-完整结果与审核-v2.xlsx','download_070900/OUTPUTS.jsonl']})
(R/'SCORING-SCOPE-REVIEW-v3.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
# New presentation builder; preserve old builders and outputs.
s=(R/'build_results_excel.mjs').read_text()
s=s.replace("const wb=Workbook.create();const previews=[];","const v3=JSON.parse(await fs.readFile(R+'SCORING-SCOPE-REVIEW-v3.json','utf8'));\nconst wb=Workbook.create();const previews=[];")
start=s.index('const selected=selection.map');end=s.index('const headers=',start)
review=s[start:end];s=s[:start]+s[end:]
pos=s.index('const summary=');s=s[:pos]+review+s[pos:]
s=s.replace("'结果汇总'","'AIv1总表待复核'")
s=s.replace("'AI provisional，输出本人审核待完成，独立人审0'","'AI v1较严格全文保真层，含口径偏离，不能当预注册主分'")
s=s.replace("'W可来自遗漏或无依据添加；词义和核心事件另列'","'原W为明确矛盾；v1将遗漏与添加并入W，须PI核对'")
s=s.replace("'AI C/W/U'","'AIv1总分 待核对'").replace("'完整译文'","'AIv1全文层 待核对'").replace("'AI评分'","'AIv1待核对'")
s=s.replace("'K与H及P配对'","'AIv1配对待核对'").replace("'翻译完整语义'","'翻译AIv1待核对'").replace("'问答完整语义'","'问答AIv1待核对'")
s=s.replace("['C/W/U','C完整保留任务所需语义；W存在实质矛盾、完整翻译遗漏或无依据具体添加；U为语义保留有歧义。核心事件另指题目所问动作与状态。']","['原协议口径','C为目标事实正确，W为明确矛盾，U为不足以确定；遗漏与添加另列。AI v1较严格全文保真总分包含未明定或偏离部分，不能当预注册错误率。']")
insert="""
sheet('评分口径待核对',[
 ['类别','追溯ID','完整原文与任务','完整答案','原AIv1标签','口径说明','PI判断'],
 ...v3.cases.map(r=>[r.kind,r.trace_id,r.message,r.answer,r.v1_label,r.disclosure,null])
],[25,35,88,75,18,85,24],180);
sheet('词义事件分项',[
 ['范围','任务','条件','既有分项','数量','C','W','U'],
 ...v3.counts.map(x=>[x.scope,x.task,x.condition,x.field==='lexical'?'词义':'核心事件',x.n,x.C,x.W,x.U])
],[20,22,14,22,14,14,14,14],32);
"""
s=s.replace('wb.recalculate();',insert+'\nwb.recalculate();')
s=s.replace('FINAL-EXCEL-','V3-EXCEL-').replace('final_excel_qa_','v3_excel_qa_').replace('06-完整结果与审核-v2.xlsx','08-完整结果与口径审核-v3.xlsx')
s=s.replace("'结果汇总!A1:G25'","'AIv1总表待复核!A1:G25'")
s=s.replace("'评分与来源':'A1:B6'","'评分与来源':'A1:B6','评分口径待核对':'A1:F3','词义事件分项':'A1:H9'")
s=s.replace('sheets:8','sheets:10')
(R/'build_results_excel_v3.mjs').write_text(s)
print(json.dumps(out['case_counts'],ensure_ascii=False))
