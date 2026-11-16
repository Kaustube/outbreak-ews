"""Metrics used to compare all models (baselines now, GBM and LSTM in M3)."""
import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, confusion_matrix, f1_score,
                             precision_score, recall_score, roc_auc_score)

ALERT_RATE = 0.20   # each week, flag the riskiest 20% of districts


def flag_top(scores, weeks, alert_rate=ALERT_RATE):
    """1 for the districts ranked in the top alert_rate within their own week."""
    rank = pd.Series(scores).groupby(np.asarray(weeks)).rank(ascending=False, method="first", pct=True)
    return (rank <= alert_rate).astype(int).values


def evaluate(y_true, scores, weeks):
    pred = flag_top(scores, weeks)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "recall": recall_score(y_true, pred, zero_division=0),
        "precision": precision_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, scores),
        "pr_auc": average_precision_score(y_true, scores),
        "base_rate": float(np.mean(y_true)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "alert_rate": float(pred.mean()),
    }
