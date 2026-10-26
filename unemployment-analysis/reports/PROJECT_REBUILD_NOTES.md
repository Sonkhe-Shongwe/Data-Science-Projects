# Project reconstruction and review notes

## What was improved over the original notebook

- Reframed the work from general EDA into a continuous question-led historical investigation.
- Rebuilt the notebook with concise chapters and chart-level interpretation, not only plotting commands.
- Exposed **30 missing observed-group/month combinations** despite no null values in CSV fields.
- Differentiated the original all-observation means from a *44-group balanced panel* to test composition sensitivity.
- Used 10-month pre-shock means and two-month shock windows for within-group percentage-point comparisons.
- Replaced prominence of t-tests and ANOVA on employed **counts** with more useful comparisons of **rates** and matched changes.
- Added a carefully labelled row-wise implied employed-share proxy, with denominator caveats.
- Assessed rural and urban shock changes only in **20 paired complete regions**.
- Added a geographic unit-level June reversal assessment that compares each area to its own baseline.
- Included outlier influence, median/interquartile spread and descriptive region-resampling sensitivity, while avoiding unwarranted survey inference.
- Designed **eight original charts**, including a LinkedIn-cover infographic and seven supporting visuals, rendered from the same analytical code.
- Preserved the original raw CSV **byte for byte**, providing SHA-256 and automated checks.
- Added methods, data dictionary, reproducibility outputs, a professionally structured README and tests.

## Publication boundaries

This package is a **local review build**. Nothing has been uploaded or changed on GitHub during this development stage. On publication approval, replace only the `unemployment-analysis` folder in `Sonkhe-Shongwe/Data-Science-Projects` with approved files. Do not touch the car-price-prediction or sms-spam-detection folders. The old notebook is preserved by Git history, so it need not be redistributed within the replacement folder.

## What to inspect before approval

1. Whether the new research title and focus represent your desired professional identity.
2. Whether chapter explanations are clear and proportionate to evidence.
3. Whether LinkedIn media is strong enough to represent your portfolio.
4. Whether you want to keep the full eight-image gallery in README or shorten it to three main figures.
5. The data-source attribution and any upstream licence information you can independently confirm.
6. Whether the finished project should be published on the existing repository or a separate standalone repository. The current plan is the existing folder.
