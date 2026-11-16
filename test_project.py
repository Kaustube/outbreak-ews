"""Quick test to verify project is working"""
import os
import json
from pathlib import Path

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("OUTBREAK EWS PROJECT VERIFICATION")
print("=" * 60)

# Check data files
data_files = {
    "Training dataset": "data/panel.csv.gz",
    "Outbreak data": "data/epiclim.csv",
    "Districts": "data/districts.csv",
    "Predictions": "data/predictions.csv.gz",
    "Parsed IDSP": "data/idsp_parsed.csv",
}

print("\n1. DATA FILES:")
all_good = True
for name, path in data_files.items():
    exists = Path(path).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {name}: {path}")
    if not exists:
        all_good = False

# Check results
print("\n2. MODEL RESULTS:")
if Path("results/metrics.json").exists():
    print("  ✓ Model metrics exist")
    with open("results/metrics.json") as f:
        metrics = json.load(f)
    
    print("\n  Logistic Regression Performance:")
    for split, perf in metrics["logreg"].items():
        print(f"    {split:12s}: Recall={perf['recall']:.3f}, ROC-AUC={perf['roc_auc']:.3f}")
else:
    print("  ✗ Model metrics missing")
    all_good = False

# Check code files
print("\n3. CODE FILES:")
code_files = [
    "ingest.py",
    "build_dataset.py", 
    "baselines.py",
    "evaluate.py",
    "dashboard.py",
    "requirements.txt"
]
for fname in code_files:
    exists = Path(fname).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {fname}")
    if not exists:
        all_good = False

# Summary
print("\n" + "=" * 60)
if all_good:
    print("✓ PROJECT IS COMPLETE AND READY!")
    print("\nNext steps:")
    print("  1. Run dashboard: streamlit run dashboard.py")
    print("  2. Push to GitHub")
    print("  3. Ready for submission!")
else:
    print("✗ Some files are missing - check above")
print("=" * 60)
