"""Publication graphics. All plotted values derive from src.analysis and the original CSV."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
from matplotlib.patches import FancyBboxPatch
import numpy as np
import pandas as pd
from .analysis import UR,LFPR,EPR,monthly,coverage,comparison_table,paired_rural_urban,regional_delta,sensitivity,metrics

BG='#081526'; PANEL='#112640'; CARD='#142b47'; WHITE='#f4f8fe'; MUTED='#a8bfd2'; TEAL='#5ee3cb'; BLUE='#7ab5fa'; ORANGE='#ffbe83'; RED='#fc868f'; GRID='#34526e'; FAINT='#58728b'
plt.rcParams.update({'figure.facecolor':BG,'savefig.facecolor':BG,'axes.facecolor':PANEL,'axes.edgecolor':PANEL,'axes.labelcolor':MUTED,'text.color':WHITE,'xtick.color':MUTED,'ytick.color':MUTED,'font.family':'DejaVu Sans','font.size':11,'axes.titleweight':'bold','pdf.fonttype':42,'svg.fonttype':'none'})


def figbase(w=15,h=9,title='',subtitle='',foot='Source: supplied Kaggle-hosted dataset | Descriptive, unweighted geographic-group analysis'):
    fig=plt.figure(figsize=(w,h),facecolor=BG)
    fig.text(.065,.945,title,fontsize=25 if w>=14 else 21,color=WHITE,fontweight='bold',va='top')
    if subtitle: fig.text(.067,.895,subtitle,color=MUTED,fontsize=11.7,va='top')
    fig.text(.067,.046,foot,color=MUTED,fontsize=8.5,va='bottom')
    return fig

def pretty(ax, ygrid=True):
    ax.set_facecolor(PANEL)
    for sp in ax.spines.values():sp.set_visible(False)
    if ygrid:ax.grid(axis='y',color=GRID,lw=.7,alpha=.55)
    ax.set_axisbelow(True)
    ax.tick_params(length=0,pad=7)


def month_axis(ax):
    ax.set_xlim(pd.Timestamp('2019-05-01'),pd.Timestamp('2020-06-30'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%y'))
    ax.tick_params(axis='x',labelsize=9.5)


def save(fig,path):
    path=Path(path)
    fig.savefig(path,dpi=170,facecolor=BG)
    plt.close(fig)
    return path


def visual_overview(full,panel,out):
    s=metrics(full,panel); m=monthly(panel)
    fig=plt.figure(figsize=(16,9),facecolor=BG)
    fig.text(.065,.915,'BEYOND THE UNEMPLOYMENT RATE',fontsize=26,color=WHITE,fontweight='bold')
    fig.text(.067,.864,"India's 2020 labour-market shock  |  Regional & rural–urban evidence",fontsize=14,color=MUTED)
    fig.text(.067,.821,'44 COMPLETE GEOGRAPHIC GROUPS  /  14 MONTHS  /  MAY 2019 – JUN 2020',fontsize=10.5,color=TEAL,fontweight='bold')
    def card(x,y,w,h,head,stat,note,tint=TEAL):
        box=FancyBboxPatch((x,y),w,h,transform=fig.transFigure,boxstyle='round,pad=.012,rounding_size=.01',linewidth=0,facecolor=CARD)
        fig.patches.append(box)
        fig.text(x+.016,y+h-.030,head,fontsize=10,color=MUTED,fontweight='bold',va='top')
        fig.text(x+.016,y+.046,stat,fontsize=28,color=tint,fontweight='bold',va='bottom')
        fig.text(x+.016,y+.018,note,fontsize=8.7,color=MUTED,va='bottom')
    card(.066,.615,.205,.156,'UNEMPLOYMENT SHOCK',f'+{s["ur_shock_pp"]:.1f} pp','Apr–May mean vs baseline',TEAL)
    card(.288,.615,.205,.156,'IMPLIED EMPLOYED SHARE',f'{s["epr_shock_pp"]:.1f} pp','Apr–May mean vs baseline',RED)
    card(.510,.615,.205,.156,'JUNE: BELOW BASELINE',f'{s["units_epr_below_base_june"]}/{s["complete_units"]}','Groups: implied employed share',ORANGE)
    card(.732,.615,.205,.156,'COMPLETE PANEL',f'{s["complete_units"]} of {s["area_units_raw"]}','Region–area groups retained',BLUE)
    ax=fig.add_axes([.075,.237,.585,.315]);pretty(ax)
    ax.axvspan(pd.Timestamp('2020-04-01'),pd.Timestamp('2020-05-31'),color=RED,alpha=.09)
    ax.plot(m.index,m.unemployment,color=TEAL,lw=3,marker='o',markersize=5.5)
    ax.set_ylim(0,31)
    ax.set_ylabel('Unemployment rate (%)',fontsize=10)
    ax.set_title('Observed shock and June reversal | consistent panel',fontsize=13,pad=12,loc='left',color=WHITE)
    month_axis(ax)
    for date in [pd.Timestamp('2020-03-31'),pd.Timestamp('2020-05-31'),pd.Timestamp('2020-06-30')]:
        v=m.loc[date,'unemployment'];ax.annotate(f'{v:.1f}%',(date,v),textcoords='offset points',xytext=(0,9),color=WHITE,ha='center',fontsize=10,fontweight='bold')
    p=fig.add_axes([.71,.237,.22,.315]);p.axis('off')
    p.text(0,1.0,'THE CORE FINDING',color=TEAL,fontsize=10,fontweight='bold',va='top')
    lines=[('The unemployment rate fell','by June 2020.'),('But the implied employed share','remained below baseline in'),(f'{s["units_epr_below_base_june"]} of {s["complete_units"]} complete groups.','')]
    yy=.76
    for first,second in lines:
        p.text(0,yy,first,color=WHITE,fontsize=14,fontweight='bold' if '44' in first else 'normal',va='top')
        if second:p.text(0,yy-.072,second,color=WHITE,fontsize=14,va='top')
        yy-=.24
    fig.text(.075,.130,'MEASUREMENT MATTERS',fontsize=11,color=ORANGE,fontweight='bold')
    fig.text(.075,.103,'The observed averages are not official national rates; the employed-share metric is derived from reported unemployment and participation.',color=MUTED,fontsize=9.7)
    fig.text(.067,.050,'Dataset: 740 raw observations, 28 named regions, May 2019–June 2020  •  Unweighted group means  •  Not a causal or national estimate',color=MUTED,fontsize=9)
    return save(fig,out/'00_portfolio_cover.png')


def visual_trend(full,panel,out):
    a=monthly(full);b=monthly(panel)
    fig=figbase(title='01  /  THE SHOCK',subtitle='Monthly unemployment means: all available observations versus a constant 44-group panel',foot='Values are unweighted region–area observation means, not official national unemployment rates.')
    ax=fig.add_axes([.09,.19,.83,.62]);pretty(ax)
    ax.axvspan(pd.Timestamp('2020-04-01'),pd.Timestamp('2020-05-31'),color=RED,alpha=.10)
    ax.plot(a.index,a.unemployment,color=BLUE,lw=2,ls='--',marker='o',markersize=4,label='All available groups (count varies)')
    ax.plot(b.index,b.unemployment,color=TEAL,lw=3,marker='o',markersize=6,label='Balanced 44-group panel')
    ax.set_ylim(0,33);ax.set_ylabel('Average unemployment rate (%)')
    month_axis(ax)
    ax.legend(loc='upper left',facecolor=PANEL,edgecolor='none',labelcolor=WHITE,fontsize=11)
    ax.annotate(f'{b.loc[pd.Timestamp("2020-05-31"),"unemployment"]:.1f}%',(pd.Timestamp('2020-05-31'),b.loc[pd.Timestamp('2020-05-31'),'unemployment']),textcoords='offset points',xytext=(0,12),ha='center',color=TEAL,fontsize=13,fontweight='bold')
    ax.text(.02,.05,'A consistent panel changes the estimated size of the spike.',transform=ax.transAxes,color=MUTED,fontsize=11)
    return save(fig,out/'01_unemployment_trend.png')


def visual_multi(panel,out):
    m=monthly(panel)
    cols=[('unemployment','Unemployment','%',TEAL,0,36),('participation','Labour-force participation','%',BLUE,0,58),('employed_share','Implied employed share','%',ORANGE,0,56)]
    fig=figbase(w=15,h=9,title='02  /  THREE VIEWS OF THE LABOUR MARKET',subtitle='Looking beyond the unemployment rate changes the recovery narrative',foot='All three indicators are unweighted averages across the same 44 complete region–area groups; employed share is a derived proxy.')
    for i,(key,label,unit,color,y0,ymax) in enumerate(cols):
        ax=fig.add_axes([.085,.645-i*.223,.83,.18]);pretty(ax)
        ax.axvspan(pd.Timestamp('2020-04-01'),pd.Timestamp('2020-05-31'),color=RED,alpha=.095)
        ax.plot(m.index,m[key],lw=2.5,color=color,marker='o',markersize=4)
        ax.set_ylim(y0,ymax)
        ax.text(.01,.80,label.upper(),transform=ax.transAxes,fontsize=10.5,color=color,fontweight='bold')
        ax.set_ylabel('%')
        month_axis(ax)
        if i<2:ax.set_xticklabels([])
    return save(fig,out/'02_three_indicators.png')


def visual_geography(panel,out):
    r=regional_delta(comparison_table(panel)).sort_values('shock_unemployment_pp')
    fig=figbase(w=15,h=11.2,title='03  /  WHERE THE SHOCK WAS LARGEST',subtitle='Mean April–May unemployment change versus each group’s May 2019–February 2020 baseline',foot='24 regions represented in the balanced panel; mean of 1–2 complete area groups per region. Not population-weighted. Extreme cases warrant caution.')
    ax=fig.add_axes([.265,.125,.68,.73]);pretty(ax,False)
    vals=r.shock_unemployment_pp
    colors=[TEAL if v>=0 else BLUE for v in vals]
    ax.barh(r.index,vals,color=colors,height=.75)
    ax.axvline(0,color=FAINT,lw=1.4)
    ax.set_xlabel('Change in unemployment (percentage points)')
    ax.grid(axis='x',color=GRID,alpha=.50)
    ax.tick_params(axis='y',labelsize=9.4)
    for y,(region,v) in enumerate(vals.items()):
        ax.text(v+(1.3 if v>=0 else -1.3),y,f'{v:+.1f}',va='center',ha='left' if v>=0 else 'right',fontsize=8.6,color=WHITE)
    ax.set_xlim(min(-11,vals.min()-4),max(79,vals.max()+8))
    return save(fig,out/'03_geographic_changes.png')


def visual_rural_urban(panel,out):
    m=paired_rural_urban(comparison_table(panel))
    fig=figbase(title='04  /  RURAL VERSUS URBAN',subtitle='Comparing each region with itself: change in unemployment from baseline to Apr–May 2020',foot=f'Only {len(m)} regions have complete rural AND urban histories; points are region-specific paired changes, not causal effects.')
    ax=fig.add_axes([.12,.19,.66,.60]);pretty(ax)
    ax.scatter(m.Rural,m.Urban,s=89,color=TEAL,edgecolor=BG,linewidth=1.0,alpha=.9)
    mx=max(m[['Rural','Urban']].max().max(),1)+6;mn=min(m[['Rural','Urban']].min().min(),0)-6
    ax.plot([mn,mx],[mn,mx],ls='--',lw=1.5,color=ORANGE,label='Same increase in both areas')
    ax.axhline(0,color=GRID);ax.axvline(0,color=GRID)
    ax.set_xlim(mn,mx);ax.set_ylim(mn,mx)
    ax.set_xlabel('Rural increase (percentage points)');ax.set_ylabel('Urban increase (percentage points)')
    for region in m.index:
        row=m.loc[region]
        if region in ['Puducherry','Jharkhand','Tamil Nadu','Tripura']:
            ax.annotate(region,(row.Rural,row.Urban),textcoords='offset points',xytext=(5,5),color=WHITE,fontsize=8)
    fig.text(.805,.62,f'{(m.urban_minus_rural_pp>0).sum()} of {len(m)}',fontsize=23,color=TEAL,fontweight='bold')
    fig.text(.807,.56,'regions had a larger',fontsize=10,color=MUTED)
    fig.text(.807,.53,'urban increase.',fontsize=10,color=MUTED)
    fig.text(.805,.39,f'{m.urban_minus_rural_pp.median():+.1f} pp',fontsize=22,color=ORANGE,fontweight='bold')
    fig.text(.807,.33,'median urban-minus-rural',fontsize=10,color=MUTED)
    fig.text(.807,.30,'difference',fontsize=10,color=MUTED)
    return save(fig,out/'04_rural_urban_comparison.png')


def visual_coverage(full,out):
    c=coverage(full)
    # Sort incomplete units first, then alphabetically, to make gaps easy to see.
    c=c.assign(missing=(~c).sum(axis=1)).sort_values(['missing'],ascending=False).drop(columns='missing')
    fig=figbase(w=15,h=13,title='05  /  THE MISSING MONTHS',subtitle='Observed region–area groups across 14 months: completeness matters for changing monthly means',foot=f'{c.shape[0]} observed region–area groups; {(~c).to_numpy().sum()} missing unit-month cells relative to 55 × 14. No data values are imputed.')
    ax=fig.add_axes([.29,.12,.635,.73]);ax.set_facecolor(PANEL)
    arr=c.astype(int).to_numpy()
    cmap=mcolors.ListedColormap([RED,TEAL])
    ax.imshow(arr,aspect='auto',interpolation='none',cmap=cmap,vmin=0,vmax=1)
    ax.set_yticks(range(c.shape[0]),labels=c.index,fontsize=7.4)
    ax.set_xticks(range(len(c.columns)),labels=[pd.Timestamp(x).strftime('%b\n%y') for x in c.columns],fontsize=9)
    ax.tick_params(length=0)
    for x in np.arange(-.5,arr.shape[1],1): ax.axvline(x,color=BG,lw=.45)
    for y in np.arange(-.5,arr.shape[0],1): ax.axhline(y,color=BG,lw=.3)
    fig.text(.35,.065,'● Observed',color=TEAL,fontsize=11);fig.text(.48,.065,'● Missing',color=RED,fontsize=11)
    return save(fig,out/'05_coverage_matrix.png')


def visual_recovery(panel,out):
    comp=comparison_table(panel)
    x=comp.ur_june_minus_baseline_pp;y=comp.employed_share_june_minus_baseline_pp
    fig=figbase(title='06  /  DID THE LABOUR MARKET RECOVER?',subtitle='June 2020 deviations from the pre-shock baseline across the 44 complete geographic groups',foot='Zero represents each group’s pre-March baseline. Employed share is inferred from UR and LFPR; neither axis is a national estimate.')
    ax=fig.add_axes([.10,.18,.65,.61]);pretty(ax)
    ax.axhspan(-30,0,color=RED,alpha=.045)
    ax.scatter(x,y,s=63,c=[ORANGE if v<0 else TEAL for v in y],alpha=.86,edgecolors=BG)
    ax.axvline(0,color=BLUE,lw=1.5,ls='--');ax.axhline(0,color=TEAL,lw=1.5,ls='--')
    ax.set_xlabel('June unemployment minus baseline (percentage points)')
    ax.set_ylabel('June implied employed share minus baseline (pp)')
    fig.text(.80,.61,f'{(y<0).sum()} / {len(y)}',fontsize=28,color=ORANGE,fontweight='bold')
    fig.text(.80,.55,'groups still below',fontsize=10,color=MUTED)
    fig.text(.80,.515,'baseline employed share',fontsize=10,color=MUTED)
    fig.text(.80,.37,f'{(x>0).sum()} / {len(x)}',fontsize=27,color=TEAL,fontweight='bold')
    fig.text(.80,.31,'groups above their',fontsize=10,color=MUTED)
    fig.text(.80,.275,'baseline unemployment',fontsize=10,color=MUTED)
    return save(fig,out/'06_june_recovery.png')


def visual_sensitivity(full,panel,out):
    z=sensitivity(full,panel)
    fig=figbase(title='07  /  DOES SAMPLE COMPOSITION MATTER?',subtitle='Compare monthly unemployment averages using all available groups against a fixed 44-group panel',foot='A difference between these lines is not a causal effect of missing data; it reveals sensitivity to which geographic groups are included.')
    ax=fig.add_axes([.10,.47,.81,.35]);pretty(ax)
    ax.plot(z.index,z.unemployment_all,color=BLUE,lw=2,marker='o',ls='--',label='All observed groups')
    ax.plot(z.index,z.unemployment_balanced,color=TEAL,lw=2.8,marker='o',label='Complete panel')
    ax.set_ylim(0,33);ax.set_ylabel('Unemployment rate (%)')
    month_axis(ax);ax.legend(loc='upper left',facecolor=PANEL,edgecolor='none',labelcolor=WHITE)
    ax2=fig.add_axes([.10,.16,.81,.20]);pretty(ax)
    ax2.bar(z.index,z.all_unit_count,color=BLUE,width=19,alpha=.75,label='Available region-area groups')
    ax2.axhline(44,color=TEAL,ls='--',lw=2,label='Complete panel: 44')
    ax2.set_ylim(0,61);ax2.set_ylabel('Group count');month_axis(ax2)
    return save(fig,out/'07_composition_sensitivity.png')


def create_all(full,panel,output_folder):
    out=Path(output_folder);out.mkdir(parents=True,exist_ok=True)
    jobs=[visual_overview(full,panel,out),visual_trend(full,panel,out),visual_multi(panel,out),visual_geography(panel,out),visual_rural_urban(panel,out),visual_coverage(full,out),visual_recovery(panel,out),visual_sensitivity(full,panel,out)]
    return jobs
