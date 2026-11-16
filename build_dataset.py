"""Build the district-week dataset: water-borne outbreaks + IMD rainfall + features.

Inputs:
  data/epiclim.csv   IDSP outbreaks 2009-2022 with district coordinates (EpiClim, Zenodo 14580510)
  data/imd/rain/     IMD 0.25 deg daily rainfall grids, downloaded with imdlib
Output:
  data/panel.csv.gz  one row per district per week
"""
import os
import difflib
import re

import imdlib as imd
import numpy as np
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # paths below are relative to this folder

START_YEAR, END_YEAR = 2009, 2022
WATERBORNE = ["acute diarrhoeal disease", "cholera", "suspected cholera",
              "acute gastroenteritis", "gastroenteritis", "diarrhea"]
HEAVY_RAIN_MM = 64.5   # IMD definition of a heavy rain day


def week_start(dates):
    dates = pd.to_datetime(dates)
    return dates - pd.to_timedelta(dates.dt.weekday, unit="D")


def norm(name):
    return re.sub(r"[^a-z]", "", str(name).lower())


def load_outbreaks():
    df = pd.read_csv("data/epiclim.csv")
    df = df[df.Disease.str.lower().str.strip().isin(WATERBORNE)].copy()
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.mon, day=df.day), errors="coerce")
    df = df.dropna(subset=["date"])
    df["week"] = week_start(df.date)
    df["state"] = df.state_ut.str.strip()

    # same district is spelt differently across years (Pudukottai / Pudukkottai),
    # so merge names inside a state when they are very close
    df["dkey"] = df.district.map(norm)
    for state, g in df.groupby("state"):
        keys = g.dkey.value_counts().index.tolist()   # most common spelling first
        canon = []
        for k in keys:
            match = difflib.get_close_matches(k, canon, n=1, cutoff=0.85)
            if match:
                df.loc[(df.state == state) & (df.dkey == k), "dkey"] = match[0]
            else:
                canon.append(k)
    df["district_id"] = df.state + "|" + df.dkey
    return df


def district_table(ob):
    d = ob.groupby("district_id").agg(
        state=("state", "first"),
        district=("district", lambda s: s.value_counts().index[0]),
        lat=("Latitude", "median"),
        lon=("Longitude", "median"),
    ).reset_index()
    return d


def weekly_rainfall(districts):
    data = imd.open_data("rain", START_YEAR, END_YEAR, "yearwise", "data/imd")
    rain = data.get_xarray()["rain"]    # (time, lat, lon), mm/day
    rain = rain.where(rain >= 0)

    # nearest grid point that is on land (coastal districts can land on a sea cell)
    valid = rain.isel(time=200).notnull().values
    lat_i, lon_i = np.nonzero(valid)
    land_lat, land_lon = rain.lat.values[lat_i], rain.lon.values[lon_i]
    nearest = [np.argmin((land_lat - r.lat) ** 2 + (land_lon - r.lon) ** 2)
               for r in districts.itertuples()]

    values = rain.values[:, lat_i[nearest], lon_i[nearest]]   # (days, districts)
    daily = pd.DataFrame(values, index=pd.to_datetime(rain.time.values),
                         columns=districts.district_id.values)

    weeks = week_start(pd.Series(daily.index)).values
    total = daily.groupby(weeks).sum(min_count=1)
    heavy = (daily >= HEAVY_RAIN_MM).groupby(weeks).sum()

    out = total.stack().rename("rain_mm").to_frame()
    out["heavy_days"] = heavy.stack()
    out.index.names = ["week", "district_id"]
    return out.reset_index()


def add_features(panel):
    panel = panel.sort_values(["district_id", "week"]).reset_index(drop=True)
    g = panel.groupby("district_id")

    for lag in range(4):
        panel[f"rain_lag{lag}"] = g.rain_mm.shift(lag)
    panel["rain_4wk"] = g.rain_mm.transform(lambda s: s.rolling(4).sum())
    panel["heavy_days_2wk"] = g.heavy_days.transform(lambda s: s.rolling(2).sum())

    # how unusual this week's 4-week rain is for this district and time of year
    panel["woy"] = panel.week.dt.isocalendar().week.astype(int).clip(upper=52)
    # (normal taken from training years only, so test years don't leak in)
    normal = (panel[panel.week.dt.year <= 2017]
              .groupby(["district_id", "woy"]).rain_4wk.mean().rename("rain_4wk_normal"))
    panel = panel.merge(normal, on=["district_id", "woy"], how="left")
    panel["rain_4wk_anomaly"] = panel.rain_4wk - panel.rain_4wk_normal
    g = panel.groupby("district_id")

    # past outbreaks (only ones that had already started by this week)
    for w in (4, 13, 52):
        panel[f"outbreaks_past_{w}wk"] = g.outbreak.transform(lambda s: s.rolling(w, min_periods=1).sum())

    panel["woy_sin"] = np.sin(2 * np.pi * panel.woy / 52)
    panel["woy_cos"] = np.cos(2 * np.pi * panel.woy / 52)
    panel["monsoon"] = panel.week.dt.month.between(6, 9).astype(int)

    # label: does an outbreak start in week t+2, t+3 or t+4?
    future = pd.concat([g.outbreak.shift(-k) for k in (2, 3, 4)], axis=1)
    panel["label"] = (future.sum(axis=1, min_count=3) > 0).astype(float)
    panel.loc[future.isna().any(axis=1), "label"] = np.nan
    return panel


def main():
    ob = load_outbreaks()
    districts = district_table(ob)
    print(f"{len(ob)} water-borne outbreaks in {len(districts)} districts")

    rain = weekly_rainfall(districts)
    counts = ob.groupby(["district_id", "week"]).size().rename("n").reset_index()
    panel = rain.merge(counts, on=["district_id", "week"], how="left")
    panel["outbreak"] = (panel.n.fillna(0) > 0).astype(int)
    panel = panel.drop(columns="n").merge(districts, on="district_id")

    panel = add_features(panel)
    panel.to_csv("data/panel.csv.gz", index=False)
    districts.to_csv("data/districts.csv", index=False)
    print(f"panel: {len(panel)} rows, {panel.outbreak.sum()} outbreak weeks, "
          f"positive label rate {panel.label.mean():.3f}")


if __name__ == "__main__":
    main()
