"""Fast invariants for data validity, prevention of target leakage and reproducibility."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import train_test_split
from src.analysis import load_data, features, make_pipeline, candidates, point_metrics
from src.catalog import classify_vehicle

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope="module")
def dataset():
    return load_data(ROOT/'car_data.csv')


def test_source_audit(dataset):
    df,audit=dataset
    assert audit['source_rows']==301 and audit['analytical_rows']==299
    assert audit['missing_cells']==0 and audit['exact_duplicates']==2
    assert audit['cars']==198 and audit['two_wheelers']==101
    assert df.duplicated().sum()==0


def test_vehicle_name_mapping_is_reviewed(dataset):
    df,_=dataset
    assert set(df.Vehicle_Type)=={'Car','Two-wheeler'}
    assert classify_vehicle('land cruiser')=='Car'
    assert classify_vehicle('Bajaj Pulsar 150')=='Two-wheeler'
    with pytest.raises(ValueError):
        classify_vehicle('unspecified spaceship x99')


def test_outlier_is_not_removed(dataset):
    df,_=dataset
    assert (df.Car_Name=='land cruiser').sum()==1
    assert float(df.Present_Price.max())==92.6


def test_no_target_derived_features():
    for included in (True,False):
        used=features(included)
        assert 'Selling_Price' not in used
        assert 'Car_Name' not in used
        assert 'Model_Key' not in used
        assert not any('Ratio' in c for c in used)


def test_seller_confounding(dataset):
    df,_=dataset
    bikes=df[df.Vehicle_Type=='Two-wheeler']
    assert set(bikes.Selling_type)=={'Individual'}


def test_held_out_split_no_overlap(dataset):
    df,_=dataset
    indices=np.arange(len(df))
    tr,te=train_test_split(indices,test_size=.2,random_state=42,stratify=df.Vehicle_Type)
    assert len(tr)==239 and len(te)==60 and not set(tr)&set(te)
    assert (df.iloc[te].Vehicle_Type=='Car').sum()==40


def test_pipeline_can_accept_unseen_categories(dataset):
    df,_=dataset
    model=make_pipeline(candidates()['Ridge regression'])
    model.fit(df.iloc[:180],df.iloc[:180].Selling_Price)
    data=df.iloc[180:185].copy()
    data.loc[data.index[0],'Fuel_Type']='Unknown fuel category'
    y=model.predict(data)
    assert len(y)==5 and np.isfinite(y).all()


def test_metrics_correct_for_simple_case():
    m=point_metrics([2,4,6],[1,4,8])
    assert m['MAE']==pytest.approx(1.0)
    assert m['RMSE']==pytest.approx((5/3)**.5)


def test_reproduced_reports_exist():
    assert (ROOT/'reports/metrics.json').is_file()
    s=json.loads((ROOT/'reports/metrics.json').read_text())
    assert s['champion'] in candidates()
    assert s['audit']['test_rows']==60
    assert s['final_test']['R2'] <= 1.0
    assert s['reference_ablation'][1]['CV_MAE'] > s['reference_ablation'][0]['CV_MAE']


def test_all_figures_are_exported():
    files=sorted((ROOT/'assets').glob('*.png'))
    assert len(files)==8
    assert all(p.stat().st_size>20_000 for p in files)
