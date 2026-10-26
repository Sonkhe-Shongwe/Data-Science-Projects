"""Tests for dataset contracts, comparisons and presentation invariants."""
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
from src.analysis import (
    UR, LFPR, EPR, load_data, checksum, coverage, complete_panel,
    monthly, comparison_table, paired_rural_urban, metrics
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'unemployment_india.csv'

@pytest.fixture(scope='module')
def raw():return load_data(SOURCE)

@pytest.fixture(scope='module')
def panel(raw):return complete_panel(raw)


def test_original_snapshot_unchanged():
    assert checksum(SOURCE)=='caa83db2077f8e08ab87e0dd1298c25e698b9c3461b94dad21ab9faad5c72e1b'


def test_dataset_contract(raw):
    assert len(raw)==740
    assert raw.Region.nunique()==28 and raw.Unit.nunique()==55
    assert raw.Date.nunique()==14
    assert not raw.duplicated(['Region','Area','Date']).any()
    assert raw[[UR,LFPR,EPR]].notna().all().all()
    assert raw[UR].between(0,100).all()


def test_proxy_computed_rowwise(raw):
    assert np.allclose(raw[EPR],raw[LFPR]*(1-raw[UR]/100))
    # Nonlinearity: do not multiply monthly mean LFPR with monthly mean UR.
    m = monthly(raw)
    assert not np.allclose(m.employed_share,m.participation*(1-m.unemployment/100))


def test_panel_gaps(raw,panel):
    seen=coverage(raw)
    assert (~seen).to_numpy().sum()==30
    assert len(panel)==616 and panel.Unit.nunique()==44
    assert panel.Region.nunique()==24
    assert (panel.groupby('Unit').Date.nunique()==14).all()


def test_period_contract(raw,panel):
    m=metrics(raw,panel)
    assert m['paired_rural_urban_regions']==20
    assert m['units_ur_up_shock']==40
    assert m['units_epr_down_shock']==44
    assert m['units_epr_below_base_june']==32
    assert m['units_lfpr_below_base_june']==34
    assert m['units_ur_above_base_june']==25
    assert m['ur_shock_pp']==pytest.approx(16.027045,abs=.00001)
    assert m['largest_shock_unit']=='Puducherry | Urban'
    assert m['mean_ur_shock_without_largest_pp']==pytest.approx(14.685395,abs=.00001)
    assert m['epr_shock_pp']==pytest.approx(-12.846293,abs=.00001)
    assert m['may_all_ur']==pytest.approx(24.8753,abs=.0001)
    assert m['may_balanced_ur']==pytest.approx(26.9586,abs=.0001)


def test_region_paired_counts(panel):
    comp=comparison_table(panel)
    a=paired_rural_urban(comp)
    assert len(a)==20 and (a.urban_minus_rural_pp>0).sum()==12
    assert a.urban_minus_rural_pp.median()==pytest.approx(4.4405,abs=.0001)


def test_invalid_values_fail(raw,tmp_path):
    d=pd.read_csv(SOURCE)
    d.loc[0,' Estimated Unemployment Rate (%)']=-5
    p=tmp_path/'bad.csv';d.to_csv(p,index=False)
    with pytest.raises(ValueError,match='Invalid indicator'):
        load_data(p)


def test_duplicate_keys_fail(tmp_path):
    d=pd.read_csv(SOURCE)
    d=pd.concat([d,d.iloc[[0]]],ignore_index=True)
    p=tmp_path/'dup.csv';d.to_csv(p,index=False)
    with pytest.raises(ValueError,match='duplicate|Duplicate'):
        load_data(p)
