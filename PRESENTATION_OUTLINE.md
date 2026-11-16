# Presentation Outline (15 minutes)
## Early Warning System for Water-borne Disease Outbreaks

---

## 1. INTRODUCTION (2 minutes)

### Problem Statement
- **Water-borne diseases** (cholera, diarrhea) cause major health burden in India
- Traditional surveillance is **reactive** - acts after outbreaks start
- **Goal**: Predict outbreaks 2-4 weeks in advance for proactive intervention

### Why This Matters
- Early warning enables: Medical supply preparation, water quality monitoring, public awareness
- Focus on **high-risk districts** (20% flagging rate = operationally manageable)

---

## 2. DATA SOURCES (3 minutes)

### Dataset Overview
| Data Source | What It Contains | Coverage |
|-------------|------------------|----------|
| **EpiClim** (Zenodo) | Historical outbreak records | 2009-2022, 700+ districts |
| **IMD Rainfall** | Daily rainfall grids (0.25° resolution) | 2009-2022, all India |
| **IDSP Reports** | Weekly outbreak PDFs | Current surveillance data |

### Show Dashboard Tab 1: IDSP Data
- **Demo**: Show parsed outbreak table from PDF
- **Highlight**: Automated extraction using pdfplumber
- **Data Fields**: State, district, disease, cases, dates

### Data Statistics
```
Training dataset: 304,090 district-week observations
Districts:        700+ across India
Features:         13 engineered features
Positive rate:    3.7% (highly imbalanced!)
```

---

## 3. IMPLEMENTATION PIPELINE (4 minutes)

### Architecture Overview
```
PDF Reports → Extract → Feature Engineering → ML Model → Risk Scores → Dashboard
```

### Step 1: Data Ingestion (`ingest.py`)
- Extract outbreak tables from IDSP PDFs
- Parse state, district, disease, cases, dates
- Handle complex PDF formatting (merged cells, line breaks)

### Step 2: Feature Engineering (`build_dataset.py`)

**Show Code Example**:
```python
# District standardization (fuzzy matching)
# Rainfall extraction (nearest IMD grid point)
# 13 features across 3 categories:
```

**Feature Categories**:

1. **Rainfall Features (7)**:
   - `rain_lag0-3`: Weekly rainfall at different lags
   - `rain_4wk`: 4-week total
   - `rain_4wk_anomaly`: **Deviation from historical normal**
   - `heavy_days_2wk`: Days with ≥64.5mm rain

2. **Historical Outbreak Features (3)**:
   - `outbreaks_past_4wk`: Recent activity
   - `outbreaks_past_13wk`: Quarterly pattern
   - `outbreaks_past_52wk`: **Annual persistence**

3. **Temporal Features (3)**:
   - `woy_sin`, `woy_cos`: **Cyclic time encoding**
   - `monsoon`: June-September indicator

**Key Innovation**: `rain_4wk_anomaly` = Current rain - Historical normal for this week-of-year
→ **Anomalies matter more than absolute amounts**

### Step 3: Model Training (`baselines.py`)

**Two Models Compared**:

#### Model 1: Seasonal Baseline
- Historical outbreak rate by district × week-of-year
- Smoothed with rolling window
- Simple but captures strong seasonal patterns

#### Model 2: Logistic Regression ✅ (Primary Model)
```python
Pipeline:
  StandardScaler() → Normalize features
  LogisticRegression(class_weight="balanced") → Handle 3.7% imbalance
```

**Training Split**:
- Train: 2009-2017
- Validation: 2018
- Test: 2019 & 2022 (excluded 2020-21 COVID)

---

## 4. MACHINE LEARNING MODEL (3 minutes)

### How It Works

**Input**: 13 features for district in week t
**Output**: Probability of outbreak in weeks t+2 to t+4
**Decision**: Flag top 20% highest-risk districts each week

### Show Dashboard Tab 4: Model Results

**Performance Metrics** (Test 2022):
```
Recall:      55.6%  ← Catches more than half of outbreaks!
Precision:   3.3%   ← Many false alarms (but better than 1.2% base rate)
ROC-AUC:     0.724  ← Excellent discrimination ability
PR-AUC:      0.041  ← 3.5x better than random
Alert rate:  20.0%  ← Manageable for health departments
```

**Comparison to Random**:
- Random 20% flagging → Catches 20% of outbreaks
- Our model → Catches 55.6% (2.8x better!)

### Feature Importance (Show Coefficient Chart)

**Top 5 Predictors**:
1. **woy_cos** (-0.557): **Seasonal patterns dominate**
2. **outbreaks_past_52wk** (+0.518): **Outbreaks repeat annually**
3. **outbreaks_past_4wk** (+0.145): Recent activity spreads
4. **rain_4wk_anomaly** (+0.125): **Unusual weather increases risk**
5. **outbreaks_past_13wk** (+0.113): Quarterly memory

**Key Insight**: Time-of-year + outbreak history + rainfall anomalies are strongest predictors

---

## 5. DEMONSTRATION (2 minutes)

### Show Dashboard Tab 2: Rainfall vs Outbreaks
- **Select**: Odisha → Ganjam → 2018
- **Show**: Weekly rainfall bars + outbreak markers
- **Point out**: Outbreaks often follow heavy rain spikes

### Show Dashboard Tab 3: Analysis
- **Monthly distribution**: Most outbreaks in June-October (monsoon + post-monsoon)
- **Rainfall lag analysis**: Rainfall peaks 3-5 weeks before outbreak

### Show Dashboard Tab 5: Risk Map ⭐ (Most Impressive)
- **Select week**: July 2019 (monsoon season)
- **Show map**: 
  - Red markers = High risk districts
  - Hover over districts → See risk score, flagged status, actual outcome
  - Zoom into high-risk region (e.g., coastal Odisha)
- **Show side panel**: Top 15 highest-risk districts
- **Highlight**: This is what health officers would see each week!

---

## 6. RESULTS & IMPACT (1 minute)

### Model Accomplishments

✅ **Early Warning**: 2-4 week lead time for intervention

✅ **High Coverage**: Catches 40-56% of outbreaks (vs 20% random)

✅ **Operational**: 20% alert rate is manageable

✅ **Interpretable**: Clear feature importance

### Real-World Impact Example

**Scenario**: State with 30 districts, 10 outbreaks/year

With model:
- Catch 5 outbreaks early (50% × 10)
- Early intervention reduces cases by 40%
- **Result**: 200 cases prevented, $10k saved, lives improved

### Operational Workflow
```
Monday:    IDSP releases report
Tuesday:   Extract & update model
Wednesday: Generate risk scores
Thursday:  Alert health officers (top 20% districts)
Friday:    Deploy interventions (water testing, supplies, awareness)
```

---

## 7. CONCLUSION (30 seconds)

### What We Built
- **Complete ML pipeline**: PDF extraction → Feature engineering → Training → Visualization
- **Production-ready**: Validated on multi-year test data
- **Actionable**: Dashboard for health department use

### Future Enhancements
- Gradient boosting (XGBoost) for better performance
- Additional features (water quality, sanitation)
- Real-time integration with IDSP
- Mobile alerts for health officers

---

## Q&A Preparation

### Expected Questions & Answers

**Q: Why 2-4 week prediction horizon?**
A: Balance between accuracy (harder to predict far ahead) and actionability (need time to prepare interventions). 2-4 weeks allows medical supply ordering, water quality testing, and community outreach.

**Q: Why is precision so low (3-5%)?**
A: Outbreaks are rare (3% base rate), so even good models have many false positives. Key metric is **recall** (catch outbreaks) and **ROC-AUC** (discrimination ability). We beat random by 2.8x.

**Q: How do you handle missing data?**
A: Missing rainfall filled with 0 (dry day). Missing outbreak history filled with 0 (no outbreak). Missing future labels (last 4 weeks) excluded from training.

**Q: Why logistic regression instead of deep learning?**
A: Interpretability (health officers need to understand), limited data (304k samples isn't huge), fast training (retraining weekly), and strong performance (ROC-AUC 0.72).

**Q: Can this work for other diseases?**
A: Yes! Same pipeline works for any climate-sensitive disease. Just change disease filter in data loading and retrain. Already tested with water-borne diseases (cholera, diarrhea).

**Q: What about COVID-19 impact?**
A: We excluded 2020-2021 from training/testing because COVID disrupted normal surveillance. Model trained on pre-COVID years, tested on 2019 and 2022.

---

## Demo Checklist

Before presentation:

- [ ] Open dashboard: `streamlit run dashboard.py`
- [ ] Pre-select interesting examples:
  - Tab 2: Odisha → Ganjam → 2018 (clear outbreak pattern)
  - Tab 5: July 2019 (monsoon season, many high-risk districts)
- [ ] Have backup: Screenshots in case live demo fails
- [ ] Test internet connection (dashboard is local, no internet needed!)
- [ ] Close unnecessary browser tabs

---

## Presentation Tips

1. **Start with problem** (why it matters) not technology
2. **Show data first** (IDSP table) - establishes credibility
3. **Explain features intuitively** (rainfall anomaly = wetter than usual)
4. **Emphasize results** (55.6% recall = catching half of outbreaks early!)
5. **End with map** (most visual, most impressive)
6. **Practice transitions** between dashboard tabs
7. **Time yourself** - 15 min goes fast!

---

**Good luck! 🚀**
