"""Train and evaluate the two baseline models.

Seasonal baseline: risk = how often this district had an outbreak in the
                   next 2-4 weeks at this time of year, in the training years.
Logistic regression: class-weighted, on rainfall + past outbreak + season features.

Split by year: train 2009-2017, validation 2018, test 2019. 2022 is also scored
as a second test year. 2020-21 left out (COVID). Each week the riskiest 20% of
districts are flagged (see evaluate.py).
"""
import json
import os
from pathlib import Path

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from evaluate import evaluate, flag_top

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # paths below are relative to this folder

FEATURES = [
    "rain_lag0", "rain_lag1", "rain_lag2", "rain_lag3", "rain_4wk",
    "rain_4wk_anomaly", "heavy_days_2wk",
    "outbreaks_past_4wk", "outbreaks_past_13wk", "outbreaks_past_52wk",
    "woy_sin", "woy_cos", "monsoon",
]


def main():
    df = pd.read_csv("data/panel.csv.gz", parse_dates=["week"])
    df = df.dropna(subset=["label"])
    df[FEATURES] = df[FEATURES].fillna(0)
    year = df.week.dt.year

    train = df[year <= 2017]
    val = df[year == 2018]
    tests = {"test_2019": df[year == 2019], "test_2022": df[year == 2022]}

    # seasonal baseline: outbreak rate for this district within +-2 weeks of this
    # time of year in the training years (smoothed so it isn't mostly zeros)
    rate = train.groupby(["district_id", "woy"]).label.mean().unstack(fill_value=0)
    rate = rate.reindex(columns=range(1, 53), fill_value=0)
    wrapped = pd.concat([rate.iloc[:, -2:], rate, rate.iloc[:, :2]], axis=1)
    smooth = wrapped.T.rolling(5, center=True).mean().T.iloc[:, 2:-2]
    smooth.columns = range(1, 53)
    seasonal = smooth.stack().rename("seasonal_score")
    seasonal.index.names = ["district_id", "woy"]
    # break ties with the district's overall outbreak rate
    overall = train.groupby("district_id").label.mean()
    seasonal = seasonal + 1e-3 * overall.reindex(seasonal.index.get_level_values(0)).values

    # logistic regression
    logreg = make_pipeline(StandardScaler(),
                           LogisticRegression(class_weight="balanced", max_iter=2000))
    logreg.fit(train[FEATURES], train.label)

    def score(part):
        part = part.join(seasonal, on=["district_id", "woy"])
        part["seasonal_score"] = part.seasonal_score.fillna(0)
        part["logreg_score"] = logreg.predict_proba(part[FEATURES])[:, 1]
        return part

    parts = {"val_2018": score(val), **{name: score(part) for name, part in tests.items()}}
    results = {"rows": {"train": len(train), "val": len(val)},
               "positive_rate_train": float(train.label.mean())}
    for model in ("seasonal", "logreg"):
        col = f"{model}_score"
        results[model] = {name: evaluate(part.label.values, part[col].values, part.week.values)
                          for name, part in parts.items()}
    for part in parts.values():
        part["flagged"] = flag_top(part.logreg_score.values, part.week.values)

    coefs = logreg.named_steps["logisticregression"].coef_[0]
    results["logreg_coefficients"] = dict(sorted(zip(FEATURES, map(float, coefs)),
                                                 key=lambda kv: -abs(kv[1])))

    Path("results").mkdir(exist_ok=True)
    Path("results/metrics.json").write_text(json.dumps(results, indent=2))
    keep = ["week", "district_id", "district", "state", "lat", "lon", "rain_4wk",
            "outbreaks_past_13wk", "label", "seasonal_score", "logreg_score", "flagged"]
    pd.concat(parts.values())[keep].to_csv("data/predictions.csv.gz", index=False)

    for model in ("seasonal", "logreg"):
        for split, m in results[model].items():
            print(f"{model:9s} {split:10s} recall {m['recall']:.2f}  precision {m['precision']:.3f}"
                  f"  f1 {m['f1']:.3f}  alerts {m['alert_rate']:.1%}  roc_auc {m['roc_auc']:.3f}"
                  f"  pr_auc {m['pr_auc']:.3f} (base rate {m['base_rate']:.3f})")


if __name__ == "__main__":
    main()
