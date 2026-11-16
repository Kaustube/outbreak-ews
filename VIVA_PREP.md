# VIVA PREP + PRESENTATION GUIDE
## Who Says What + Q&A Prep

---

## 🎤 WHO SAYS WHAT (PRESENTATION ORDER)

---

### KAUSTUBH STARTS (2 min) — Project Overview + ML Model

**Say this:**
> "Our project is an Early Warning System for water-borne disease outbreaks in India.
> The idea is simple — diseases like cholera and diarrhea mostly happen during and after monsoon season.
> If we can predict 2 to 4 weeks in advance which districts are at risk, health departments can act early —
> send medicines, test water quality, warn people.
>
> We used 14 years of outbreak data from 2009 to 2022, combined with daily rainfall data from IMD,
> to train a Logistic Regression model on 304,000 observations across 700+ districts in India.
> The model flags the top 20% riskiest districts every week.
> On our test data, it catches 55.6% of real outbreaks — 2.8 times better than random."

**Then show:** Dashboard Tab 5 (Risk Map) — point to red districts, explain the slider

---

### ARYAN NEXT (1.5 min) — Data + Ingestion

**Say this:**
> "I handled the data side. We used three sources.
>
> First, the EpiClim dataset from Zenodo — this has historical outbreak records for all of India from 2009 to 2022,
> with district names, coordinates, disease type, and case counts.
>
> Second, IMD rainfall grids — daily rainfall measurements across India at 25km resolution.
> For each district we found the nearest grid point and extracted weekly rainfall totals.
>
> Third, IDSP weekly PDF reports — the government publishes these every week.
> I built a pipeline using pdfplumber that automatically extracts the outbreak table from these PDFs
> and converts it into a clean CSV."

**Then show:** Dashboard Tab 1 (IDSP Data) — the parsed table from the PDF

---

### RAGHAV LAST (1.5 min) — Features + Results

**Say this:**
> "I worked on building the features and evaluating the model.
>
> We engineered 13 features total — 7 rainfall features like weekly totals, lags, and anomalies,
> 3 past outbreak features at 4-week, 13-week, and 52-week windows,
> and 3 time features including a seasonal sine-cosine encoding.
>
> The most important feature turned out to be seasonality — time of year dominates.
> Second is annual outbreak recurrence — if a district had outbreaks last year at this time, it likely will again.
> Third is rainfall anomaly — wetter than normal for that time of year increases risk.
>
> We compared two models — a seasonal baseline and logistic regression.
> Logistic regression wins on every metric. On 2022 test data it gets 55.6% recall and 0.724 ROC-AUC."

**Then show:** Dashboard Tab 4 (Model Results) — the metrics table and feature importance chart

---

## ❓ VIVA Q&A — EXPECTED QUESTIONS

---

### BASIC PROJECT QUESTIONS

**Q: What is your project about in one line?**
> "It predicts water-borne disease outbreaks in India 2 to 4 weeks in advance using rainfall and historical data."

**Q: Why water-borne diseases specifically?**
> "They are strongly linked to rainfall — contaminated water sources spread during floods and heavy rain. This makes them more predictable than other diseases."

**Q: Why 2 to 4 weeks prediction window?**
> "Short enough to be accurate, long enough to act. 2 weeks gives time to pre-position medicines and alert communities."

**Q: What does the model actually output?**
> "A risk score between 0 and 1 for every district every week. We flag the top 20% highest scores as alerts."

---

### DATA QUESTIONS (ARYAN ANSWERS)

**Q: Where did you get the data?**
> "EpiClim from Zenodo — a research data repository. Rainfall from India Meteorological Department via imdlib. Current outbreak reports from IDSP PDFs."

**Q: How did you extract data from PDFs?**
> "Using pdfplumber Python library. We used regex to identify outbreak rows by their ID pattern, then parsed each row into structured fields — state, district, disease, cases, date."

**Q: How did you handle district name inconsistencies?**
> "Fuzzy string matching using Python's difflib library with 85% similarity threshold within each state. So Pudukottai and Pudukkottai get merged into one ID."

**Q: How much data do you have?**
> "304,090 district-week observations across 700+ districts over 14 years."

---

### ML MODEL QUESTIONS (KAUSTUBH ANSWERS)

**Q: Why Logistic Regression and not something more complex?**
> "Three reasons — interpretability (health officers need to understand why a district is flagged), speed (retrains in seconds weekly), and it already performs well with ROC-AUC 0.724. Deep learning needs more data and is a black box."

**Q: What is class imbalance and how did you handle it?**
> "Only 3.7% of district-weeks have outbreaks. If we train normally, the model just always says 'no outbreak' and gets 96% accuracy but catches zero real cases. We used class_weight=balanced in scikit-learn which penalises missed outbreaks 27x more than false alarms."

**Q: What is ROC-AUC?**
> "Area Under the ROC Curve. It measures how well the model separates outbreak from non-outbreak cases. 0.5 is random, 1.0 is perfect. We get 0.724 which is good."

**Q: What is recall?**
> "Out of all actual outbreaks that happened, what percentage did we catch. We catch 55.6% — more than half — by flagging only 20% of districts."

**Q: Why is precision so low at 3.3%?**
> "Because outbreaks are rare — only 1.2% of district-weeks have them. Even with a good model, most alerts will be false positives. What matters is recall — are we catching real outbreaks — and ROC-AUC."

---

### FEATURES QUESTIONS (RAGHAV ANSWERS)

**Q: What are your 13 features?**
> "7 rainfall features — current week, 3 weekly lags, 4-week total, rainfall anomaly, heavy rain days.
> 3 past outbreak features — 4-week, 13-week, 52-week windows.
> 3 time features — sine and cosine of week-of-year, monsoon binary flag."

**Q: What is the rainfall anomaly feature?**
> "It's this week's 4-week rainfall minus the historical average for that district at that time of year. So if it normally rains 100mm in July in Ganjam but this year it rained 180mm, the anomaly is +80mm. This matters more than absolute rainfall."

**Q: Why sine and cosine for week of year instead of just the number?**
> "Because week 52 and week 1 are adjacent in time but numerically far apart. If we use raw numbers the model thinks January and December are very different. Sine-cosine encoding wraps the year into a circle so the model understands the cycle."

**Q: What was the most important feature?**
> "woy_cos — the cosine of week of year. Seasonality is the strongest signal. Second is outbreaks_past_52wk — annual recurrence. Rainfall anomaly is fourth."

---

### RESULTS QUESTIONS

**Q: How does your model compare to a random guess?**
> "Random 20% flagging catches 20% of outbreaks. Our model catches 55.6% — 2.8 times better — at the same 20% alert rate."

**Q: Why did you exclude 2020 and 2021?**
> "COVID-19 disrupted normal disease surveillance. IDSP reporting was inconsistent during those years so including them would corrupt the training data."

**Q: What is PR-AUC and why mention it?**
> "Precision-Recall AUC. For imbalanced datasets it is more informative than ROC-AUC. Random baseline PR-AUC equals the positive rate — 0.012 for Test 2022. We get 0.041 — 3.5x better than random."

---

### DASHBOARD QUESTIONS

**Q: What does the dashboard show?**
> "5 tabs — parsed IDSP data, rainfall vs outbreak time series, seasonal analysis, model performance metrics with confusion matrix, and a risk map of India where each district is coloured by its risk score for any selected week."

**Q: What technology did you use for the dashboard?**
> "Streamlit for the web app framework and Plotly for interactive charts including the scatter map."

---

### FUTURE WORK QUESTIONS

**Q: How would you improve the model?**
> "Add XGBoost or LightGBM for non-linear interactions. Add water quality and sanitation data as features. Build a real-time pipeline that auto-fetches IDSP reports. Extend to other climate-sensitive diseases like dengue and malaria."

---

## 📋 SECTION SUMMARY — WHO OWNS WHAT IN VIVA

| Topic | Who Answers |
|-------|-------------|
| Project overview, what it does, why | **Kaustubh** |
| ML model, Logistic Regression, class balancing | **Kaustubh** |
| ROC-AUC, recall, confusion matrix | **Kaustubh** |
| Data sources, EpiClim, IMD, IDSP | **Aryan** |
| PDF extraction, pdfplumber | **Aryan** |
| District name cleaning, fuzzy matching | **Aryan** |
| 13 features, what each one means | **Raghav** |
| Rainfall anomaly, seasonal encoding | **Raghav** |
| Feature importance, results table | **Raghav** |
| Any question you're unsure of | **Kaustubh** as fallback |

---

## ⚡ 30-SECOND PROJECT EXPLANATION (ALL THREE MEMORISE)

> "We built a machine learning system that predicts water-borne disease outbreaks in India 2 to 4 weeks in advance.
> We trained a Logistic Regression model on 14 years of outbreak and rainfall data across 700+ districts.
> The model flags the top 20% riskiest districts each week so health departments can act before outbreaks start.
> It catches 55.6% of real outbreaks, which is 2.8 times better than random."

---

## ✅ NIGHT BEFORE CHECKLIST

- [ ] All three read this file once
- [ ] Kaustubh: know the model details cold
- [ ] Aryan: know the 3 data sources and PDF extraction
- [ ] Raghav: know all 13 features and results numbers
- [ ] Deploy dashboard on Streamlit Cloud, test the URL
- [ ] Submit GitHub link before 9:15 AM
- [ ] Sleep!
