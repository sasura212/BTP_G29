# Project Organization Guide

## 📁 Folder Structure Explanation

This document explains the reorganized folder structure and the purpose of each directory.

---

## Directory Layout

### `/config/`
**Purpose:** Configuration files and project dependencies

**Contents:**
- `requirements.txt` - Python package dependencies

**Usage:**
```bash
pip install -r config/requirements.txt
```

---

### `/dashboard/`
**Purpose:** Interactive web application for parameter prediction and model comparison

**Contents:**
- `dashboard.py` - Main Streamlit application
- `README.md` - Dashboard usage guide and troubleshooting

**Running:**
```bash
cd dashboard
python3 -m streamlit run dashboard.py
```

**Features:**
- Real-time parameter prediction
- Model selection (Random Forest vs SVR)
- Three-way comparison (RF vs SVR vs Optimal)
- Interactive visualizations
- System parameter display

---

### `/scripts/`
**Purpose:** All Python scripts for data generation, optimization, and ML training

#### `/scripts/optimization/`
**Contains:**
- `integrated_optimizer.py` ⭐ **RECOMMENDED** - Multi-mode grid-search optimizer
- `dataset_generator.py` - Fast SLSQP-based optimizer

**When to use:**
- **integrated_optimizer.py**: When you need globally optimal solutions (searches all modes)
- **dataset_generator.py**: When you need quick approximate solutions (< 1 second)

**Run:**
```bash
# Full optimization (91 points)
python3 scripts/optimization/integrated_optimizer.py

# Quick test (5 points)
python3 scripts/optimization/integrated_optimizer.py --test

# SLSQP method
python3 scripts/optimization/dataset_generator.py
```

#### `/scripts/machine_learning/`
**Contains:**
- `train_tps_regressor.py` - Random Forest model training
- `train_tps_svr.py` - Support Vector Regression model training

**When to use:**
- After generating optimal dataset
- When you want to retrain models with new data
- To evaluate model performance

**Run:**
```bash
python3 scripts/machine_learning/train_tps_regressor.py
python3 scripts/machine_learning/train_tps_svr.py
```

**Outputs:**
- Trained models (saved to `/models/`)
- Performance metrics (printed to console)
- Visualization plots (saved to `/figures/`)

#### `/scripts/modes/`
**Contains:**
- `mode1.py` through `mode6.py` - Individual mode dataset generators

**Purpose:**
- Educational: Understand each mode's characteristics
- Debugging: Isolate issues in specific modes
- Research: Analyze mode-specific behavior

**Run:**
```bash
python3 scripts/modes/mode1.py  # Creates mode1_dataset.csv
```

**Note:** These are for educational purposes. Use `integrated_optimizer.py` for production datasets.

---

### `/data/`
**Purpose:** All CSV data files (input/output)

**Contents:**
- `integrated_optimal_lookup_table.csv` - **Primary dataset** (91 optimal points)
- `optimized_lookup_table_tps.csv` - SLSQP optimizer results
- `rf_interpolated_lookup_table.csv` - Random Forest predictions (100 points)
- `svr_interpolated_lookup_table.csv` - SVR predictions (100 points)

**File Format:**
```csv
Power_Target_W, D0, D1, D2, Irms_A, Power_Actual_W, Power_Error_W, Mode
100.0, 0.35, 0.12, 0.08, 0.86, 100.5, 0.5, 3
...
```

**Primary Dataset:** `integrated_optimal_lookup_table.csv`
- 91 power points (100W to 1000W in 10W steps)
- Contains globally optimal parameters for each power level
- Used for ML model training and dashboard reference

---

### `/models/`
**Purpose:** Trained machine learning models (binary files)

**Contents:**

**Random Forest:**
- `tps_rf_model.pkl` (2.6 MB) - Multi-output regressor for all 4 parameters

**SVR Models:**
- `svr_model_D0.pkl` (3.3 KB) - D₀ predictor
- `svr_model_D1.pkl` (3.1 KB) - D₁ predictor
- `svr_model_D2.pkl` (3.2 KB) - D₂ predictor
- `svr_model_Irms_A.pkl` (3.3 KB) - Irms predictor
- `svr_scaler.pkl` (623 B) - StandardScaler for feature normalization

**Loading Models:**
```python
import joblib

# Random Forest
rf_model = joblib.load('models/tps_rf_model.pkl')

# SVR
svr_scaler = joblib.load('models/svr_scaler.pkl')
svr_d2 = joblib.load('models/svr_model_D2.pkl')
```

---

### `/figures/`
**Purpose:** Visualization outputs (PNG format, 300 DPI)

**Contents:**
- `optimization_results.png` - Optimal duty cycles and Irms vs power
- `ml_comparison.png` - RF vs SVR scatter plots (4 subplots)
- `mode_distribution.png` - Bar chart showing mode distribution
- `rf_predictions_vs_actual.png` - RF validation plots
- `svr_predictions_vs_actual.png` - SVR validation plots
- `svr_power_trends.png` - SVR parameter trends

**Usage:**
- Include in reports/presentations
- Visual verification of model performance
- Mode distribution analysis

---

### `/docs/`
**Purpose:** All documentation, reports, and technical notes

**Contents:**

**Main Documentation:**
- `README.md` - Original project README
- `final_report.tex` - IEEE format final report (LaTeX)
- `report.tex` - Mid-term report

**Technical Summaries:**
- `INTEGRATION_COMPLETE.md` - Mode 5 integration overview
- `MODE5_INTEGRATION_SUMMARY.md` - Detailed Mode 5 technical notes
- `MODE5_QUICK_REF.md` - Quick reference for Mode 5
- `SVR_IMPLEMENTATION_SUMMARY.md` - SVR implementation details
- `SVR_MODEL_README.md` - SVR model guide

**Guides:**
- `REQUIRED_FIGURES.md` - Figure generation instructions
- `optimization_log.txt` - Optimization run logs

**Compiling Report:**
```bash
cd docs
pdflatex final_report.tex
```

---

### `/src/`
**Purpose:** Python package source code (currently minimal)

**Contents:**
- `__init__.py` - Package initialization

**Future Use:**
- Shared utility functions
- Common constants/configurations
- Reusable modules

---

## 🔄 Typical Workflow

### 1. Initial Setup
```bash
# Install dependencies
pip install -r config/requirements.txt
```

### 2. Generate Optimal Dataset
```bash
# Run multi-mode optimization (recommended)
python3 scripts/optimization/integrated_optimizer.py

# Output: data/integrated_optimal_lookup_table.csv
```

### 3. Train Machine Learning Models
```bash
# Train Random Forest
python3 scripts/machine_learning/train_tps_regressor.py

# Train SVR
python3 scripts/machine_learning/train_tps_svr.py

# Output: models/*.pkl, figures/*.png
```

### 4. Run Dashboard
```bash
# Start web application
cd dashboard
python3 -m streamlit run dashboard.py

# Access at http://localhost:8501
```

### 5. Generate Report Figures
```bash
# See docs/REQUIRED_FIGURES.md for instructions
cd docs
# Follow figure generation scripts
```

### 6. Compile Final Report
```bash
cd docs
pdflatex final_report.tex
```

---

## 📋 File Dependencies

### Dashboard Dependencies
The dashboard requires:
- `models/tps_rf_model.pkl` (RF model)
- `models/svr_model_*.pkl` (SVR models)
- `models/svr_scaler.pkl` (SVR scaler)
- `data/integrated_optimal_lookup_table.csv` (reference data)
- `data/rf_interpolated_lookup_table.csv` (RF predictions)
- `data/svr_interpolated_lookup_table.csv` (SVR predictions)

**Generate these first:**
```bash
python3 scripts/optimization/integrated_optimizer.py
python3 scripts/machine_learning/train_tps_regressor.py
python3 scripts/machine_learning/train_tps_svr.py
```

### Report Dependencies
The LaTeX report requires:
- `figures/*.png` (all visualization figures)
- Generate figures using scripts in `docs/REQUIRED_FIGURES.md`

---

## 🧹 Cleaning Up

### Remove Generated Files
```bash
# Remove all generated data
rm data/*.csv

# Remove all models
rm models/*.pkl

# Remove all figures
rm figures/*.png

# Remove LaTeX auxiliary files
cd docs
rm *.aux *.log *.out *.toc *.bbl *.blg
```

### Regenerate Everything
```bash
# 1. Generate optimal dataset
python3 scripts/optimization/integrated_optimizer.py

# 2. Train both ML models
python3 scripts/machine_learning/train_tps_regressor.py
python3 scripts/machine_learning/train_tps_svr.py

# 3. Generate report figures
# (See docs/REQUIRED_FIGURES.md)

# 4. Compile report
cd docs
pdflatex final_report.tex
```

---

## 🎯 Quick Reference

| Task | Command | Output |
|------|---------|--------|
| Install dependencies | `pip install -r config/requirements.txt` | - |
| Generate optimal data | `python3 scripts/optimization/integrated_optimizer.py` | `data/*.csv` |
| Train Random Forest | `python3 scripts/machine_learning/train_tps_regressor.py` | `models/tps_rf_model.pkl` |
| Train SVR | `python3 scripts/machine_learning/train_tps_svr.py` | `models/svr_model_*.pkl` |
| Run dashboard | `cd dashboard && streamlit run dashboard.py` | Web UI @ :8501 |
| Compile report | `cd docs && pdflatex final_report.tex` | `final_report.pdf` |

---

## 💡 Tips

1. **Always run optimization before ML training** - ML models need the optimal dataset
2. **Check data/ folder before running dashboard** - Ensure all CSV files exist
3. **Use integrated_optimizer.py for final results** - It finds global optimum across all modes
4. **SVR models need proper scaling** - The scaler.pkl file is critical for SVR predictions
5. **Dashboard auto-loads models** - Just ensure files are in correct locations

---

## 🐛 Troubleshooting

### "FileNotFoundError: tps_rf_model.pkl"
```bash
# Solution: Train the model first
python3 scripts/machine_learning/train_tps_regressor.py
```

### "FileNotFoundError: integrated_optimal_lookup_table.csv"
```bash
# Solution: Run optimization first
python3 scripts/optimization/integrated_optimizer.py
```

### "Dashboard shows no data"
```bash
# Solution: Ensure all required files exist
ls data/integrated_optimal_lookup_table.csv
ls models/tps_rf_model.pkl
ls models/svr_scaler.pkl
```

### "Import errors in scripts"
```bash
# Solution: Install dependencies
pip install -r config/requirements.txt
```

---

**Last Updated:** November 11, 2025
