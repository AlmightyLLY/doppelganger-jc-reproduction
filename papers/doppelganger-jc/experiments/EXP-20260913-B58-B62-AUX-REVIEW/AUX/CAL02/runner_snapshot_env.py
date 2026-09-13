"""AUX-CAL-02 finite fixed-shape calibration. No retries or donor interventions."""
import os,json,time,hashlib,traceback
from pathlib import Path
os.environ['HF_HUB_OFFLINE']='1'
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
P=Path(__file__).resolve().parent;O=P/'results';O.mkdir(exist_ok=True)
load=lambda n:json.loads((P/n).read_text())
def save(n,x):(O/n).write_text(json.dumps(x,ensure_ascii=False,indent=2))
def append(n,x):
 with (O/n).open('a') as f:f.write(json.dumps(x,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
S=os.environ['APERTUS_SNAPSHOT']
class Run:
 def __init__(self):
  self.rows={r['input_id']:r for r in load('EXECUTION-INPUTS.json')['inputs']};self.jobs=load('JOBS.json');self.qa=load('CPU-QA.json');self.started=set();self.count=0;self.scored=0;self.t0=time.monotonic();self.done=[];self.states={};self.handles=[];self.gen={}
 def check(self):assert time.monotonic()-self.t0<1800,'TIME_LIMIT'
 def hooks(self):
  def make(l):
   def hook(mod,args,h):
    if self.patch and l==self.patch['layer']:
     a=self.patch['anchor'];ix=self.r['anchors'][a]['index'];v=self.states[self.r['input_id']][a][l].to(h);before=h[0,ix];eq=torch.equal(before,v)
     append('SELF-STATE.jsonl',{'key':self.key,'layer':l,'anchor':a,'equal':eq,'max_abs':float((before.float()-v.float()).abs().max())})
     assert eq,'SELF_STATE_FAILED'
     h=h.clone();h[0,ix]=v
    if self.capture:
     for a,d in self.r['anchors'].items():self.current[a][l]=h[0,d['index']].detach().cpu().clone()
    if self.rebuild and l==32:self.last=h.detach().clone()
    return h
   return hook
  self.handles=[self.model.model.embed_tokens.register_forward_hook(make(0))]+[b.register_forward_hook(make(i+1)) for i,b in enumerate(self.model.model.layers)]
 def unhook(self):
  for h in self.handles:h.remove()
  self.handles=[]
 def forward(self,ids,key,scored=0,capture=False,patch=None,rebuild=False):
  self.check();assert key not in self.started and self.count<2648 and self.scored+scored<=5120 and len(ids)<512
  free,_=torch.cuda.mem_get_info();assert free>=6*1024**3,'HEADROOM'
  self.started.add(key);self.count+=1;self.scored+=scored;self.key=key;self.patch=patch;self.capture=capture;self.rebuild=rebuild;self.last=None;self.current={a:[None]*33 for a in self.r['anchors']}
  append('LEDGER.jsonl',dict(event='STARTED',key=key,forwards=self.count,positions=self.count*512,scored_tokens=self.scored,real_length=len(ids)))
  x=torch.tensor([ids+[self.qa['pad_token_id']]*(512-len(ids))],device='cuda');m=torch.zeros_like(x);m[:,:len(ids)]=1
  out=self.model(input_ids=x,attention_mask=m,position_ids=torch.arange(512,device='cuda').unsqueeze(0),use_cache=False,return_dict=True,logits_to_keep=0).logits
  assert out.shape[:2]==(1,512) and torch.isfinite(out).all(),'NONFINITE_OR_SHAPE'
  append('LEDGER.jsonl',dict(event='COMPLETE',key=key));self.check();return out
 def run(self):
  assert self.qa['status']=='PASS' and self.qa['pad_token_id']==3
  assert not (O/'LEDGER.jsonl').exists(),'NO_RETRY'
  for f,h in load('FREEZE.json')['runtime_files'].items():assert sha(P/f)==h,('HASH_DRIFT',f)
  torch.manual_seed(0);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
  free,total=torch.cuda.mem_get_info();assert free>=28*1024**3
  save('RESOURCE.json',dict(pid=os.getpid(),start_unix=time.time(),free_bytes=free,total_bytes=total,gpu=os.environ.get('CUDA_VISIBLE_DEVICES'),torch=torch.__version__))
  self.tok=AutoTokenizer.from_pretrained(S,local_files_only=True);self.eos=self.qa['eos_token_ids'];self.eos=[self.eos] if isinstance(self.eos,int) else self.eos
  self.model=AutoModelForCausalLM.from_pretrained(S,local_files_only=True,torch_dtype=torch.bfloat16,attn_implementation='eager',device_map={'':'cuda'}).eval();self.hooks()
  for j in self.jobs:
   self.check();self.r=self.rows[j['input_id']];ids=self.r['ids'];key=j['job_id'];task=j['task'];append('TASKS.jsonl',dict(j,status='STARTED'))
   if task=='PREFILL':
    do=list(self.rows).index(j['input_id'])<4
    out=self.forward(ids,key,capture=True,rebuild=do)
    if do:
     rebuilt=self.model.lm_head(self.model.model.norm(self.last));d=float((rebuilt.float()-out.float()).abs().max());eq=torch.equal(rebuilt.argmax(-1),out.argmax(-1));append('REBUILD.jsonl',dict(job_id=key,max_abs=d,argmax_equal=eq));assert d<=1e-4 and eq,'REBUILD_FAILED';del rebuilt
    f=O/(j['input_id']+'-prefill.pt');st={a:torch.stack(v) for a,v in self.current.items()};torch.save(st,f);h=sha(f);self.states[j['input_id']]=torch.load(f,weights_only=True);assert sha(f)==h and all(torch.equal(st[a],self.states[j['input_id']][a]) for a in st);append('TENSOR-HASHES.jsonl',dict(file=f.name,sha256=h,reloaded_equal=True))
   elif task in ['CANDIDATE_BASE','SELF_CANDIDATE']:
    c=next(c for c in self.r['candidates'] if c['candidate_id']==j['candidate_id']);cs=c['ids'];isbase=task=='CANDIDATE_BASE'
    out=self.forward(ids+cs,key,len(cs),capture=isbase,patch=None if isbase else j)
    if isbase:
     failures=[]
     for a,v in self.current.items():
      for l,h in enumerate(v):
       st=self.states[j['input_id']][a][l];eq=torch.equal(h,st);d=float((h.float()-st.float()).abs().max());append('PREFIX-STATE.jsonl',dict(job_id=key,anchor=a,layer=l,equal=eq,max_abs=d))
       if not eq:failures.append([a,l,d])
     assert not failures,('PREFIX_STATE_FAILED',failures)
    logits=out[0,len(ids)-1:len(ids)+len(cs)-1].detach().cpu().clone();lp=logits.float().log_softmax(-1)[torch.arange(len(cs)),torch.tensor(cs)]
    torch.save({'logits':logits,'token_logps':lp},O/(key+'.pt'))
    result=dict(j,token_logps=lp.tolist(),sum_logp=float(lp.double().sum()),logits_file=key+'.pt')
    if not isbase:
     base=torch.load(O/('CAL02-BASE-'+c['candidate_id']+'.pt'),weights_only=True);eq=torch.equal(logits,base['logits']) and torch.equal(lp,base['token_logps']);result.update(equal=eq,max_logit_abs=float((logits.float()-base['logits'].float()).abs().max()),max_logp_abs=float((lp-base['token_logps']).abs().max()))
    append('SCORES.jsonl',result)
    if not isbase:assert eq,'SELF_SCORE_FAILED'
   else:
    if task=='GEN_NOHOOK':self.unhook()
    elif not self.handles:self.hooks()
    gen=[]
    for step in range(128):
     out=self.forward(ids+gen,key+':'+str(step),patch=j if task=='GEN_SELF' else None);n=int(out[0,len(ids)+len(gen)-1].argmax());gen.append(n);append('GENERATION-STEPS.jsonl',dict(job_id=key,step=step,token=n))
     if n in self.eos:break
    text=self.tok.decode(gen[:-1] if gen[-1] in self.eos else gen,skip_special_tokens=False,clean_up_tokenization_spaces=False);result=dict(j,generated_ids=gen,generated_text=text,finish_reason='EOS' if gen[-1] in self.eos else 'LENGTH')
    if task=='GEN_BASE':self.gen[j['input_id']]=gen
    else:result['equal']=gen==self.gen[j['input_id']]
    append('GENERATIONS.jsonl',result)
    if task!='GEN_BASE':assert result['equal'],'GENERATION_IDENTITY_FAILED'
   self.done.append(key);append('TASKS.jsonl',dict(j,status='COMPLETE'));print(len(self.done),task,key,flush=True)
  return 'FIXED_SHAPE_CALIBRATION_PASS'
r=Run()
try:
 with torch.inference_mode():status=r.run()
 reason=None
except Exception as e:status='MEASUREMENT_NOT_CALIBRATED';reason=str(e);save('ERROR.json',dict(error=reason,traceback=traceback.format_exc()));print(traceback.format_exc(),flush=True)
finally:
 save('FINAL-STATUS.json',dict(status=status,reason=reason,completed_tasks=len(r.done),forwards=r.count,positions=r.count*512,scored_tokens=r.scored,seconds=time.monotonic()-r.t0,job_status=[dict(j,status='COMPLETE' if j['job_id'] in r.done else 'STARTED_INCOMPLETE' if any(k==j['job_id'] or k.startswith(j['job_id']+':') for k in r.started) else 'NOT_RUN') for j in r.jobs]));r.unhook()
