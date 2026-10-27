# Data Science & Analytics Projects

Python portfolio projects focused on **data quality, statistical analysis, machine learning and reproducible evaluation**. Each project has its own README explaining the question, data, methodology, findings and limitations.

## Featured projects

### 1. Used Vehicle Price Intelligence
**Python · Pandas · NumPy · Scikit-learn · Regression · Model validation**

**Question:** How reliably can a model estimate used-vehicle resale prices, and where does it fail?

- Examined **301 vehicle records**, removed **2 exact duplicates** and modelled **299 unique records** spanning cars and two-wheelers.
- Compared regression models using **five-fold cross-validation** on the development data; selected **Random Forest** before evaluating the protected **60-record test set**.
- Achieved **test R² = 0.934** and **MAE = 0.702 lakh INR** (approximately ₹70,200) on that historical sample.
- Stress-tested model reliability: removing the reference price increased development CV MAE from **0.684 to 1.617 lakh INR**. Investigated high-priced vehicles and unfamiliar vehicle models to document limitations.

**[Project, executed notebook and methodology](car-price-prediction/README.md)**

![Used Vehicle Price Intelligence portfolio overview](car-price-prediction/assets/00_portfolio_cover.png)

---

### 2. India's 2020 Labour-Market Shock
**Python · Pandas · Statistical analysis · Data validation · Visualisation**

**Question:** How did unemployment and labour-force participation change across Indian regions during the 2020 disruption, and how does incomplete coverage affect the interpretation?

- Analysed **740 observations** across region–rural/urban groups and **14 months**, identifying gaps in geographic and temporal coverage.
- Used a consistently observed **44-group panel** for comparable period-level analysis.
- Found a **16.03 percentage-point** mean unemployment increase between the May 2019–February 2020 baseline and April–May 2020 in those groups.
- Compared unemployment, labour-force participation and a carefully defined implied employed-share indicator. Results are **descriptive group averages, not official national estimates or causal effects**.

**[Project, executed notebook and methodology](unemployment-analysis/README.md)**

![India's 2020 Labour-Market Shock portfolio overview](unemployment-analysis/assets/00_portfolio_cover.png)

---

### 3. SMS Spam Detection with Machine Learning
**Python · Pandas · NLTK · TF-IDF · Scikit-learn · Classification**

**Question:** How well can classical machine-learning models identify spam SMS messages while balancing false positives and missed spam?

- Started with **5,572 labelled SMS messages**; removed **403 duplicate rows**, leaving **5,169 messages**.
- Compared **Extra Trees, Random Forest, Logistic Regression and SVM**, with text preprocessing and training-time class balancing.
- The saved notebook reports **97.78% test accuracy** for Extra Trees on a **1,034-message** test split, with spam-class recall of **0.88**.
- Noted the trade-off: Logistic Regression obtained higher spam recall (**0.93**) despite lower overall accuracy. Results are from an SMS dataset and are **not validated for email or production deployment**.

**[Project, notebook and limitations](sms-spam-detection/README.md)**

![SMS spam classification analysis](sms-spam-detection/sms_spam_analysis.png)

---

## How to explore

Open each project's README for its dataset, implementation, tests or notebook, methodology, results and limitations. The **Used Vehicle Price Intelligence** and **Labour-Market Shock** projects include documented reproducible analysis workflows. The older SMS project is a saved notebook experiment and documents its own limitations.

This repository presents **historical-data investigations and prototypes**, not deployed commercial applications or guarantees of real-world predictive performance.
