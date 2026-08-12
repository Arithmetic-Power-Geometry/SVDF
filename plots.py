from pathlib import Path
import matplotlib.pyplot as plt

def frontier_plot(results,path):
    r=results.copy(); p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(8.4,5.1))
    other=r[~r.frontier]; front=r[r.frontier].sort_values('implementation_complexity')
    ax.scatter(other.implementation_complexity,other.shared_value_gain,s=38,alpha=.48,label='Dominated interventions')
    ax.scatter(front.implementation_complexity,front.shared_value_gain,s=90,marker='D',label='SVDF frontier')
    ax.plot(front.implementation_complexity,front.shared_value_gain,linewidth=1.5)
    for _,row in front.iterrows():
        ax.annotate(str(row.project_id),(row.implementation_complexity,row.shared_value_gain),xytext=(5,6),textcoords='offset points',fontsize=9,fontweight='bold')
    ax.set_xlabel('Implementation Complexity, IC (lower is preferred)')
    ax.set_ylabel('Shared Value Gain, SVG (higher is preferred)')
    ax.set_title('Shared Value Decision Frontier')
    ax.legend(frameon=False,loc='lower right'); ax.grid(alpha=.18)
    fig.tight_layout(); fig.savefig(p,dpi=300,bbox_inches='tight'); plt.close(fig); return p

def robustness_plot(results,path):
    r=results.sort_values('frontier_frequency',ascending=False).head(10).copy(); p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    fig,ax=plt.subplots(figsize=(8.4,4.7))
    bars=ax.bar(r.project_id.astype(str),100*r.frontier_frequency)
    ax.set_ylim(0,105); ax.set_ylabel('Frontier selection frequency (%)')
    ax.set_xlabel('Intervention ID'); ax.set_title('Robustness across alternative model specifications')
    ax.grid(axis='y',alpha=.18)
    for b,v in zip(bars,100*r.frontier_frequency):
        if v>=20: ax.text(b.get_x()+b.get_width()/2,v+2,f'{v:.1f}',ha='center',fontsize=8)
    fig.tight_layout(); fig.savefig(p,dpi=300,bbox_inches='tight'); plt.close(fig); return p
