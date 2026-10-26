# Dataset dictionary and scope

The project uses one pre-existing Kaggle-hosted CSV: `unemployment_india.csv`.

| Raw field | Observed type | Analytical use | Interpretation warning |
|---|---|---|---|
| `Region` | Text | Grouping by geographic area | Names are dataset labels, not a verified harmonised administrative boundary series |
| ` Date` | `DD-MM-YYYY` text, with leading whitespace in raw column name | Month-end period after strict conversion | Not an individual job-transition timestamp |
| ` Frequency` | Text (`Monthly`) | Schema/data quality validation | Constant within this snapshot; cannot add predictive information |
| ` Estimated Unemployment Rate (%)` | Numeric percentage | Primary unemployment-rate analysis | Aggregated rate; original survey denominator / standard errors unavailable |
| ` Estimated Employed` | Numeric count | Data validation and context | Counts strongly influenced by region population and must not be compared as rates |
| ` Estimated Labour Participation Rate (%)` | Numeric percentage | Secondary participation measure | Its population base must be compatible with UR before deriving implied EPR |
| `Area` | Rural / Urban | Geography-matched comparisons | Area categories exist for 55 observed region–area combinations, not all theoretical combinations |

Column names are cleaned by removing leading/trailing whitespace, while **source file bytes remain unchanged**. The analysis adds `Unit` and an `Implied employed share (%)` measure, without modifying the raw CSV.

**Period definition:** May 2019–February 2020 baseline, March 2020 transition, April–May 2020 shock window, June 2020 initial reversal. The resulting comparison is descriptive and does not infer causal effects.

**Observed time coverage:** 55 distinct region–area groups × 14 months would contain 770 records if every observed group were present in every month; 740 are present and 30 absent. A complete panel of 44 such groups contains 616 observations from 24 regions. This narrower panel is used for matched comparisons.

**Data-source qualification:** Kaggle is the recognised hosting platform for this file in the project. Upstream survey producer, sample-weighting and redistribution rights are **not** verified by the CSV alone. No extra dataset is merged or used to fill the gaps.
