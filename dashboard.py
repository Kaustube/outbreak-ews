"""M2 demo dashboard.  Run with:  streamlit run dashboard.py"""
import json
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # paths below are relative to this folder

st.set_page_config(page_title="Outbreak Early Warning (M2 demo)", layout="wide")
st.title("Early Warning System for Water-borne Disease Outbreaks")
st.caption("M2 demo: data pipeline, rainfall vs outbreaks, baseline models, risk map")


@st.cache_data
def load():
    panel = pd.read_csv("data/panel.csv.gz", parse_dates=["week"])
    preds = pd.read_csv("data/predictions.csv.gz", parse_dates=["week"])
    idsp = pd.read_csv("data/idsp_parsed.csv")
    metrics = json.load(open("results/metrics.json"))
    return panel, preds, idsp, metrics


panel, preds, idsp, metrics = load()
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["1. IDSP data", "2. Rainfall vs outbreaks", "3. Analysis", "4. Baseline results", "5. Risk map"])

# ---------------------------------------------------------------- 1
with tab1:
    st.subheader("Outbreak table extracted from an IDSP weekly report PDF")
    st.write(f"{len(idsp)} outbreaks parsed from `{idsp.source_file.iloc[0]}` using pdfplumber (`ingest.py`).")
    st.dataframe(idsp.drop(columns=["source_file"]), width="stretch", hide_index=True)

    st.subheader("Water-borne outbreaks used for training (2009 to 2022)")
    ob = panel[panel.outbreak == 1]
    c1, c2, c3 = st.columns(3)
    c1.metric("Outbreak weeks", f"{len(ob):,}")
    c2.metric("Districts", panel.district_id.nunique())
    c3.metric("District-week rows", f"{len(panel):,}")
    per_year = ob.groupby(ob.week.dt.year).size().reset_index(name="outbreaks")
    st.plotly_chart(px.bar(per_year, x="week", y="outbreaks",
                           labels={"week": "Year"}, title="Water-borne outbreaks per year"),
                    width="stretch")

# ---------------------------------------------------------------- 2
with tab2:
    st.subheader("Weekly rainfall and outbreaks for one district")
    c1, c2, c3 = st.columns(3)
    states = sorted(panel.state.unique())
    state = c1.selectbox("State", states, index=states.index("Odisha") if "Odisha" in states else 0)
    dists = (panel[panel.state == state].groupby("district").outbreak.sum()
             .sort_values(ascending=False).index.tolist())
    district = c2.selectbox("District (most outbreaks first)", dists)
    year = c3.selectbox("Year", list(range(2022, 2008, -1)), index=4)

    d = panel[(panel.state == state) & (panel.district == district) & (panel.week.dt.year == year)]
    fig = go.Figure()
    fig.add_bar(x=d.week, y=d.rain_mm, name="Weekly rainfall (mm)")
    hits = d[d.outbreak == 1]
    fig.add_scatter(x=hits.week, y=[d.rain_mm.max() * 1.05] * len(hits), mode="markers",
                    marker=dict(symbol="triangle-down", size=14, color="crimson"),
                    name="Outbreak started")
    fig.update_layout(title=f"{district}, {state} ({year})", yaxis_title="Rainfall (mm/week)")
    st.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- 3
with tab3:
    ob = panel[panel.outbreak == 1]
    c1, c2 = st.columns(2)
    by_month = ob.groupby(ob.week.dt.month).size().reindex(range(1, 13), fill_value=0)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    c1.plotly_chart(px.bar(x=months, y=by_month.values,
                           labels={"x": "Month", "y": "Outbreaks"},
                           title="When do water-borne outbreaks start?"),
                    width="stretch")

    # rainfall in the weeks around each outbreak, compared with normal for that time of year
    p = panel.sort_values(["district_id", "week"]).copy()
    p["rain_ratio"] = p.rain_mm / (p.rain_4wk_normal / 4).where(p.rain_4wk_normal > 4)
    g = p.groupby("district_id").rain_ratio
    rows = []
    for k in range(-8, 3):
        shifted = g.shift(-k)
        rows.append({"weeks": k, "ratio": shifted[p.outbreak == 1].median()})
    lag = pd.DataFrame(rows)
    fig = px.line(lag, x="weeks", y="ratio", markers=True,
                  labels={"weeks": "Weeks relative to outbreak start (0)",
                          "ratio": "Rainfall / normal for that week (median)"},
                  title="Rainfall before and after an outbreak starts")
    fig.add_hline(y=1, line_dash="dash", annotation_text="normal")
    c2.plotly_chart(fig, width="stretch")

# ---------------------------------------------------------------- 4
with tab4:
    st.subheader("Baseline models")
    st.write("Trained on 2009 to 2017 and tested on 2019 and 2022 (2020 and 2021 left out because of COVID). "
             "Each week, the 20% of districts with the highest risk score are flagged. "
             "Only about 3% of district-weeks have an outbreak in the next 2 to 4 weeks, so a random guess "
             "would have precision of about 0.03 and ROC-AUC of 0.5.")
    rows = []
    for model, label in (("seasonal", "Seasonal baseline"), ("logreg", "Logistic regression")):
        for split, m in metrics[model].items():
            rows.append({"Model": label, "Data": split, "Recall": round(m["recall"], 3),
                         "Precision": round(m["precision"], 3), "F1": round(m["f1"], 3),
                         "ROC-AUC": round(m["roc_auc"], 3), "PR-AUC": round(m["pr_auc"], 3),
                         "% flagged": round(100 * m["alert_rate"], 1)})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    c1, c2 = st.columns(2)
    model = c1.radio("Model", ["logreg", "seasonal"], horizontal=True)
    split = c1.radio("Data", ["test_2019", "test_2022", "val_2018"], horizontal=True)
    cm = metrics[model][split]["confusion_matrix"]
    z = [[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]]
    c1.plotly_chart(px.imshow(z, text_auto=True, color_continuous_scale="Blues",
                              x=["Predicted no", "Predicted outbreak"],
                              y=["Actual no", "Actual outbreak"], title="Confusion matrix"),
                    width="stretch")
    coef = pd.Series(metrics["logreg_coefficients"]).sort_values()
    c2.plotly_chart(px.bar(coef, orientation="h", title="Logistic regression coefficients",
                           labels={"value": "Coefficient (scaled features)", "index": ""})
                    .update_layout(showlegend=False), width="stretch")

# ---------------------------------------------------------------- 5
with tab5:
    st.subheader("District risk for the next 2 to 4 weeks (logistic regression)")
    weeks = sorted(preds[preds.week.dt.year.isin([2019, 2022])].week.dt.date.unique())
    default = next((i for i, w in enumerate(weeks) if w.year == 2019 and w.month == 7), 0)
    week = st.select_slider("Week", options=weeks, value=weeks[default])
    w = preds[preds.week.dt.date == week].copy()
    w["flagged"] = w.flagged == 1
    w["Flagged"] = w.flagged.map({True: "yes", False: "no"})
    w["Risk"] = w.logreg_score.round(2)
    w["Outbreak in next 2-4 weeks"] = w.label.map({1: "yes", 0: "no"})

    c1, c2 = st.columns([3, 2])
    fig = px.scatter_map(w, lat="lat", lon="lon", color="Risk", size="Risk",
                         color_continuous_scale="YlOrRd", zoom=3.6,
                         center={"lat": 22.5, "lon": 80}, height=620,
                         hover_name="district",
                         hover_data={"state": True, "Risk": True, "lat": False, "lon": False,
                                     "Flagged": True, "Outbreak in next 2-4 weeks": True})
    c1.plotly_chart(fig, width="stretch")

    c2.metric("Districts flagged", int(w.flagged.sum()))
    caught = int((w.flagged & (w.label == 1)).sum())
    c2.metric("Real outbreaks caught / total", f"{caught} / {int(w.label.sum())}")
    c2.write("Highest risk districts this week")
    c2.dataframe(w.sort_values("logreg_score", ascending=False)
                 [["district", "state", "Risk", "Flagged", "Outbreak in next 2-4 weeks"]].head(15),
                 hide_index=True, width="stretch")
