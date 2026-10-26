# Methodology and audit trail

## Design principles

**Research goal:** derive defensible observations about a 301-row historical used-vehicle dataset and evaluate small-sample resale-price prediction. This is not a causal or current-market valuation study.

### Data provenance

- Source copy: local `car_data.csv`, originally derived from [Kaggle's CarDekho vehicle dataset](https://www.kaggle.com/datasets/nehalbirla/vehicle-dataset-from-cardekho).
- Original file SHA-256: `7f4f8dd90147fd735e4e5a02d174995b7d2d404837b6f11769f364b7c5f48024`.
- Unit: lakh INR is widely stated in documentation for this matching source sample; it is **not embedded in CSV metadata**.
- `Present_Price` is described as current showroom/reference price in dataset descriptions; interpretation is contingent on the data publisher's definitions.
- No transaction date, vehicle condition details or sampling methodology are provided. Asking versus completed transaction price is not independently verified.

### Data audit

- Source rows: 301; exact duplicates: 2; remaining rows: 299.
- Source columns: 9; missing values: 0; distinct model names: 98.
- Sample category split: 198 cars / 101 motorcycles and scooters, mapped from the reviewed names in this CSV.
- Vehicle year range: 2003–2018; these are manufacture/model years, not observation dates.
- Land Cruiser record with maximum `Present_Price` 92.6 is **retained**. It may be an extreme valid case; it is not identified as erroneous.
- Validation rejects missing values, nonpositive prices, negative odometer or owner counts, unexpected columns and unreviewed vehicle names.

### Guarding against leakage

1. Exact duplicates are eliminated before splitting.
2. `train_test_split` uses `random_state=42`, with stratification by reviewed vehicle category, yielding 239 development and 60 final test cases.
3. Preprocessing (`SimpleImputer`, `StandardScaler`, `OneHotEncoder`) is fitted **within** each scikit-learn pipeline and CV fold.
4. `Selling_Price` is the label; `Car_Name` is used only to review classes and construct disjoint-model stress splits, not as a main predictor.
5. Target-derived retention or depreciation ratios are excluded from predictive features.
6. Model choice uses shuffled five-fold `KFold` on **development only**, ranked by average negative MAE. Fixed candidate hyperparameters are specified in code; **no optimisation over the held-out test set**.
7. The chosen algorithm is fitted once on the development set and evaluated on the protected test set.
8. Final test predictions are used for post-hoc error diagnostics and permutation importance, not hyperparameter selection.

### Cross-validation and model selection

The fixed candidate list is: median-only baseline, Ridge, Random Forest, Extra Trees, and Gradient Boosting. A simple baseline documents how much complexity adds. Comparisons emphasise MAE, with RMSE and R² for context. The winner is **Random forest** with CV MAE 0.684 lakh INR.

Note that **the original notebook** picked Extra Trees from its single test-set comparison (R² about 0.918 on 298 rows). The new protocol keeps the expensive Land Cruiser, uses 299 unique rows and chooses models on development-fold scores instead. The two numbers are **not comparable as if they came from the same experiment**.

### Supplementary experiments

**Reference-price ablation:** the same candidate algorithm is evaluated with and without the reference-price column on the same development sample and KFold assignments. Results are not used to shop for the best held-out test outcome. Feature distributions shift when dropping the anchor, which is the intended sensitivity test.

**Unfamiliar-model stress:** separate `GroupShuffleSplit` produces non-overlapping model-name groups. Since this uses a different train/test mix from the primary split, the test-set R² values are not directly comparable causal effects of unseen names. Because `Car_Name` is excluded from predictors, unfamiliarity is a proxy for a shift in the composition of vehicle attributes, not a direct unknown-category encoder penalty.

**Outlier sensitivity:** the most expensive *reference-price* record is retained for the primary comparison. Where it appears in development, a supplementary development-only re-fit after excluding it can show sensitivity; however, fold composition also changes, so any difference is not a causal estimate of that record's influence.

**Group errors:** bins are defined using the actual target solely for **post-hoc evaluation**, never used in training. Some bins have very few observations. MAE across different price ranges is absolute, not inherently comparable in percentage terms.

**Feature importance:** permutation on held-out rows measures the worsening in MAE when each original predictor is independently shuffled. Correlated variables can attenuate individual importances; importance is not a causal estimate.

### Limits and modelling choices

- No price-date field: don't calculate a precise age or fit a valid temporal backtest.
- No per-listing vehicle-condition field or geographic location: the model omits important commercial variables.
- Small sample and extreme price variation: high-value performance and CV ranks are uncertain.
- No deployment, real-time price quotation, or post-2018 market claims.
- Source licence is attributed to Kaggle; the user should confirm use restrictions on the original dataset page before downstream commercial redistribution.

### Reproducibility

`python run_analysis.py` recreates the numeric reports and all figures; `python -m pytest -q` checks critical data and evaluation invariants. Every random split, CV fold and model supporting randomness has a specified seed. The original CSV is not mutated.
