import subprocess, sys, time, os
import sys
sys.stdout.reconfigure(encoding='utf-8')

steps = [
    ("Step 0 · Generating datasets",         [sys.executable, "data/generate_dataset.py"]),
    ("Step 1 · EDA Analysis",                 [sys.executable, "part1_eda.py"]),
    ("Step 2 · Deep Dive Analysis",           [sys.executable, "part2_deep_dive.py"]),
    ("Step 3 · Hypothesis Testing",           [sys.executable, "part3_hypothesis.py"]),
    ("Step 4 · Building PowerPoint",          [sys.executable, "build_presentation.py"]),
]

print("\n" + "="*58)
print("  DATA STORYTELLING & STATISTICAL VALIDATION PIPELINE")
print("="*58)

os.makedirs('reports/figures', exist_ok=True)

for label, cmd in steps:
    print(f"\n▶  {label} ...")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=False)
    if r.returncode != 0:
        print(f"\n  ❌ FAILED at: {' '.join(cmd)}")
        sys.exit(1)
    print(f"   ✓  Done in {time.time()-t0:.1f}s")

print("\n" + "="*58)
print("  ✅  ALL STEPS COMPLETE")
print("="*58)
print("""
  Output files:
  ┌─────────────────────────────────────────────────────┐
  │  data/ab_test_results.csv          → A/B test data  │
  │  data/monthly_sales.csv            → Sales data     │
  │  data/customer_segments.csv        → Customer data  │
  │  reports/figures/part1_eda.png     → EDA charts     │
  │  reports/figures/part2_deep_dive.png                │
  │  reports/figures/part3_hypothesis.png               │
  │  reports/hypothesis_summary.json  → Stats results   │
  │  reports/Data_Storytelling_Presentation.pptx  ★     │
  └─────────────────────────────────────────────────────┘
  ★  Open the .pptx in PowerPoint or LibreOffice Impress
""")
