# Unemployment Analysis in India

An exploratory and statistical analysis of unemployment and employment trends across India before and during the COVID-19 pandemic.

**Tools:** Python, Pandas, Matplotlib, Seaborn, SciPy  
**Analysis:** Data cleaning, exploratory data analysis, time-series trends, hypothesis testing and correlation

![Unemployment Analysis](./Unemployment_ScreenShot.png)

## Questions explored

- How did unemployment and labour force participation change over time?
- How did employment patterns differ between rural and urban areas?
- Were differences in estimated employment across areas and regions statistically significant?
- Was labour force participation associated with estimated employment counts?

## Dataset

The analysis uses the included [Unemployment in India.csv](./Unemployment%20in%20India.csv):

| Detail | Value |
| --- | --- |
| Records | 740 |
| Regions | 28 |
| Period | May 2019 – June 2020 (14 months) |
| Geographic breakdown | Region and rural/urban area |
| Main measures | Estimated unemployment rate (%), estimated employed count, estimated labour participation rate (%) |

The dataset contains monthly observations for individual regions and areas, rather than a single national monthly total.

## Approach

1. **Prepare the data:** Load the CSV, standardise column names, check for missing values and duplicates, parse dates and normalise category labels.
2. **Explore the trends:** Compare unemployment rates by region and month, examine labour participation and visualise rural-versus-urban employment patterns.
3. **Test relationships:** Apply an independent-samples t-test, Pearson correlation and one-way ANOVA to the estimated employment and labour participation measures.
4. **Interpret the results:** Separate descriptive patterns from statistical evidence and consider limitations in the comparisons.

## Key findings

### Unemployment increased sharply during the pandemic period

The mean unemployment rate across the observations available for each month rose from **10.70% in March 2020** to **23.64% in April** and **24.88% in May**, before falling to **11.90% in June**.

These are averages of the dataset's regional/area observations for each month, not population-weighted national unemployment estimates.

### Rural and urban estimated employment counts differed

The independent-samples t-test comparing **estimated employed counts** between rural and urban observations reported:

- **t-statistic:** 10.45
- **p-value:** 6.46 × 10⁻²⁴

The difference is statistically significant in this sample. Because the test compares counts rather than employment rates, it does not establish that one area's employment *rate* is higher.

### Labour participation and employment count showed little linear association

Pearson correlation between the estimated labour participation rate and estimated employed count returned:

- **Correlation (r):** 0.011
- **p-value:** 0.759

The sample showed no statistically significant linear correlation between these two measures.

### Estimated employment counts varied across regions

A one-way ANOVA of **estimated employed counts** by region returned:

- **F-statistic:** 58.23
- **p-value:** 3.21 × 10⁻¹⁶⁰

This indicates differences among the regional group means in the sample, but those differences may also reflect regional population sizes.

## Explore the analysis

Open [Oasis_Unemployment_Analysis.ipynb](./Oasis_Unemployment_Analysis.ipynb) to see the preprocessing, charts, statistical tests and written interpretation.

To run it locally:

1. Install Python and Jupyter Notebook.
2. Install the required packages: `pip install pandas matplotlib seaborn scipy notebook`
3. Keep the notebook and `Unemployment in India.csv` in the same folder.
4. Open the notebook with Jupyter and run the cells in order.

## Limitations

This is an observational analysis. Differences in observation counts, regional population sizes and repeated monthly measurements affect how comparisons should be interpreted. The results show patterns and associations, not proof that lockdown measures caused a particular change.

