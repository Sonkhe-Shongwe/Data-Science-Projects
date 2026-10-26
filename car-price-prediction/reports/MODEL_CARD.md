# Model card: historical used-vehicle selling-price estimator

**Model:** Random forest (selected through development-set CV by MAE).  
**Intended use:** learning, portfolio demonstration and research on prediction error; *not* a live commercial vehicle valuation system.  
**Input sample:** 299 unique vehicle rows, 198 cars and 101 two-wheelers.  
**Target:** `Selling_Price` (interpreted as lakh INR based on dataset source descriptions).

## Model development

- 239 training/development rows; 5-fold shuffled CV (seed 42); final stratified held-out set of 60 rows (seed 42).
- Categorical one-hot encoding and numeric imputation/standardisation are fitted within CV pipelines.
- Excludes model-name text to reduce small-sample memorisation risks.
- Includes a reference-price feature that may not be available in all real-world pricing circumstances.

## Final test results (single split)

| Measure | Score |
|:--|--:|
| R² | 0.934 |
| MAE (lakh) | 0.702 |
| RMSE (lakh) | 1.495 |
| Median AE (lakh) | 0.346 |
| P90 AE (lakh) | 1.293 |

**Caution:** the test population is small, nonrandomly sourced and contains very different classes of vehicles. Model validity in today's market is unknown.

## Failure modes

- Test-set MAE above 10 lakh asking/selling price: approximately 2.88 lakh (n=7); interpret cautiously.
- Without `Present_Price`, the selected model's development-fold MAE rises from 0.684 to 1.617 lakh.
- Unseen-name group stress (separate split): R² 0.629, n=69. This is not a paired comparison with the standard test.
- Dealer and vehicle-type effects are strongly confounded and should not be interpreted as an independent seller premium.

## Not suitable for

- Pricing newly listed vehicles without validation on a fresh real-market sample.
- Financial lending, underwriting, or automated purchases.
- Explanations of causal depreciation.
- Robust predictions in rare vehicle types or premium segments based solely on this sample.

## Suggested next research

Before deployment, acquire a larger, time-stamped, accurately labelled dataset with comparable vehicle class, trim, condition, location and transaction dates. **This is a suggestion for future validation, not a new dataset used in this project.**
