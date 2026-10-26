# Methodology and interpretation notes

## Research scope

Historical descriptive investigation: India, May 2019 to June 2020. The exact supplied `unemployment_india.csv` is the **only numerical data source**. Dataset credited to [Unemployment in India on Kaggle](https://www.kaggle.com/datasets/gokulrajkmv/unemployment-in-india). The dataset's upstream sampling frame, survey design, weighting and complete metadata are not supplied in the CSV, and are not inferred.

## Provenance, unchanged source and grain

- Source file: `unemployment_india.csv`.
- Source file SHA-256: `caa83db2077f8e08ab87e0dd1298c25e698b9c3461b94dad21ab9faad5c72e1b`.
- Source rows: 740; source columns: 7; zero null field entries; zero exact duplicates; zero duplicate `(Region, Area, Date)` keys.
- Coverage: 28 region labels; 55 observed `(Region, Area)` combinations; 14 monthly periods, May 2019–June 2020.
- Total within-observed-group potential records: `55 × 14 = 770`; 740 observed; **30 group-month gaps**.
- Fully observed units: 44 geographic groups (24 regions), yielding 616 complete-panel rows. A theoretical 56th `(Region, Area)` category is not assumed to be required because one region appears under only one area label.
- Rows represent reported *region × area × month estimated aggregate indicators*, not 740 sampled individuals.

## Transformations

1. Strip whitespace from original column names and categorical values.
2. Strictly parse original date strings using `%d-%m-%Y`.
3. Preserve all observed rows; fail loudly on invalid numeric fields, duplicate unit-month keys, missing required values or out-of-range rates.
4. Derive `Unit = Region + ' | ' + Area`.
5. Derive **implied employed share** from each row: `EPR_proxy = LFPR × (1 − UR/100)`. This requires compatible populations/definitions of LFPR and UR. It is not a separately measured indicator and should not be represented as an official population estimate.
6. Define May 2019–February 2020 as baseline, March 2020 as transition, April–May 2020 as acute disruption, and June 2020 as initial reversal observation. This partition is an **analysis convention** and does not itself establish causation.

## Population and aggregation cautions

All comparisons are **unweighted averages of region–area observations** unless explicitly noted. No national denominator, regional population weight or variance stratum/cluster information is provided. Therefore:

- Dataset means are **not** India-wide official rates.
- Derived EPRs are an inferential *identity* applied to the reported percentages, not surveyed worker-population ratios.
- Employed counts can reflect region size. We avoid comparing their levels as a proxy for comparable employment rates.
- Repeated region–area months are correlated, and rural and urban groups within a region are likely dependent. Their 740 observed rows must not be treated as 740 independent draws for hypothesis tests.
- An empty region–area–month cell is absent coverage, **not** zero unemployment.

## Primary comparison contract

For each geographic unit with all 14 months:

- `baseline_UR = mean(UR_May2019 ... UR_Feb2020)`
- `shock_UR = mean(UR_Apr2020, UR_May2020)`
- `June_UR = UR_Jun2020`
- `Δ_shock = shock − baseline`, and `Δ_June = June − baseline`, using **percentage points**.

The same approach applies to LFPR and the row-level implied EPR proxy. The unit-level values are averaged with **equal geographic-group weights** across the 44 complete units. A region with two complete rural/urban groups counts twice compared with a region with only one. This is a transparent **group** comparison, not an equal-region or population-weighted estimate.

## Rural/urban comparison

Use only the **20 regions** with both complete rural and complete urban groups. Compare their own within-area unemployment changes from baseline to Apr–May. Report the distribution of `urban change − rural change` (percentage points), counts above/below zero and the median. No effect of residence is causally identified.

## Robustness and dependence

- **All observed vs complete panel:** compare monthly averages; the discrepancy shows sensitivity to differing group composition and selecting 44 fully observed units. This is a sensitivity comparison, not a corrected national estimate.
- **Median and quartiles:** summarise geographic group dispersion alongside means, reducing overinterpretation of extreme cases. We also calculate a transparent one-group influence diagnostic: Puducherry | Urban experienced a +73.72 pp shock; the all-group mean is +16.03 pp and drops to +14.69 pp if that group is omitted for diagnosis. The observation is not deleted from the primary analysis.
- **Region-cluster resampling:** repeatedly sample the 24 complete-panel regions with replacement while retaining every selected region's included area groups; recompute the descriptive mean shock change and report the 2.5th–97.5th percentiles. The random seed is fixed (`2026`) with 4,000 draws. The resulting interval assesses **sensitivity to region composition**; it is **NOT a survey sampling confidence interval** or causal interval. Its interpretation is conditional on observed regions and the chosen resampling procedure.

A multi-year seasonal model, national causal estimate or long-term employment forecast is not justified by 14 monthly periods.

## Key reproducible results

| Metric | Result |
|---|---:|
| Balanced pre-shock UR mean | 9.69% |
| Balanced Apr–May UR mean | 25.71% |
| Mean balanced UR change | +16.03 percentage points |
| Geographic groups with UR increase | 40/44 |
| Mean LFPR change in shock | −7.83 pp |
| Mean implied EPR change in shock | −12.85 pp |
| June balanced unemployment mean | 12.50% |
| June balanced implied EPR mean | 36.05% |
| Units whose implied EPR remained below baseline in June | 32/44 |
| Median urban minus rural shock change | +4.44 pp (20 matched regions) |
| May UR all-available mean | 24.88% |
| May UR balanced mean | 26.96% |

Full precision, unit-level results and row-level panels are in `reports/reproduced_metrics.json` and the companion CSV exports.

## Reasonable conclusions and excluded claims

This project's observed series shows acute early 2020 disruption and a substantial June decline in unemployment rates. However, both mean participation and the derived employed-share proxy were still below their pre-March baseline in the 44 complete groups. Geographic patterns vary; many group-month records are missing outside the complete panel. These patterns justify a more cautious interpretation of June's early improvement.

Do **not** infer official national unemployment rates, overall employment/population recovery, individual reasons for labour-market exit, actual persons losing jobs, long-run recovery, or estimated causal impacts from this dataset alone.

## Software

The notebook and graphics were reconstructed and tested using Python, NumPy, Pandas, Matplotlib, Jupyter/nbclient and pytest. `requirements.txt` states the supported minimum packages; regenerated metrics and images are created with exactly the same source file and processing code.

## Publishing note

The source CSV is already included in the prior public repository. Before any new distribution outside that repository, verify the Kaggle listing's underlying redistribution terms, especially where the hosting listing does not unambiguously identify an upstream data producer. Git version history can preserve the original notebook; no need to keep duplicate legacy notebooks in the replacement folder.
