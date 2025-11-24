# 🚀 Quick Start Guide

## For First-Time Users

### 1. Install Dependencies (30 seconds)
```bash
pip install -r config/requirements.txt
```

### 2. Run the Dashboard (Instant)
```bash
cd dashboard
streamlit run dashboard.py
```
→ Open browser at `http://localhost:8501`

**That's it!** All required files are already included.

---

## For Developers

### Option A: Use Existing Data & Models
All necessary files are already in the repository:
- ✅ Optimal lookup table: `data/integrated_optimal_lookup_table.csv`
- ✅ Trained models: `models/*.pkl`
- ✅ Interpolated datasets: `data/*_interpolated_lookup_table.csv`

Just run the dashboard (see above).

### Option B: Regenerate Everything
```bash
# This takes ~10-15 minutes
./regenerate_all.sh
```

This will:
1. Generate optimal lookup table (91 points)
2. Train Random Forest model
3. Train SVR models
4. Create interpolated datasets
5. Generate performance visualizations

---

## Common Tasks

### Run Optimization Only
```bash
python3 scripts/optimization/integrated_optimizer.py
```

### Train Machine Learning Models
```bash
# Random Forest
python3 scripts/machine_learning/train_tps_regressor.py

# SVR
python3 scripts/machine_learning/train_tps_svr.py
```

### Compile Final Report
```bash
cd docs
pdflatex final_report.tex
```

---

## Folder Structure at a Glance

```
config/         - Dependencies
dashboard/      - Web application
scripts/        - Python scripts
  ├── optimization/
  ├── machine_learning/
  └── modes/
data/           - CSV datasets
models/         - Trained ML models
figures/        - Visualizations
docs/           - Documentation
```

---

## Need Help?

- **Dashboard Guide:** `dashboard/README.md`
- **Detailed Organization:** `docs/PROJECT_ORGANIZATION.md`
- **Complete Analysis:** `docs/CODEBASE_SUMMARY.md`
- **Main README:** `README.md`

---

## System Requirements

- Python 3.8+
- 4GB RAM (for optimization)
- 100MB disk space

---

**Last Updated:** November 11, 2025
