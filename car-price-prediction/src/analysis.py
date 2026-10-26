"""Reproducible used-vehicle valuation analysis. Only car_data.csv is required.

No test-set feedback is used to choose a model: cross-validation on the
80% development set picks the champion before one final test evaluation.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, median_absolute_error, r2_score
from sklearn.model_selection import GroupShuffleSplit, KFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from .catalog import classify_vehicle

BASE_NUMERIC = ["Year", "Driven_kms", "Owner"]
CATEGORICAL = ["Fuel_Type", "Selling_type", "Transmission", "Vehicle_Type"]
REFERENCE = "Present_Price"
TARGET = "Selling_Price"
EXPECTED = {"Car_Name", "Year", "Selling_Price", "Present_Price", "Driven_kms", "Fuel_Type", "Selling_type", "Transmission", "Owner"}


def load_data(path: Path) -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(path)
    if set(raw.columns) != EXPECTED:
        raise ValueError(f"Unexpected columns: {list(raw.columns)}")
    if raw.isna().any().any():
        raise ValueError(f"Input has missing values: {raw.isna().sum().to_dict()}")
    if (raw[["Present_Price", "Selling_Price"]] <= 0).any().any():
        raise ValueError("Prices must be strictly positive")
    if (raw["Driven_kms"] < 0).any() or (raw["Owner"] < 0).any():
        raise ValueError("Negative mileage or ownership")
    if ((raw["Year"] < 1900) | (raw["Year"] > 2026)).any():
        raise ValueError("Implausible model year")
    audit = {"source_rows": int(len(raw)), "missing_cells": int(raw.isna().sum().sum()),
             "exact_duplicates": int(raw.duplicated().sum()), "source_model_names": int(raw.Car_Name.nunique())}
    df = raw.drop_duplicates().reset_index(drop=True).copy()
    df["Vehicle_Type"] = df.Car_Name.map(classify_vehicle)
    df["Model_Key"] = df.Car_Name.str.strip().str.lower()
    audit.update({"analytical_rows": int(len(df)),
                  "cars": int((df.Vehicle_Type == "Car").sum()),
                  "two_wheelers": int((df.Vehicle_Type == "Two-wheeler").sum()),
                  "model_names": int(df.Model_Key.nunique()),
                  "vehicle_year_min": int(df.Year.min()), "vehicle_year_max": int(df.Year.max()),
                  "selling_price_min": float(df.Selling_Price.min()),
                  "selling_price_max": float(df.Selling_Price.max()),
                  "max_reference_price_model": str(df.loc[df.Present_Price.idxmax(), "Car_Name"]),
                  "max_reference_price": float(df.Present_Price.max()),
                  "car_individual_pct": float(round(100 * (df.loc[df.Vehicle_Type=="Car","Selling_type"]=="Individual").mean(),1)),
                  "two_wheeler_individual_pct": float(round(100 * (df.loc[df.Vehicle_Type=="Two-wheeler","Selling_type"]=="Individual").mean(),1))})
    # This domain review comes from manually checking all unique names in this sample.
    assert len(raw)==301 and audit["exact_duplicates"]==2 and audit["analytical_rows"]==299
    assert audit["cars"]==198 and audit["two_wheelers"]==101, audit
    assert df.Model_Key.notna().all() and (df.Model_Key.str.len()>0).all()
    return df, audit


def features(include_reference: bool = True):
    return BASE_NUMERIC + ([REFERENCE] if include_reference else []) + CATEGORICAL


def make_pipeline(model, include_reference=True):
    num = BASE_NUMERIC + ([REFERENCE] if include_reference else [])
    preprocessing = ColumnTransformer(transformers=[
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")),
                              ("scale", StandardScaler())]), num),
        ("categorical", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), CATEGORICAL)
    ], remainder="drop", verbose_feature_names_out=False)
    return Pipeline([("preprocessor", preprocessing), ("regressor", clone(model))])


def candidates():
    # Fixed, modest-capacity candidate settings; no test-set-informed tuning.
    return {
      "Median baseline": DummyRegressor(strategy="median"),
      "Ridge regression": Ridge(alpha=10.0),
      "Random forest": RandomForestRegressor(n_estimators=180, min_samples_leaf=2, random_state=42, n_jobs=1),
      "Extra Trees": ExtraTreesRegressor(n_estimators=180, min_samples_leaf=2, random_state=42, n_jobs=1),
      "Gradient boosting": GradientBoostingRegressor(n_estimators=120, max_depth=2, learning_rate=0.05, random_state=42),
    }


def point_metrics(actual, predicted):
    y=np.asarray(actual, dtype=float);p=np.asarray(predicted, dtype=float)
    return {"MAE":float(mean_absolute_error(y,p)),
            "RMSE":float(np.sqrt(mean_squared_error(y,p))),
            "MedAE":float(median_absolute_error(y,p)),
            "R2":float(r2_score(y,p)) if len(y)>1 else None,
            "P90_AE":float(np.quantile(np.abs(y-p),.9))}


def main_analysis(dataset: Path, output: Path):
    output.mkdir(exist_ok=True,parents=True)
    df,audit=load_data(dataset)
    # Stratify by vehicle category to ensure representation, after removing exact duplicates.
    train_idx,test_idx=train_test_split(np.arange(len(df)),test_size=.20,random_state=42,stratify=df.Vehicle_Type)
    tr=df.iloc[train_idx].copy(); te=df.iloc[test_idx].copy()
    assert not set(tr.index)&set(te.index)
    folds=KFold(n_splits=5, shuffle=True, random_state=42)
    score_cfg={"neg_mae":"neg_mean_absolute_error", "r2":"r2", "neg_rmse":"neg_root_mean_squared_error"}
    rows=[]; cache={}
    for name,model in candidates().items():
        pipe=make_pipeline(model)
        scores=cross_validate(pipe,tr, tr[TARGET],cv=folds, scoring=score_cfg, n_jobs=1)
        row={"Model":name,"CV_MAE":float(-scores["test_neg_mae"].mean()),
             "CV_MAE_SD":float(scores["test_neg_mae"].std(ddof=1)),
             "CV_RMSE":float(-scores["test_neg_rmse"].mean()),
             "CV_R2":float(scores["test_r2"].mean())}
        rows.append(row)
        cache[name]=pipe
    table=pd.DataFrame(rows).sort_values("CV_MAE").reset_index(drop=True)
    top=table.iloc[0].Model
    champion=clone(cache[top]); champion.fit(tr,tr[TARGET])
    pred=champion.predict(te)
    test_metrics=point_metrics(te[TARGET],pred)
    test_rows=te[["Car_Name","Model_Key","Vehicle_Type","Selling_Price","Present_Price","Driven_kms","Year"]].copy()
    test_rows["Predicted"] = pred
    test_rows["Absolute_Error"] = (test_rows.Selling_Price - test_rows.Predicted).abs()
    test_rows["Price_Segment"] = np.where(test_rows.Selling_Price < 2, "Under 2L", np.where(test_rows.Selling_Price <= 10,"2–10L", "Over 10L"))
    segment_rows=[]
    for attr in ("Vehicle_Type", "Price_Segment"):
        for label,g in test_rows.groupby(attr):
            segment_rows.append({"Dimension":attr, "Group":str(label),"Count":len(g), **point_metrics(g.Selling_Price,g.Predicted)})
    segment_table=pd.DataFrame(segment_rows)
    # SAME development folds for controlled with/without reference-price comparisons.
    ablation_rows=[]
    chosen_model=candidates()[top]
    for include in [True,False]:
        pipe=make_pipeline(chosen_model,include_reference=include)
        scores=cross_validate(pipe,tr,tr[TARGET],cv=folds,scoring=score_cfg,n_jobs=1)
        ablation_rows.append({"Experiment":"With reference price" if include else "Without reference price",
                              "CV_MAE":float(-scores['test_neg_mae'].mean()),
                              "CV_RMSE":float(-scores['test_neg_rmse'].mean()),
                              "CV_R2":float(scores['test_r2'].mean())})
    ablation=pd.DataFrame(ablation_rows)
    # Counterfactual stress: different training / holdout sample, with disjoint model names.
    group_train_idx,group_test_idx=next(GroupShuffleSplit(n_splits=1,test_size=.20,random_state=21).split(df,df[TARGET],groups=df.Model_Key))
    gt=df.iloc[group_train_idx]; gh=df.iloc[group_test_idx]
    assert not set(gt.Model_Key)&set(gh.Model_Key)
    group_model=make_pipeline(chosen_model).fit(gt,gt[TARGET])
    group_pred=group_model.predict(gh)
    group_score=point_metrics(gh[TARGET],group_pred)
    # Outlier sensitivity: analyze training using the same development CV with/without the highest reference-price row.
    outlier_index=int(df.Present_Price.idxmax())
    outlier_is_training=outlier_index in set(train_idx)
    if outlier_is_training:
        trimmed=tr[tr.index != outlier_index]
        sensitivity=cross_validate(make_pipeline(chosen_model),trimmed,trimmed[TARGET],cv=KFold(n_splits=5,shuffle=True,random_state=42),scoring=score_cfg,n_jobs=1)
        outlier_cv_mae=float(-sensitivity['test_neg_mae'].mean())
    else:
        outlier_cv_mae=None
    # Permutation importance: explanatory diagnostic after final model evaluation, not feature selection.
    perm=permutation_importance(champion,te[features(True)],te[TARGET],n_repeats=8,random_state=42,scoring="neg_mean_absolute_error")
    importances=pd.DataFrame({"Feature":features(True),"MAE_Increase":perm.importances_mean,"Repeat_SD":perm.importances_std}).sort_values("MAE_Increase",ascending=False)
    # Sales-price retention ratio is EDA ONLY. It directly contains the target and is never passed to models.
    retention=df.Selling_Price.div(df.Present_Price)
    rs = {"overall_median_ratio":float(retention.median()),
          "ratio_over_one":int((retention>1).sum()),
          "car_median_selling":float(df[df.Vehicle_Type=="Car"].Selling_Price.median()),
          "two_wheeler_median_selling":float(df[df.Vehicle_Type=="Two-wheeler"].Selling_Price.median())}
    # Unequal segment distributions are crucial to interpretation of pooled score.
    audit["development_rows"]=len(tr);audit["test_rows"]=len(te)
    summary={"audit":audit,"champion":str(top),"final_test":test_metrics,
             "reference_ablation":ablation_rows,"unseen_model_stress":{"count":len(gh),"unique_unseen_names":gh.Model_Key.nunique(),"metrics":group_score},
             "outlier_sensitivity":{"largest_reference_price_record_in_development":outlier_is_training,
                                    "development_CV_MAE_without_record":outlier_cv_mae,
                                    "development_CV_MAE_with_record":float(table[table.Model==top].CV_MAE.iloc[0])},
             "retention_descriptive":rs,"evaluation_protocol":"Five shuffled K-fold splits on 80% development; winner by CV MAE; one 20% stratified test evaluation. Separate unfamiliar-name stress split."}
    (output/'metrics.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    table.to_csv(output/'cv_model_comparison.csv',index=False)
    test_rows.to_csv(output/'test_predictions.csv',index=False)
    segment_table.to_csv(output/'subgroup_performance.csv',index=False)
    ablation.to_csv(output/'reference_price_ablation.csv',index=False)
    importances.to_csv(output/'permutation_importance.csv',index=False)
    return dict(df=df,train=tr,test=te,table=table,test_rows=test_rows,segments=segment_table,
                ablation=ablation,imp=importances,summary=summary, champion=champion)
