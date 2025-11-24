# DAB Triple Phase Shift (TPS) Optimization Project

## 📋 Project Overview

This project implements optimal control parameter selection for **Dual Active Bridge (DAB) converters** using **Triple Phase Shift (TPS) modulation** for electric vehicle charging applications. It combines analytical optimization methods with machine learning to predict optimal control parameters across variable load conditions (100-1000W).

### Key Features
- ✅ Multi-mode analytical optimization (6 operating modes)
- ✅ Dual machine learning models (Random Forest & SVR)
- ✅ Interactive web dashboard with model comparison
- ✅ Comprehensive dataset generation and validation
- ✅ Real-time parameter prediction

---

## 🏗️ Project Structure

```
BTP_G29/
├── config/
│   └── requirements.txt           # Python dependencies
│
├── dashboard/
│   ├── dashboard.py              # Streamlit web application
│   └── README.md                 # Dashboard usage guide
│
├── scripts/
│   ├── optimization/
│   │   ├── dataset_generator.py  # SLSQP optimization approach
│   │   └── integrated_optimizer.py  # Multi-mode grid-search ⭐ (Recommended)
│   │
│   ├── machine_learning/
│   │   ├── train_tps_regressor.py   # Random Forest training
│   │   └── train_tps_svr.py         # SVR training
│   │
│   └── modes/
│       ├── mode1.py              # Mode 1 dataset generator
│       ├── mode2.py              # Mode 2 dataset generator
│       ├── mode3.py              # Mode 3 dataset generator
│       ├── mode4.py              # Mode 4 dataset generator
│       ├── mode5.py              # Mode 5 dataset generator
│       └── mode6.py              # Mode 6 dataset generator
│
├── data/
│   ├── integrated_optimal_lookup_table.csv    # Optimal parameters (91 points)
│   ├── optimized_lookup_table_tps.csv         # SLSQP results
│   ├── rf_interpolated_lookup_table.csv       # RF model predictions
│   └── svr_interpolated_lookup_table.csv      # SVR model predictions
│
├── models/
│   ├── tps_rf_model.pkl          # Random Forest model (2.6 MB)
│   ├── svr_model_D0.pkl          # SVR model for D0
│   ├── svr_model_D1.pkl          # SVR model for D1
│   ├── svr_model_D2.pkl          # SVR model for D2
│   ├── svr_model_Irms_A.pkl      # SVR model for Irms
│   └── svr_scaler.pkl            # Feature scaler for SVR
│
├── figures/
│   ├── optimization_results.png  # Optimal parameters visualization
│   ├── ml_comparison.png         # RF vs SVR comparison
│   ├── mode_distribution.png     # Mode distribution chart
│   ├── rf_predictions_vs_actual.png
│   └── svr_predictions_vs_actual.png
│
├── docs/
│   ├── README.md                 # Original project README
│   ├── final_report.tex          # IEEE format final report
│   ├── report.tex                # Mid-term report
│   ├── INTEGRATION_COMPLETE.md   # Mode 5 integration notes
│   ├── MODE5_INTEGRATION_SUMMARY.md
│   ├── MODE5_QUICK_REF.md
│   ├── SVR_IMPLEMENTATION_SUMMARY.md
│   ├── SVR_MODEL_README.md
│   ├── REQUIRED_FIGURES.md
│   └── optimization_log.txt
│
└── src/
    └── __init__.py
```

---

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r config/requirements.txt
```

### 2. Generate Optimal Dataset

**Recommended: Multi-mode Grid Search** (Finds global optimum)
```bash
# Full optimization (91 points, ~10 minutes)
python3 scripts/optimization/integrated_optimizer.py

# Quick test (5 points)
python3 scripts/optimization/integrated_optimizer.py --test
```

**Alternative: Fast SLSQP Optimizer** (< 1 second)
```bash
python3 scripts/optimization/dataset_generator.py
```

### 3. Train Machine Learning Models

**Random Forest (Recommended for D0 and Irms)**
```bash
python3 scripts/machine_learning/train_tps_regressor.py
```

**Support Vector Regression (Recommended for D2)**
```bash
python3 scripts/machine_learning/train_tps_svr.py
```

### 4. Run Interactive Dashboard

```bash
cd dashboard
python3 -m streamlit run dashboard.py
```

Then open your browser at `http://localhost:8501`

---

## 📊 System Specifications

| Parameter | Value |
|-----------|-------|
| Primary Voltage (V₁) | 200 V |
| Secondary Voltage (V₂) | 50 V |
| Inductance (L) | 20 µH |
| Switching Frequency (f) | 50 kHz |
| Half Period (T) | 10 µs |
| Power Range | 100 - 1000 W |
| Operating Modes | 1, 2, 3, 4, 5, 6 |

---

## 🎯 Operating Modes

Based on Tong et al. (2016) analytical methods:

| Mode | Constraints | Typical Power Range |
|------|------------|---------------------|
| 1 | D₁ < D₀, D₁ < D₀+D₂, D₀+D₂ < 1 | High (600-1000W) |
| 2 | D₁ < D₀, 1 < D₀+D₂ < 1+D₁ | Low-Medium |
| 3 | D₁ < D₀, 1+D₁ < D₀+D₂ < 2 | Low (100-200W) |
| 4 | D₀ < D₁, 0 < D₀+D₂ < D₁ | Medium |
| 5 | D₀ < D₁, D₁ < D₀+D₂ < 1 | Medium (200-550W) |
| 6 | D₀ < D₁, 1 < D₀+D₂ < 1+D₁ | Low |

---

## 🤖 Machine Learning Performance

### Random Forest Model
- **Test R² (D₀):** 0.686 ⭐
- **Test R² (D₁):** -0.262
- **Test R² (D₂):** 0.589
- **Test R² (Irms):** 0.985 ⭐
- **Model Size:** 2.6 MB

### SVR Model
- **Test R² (D₀):** 0.401
- **Test R² (D₁):** -0.204
- **Test R² (D₂):** 0.930 ⭐ (+58% vs RF)
- **Test R² (Irms):** 0.986 ⭐
- **Model Size:** 13 KB (200× smaller)

### Recommendations
- Use **Random Forest** for D₀ prediction
- Use **SVR** for D₂ prediction (superior accuracy)
- Both models excel at Irms prediction
- SVR is better for embedded/edge deployment (compact size)

---

## 📈 Dataset Distribution

After Mode 5 integration, the optimal lookup table contains 91 points:

| Mode | Points | Percentage |
|------|--------|-----------|
| Mode 1 | 51 | 56% |
| Mode 5 | 28 | 31% |
| Mode 3 | 7 | 8% |
| Mode 6 | 3 | 3% |
| Mode 4 | 2 | 2% |

**Note:** Mode 2 is rarely optimal for this power range and system parameters.

---

## 🎓 Usage Examples

### Predict Parameters for Specific Power

**Using Random Forest:**
```python
import joblib
import numpy as np

# Load model
model = joblib.load('models/tps_rf_model.pkl')

# Predict for 500W
power = 500.0
prediction = model.predict([[power]])[0]

D0, D1, D2, Irms = prediction
print(f"D0: {D0:.4f}, D1: {D1:.4f}, D2: {D2:.4f}, Irms: {Irms:.2f}A")
```

**Using SVR:**
```python
import joblib
import numpy as np

# Load models and scaler
scaler = joblib.load('models/svr_scaler.pkl')
model_D2 = joblib.load('models/svr_model_D2.pkl')
model_Irms = joblib.load('models/svr_model_Irms_A.pkl')

# Predict for 500W
power = 500.0
power_scaled = scaler.transform([[power]])

D2_pred = model_D2.predict(power_scaled)[0]
Irms_pred = model_Irms.predict(power_scaled)[0]

print(f"D2: {D2_pred:.4f}, Irms: {Irms_pred:.2f}A")
```

---

## 📚 Documentation

- **Dashboard Guide:** `dashboard/README.md`
- **Final Report:** `docs/final_report.tex` (IEEE format)
- **Mode 5 Integration:** `docs/INTEGRATION_COMPLETE.md`
- **SVR Implementation:** `docs/SVR_IMPLEMENTATION_SUMMARY.md`
- **Figure Generation:** `docs/REQUIRED_FIGURES.md`

---

## 🔬 Research Background

This work is based on the analytical Triple Phase Shift modulation method presented in:

> **Tong et al. (2016)**, "Analytical Model for Triple Phase Shift Control for DAB Converters"

The project extends the analytical approach with:
1. Exhaustive multi-mode optimization
2. Machine learning-based parameter prediction
3. Interactive visualization and comparison tools

---

## 👥 Authors

- **Harshit Singh** - Department of Electrical Engineering, IIT Roorkee
- **Jatin Singal** - Department of Electrical Engineering, IIT Roorkee
- **Karthik Ayangar** - Department of Electrical Engineering, IIT Roorkee

**BTP Project, IIT Roorkee | November 2025**

---

## 📄 License

This project is part of academic research at IIT Roorkee.

---

## 🙏 Acknowledgments

- Prof. [Supervisor Name] - Project Supervisor
- Department of Electrical Engineering, IIT Roorkee
- Based on analytical methods by Tong et al. (2016)

---

## 📞 Contact

For questions or collaboration:
- Email: harshit_s@ee.iitr.ac.in
- GitHub: [Repository Link]

---

**Last Updated:** November 11, 2025
