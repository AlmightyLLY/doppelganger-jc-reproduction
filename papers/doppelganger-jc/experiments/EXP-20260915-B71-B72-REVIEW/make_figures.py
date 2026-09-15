from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;F=P/'figures';F.mkdir(exist_ok=True)
summary=json.loads((P/'SUMMARY.json').read_text());strata=json.loads((P/'STRATA.json').read_text())
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
labels=['0.6B','1.7B','4B','8B','14B','32B'];keys=['B72|K0|qwen-'+s if s!='8B' else 'B71|K0|qwen' for s in labels]
ix={'|'.join(x[k] for k in ['batch','contract','model']):x for x in summary};x=np.arange(6);C=np.array([ix[k]['C'] for k in keys]);strict=np.array([ix[k]['C_and_format'] for k in keys])
fig,ax=plt.subplots(figsize=(9,4.7));ax.bar(x-.18,C/576*100,.35,label='Correct role mapping',color='#246B8E');ax.bar(x+.18,strict/576*100,.35,label='Correct mapping and required format',color='#E3A34A')
for i in x:ax.text(i-.18,C[i]/576*100+2,str(C[i]),ha='center',fontsize=10);ax.text(i+.18,strict[i]/576*100+2,str(strict[i]),ha='center',fontsize=10)
ax.set(xticks=x,xticklabels=labels,ylim=(0,121),ylabel='Accuracy (%)',xlabel='Qwen3 model snapshot',title='Same 576 K0 inputs across six Qwen3 sizes');ax.legend(loc='upper left',frameon=False,ncols=2,fontsize=10);ax.set_yticks([0,25,50,75,100]);ax.grid(axis='y',alpha=.15);ax.set_axisbelow(True)
fig.text(.13,.01,'Bar labels are counts / 576. The 8B reference is reused from B71; no new materials or human gold.',fontsize=9);fig.tight_layout(rect=[0,.04,1,1]);
for ext in ['png','svg']:fig.savefig(F/('scale-correctness.'+ext),dpi=190)
plt.close(fig)
cols=keys+['B71|K0|apertus'];clabels=labels+['Apertus 8B'];conditions=[(co,sc,bg) for co in ['BA','BEI'] for sc in ['AU','UA'] for bg in ['NONE','BA','BEI']];mat=np.array([[strata[k+'|'+'|'.join(c)]['R'] for k in cols] for c in conditions]);fig,ax=plt.subplots(figsize=(9.2,7.4));im=ax.imshow(mat,cmap='YlOrRd',vmin=0,vmax=48,aspect='auto')
for i in range(12):
 for j in range(7):ax.text(j,i,str(mat[i,j]),ha='center',va='center',color='white' if mat[i,j]>=29 else '#202020',fontsize=11)
ax.set(xticks=np.arange(7),xticklabels=clabels,yticks=np.arange(12),yticklabels=[f'{co} / {sc} / {bg}' for co,sc,bg in conditions],title='Role reversals change location across model snapshots',ylabel='Target / output order / background')
for pos in [2.5,5.5,8.5]:ax.axhline(pos,color='white',lw=2)
cb=fig.colorbar(im,ax=ax,shrink=.85);cb.set_label('Exact reversals / 48 inputs');fig.text(.12,.01,'AU = actor first; UA = undergoer first. NONE = no background.\nReversal counts exclude other errors; 0.6B has 226 other errors and extensive format failures.',fontsize=9);fig.tight_layout(rect=[0,.055,1,1]);
for ext in ['png','svg']:fig.savefig(F/('reversal-strata.'+ext),dpi=190)
plt.close(fig)
ps=json.loads((P/'K0-K1-TRANSITIONS.json').read_text());fig,ax=plt.subplots(figsize=(7.4,4));xx=np.arange(2);models=['qwen','apertus'];res=[sum(p['rescue'] for p in ps if p['model']==m) for m in models];har=[sum(p['harm'] for p in ps if p['model']==m) for m in models];ax.barh(xx+.15,res,.29,color='#246B8E',label='Rescued');ax.barh(xx-.15,[-v for v in har],.29,color='#B84D46',label='Newly harmed');ax.axvline(0,color='#333',lw=.7)
for i in range(2):ax.text(res[i]+.7,i+.15,str(res[i]),va='center');ax.text(-har[i]-.7,i-.15,str(har[i]),ha='right',va='center')
ax.set(yticks=xx,yticklabels=['Qwen3 8B','Apertus 8B'],xlim=(-33,17),xlabel='Number of changed items out of 576 paired inputs',title='Changing the output contract brings both rescues and harms');ax.legend(frameon=False,loc='lower right');ax.grid(axis='x',alpha=.15);ax.set_axisbelow(True);fig.tight_layout()
for ext in ['png','svg']:fig.savefig(F/('contract-transitions.'+ext),dpi=190)
plt.close(fig)
print('Three scientific figures written')
