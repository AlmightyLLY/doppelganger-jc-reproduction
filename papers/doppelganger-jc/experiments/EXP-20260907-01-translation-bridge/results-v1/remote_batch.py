import os,json,hashlib,sys,time,platform,subprocess,gc
from pathlib import Path
from datetime import datetime,timezone
R=Path(__file__).resolve().parent
for k in ['HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE','HF_HUB_DISABLE_IMPLICIT_TOKEN','HF_HUB_DISABLE_TELEMETRY']:os.environ[k]='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
os.environ['HF_HOME']=str(R/'cache');os.environ['XDG_CACHE_HOME']=str(R/'cache')
def now():return datetime.now(timezone.utc).isoformat()
def read(p):return json.loads(Path(p).read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(n,v):
 with (R/n).open('x') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def append(n,v):
 with (R/n).open('a') as f:f.write(json.dumps(v,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
S=read(R/'FROZEN-RUN-SPEC.json');P=read(R/'PROMPTS.json');E=read(R/'ENGINEERING.json')
def gpu():return subprocess.check_output(['nvidia-smi','--query-gpu=index,uuid,memory.used,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True)
def inputs(info):
 from transformers import AutoTokenizer
 tok=AutoTokenizer.from_pretrained(info['snapshot'],local_files_only=True,trust_remote_code=False)
 template=tok.get_chat_template();assert hashlib.sha256(template.encode()).hexdigest()==S['expected_template_hashes'][info['key']]
 rows=[]
 for p in P:
  kwargs={'add_generation_prompt':True,'tokenize':False}
  if info['key']=='qwen':kwargs['enable_thinking']=False
  rendered=tok.apply_chat_template(p['messages'],**kwargs)
  tokenkwargs=dict(kwargs,tokenize=True)
  ids=tok.apply_chat_template(p['messages'],**tokenkwargs)
  assert ids==tok.encode(rendered,add_special_tokens=False)
  rows.append(dict(**p,rendered_native_input=rendered,input_token_ids=ids,input_token_n=len(ids),input_full_decode=tok.decode(ids,skip_special_tokens=False),template_sha256=hashlib.sha256(template.encode()).hexdigest(),template_kwargs=kwargs))
 return tok,rows,template
def preflight():
 assert len(P)==48 and sha(R/'FROZEN-RUN-SPEC.json')=='47a4f6440a4e98c623fb2ee5af21563c8d0d8b9ee0309cb4bf6d8c2191291074'
 for x in read(R/'MANIFEST.json')['files']:assert sha(R/x['path'])==x['sha256']
 import torch,transformers
 save('ENVIRONMENT.json',dict(at=now(),python=platform.python_version(),torch=torch.__version__,transformers=transformers.__version__,uid=os.getuid(),gpu=gpu(),pip_freeze=subprocess.check_output([sys.executable,'-m','pip','freeze'],text=True)))
 for info in E['models']:
  frozen=next(x for x in S['models'] if x['key']==info['key'])
  assert info['revision']==frozen['revision'] and info['model_id']==frozen['model_id'] and Path(info['snapshot']).name==frozen['revision']
  weights={}
  for n,v in E['model_files'][info['key']].items():
   p=Path(info['snapshot'])/n
   assert p.stat().st_size==v['bytes'] and sha(p)==v['sha256'],str(p)
   weights[n]=v
  tok,rows,template=inputs(info)
  save('PREFLIGHT-'+info['key']+'.json',dict(at=now(),model=info,weights=weights,template=template,rows=rows,generation_config=read(Path(info['snapshot'])/'generation_config.json'),model_loaded=False,new_outputs=0))
  print(json.dumps(dict(event='PREFLIGHT_MODEL_PASS',model=info['key'],rows=len(rows))),flush=True)
 save('PREGENERATION-GATE.json',dict(at=now(),status='PASS',models=3,exact_messages=48,native_inputs=144,planned_outputs=144,new_outputs=0))
def run():
 assert read(R/'PREGENERATION-GATE.json')['status']=='PASS'
 assert not (R/'INFERENCE-START.json').exists(),'No duplicate execution'
 import torch,transformers
 from transformers import AutoModelForCausalLM
 started=time.monotonic();deadline=started+60*60
 save('INFERENCE-START.json',dict(at=now(),pid=os.getpid(),max_wall_minutes=60))
 torch.manual_seed(0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 attempts=0;failed=0;outputs=0
 try:
  for info in E['models']:
   assert time.monotonic()<deadline
   lines=gpu().splitlines(); fields=[x.strip() for x in lines[0].split(',')]; uuid=fields[1]
   apps=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid','--format=csv,noheader'],text=True)
   assert uuid not in apps and int(fields[3])>32000 and int(fields[2])<4096,'GPU0 not free'
   save('GPU-BEFORE-'+info['key']+'.json',dict(at=now(),state=lines,apps=apps))
   tok,rows,_=inputs(info);pre=read(R/('PREFLIGHT-'+info['key']+'.json'))
   assert rows==pre['rows']
   model=AutoModelForCausalLM.from_pretrained(info['snapshot'],local_files_only=True,trust_remote_code=False,torch_dtype=torch.bfloat16,device_map={'':'cuda:0'},attn_implementation='eager',use_safetensors=True);model.eval()
   config=model.generation_config.to_dict()
   save('RUNTIME-'+info['key']+'.json',dict(at=now(),model=info,dtype='bfloat16',attention='eager',use_cache=True,do_sample=False,seed=0,max_new_tokens=256,model_generation_config=config,explicit_generate_kwargs=dict(do_sample=False,max_new_tokens=256,use_cache=True),runner_sha256=sha(Path(__file__))))
   print(json.dumps(dict(event='MODEL_LOADED',model=info['key'])),flush=True)
   for p in rows:
    for retry in range(2):
     assert attempts<156 and time.monotonic()<deadline and failed<2,'Budget or consecutive failure stop'
     attempts+=1; t=time.monotonic();trace=info['key']+'-'+p['prompt_id']
     append('ATTEMPTS.jsonl',dict(event='START',at=now(),attempt=attempts,retry=retry,trace_id=trace))
     try:
      ids=torch.tensor([p['input_token_ids']],device='cuda:0')
      with torch.inference_mode():
       result=model.generate(input_ids=ids,attention_mask=torch.ones_like(ids),do_sample=False,max_new_tokens=256,use_cache=True)
      seq=result[0].tolist();assert seq[:len(p['input_token_ids'])]==p['input_token_ids']
      out=seq[len(p['input_token_ids']):];eos=config.get('eos_token_id');eos=[eos] if isinstance(eos,int) else eos
      stop='eos' if out and out[-1] in eos else 'max_new_tokens'
      row=dict(**p,trace_id=trace,model=info['key'],revision=info['revision'],attempt=attempts,retry=retry,at=now(),seconds=time.monotonic()-t,output_token_ids=out,output_token_n=len(out),raw_output=tok.decode(out,skip_special_tokens=True),output_full_decode=tok.decode(out,skip_special_tokens=False),full_sequence_decode=tok.decode(seq,skip_special_tokens=False),stop_reason=stop)
      append('OUTPUTS.jsonl',row);outputs+=1;failed=0
      append('ATTEMPTS.jsonl',dict(event='SUCCESS',at=now(),attempt=attempts,trace_id=trace,stop_reason=stop,output_token_n=len(out)))
      print(json.dumps(dict(event='OUTPUT',model=info['key'],outputs=outputs,attempts=attempts)),flush=True)
      del result,ids;break
     except Exception as exc:
      failed+=1;append('ATTEMPTS.jsonl',dict(event='ERROR',at=now(),attempt=attempts,trace_id=trace,error_type=type(exc).__name__,error=str(exc)))
      if failed>=2:raise
      torch.cuda.empty_cache()
   del model;gc.collect();torch.cuda.empty_cache()
   save('GPU-AFTER-'+info['key']+'.json',dict(at=now(),state=gpu()))
  save('COMPLETE.json',dict(at=now(),outputs=outputs,attempts=attempts,wall_seconds=time.monotonic()-started,paid_usd=0))
 except BaseException as exc:
  save('FAILED.json',dict(at=now(),outputs=outputs,attempts=attempts,error_type=type(exc).__name__,error=str(exc),wall_seconds=time.monotonic()-started));raise
if __name__=='__main__':
 if sys.argv[1]=='preflight':preflight()
 elif sys.argv[1]=='run':run()
