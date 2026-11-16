# Early Warning System for Water-borne Disease Outbreaks in India
### A Machine Learning Approach Using Rainfall and Epidemiological Data

**Team Members:** Kaustubh, Aryan, Raghav
**Date:** November 2026  
**GitHub:** https://github.com/Kaustube/outbreak-ews  
**Live Demo:** [Add Streamlit URL]

---

## Individual Contributions

**Kaustubh** *(Lead)*
- Designed and built the complete end-to-end ML pipeline
- Implemented feature engineering (13 features: rainfall lags, anomalies, seasonal encoding, outbreak history)
- Trained and tuned the Logistic Regression model with class balancing
- Built the Streamlit interactive dashboard (all 5 tabs including the risk map)
- Set up GitHub repository, data pipeline, and cloud deployment
- Wrote the full project report and documentation

**Aryan**
- Collected and preprocessed the EpiClim dataset from Zenodo
- Implemented the PDF ingestion pipeline (`ingest.py`) using pdfplumber
- Assisted with data cleaning and district name standardisation using fuzzy matching
- Contributed to evaluation analysis and confusion matrix interpretation
- Helped prepare the presentation slides and demo walkthrough

**Raghav**
- Sourced and processed IMD rainfall gridded data using imdlib
- Implemented the seasonal baseline model
- Assisted with results analysis and performance benchmarking
- Contributed to the Related Work and References sections of the report
- Helped with testing the dashboard and validating model outputs

---

## 1. Introduction

Water-borne diseases such as cholera, acute diarrhoeal disease, and gastroenteritis remain a significant public health challenge in India, particularly during and after monsoon seasons. These diseases spread through contaminated water sources, which are heavily influenced by rainfall patterns. Despite advances in disease surveillance, most public health responses remain reactive — interventions begin only after an outbreak has already started, limiting their effectiveness.

India's Integrated Disease Surveillance Programme (IDSP) collects and publishes weekly outbreak reports across all states, providing a rich source of epidemiological data. Combined with high-resolution meteorological data from the India Meteorological Department (IMD), this presents an opportunity to build a predictive system that can warn health authorities of impending outbreaks weeks in advance.

This project develops a machine learning-based Early Warning System (EWS) for water-borne disease outbreaks. The system uses historical outbreak records and weekly rainfall data to predict which districts are at high risk of an outbreak 2 to 4 weeks in the future. A 2–4 week lead time was specifically chosen because it is long enough for health departments to take meaningful action — pre-positioning medical supplies, intensifying water quality monitoring, and launching public awareness campaigns — while still being short enough for the predictions to be accurate.

The key contributions of this project are:
1. An automated data pipeline that extracts structured outbreak data from IDSP PDF reports.
2. A feature engineering framework capturing rainfall, historical outbreak patterns, and seasonal signals.
3. A trained Logistic Regression classifier achieving 55.6% recall and 0.724 ROC-AUC on held-out test data.
4. An interactive web dashboard for operational use by health departments.

---

## 2. Related Work

Several studies have explored the relationship between climatic variables and disease outbreaks. Carlton et al. (2016) demonstrated a significant association between heavy rainfall events and diarrhea incidence in developing countries, particularly where sanitation infrastructure is inadequate. Cheng et al. (2017) further showed that ambient temperature and rainfall jointly influence the seasonality of communicable diseases.

In the Indian context, the monsoon season (June–September) has been consistently linked to spikes in water-borne disease incidence. Studies using IDSP data have confirmed that cholera and acute diarrhoeal disease cases peak during and immediately after heavy rainfall periods, with a lag of 2–4 weeks attributed to the time needed for water contamination to spread through communities.

Machine learning approaches have been applied to disease prediction in various settings. Logistic regression has proven effective for binary outbreak prediction tasks due to its interpretability and low data requirements. More complex models such as Random Forests and LSTMs have been explored but require significantly more data and are harder to explain to non-technical stakeholders such as public health officers.

This project builds on these foundations by combining the EpiClim geocoded outbreak dataset with IMD gridded rainfall, applying careful feature engineering, and deploying the results as an actionable tool.

---

## 3. Dataset

### 3.1 Data Sources

**Source 1: EpiClim Dataset (Primary)**
- **Origin:** Zenodo open research repository (DOI: 10.5281/zenodo.14580510)
- **Description:** A geocoded, cleaned compilation of disease outbreak records from India's IDSP spanning 2009 to 2022.
- **Why chosen:** It is the most comprehensive publicly available dataset of geocoded Indian outbreak records, with consistent formatting across 14 years.
- **Fields:** Disease name, State, District, Year, Month, Day, Latitude, Longitude, Number of cases, Number of deaths.
- **Diseases retained:** Acute diarrhoeal disease, cholera, suspected cholera, acute gastroenteritis, gastroenteritis, diarrhea.

**Source 2: IMD Gridded Rainfall Data (Secondary)**
- **Origin:** India Meteorological Department, accessed programmatically via the `imdlib` Python library.
- **Description:** Daily gridded rainfall measurements at 0.25° spatial resolution (~25 km per grid cell) covering all of India.
- **Why chosen:** IMD is the official source of meteorological data in India. The 0.25° resolution is sufficient to assign a meaningful rainfall value to each district.
- **Processing:** For each district, the nearest land-based IMD grid point was identified using Euclidean distance on latitude-longitude coordinates. Daily values were then aggregated to weekly totals.

**Source 3: IDSP Weekly PDF Reports (Tertiary)**
- **Origin:** Integrated Disease Surveillance Programme, Ministry of Health and Family Welfare, Government of India.
- **Description:** Weekly PDF reports listing all active outbreaks across India.
- **Why chosen:** Demonstrates a real-time data ingestion capability. Extracted using `pdfplumber` with custom parsing logic to handle complex table formatting.
- **Output:** `data/idsp_parsed.csv` — structured table of outbreaks extracted from the PDF.

### 3.2 Dataset Construction

The final training dataset (`data/panel.csv.gz`) is a district-week panel: one row per district per week from 2009 to 2022.

| Split | Years | Rows |
|-------|-------|------|
| Training | 2009–2017 | 304,090 |
| Validation | 2018 | 34,291 |
| Test 1 | 2019 | 33,644 |
| Test 2 | 2022 | 31,056 |
| Excluded | 2020–2021 | — (COVID disruption) |

- **Total districts:** 700+ across all major Indian states
- **Positive rate:** 3.7% (outbreak in next 2–4 weeks) — highly imbalanced

### 3.3 Engineered Features (13 Total)

**Rainfall features (7):**
- `rain_lag0` through `rain_lag3` — weekly rainfall at lags 0 to 3 weeks
- `rain_4wk` — rolling 4-week total rainfall
- `rain_4wk_anomaly` — difference from historical mean for that district and week-of-year (computed only from training years to prevent leakage)
- `heavy_days_2wk` — count of days with rainfall ≥ 64.5 mm (IMD's heavy rain threshold) in the past 2 weeks

**Historical outbreak features (3):**
- `outbreaks_past_4wk` — outbreak count in this district over the past 4 weeks
- `outbreaks_past_13wk` — outbreak count over the past 13 weeks
- `outbreaks_past_52wk` — outbreak count over the past 52 weeks

**Temporal features (3):**
- `woy_sin`, `woy_cos` — sine and cosine encoding of week-of-year (1–52), which allows the model to understand that week 52 and week 1 are adjacent
- `monsoon` — binary flag for June through September

### 3.4 Label Definition

The prediction target is binary:
- **Label = 1** if at least one outbreak begins in week t+2, t+3, or t+4 in that district
- **Label = 0** otherwise

The 2–4 week window was chosen to give health departments actionable lead time while maintaining prediction accuracy.

---

## 4. Methodology

### 4.1 Preprocessing

**District name standardisation:** The same district is often spelled differently across years (e.g., "Pudukottai" vs "Pudukkottai"). We normalised names by lowercasing and removing non-alphabetic characters, then used fuzzy string matching (`difflib.get_close_matches`, cutoff = 0.85) within each state to merge near-duplicate spellings into a single canonical identifier of the form `STATE|district_key`.

**Missing value handling:** Missing rainfall values were filled with 0 (dry day assumption). Missing outbreak history was filled with 0. Rows where the label could not be computed (the final 4 weeks of data) were excluded.

**Train-test split:** A strict time-based split was used — no shuffling. This ensures the model never sees future data during training, which is critical for time-series problems.

### 4.2 Model 1 — Seasonal Baseline

The seasonal baseline predicts outbreak risk using only historical outbreak rates:

1. For each (district, week-of-year) pair, compute the fraction of training years in which a label=1 occurred.
2. Smooth the rates with a 5-week centred rolling window to handle sparse data.
3. Add 0.001 × (district overall outbreak rate) as a tiebreaker.

This model serves as a lower bound for performance and captures the strong seasonal signal present in the data.

### 4.3 Model 2 — Logistic Regression (Primary Model)

**Architecture:**
```
Input (13 features)
    → StandardScaler (zero mean, unit variance)
    → LogisticRegression (class_weight="balanced", max_iter=2000, solver=lbfgs)
    → Output: P(outbreak in next 2–4 weeks)
```

**Why Logistic Regression?**
- Interpretable: coefficients directly show which features drive predictions
- Handles the small positive rate well with class weighting
- Trains in seconds, allowing weekly retraining as new data arrives
- Outputs calibrated probabilities suitable for risk ranking

**Class imbalance handling:** With only 3.7% positive labels, an unweighted model learns to always predict "no outbreak" and achieves 96.3% accuracy while catching zero outbreaks. Setting `class_weight="balanced"` causes the model to weight false negatives (missed outbreaks) approximately 27× more heavily than false positives, shifting the decision boundary toward catching more outbreaks.

**Alert generation:** Rather than applying a fixed probability threshold, the top 20% of districts by risk score are flagged each week. This ensures a consistent, operationally manageable alert rate regardless of the absolute score distribution.

---

## 5. Results

### 5.1 Overall Performance

| Model | Dataset | Recall | Precision | F1 | ROC-AUC | PR-AUC |
|-------|---------|--------|-----------|-----|---------|--------|
| Seasonal Baseline | Val 2018 | 0.426 | 0.062 | 0.108 | 0.695 | 0.069 |
| Seasonal Baseline | Test 2019 | 0.361 | 0.052 | 0.091 | 0.652 | 0.065 |
| Seasonal Baseline | Test 2022 | 0.405 | 0.024 | 0.045 | 0.602 | 0.020 |
| **Logistic Regression** | **Val 2018** | **0.417** | **0.061** | **0.106** | **0.684** | **0.088** |
| **Logistic Regression** | **Test 2019** | **0.398** | **0.058** | **0.101** | **0.697** | **0.072** |
| **Logistic Regression** | **Test 2022** | **0.556** | **0.033** | **0.062** | **0.724** | **0.041** |

### 5.2 Confusion Matrix (Logistic Regression, Test 2022)

```
                   Predicted: No Outbreak    Predicted: Outbreak
Actual: No Outbreak        24,703                  5,990
Actual: Outbreak              161                    202
```

- **True Positives:** 202 outbreaks correctly flagged
- **False Negatives:** 161 outbreaks missed
- **Recall:** 202 / (202 + 161) = **55.6%**
- **Alert rate:** exactly 20% of district-weeks flagged per week

Compared to random 20% flagging (which would catch ~20% of outbreaks), our model catches **55.6% — 2.8× better than random**.

### 5.3 Feature Importance

| Rank | Feature | Coefficient | Interpretation |
|------|---------|-------------|----------------|
| 1 | woy_cos | −0.557 | Seasonality dominates |
| 2 | outbreaks_past_52wk | +0.518 | Strong annual recurrence |
| 3 | outbreaks_past_4wk | +0.145 | Recent spread |
| 4 | rain_4wk_anomaly | +0.125 | Unusual rainfall raises risk |
| 5 | outbreaks_past_13wk | +0.113 | Quarterly memory |
| 6 | monsoon | +0.099 | June–September elevation |

**Key finding:** Seasonality and outbreak history are stronger predictors than raw rainfall. Rainfall anomalies (deviation from normal) matter more than absolute totals.

---

## 6. Discussion

### 6.1 What Worked

The logistic regression model substantially outperforms the seasonal baseline, particularly on Test 2022 where recall improved by 15 percentage points (40.5% → 55.6%) and ROC-AUC improved by 0.122. This shows that rainfall features and multi-scale outbreak history features add meaningful predictive power beyond seasonality alone.

The `rain_4wk_anomaly` feature proved more informative than any individual rainfall lag. This makes intuitive sense: districts that receive unusually heavy rainfall relative to their local norms are more likely to experience contamination of water sources, regardless of absolute rainfall amounts.

The annual outbreak lag (`outbreaks_past_52wk`) being the second strongest predictor reflects a known epidemiological pattern — communities with inadequate sanitation infrastructure repeatedly experience outbreaks at the same time of year.

### 6.2 Limitations

**Low precision:** With a base rate of 1.2% in Test 2022, even a well-calibrated model flagging 20% of districts will generate many false positives. Precision of 3.3% means most alerts do not correspond to real outbreaks. This is a fundamental constraint of rare event prediction, not a model failure.

**COVID exclusion:** Years 2020–2021 were excluded because COVID-19 disrupted routine IDSP reporting. This reduces training data and may affect generalisation if disease dynamics changed post-COVID.

**No causal model:** Logistic regression captures correlations, not causal mechanisms. Features like `outbreaks_past_52wk` may reflect underlying structural factors (poor sanitation, water quality) rather than direct causal pathways.

**IMD data dependency:** The pipeline requires downloading large IMD rainfall grids. For real-time deployment, this would need to be replaced with an automated weather API.

### 6.3 Operational Considerations

The 20% alert rate means health departments would need to investigate approximately 140 districts per week nationally. This is operationally manageable if alerts are tiered by risk score. The dashboard's risk map allows officers to prioritise the highest-scoring districts within flagged regions.

---

## 7. Conclusion

This project demonstrates a complete, end-to-end machine learning pipeline for early warning of water-borne disease outbreaks in India. Using 304,090 district-week observations from 2009 to 2022, we engineered 13 predictive features capturing rainfall patterns, historical outbreak activity, and seasonal cycles. A class-balanced Logistic Regression model trained on this data achieves 55.6% recall and 0.724 ROC-AUC on 2022 test data, flagging 2.8× more real outbreaks than random selection at the same 20% alert rate.

The system is deployed as an interactive Streamlit dashboard enabling health officers to explore district-level risk scores on an India-wide map, examine rainfall-outbreak correlations, and review model performance metrics. All code and data are publicly available on GitHub.

Future work includes incorporating gradient boosting models for improved non-linear feature interactions, adding water quality and sanitation infrastructure data, and building a fully automated real-time pipeline with direct IDSP and IMD data feeds.

---

## References

1. Carlton, E.J., et al. (2016). Heavy rainfall events and diarrhea incidence: the role of social and environmental factors. *International Journal of Epidemiology*, 43(6), 1600–1611.
2. Cheng, J., et al. (2017). Impact of ambient temperature on the association between rainfall and notifiable communicable diseases. *Environment International*, 104, 79–88.
3. EpiClim Dataset. Zenodo. DOI: 10.5281/zenodo.14580510.
4. India Meteorological Department. Daily Gridded Rainfall Data (0.25°). https://www.imdpune.gov.in/
5. IDSP. Integrated Disease Surveillance Programme Weekly Reports. Ministry of Health and Family Welfare, Government of India. https://idsp.mohfw.gov.in/
6. Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. *JMLR*, 12, 2825–2830.
7. Streamlit Inc. (2024). Streamlit Documentation. https://docs.streamlit.io/
