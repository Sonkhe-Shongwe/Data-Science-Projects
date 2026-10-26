"""Validation and evidence-first analysis of the supplied Kaggle-hosted dataset.

All summary rates are *unweighted means of observed region-area units*.
They are NOT estimates of national unemployment or sampling uncertainty.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd

UR = 'Estimated Unemployment Rate (%)'
LFPR = 'Estimated Labour Participation Rate (%)'
EMP = 'Estimated Employed'
EPR = 'Implied employed share (%)'
MEASURES = [UR, LFPR, EPR]
DATES = pd.date_range('2019-05-31', '2020-06-30', freq='ME')
BASE_END = pd.Timestamp('2020-02-29')
MARCH = pd.Timestamp('2020-03-31')
SHOCK = [pd.Timestamp('2020-04-30'), pd.Timestamp('2020-05-31')]
JUNE = pd.Timestamp('2020-06-30')


def checksum(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_data(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    required = ['Region','Date','Frequency',UR,EMP,LFPR,'Area']
    missing = set(required) - set(df)
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    df['Region'] = df.Region.astype(str).str.strip()
    df['Area'] = df.Area.astype(str).str.strip()
    df['Frequency'] = df.Frequency.astype(str).str.strip()
    df['Date'] = pd.to_datetime(df.Date.astype(str).str.strip(), format='%d-%m-%Y', errors='raise')
    for field in [UR, EMP, LFPR]:
        df[field] = pd.to_numeric(df[field], errors='raise')
    if df[required].isna().any().any():
        raise ValueError('Missing values in required columns; inspect input, do not silently drop rows')
    if not df.Area.isin(['Rural','Urban']).all() or not df.Frequency.eq('Monthly').all():
        raise ValueError('Unexpected geographic-area or frequency values')
    if not (df[UR].between(0,100).all() and df[LFPR].between(0,100).all() and (df[EMP]>=0).all()):
        raise ValueError('Invalid indicator values')
    if df.duplicated().any():
        raise ValueError('Exact duplicate data rows require inspection')
    if df.duplicated(['Region','Area','Date']).any():
        raise ValueError('Duplicate geographic-unit-month keys require inspection')
    df['Unit'] = df['Region'] + ' | ' + df['Area']
    # Implied employment-to-population percentage IF UR/LFPR definitions are consistent.
    df[EPR] = df[LFPR] * (1-df[UR]/100)
    df = df.sort_values(['Region','Area','Date']).reset_index(drop=True)
    return df


def coverage(df: pd.DataFrame) -> pd.DataFrame:
    """Explicit presence matrix: every observed region-area unit x all observed months."""
    units = sorted(df.Unit.unique())
    months = sorted(df.Date.unique())
    idx = pd.MultiIndex.from_product([units,months],names=['Unit','Date'])
    presence = df.set_index(['Unit','Date']).reindex(idx)[UR].notna().unstack('Date')
    return presence.astype(bool)


def complete_panel(df: pd.DataFrame) -> pd.DataFrame:
    c = coverage(df)
    units = c.index[c.all(axis=1)]
    return df.loc[df.Unit.isin(units)].copy()


def monthly(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby('Date').agg(
        unemployment=(UR,'mean'), participation=(LFPR,'mean'),
        employed_share=(EPR,'mean'), observations=('Unit','size'),
        units=('Unit','nunique'), regions=('Region','nunique')
    ).sort_index()


def periods(panel: pd.DataFrame) -> pd.DataFrame:
    """Matched unit baselines; May19-Feb20, Mar20, Apr-May20, Jun20."""
    pre = panel.loc[panel.Date<=BASE_END].groupby('Unit')[MEASURES].mean()
    march = panel.loc[panel.Date==MARCH].groupby('Unit')[MEASURES].mean()
    shock = panel.loc[panel.Date.isin(SHOCK)].groupby('Unit')[MEASURES].mean()
    june = panel.loc[panel.Date==JUNE].groupby('Unit')[MEASURES].mean()
    shared = pre.index.intersection(march.index).intersection(shock.index).intersection(june.index)
    # Panels selected above have complete 14-month histories.
    if len(shared)!=panel.Unit.nunique():
        raise ValueError('Incomplete comparison groups; review the unit inclusion contract')
    parts={'baseline':pre,'march':march,'shock':shock,'june':june}
    out=pd.concat({k:v.loc[shared] for k,v in parts.items()}, axis=1)
    return out


def comparison_table(panel: pd.DataFrame) -> pd.DataFrame:
    p=periods(panel)
    base=p['baseline'];shock=p['shock'];june=p['june']
    meta=panel.groupby('Unit')[['Region','Area']].first()
    delta=shock-base
    residual=june-base
    d=meta.copy()
    for m,name in [(UR,'ur'),(LFPR,'lfpr'),(EPR,'employed_share')]:
        d[name+'_baseline']=base[m]
        d[name+'_shock']=shock[m]
        d[name+'_june']=june[m]
        d[name+'_shock_change_pp']=delta[m]
        d[name+'_june_minus_baseline_pp']=residual[m]
    return d.sort_index()


def paired_rural_urban(comp: pd.DataFrame) -> pd.DataFrame:
    """Region-matched area change comparison: only regions containing both areas."""
    piv=comp.pivot(index='Region',columns='Area',values='ur_shock_change_pp')
    out=piv.dropna(subset=['Rural','Urban']).copy()
    out['urban_minus_rural_pp']=out['Urban']-out['Rural']
    return out.sort_values('urban_minus_rural_pp')


def regional_delta(comp: pd.DataFrame) -> pd.DataFrame:
    """Mean of the available complete unit changes within each region; not a weighted rate."""
    return comp.groupby('Region').agg(
        unit_count=('Area','count'),
        shock_unemployment_pp=('ur_shock_change_pp','mean'),
        june_unemployment_pp=('ur_june_minus_baseline_pp','mean'),
        shock_employed_share_pp=('employed_share_shock_change_pp','mean')
    ).sort_values('shock_unemployment_pp')


def sensitivity(full: pd.DataFrame,panel: pd.DataFrame) -> pd.DataFrame:
    a=monthly(full); b=monthly(panel)
    t=pd.DataFrame(index=a.index)
    for field in ('unemployment','participation','employed_share'):
        t[field+'_all']=a[field]
        t[field+'_balanced']=b[field]
        t[field+'_gap_pp']=b[field]-a[field]
    t['all_unit_count']=a['units']; t['balanced_unit_count']=b['units']
    return t


def region_resampling_interval(comp: pd.DataFrame, column: str, seed: int=2026, draws:int=4000) -> tuple[float,float]:
    """Descriptive region-cluster resampling sensitivity interval, NOT a population CI.

    Resample regions rather than treating rural/urban cells as independent.
    This probes how sensitive the sample average is to region composition.
    """
    rng=np.random.default_rng(seed)
    group_means=comp.groupby('Region')[column].apply(list)
    names=group_means.index.to_numpy()
    values=[]
    for _ in range(draws):
        chosen=rng.choice(names,size=len(names),replace=True)
        flattened=[v for region in chosen for v in group_means[region]]
        values.append(float(np.mean(flattened)))
    return tuple(float(x) for x in np.quantile(values,[.025,.975]))


def metrics(full: pd.DataFrame,panel: pd.DataFrame) -> dict:
    c=coverage(full); comp=comparison_table(panel); m=monthly(full); b=monthly(panel)
    a=paired_rural_urban(comp)
    out={
        'raw_rows':int(len(full)), 'regions_raw':int(full.Region.nunique()),
        'area_units_raw':int(full.Unit.nunique()),
        'months':int(full.Date.nunique()), 'observed_panel_gaps':int((~c).to_numpy().sum()),
        'complete_units':int(panel.Unit.nunique()), 'complete_regions':int(panel.Region.nunique()),
        'balanced_rows':int(len(panel)), 'paired_rural_urban_regions':int(len(a)),
        'baseline_ur':float(comp.ur_baseline.mean()),'shock_ur':float(comp.ur_shock.mean()),
        'june_ur':float(comp.ur_june.mean()),
        'baseline_lfpr':float(comp.lfpr_baseline.mean()),
        'shock_lfpr':float(comp.lfpr_shock.mean()),
        'june_lfpr':float(comp.lfpr_june.mean()),
        'baseline_epr':float(comp.employed_share_baseline.mean()),
        'shock_epr':float(comp.employed_share_shock.mean()),
        'june_epr':float(comp.employed_share_june.mean()),
        'ur_shock_pp':float(comp.ur_shock_change_pp.mean()),
        'lfpr_shock_pp':float(comp.lfpr_shock_change_pp.mean()),
        'epr_shock_pp':float(comp.employed_share_shock_change_pp.mean()),
        'ur_june_residual_pp':float(comp.ur_june_minus_baseline_pp.mean()),
        'lfpr_june_residual_pp':float(comp.lfpr_june_minus_baseline_pp.mean()),
        'epr_june_residual_pp':float(comp.employed_share_june_minus_baseline_pp.mean()),
        'units_ur_up_shock':int((comp.ur_shock_change_pp>0).sum()),
        'units_epr_down_shock':int((comp.employed_share_shock_change_pp<0).sum()),
        'units_epr_below_base_june':int((comp.employed_share_june_minus_baseline_pp<0).sum()),
        'units_ur_above_base_june':int((comp.ur_june_minus_baseline_pp>0).sum()),
        'units_lfpr_below_base_june':int((comp.lfpr_june_minus_baseline_pp<0).sum()),
        'mar_all_ur':float(m.loc[MARCH,'unemployment']),
        'apr_all_ur':float(m.loc[SHOCK[0],'unemployment']),
        'may_all_ur':float(m.loc[SHOCK[1],'unemployment']),
        'jun_all_ur':float(m.loc[JUNE,'unemployment']),
        'may_balanced_ur':float(b.loc[SHOCK[1],'unemployment']),
        'matched_area_mean_difference_pp':float(a.urban_minus_rural_pp.mean()),
        'matched_area_median_difference_pp':float(a.urban_minus_rural_pp.median()),
        'matched_area_urban_greater':int((a.urban_minus_rural_pp>0).sum()),
        'shock_ur_median_delta_pp':float(comp.ur_shock_change_pp.median()),
        'shock_ur_q1_pp':float(comp.ur_shock_change_pp.quantile(.25)),
        'shock_ur_q3_pp':float(comp.ur_shock_change_pp.quantile(.75)),
        'largest_shock_unit':str(comp.ur_shock_change_pp.idxmax()),
        'largest_shock_unit_change_pp':float(comp.ur_shock_change_pp.max()),
        'mean_ur_shock_without_largest_pp':float(comp.ur_shock_change_pp.drop(comp.ur_shock_change_pp.idxmax()).mean()),
        'shock_ur_region_resample_low_pp':float(region_resampling_interval(comp,'ur_shock_change_pp')[0]),
        'shock_ur_region_resample_high_pp':float(region_resampling_interval(comp,'ur_shock_change_pp')[1]),
    }
    return out
