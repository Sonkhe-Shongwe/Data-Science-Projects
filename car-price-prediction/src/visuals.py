"""Publication-ready static figures generated exclusively from reproduced results."""
from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import numpy as np
import pandas as pd

BG='#081426';PANEL='#10233a';PANEL2='#132b44';INK='#eff6fd';MUTED='#a4b9cc';TEAL='#48d4bf';BLUE='#75aef9';ORANGE='#ffb36d';ROSE='#f47b87';GRID='#2b4763';SOFT='#738aa3'
COLORS={"Car":BLUE,"Two-wheeler":TEAL}


def theme():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'text.color':INK,
      'figure.facecolor':BG,'savefig.facecolor':BG, 'axes.facecolor':PANEL,
      'axes.edgecolor':GRID,'axes.labelcolor':MUTED,
      'xtick.color':MUTED,'ytick.color':MUTED,'grid.color':GRID,
      'legend.facecolor':PANEL,'legend.edgecolor':GRID,
      'savefig.dpi':145})


def start(title,subtitle,w=15.5,h=8.5):
    fig=plt.figure(figsize=(w,h),facecolor=BG)
    fig.text(.056,.934,title,fontsize=29,fontweight='bold',color=INK,va='top')
    fig.text(.057,.871,subtitle,fontsize=12.5,color=MUTED,va='top')
    fig.text(.942,.956,'SONKHE SHONGWE   /   DATA SCIENCE',fontsize=8.3,ha='right',va='top',color=TEAL,fontweight='bold')
    return fig


def clean(ax,xgrid=False,ygrid=False):
    for sp in ax.spines.values():sp.set_visible(False)
    ax.set_axisbelow(True)
    if xgrid:ax.grid(axis='x',alpha=.65)
    if ygrid:ax.grid(axis='y',alpha=.65)
    ax.tick_params(length=0,pad=8)


def footer(fig,txt):
    fig.text(.055,.040,txt,fontsize=9.0,color=MUTED,va='bottom')


def save(fig,path):
    fig.savefig(path,dpi=145,facecolor=BG)
    plt.close(fig)


def generate_all_figures(r,out:Path):
    theme(); out.mkdir(parents=True,exist_ok=True)
    df=r['df'];score=r['table'];test=r['test_rows'];summ=r['summary'];seg=r['segments'];ab=r['ablation'];imp=r['imp']
    top=summ['champion'];ts=summ['final_test'];grp=summ['unseen_model_stress']
    # Cover 0: high-impact executive overview
    fig=start('USED VEHICLE PRICE INTELLIGENCE',
              'Resale valuation  /  299 unique records  /  cross-validated model selection  /  reliability diagnostics',16,9)
    for j,(heading,value,small) in enumerate([('CHAMPION',top,'selected by 5-fold CV MAE'),
          ('HELD-OUT R²',f'{ts["R2"]:.3f}','60 unseen evaluation rows'),
          ('HELD-OUT MAE',f'{ts["MAE"]:.2f}','in source price units'),
          ('HIGH-VALUE ERROR',f'{seg.loc[(seg.Dimension=="Price_Segment")&(seg.Group=="Over 10L"),"MAE"].iloc[0]:.2f}','MAE for 7 vehicles over 10L')]):
        x=.055+j*.2325
        fig.add_artist(plt.Rectangle((x,.700),.212,.128,transform=fig.transFigure,facecolor=PANEL,edgecolor='none'))
        fig.text(x+.013,.790,heading,fontsize=11,color=MUTED,fontweight='bold')
        fig.text(x+.013,.741,value,fontsize=24 if j!=0 else 19,color=TEAL if j in (1,2) else INK,fontweight='bold')
        fig.text(x+.013,.716,small,fontsize=9,color=MUTED)
    ax=fig.add_axes([.183,.218,.327,.39]);clean(ax,xgrid=True)
    q=score.sort_values('CV_MAE',ascending=False)
    bars=ax.barh(q.Model,q.CV_MAE,color=[TEAL if x==top else SOFT for x in q.Model],height=.56)
    ax.set_xlim(0,score.CV_MAE.max()*1.28)
    ax.set_xlabel('Average 5-fold CV MAE  /  lower is better',fontsize=10.5)
    ax.set_title('MODEL SELECTION',fontsize=15,fontweight='bold',color=INK,pad=22)
    for b,val in zip(bars,q.CV_MAE):ax.text(b.get_width()+.055,b.get_y()+b.get_height()/2,f'{val:.2f}',va='center',color=INK,fontsize=11,fontweight='bold')
    ax2=fig.add_axes([.658,.235,.257,.350]);clean(ax2,xgrid=True)
    labels=['With price anchor','Without anchor'];vals=ab.CV_MAE.values
    ax2.barh([1,0], vals,color=[TEAL,ORANGE],height=.48)
    ax2.set_yticks([1,0],labels)
    ax2.set_xlim(0,max(vals)*1.25)
    for y,v in zip([1,0],vals):ax2.text(v+.04,y,f'{v:.2f}',va='center',fontsize=12,fontweight='bold')
    ax2.set_xlabel('5-fold CV MAE  /  lower is better',fontsize=10.5)
    ax2.set_title('THE PRICE-ANCHOR EFFECT',fontsize=15,fontweight='bold',color=INK,pad=22)
    fig.text(.057,.130,'KEY FINDING',fontsize=11,fontweight='bold',color=TEAL)
    fig.text(.057,.089,'Strong average accuracy masks higher errors on expensive vehicles. The reference-price feature is essential.',fontsize=13,color=INK)
    footer(fig,'Source: CarDekho-derived Kaggle sample  |  Prices reported in lakh INR in source documentation  |  Historical research, not a live quotation service')
    save(fig,out/'00_portfolio_cover.png')
    # 1: sampling and distribution
    fig=start('ONE DATASET, TWO VERY DIFFERENT VEHICLE MARKETS',
       'Seller type is heavily confounded with vehicle category; mixing them can create misleading explanations.')
    ax=fig.add_axes([.08,.25,.43,.51]);clean(ax,ygrid=True)
    rng=np.random.default_rng(43)
    for i,(cat,col) in enumerate(COLORS.items()):
        v=df.loc[df.Vehicle_Type==cat,'Selling_Price'].values
        ax.scatter(i+rng.normal(0,.09,len(v)),v,alpha=.55,s=22,color=col,linewidths=0)
        ax.hlines(np.median(v),i-.21,i+.21,color=INK,lw=3)
    ax.set_yscale('log');ax.set_ylim(.075,55)
    ax.set_xticks([0,1],['Cars','Motorcycles / scooters'])
    ax.set_ylabel('Selling price (lakh INR, logarithmic scale)')
    ax.set_title('Prices span very different ranges',fontsize=15,color=INK,pad=17,fontweight='bold')
    ax2=fig.add_axes([.62,.25,.30,.51]);clean(ax2,xgrid=True)
    tab=pd.crosstab(df.Vehicle_Type,df.Selling_type).reindex(['Car','Two-wheeler'])
    y=np.array([1,0]);den=tab.sum(axis=1).values
    frac=tab.get('Individual',pd.Series(0,index=tab.index)).values/den
    ax2.barh(y,1-frac,color=BLUE,label='Dealer',height=.46)
    ax2.barh(y,frac,left=1-frac,color=TEAL,label='Individual',height=.46)
    ax2.set_xlim(0,1.02)
    ax2.set_yticks(y,['Cars','Two-wheelers'])
    ax2.set_xticks(np.linspace(0,1,5),[f'{int(v*100)}%' for v in np.linspace(0,1,5)])
    ax2.legend(frameon=False,loc='lower right',fontsize=11)
    ax2.set_title('Seller channel by vehicle type',fontsize=15,color=INK,pad=17,fontweight='bold')
    fig.text(.08,.146,f'{summ["audit"]["cars"]} cars    ·    {summ["audit"]["two_wheelers"]} two-wheelers    ·    2 exact duplicates removed',fontsize=14,color=TEAL,fontweight='bold')
    footer(fig,'Classification based on a manually reviewed list of vehicle model names in the supplied 301-row dataset.')
    save(fig,out/'01_vehicle_mix.png')
    # 2 price relationships, log log and outlier
    fig=start('THE REFERENCE PRICE DOMINATES THE PRICING SIGNAL',
       'A log-scale view separates inexpensive motorcycles from higher-priced cars without hiding either segment.')
    ax=fig.add_axes([.12,.20,.67,.61]);clean(ax,xgrid=True,ygrid=True)
    for cat,col in COLORS.items():
        d=df[df.Vehicle_Type==cat]
        ax.scatter(d.Present_Price,d.Selling_Price,s=32,c=col,alpha=.72,label=cat,linewidths=0)
    ax.plot([.08,110],[.08,110],ls='--',color=ORANGE,lw=1.7,label='Selling = reference price')
    ax.set_xscale('log');ax.set_yscale('log');ax.set_xlim(.3,120);ax.set_ylim(.08,80)
    ax.set_xlabel('Reference / present price (lakh INR)');ax.set_ylabel('Selling price (lakh INR)')
    ax.legend(loc='upper left',frameon=False,fontsize=11)
    cruiser=df.loc[df.Present_Price.idxmax()]
    ax.annotate('Land Cruiser retained',xy=(cruiser.Present_Price,cruiser.Selling_Price),
        xytext=(12,48),color=INK,fontsize=12,arrowprops={'color':ROSE,'arrowstyle':'->','lw':1.6})
    fig.text(.08,.110,'Note: Observed association is not evidence of a causal pricing effect.',fontsize=11,color=MUTED)
    footer(fig,'Vehicle age cannot be calculated precisely without a verified valuation/reference date. Price-retention ratios are descriptive, not model features.')
    save(fig,out/'02_price_relationship.png')
    # 3 model comparison uncertainty
    fig=start('MODEL CHOICE WAS MADE BEFORE VIEWING THE FINAL TEST',
       'A consistent 5-fold CV process on the 239-row development set selects the model with lowest mean MAE.')
    ax=fig.add_axes([.24,.18,.65,.63]);clean(ax,xgrid=True)
    data=score.sort_values('CV_MAE',ascending=False)
    bars=ax.barh(data.Model,data.CV_MAE,xerr=data.CV_MAE_SD,
      color=[TEAL if name==top else SOFT for name in data.Model],height=.50,
      error_kw={'ecolor':INK,'elinewidth':1.4,'capsize':4})
    ax.set_xlim(0,score.CV_MAE.max()*1.35)
    ax.set_xlabel('Cross-validated mean absolute error  /  lakh INR')
    for b,v,sd in zip(bars,data.CV_MAE,data.CV_MAE_SD):ax.text(v+sd+.095,b.get_y()+b.get_height()/2,f'{v:.2f}',va='center',fontsize=11,color=INK)
    fig.text(.057,.094,f'SELECTED: {top.upper()}  ·  CV MAE {score.iloc[0].CV_MAE:.2f}  ·  test data not used in model choice',fontsize=13,color=TEAL,fontweight='bold')
    footer(fig,'Error bars = standard deviation of fold MAE (not a confidence interval). CV uses shuffled KFold(random_state=42).')
    save(fig,out/'03_cross_validation.png')
    # 4 holdout predicted vs actual
    fig=start('WHERE THE FINAL MODEL GETS PRICES RIGHT — AND WRONG',
       'The final 60-row test set was kept out of model selection and fitting.')
    ax=fig.add_axes([.12,.20,.59,.59]);clean(ax,xgrid=True,ygrid=True)
    for cat,col in COLORS.items():
        d=test[test.Vehicle_Type==cat]
        ax.scatter(d.Selling_Price,d.Predicted,s=54,c=col,alpha=.75,label=cat,edgecolors=BG,linewidths=.45)
    lim=max(test[['Selling_Price','Predicted']].max())*1.07
    ax.plot([0,lim],[0,lim],ls='--',color=ORANGE,lw=1.7,label='Perfect prediction')
    ax.set_xlim(-.5,lim);ax.set_ylim(-.5,lim)
    ax.set_xlabel('Actual selling price (lakh INR)');ax.set_ylabel('Predicted selling price (lakh INR)')
    ax.legend(loc='upper left',frameon=False)
    for _,row in test.nlargest(2,'Absolute_Error').iterrows():
        ax.annotate(f'{row.Car_Name[:17]}\nerror {row.Absolute_Error:.1f}',xy=(row.Selling_Price,row.Predicted),
          xytext=(5,-27),textcoords='offset points',color=INK,fontsize=10,
          arrowprops={'arrowstyle':'-','lw':.5,'color':ROSE})
    fig.text(.75,.60,f'{ts["R2"]:.3f}',fontsize=39,color=TEAL,fontweight='bold')
    fig.text(.75,.55,'Held-out R²',fontsize=12,color=MUTED)
    fig.text(.75,.44,f'{ts["MAE"]:.2f} L',fontsize=36,color=INK,fontweight='bold')
    fig.text(.75,.39,'Held-out MAE',fontsize=12,color=MUTED)
    fig.text(.75,.29,f'{ts["P90_AE"]:.2f} L',fontsize=32,color=INK,fontweight='bold')
    fig.text(.75,.24,'90th percentile abs. error',fontsize=11,color=MUTED)
    footer(fig,'Single protected held-out set  |  40 cars and 20 two-wheelers  |  R² is sample-specific; real-world accuracy is unverified.')
    save(fig,out/'04_holdout_predictions.png')
    # 5 subgroups
    fig=start('HIGH-PRICED VEHICLES REMAIN THE WEAK POINT',
       'A strong pooled R² conceals a much higher average absolute error for the small high-value test segment.')
    ax=fig.add_axes([.14,.25,.43,.51]);clean(ax,xgrid=True)
    p=seg[seg.Dimension=='Price_Segment'].set_index('Group').reindex(['Under 2L','2–10L','Over 10L'])
    labels=[f'{nm}  (n={int(p.loc[nm,"Count"])})' for nm in p.index]
    v=p.MAE.values
    bars=ax.barh(np.arange(3),v,color=[TEAL,BLUE,ORANGE],height=.55)
    ax.set_yticks(np.arange(3),labels);ax.invert_yaxis();ax.set_xlim(0,max(v)*1.28)
    ax.set_xlabel('Holdout MAE / lakh INR')
    for y,k in enumerate(v):ax.text(k+.05,y,f'{k:.2f}',va='center',color=INK,fontweight='bold')
    ax.set_title('Errors by selling-price band',fontsize=16,pad=20,fontweight='bold',color=INK)
    ax2=fig.add_axes([.69,.25,.22,.51]);clean(ax2,ygrid=True)
    z=seg[seg.Dimension=='Vehicle_Type'].set_index('Group').reindex(['Car','Two-wheeler'])
    ax2.bar(['Cars','Two-wheelers'],z.MAE.values,color=[BLUE,TEAL],width=.56)
    ax2.set_ylim(0,z.MAE.max()*1.25)
    ax2.set_ylabel('MAE / lakh INR')
    for i,v in enumerate(z.MAE.values):ax2.text(i,v+.03,f'{v:.2f}',color=INK,ha='center',fontweight='bold')
    ax2.set_title('Errors by category',fontsize=16,pad=20,fontweight='bold',color=INK)
    fig.text(.075,.126,'Interpretation: subgroup price levels differ; absolute MAE is not a like-for-like measure of relative accuracy.',color=MUTED,fontsize=11)
    footer(fig,'Small test subgroups, especially the 7 vehicles over 10L, yield unstable estimates. These are diagnostic, not production guarantees.')
    save(fig,out/'05_segment_errors.png')
    # 6 controlled feature ablation (development CV only)
    fig=start('HOW MUCH DOES THE REFERENCE PRICE REALLY MATTER?',
       'A controlled 5-fold CV experiment uses the same model, training rows and fold assignments in both scenarios.')
    ax=fig.add_axes([.17,.25,.51,.48]);clean(ax,xgrid=True)
    vals=ab.CV_MAE.values
    yy=[1,0];labs=['Reference price included','Reference price excluded']
    ax.barh(yy,vals,height=.43,color=[TEAL,ORANGE]);ax.set_yticks(yy,labs)
    ax.set_xlim(0,max(vals)*1.36);ax.set_xlabel('CV mean absolute error / lakh INR')
    for y,v in zip(yy,vals):ax.text(v+.06,y,f'{v:.2f}',va='center',color=INK,fontsize=15,fontweight='bold')
    change=vals[1]/vals[0]
    fig.text(.73,.55,f'{change:.1f}×',fontsize=54,color=ORANGE,fontweight='bold')
    fig.text(.73,.48,'higher error',fontsize=17,color=INK)
    fig.text(.73,.43,'without price anchor',fontsize=12,color=MUTED)
    fig.text(.12,.128,'Without a trustworthy reference price, this small dataset cannot support equally reliable valuation.',color=MUTED,fontsize=12)
    footer(fig,'The price-retention ratio uses the target and is intentionally excluded from all predictive features to avoid target leakage.')
    save(fig,out/'06_reference_price_ablation.png')
    # 7 stress and explainability
    fig=start('PREDICTIVE POWER IS NOT THE SAME AS GENERALISATION',
       'Additional stress checks and post-hoc permutation importance expose limitations hidden by a single score.')
    ax=fig.add_axes([.14,.23,.40,.53]);clean(ax,xgrid=True)
    v=imp.head(6).sort_values('MAE_Increase')
    ax.barh(v.Feature,v.MAE_Increase,color=[TEAL if s=='Present_Price' else SOFT for s in v.Feature],height=.55)
    ax.set_xlabel('Increase in holdout MAE when feature is permuted')
    ax.set_title('Permutation importance',fontsize=16,color=INK,pad=17,fontweight='bold')
    ax2=fig.add_axes([.64,.29,.25,.39]);clean(ax2,ygrid=True)
    vals=[ts['R2'],grp['metrics']['R2']]
    ax2.bar(['Standard test','Unseen names'],vals,color=[BLUE,ORANGE],width=.55)
    ax2.set_ylim(0,1.08);ax2.set_ylabel('Held-out R²')
    for i,v in enumerate(vals):ax2.text(i,v+.03,f'{v:.3f}',ha='center',color=INK,fontsize=12,fontweight='bold')
    ax2.set_title('Different evaluation populations',fontsize=14,color=INK,pad=16,fontweight='bold')
    fig.text(.65,.193,f'Unseen-name stress: {grp["count"]} rows, {grp["unique_unseen_names"]} unseen names',fontsize=11,color=MUTED)
    footer(fig,'Two tests use different population mixes and train/test splits; their R² values are not a controlled paired experiment. Importance is predictive, not causal.')
    save(fig,out/'07_robustness_and_importance.png')
    return sorted(out.glob('*.png'))
