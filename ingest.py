"""Extract the outbreak table from IDSP weekly outbreak report PDFs.

Usage: python ingest.py            (reads every PDF in data/idsp_pdfs/)
Output: data/idsp_parsed.csv
"""
import os
import re
from pathlib import Path

import pandas as pd
import pdfplumber

os.chdir(os.path.dirname(os.path.abspath(__file__)))  # paths below are relative to this folder

PDF_DIR = Path("data/idsp_pdfs")
OUT = Path("data/idsp_parsed.csv")

# every outbreak row starts with an ID like AP/KAK/2025/17/701
ROW_ID = re.compile(r"^[A-Z]{2}/[A-Z]{2,4}/\d{4}/\d{1,2}/\d+")
DATE = re.compile(r"^\d{2}-\d{2}-\d{4}$")


def clean(text):
    # narrow PDF columns break long words over lines ("Tiruchirappall\ni"),
    # so glue a short lowercase piece back onto the line before it
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    out = []
    for l in lines:
        if out and l.islower() and len(l) <= 4:
            out[-1] += l
        else:
            out.append(l)
    return " ".join(out)


def parse_row(cells):
    # pdfplumber gives each merged cell twice: the full text, then a cut-off
    # copy of its first line. Drop the copies and keep the full values.
    values = []
    for c in cells:
        if c is None or c.strip() == "":
            continue
        prev = values[-1] if values else ""
        if "\n" in prev and prev.startswith(c.strip()):
            continue
        values.append(c.strip())

    # cases is the first plain number after the ID
    num_idx = next(i for i, v in enumerate(values) if i > 0 and v.isdigit())
    text_cols = [clean(v) for v in values[1:num_idx]]
    dates = [v for v in values[num_idx:] if DATE.match(v)]
    return {
        "id": values[0],
        "state": text_cols[0],
        "district": text_cols[1],
        "disease": text_cols[2] if len(text_cols) > 2 else "",
        "cases": int(values[num_idx]),
        "deaths": int(values[num_idx + 1]) if values[num_idx + 1].isdigit() else 0,
        "date_of_start": dates[0] if dates else None,
        "date_of_reporting": dates[1] if len(dates) > 1 else None,
    }


def parse_pdf(path):
    rows = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for r in table:
                    if r and r[0] and ROW_ID.match(r[0].strip()):
                        try:
                            rows.append(parse_row(r))
                        except (StopIteration, IndexError):
                            print("  could not parse row:", r[0])
    return rows


def main():
    all_rows = []
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        rows = parse_pdf(pdf)
        print(f"{pdf.name}: {len(rows)} outbreaks")
        for r in rows:
            r["source_file"] = pdf.name
        all_rows += rows

    df = pd.DataFrame(all_rows)
    df.to_csv(OUT, index=False)
    print(f"saved {len(df)} rows to {OUT}")


if __name__ == "__main__":
    main()
