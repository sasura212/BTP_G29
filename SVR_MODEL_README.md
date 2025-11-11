# Support Vector Regression (SVR) Model Implementation

## Overview
This document describes the Support Vector Regression (SVR) implementation for predicting optimal TPS parameters in DAB converters. The SVR models complement the existing Random Forest approach, providing an alternative machine learning method for real-time control parameter prediction.

---

## Model Architecture

### Algorithm Details
- **Algorithm**: Support Vector Regression (SVR)
- **Kernel**: Radial Basis Function (RBF)
- **Hyperparameters**:
  - C = 100 (regularization parameter)
  - gamma = 0.1 (kernel coefficient)
  - epsilon = 0.001 (epsilon-tube tolerance)

### Multi-Output Approach
Unlike Random Forest which supports native multi-output regression, SVR requires separate models for each output:
- **svr_model_D0.pkl**: Predicts D₀ (external phase shift)
- **svr_model_D1.pkl**: Predicts D₁ (primary internal phase shift)
- **svr_model_D2.pkl**: Predicts D₂ (secondary internal phase shift)
- **svr_model_Irms_A.pkl**: Predicts minimum RMS current

### Feature Scaling
SVR is sensitive to feature scales, requiring standardization:
- **svr_scaler.pkl**: StandardScaler fitted on training data
- Transforms power input to zero mean and unit variance
- **Critical**: Must apply same scaler to new predictions

---

## Performance Comparison

### SVR Model Performance

| Output | Train R² | Test R² | MAE | RMSE |
|--------|----------|---------|-----|------|
| D₀ | 0.4131 | 0.4014 | 0.0538 | 0.0812 |
| D₁ | -0.0664 | -0.2044 | 0.0897 | 0.2561 |
| D₂ | **0.8972** | **0.9297** | 0.0395 | 0.0740 |
| **Irms** | **0.9912** | **0.9859** | 0.3865 | 0.6680 |
| **Average** | 0.5588 | 0.5281 | - | - |

### Random Forest Performance (for comparison)

| Output | Train R² | Test R² | MAE | RMSE |
|--------|----------|---------|-----|------|
| D₀ | 0.9990 | 0.6860 | 0.0420 | 0.0660 |
| D₁ | 0.9970 | -0.2620 | 0.1500 | 0.2140 |
| D₂ | 0.9990 | 0.5890 | 0.0520 | 0.0750 |
| **Irms** | **1.0000** | **0.9850** | 0.3140 | 0.6940 |
| **Average** | 0.9970 | 0.5190 | - | - |

---

## Key Findings

### ✅ Strengths of SVR

1. **Excellent Irms Prediction**
   - Test R² = 0.9859 (comparable to Random Forest's 0.9850)
   - Critical for loss minimization and efficiency optimization
   - MAE = 0.39A across 100-1000W range

2. **Superior D₂ Prediction**
   - Test R² = 0.9297 (vs Random Forest's 0.5890)
   - 57.8% improvement in generalization
   - Better captures non-linear relationships for secondary phase shift

3. **No Overfitting for Irms and D₂**
   - Train and test R² values are close
   - Indicates good generalization capability
   - More robust to unseen power levels

4. **Smaller Model Size**
   - Total SVR models: ~13 KB (4 models + scaler)
   - Random Forest: 2.6 MB
   - 200× smaller footprint for embedded systems

### ⚠️ Limitations of SVR

1. **D₁ Prediction Challenges**
   - Negative Test R² (-0.2044) indicates poor performance
   - Similar issue as Random Forest (-0.2620)
   - Both models struggle with discrete mode transitions affecting D₁

2. **D₀ Moderate Performance**
   - Test R² = 0.4014 (vs Random Forest's 0.6860)
   - Lower accuracy compared to Random Forest
   - May require hyperparameter tuning or kernel modification

3. **Computational Overhead**
   - Requires feature scaling (additional step)
   - Four separate models vs one Random Forest
   - More complex deployment pipeline

---

## Usage Instructions

### Training the SVR Models

```bash
# Train all SVR models
python3 train_tps_svr.py
```

**Output Files:**
- `svr_model_D0.pkl`, `svr_model_D1.pkl`, `svr_model_D2.pkl`, `svr_model_Irms_A.pkl`
- `svr_scaler.pkl` (feature scaler)
- `svr_interpolated_lookup_table.csv` (100 interpolated points)
- `svr_predictions_vs_actual.png` (validation plots)
- `svr_power_trends.png` (parameter trends)

### Making Predictions (Python)

```python
import joblib
import numpy as np

# Load models and scaler
scaler = joblib.load('svr_scaler.pkl')
model_D0 = joblib.load('svr_model_D0.pkl')
model_D1 = joblib.load('svr_model_D1.pkl')
model_D2 = joblib.load('svr_model_D2.pkl')
model_Irms = joblib.load('svr_model_Irms_A.pkl')

# Predict for 500W
power = 500.0
power_scaled = scaler.transform([[power]])

D0_pred = model_D0.predict(power_scaled)[0]
D1_pred = model_D1.predict(power_scaled)[0]
D2_pred = model_D2.predict(power_scaled)[0]
Irms_pred = model_Irms.predict(power_scaled)[0]

print(f"Power: {power}W")
print(f"D0: {D0_pred:.4f}")
print(f"D1: {D1_pred:.4f}")
print(f"D2: {D2_pred:.4f}")
print(f"Irms: {Irms_pred:.2f}A")
```

### Using the Dashboard

The updated dashboard now supports both Random Forest and SVR models:

1. **Start the dashboard:**
   ```bash
   python3 -m streamlit run dashboard.py --server.port 8501
   ```

2. **Access**: Open browser to `http://localhost:8501`

3. **Select Model**: Use the radio buttons at the top to choose:
   - Random Forest
   - Support Vector Regression (SVR)

4. **Features**:
   - Real-time predictions from selected model
   - Side-by-side comparison with other model (if available)
   - Comparison with optimal lookup table
   - Interactive charts showing both model predictions and optimal data points

---

## Model Selection Guidelines

### Choose Random Forest When:
- ✅ D₀ prediction accuracy is critical
- ✅ Memory/storage is not constrained
- ✅ Single-model simplicity is preferred
- ✅ Slight overfitting is acceptable

### Choose SVR When:
- ✅ D₂ prediction accuracy is paramount
- ✅ Embedded system with limited memory
- ✅ Better generalization to unseen data is needed
- ✅ Model interpretability through kernel functions is desired

### For Production:
Consider **ensemble approach**:
- Use SVR for Irms and D₂ (higher test R²)
- Use Random Forest for D₀ (higher test R²)
- Averaging or weighted voting for D₁ (both models struggle)

---

## Technical Details

### Feature Engineering
- **Input**: Single feature (Power_Target_W)
- **Preprocessing**: StandardScaler normalization
- **Range**: 100W to 1000W
- **Resolution**: 10W steps in training data

### Training Dataset
- **Total Samples**: 91 optimal points
- **Train Split**: 72 samples (80%)
- **Test Split**: 19 samples (20%)
- **Random State**: 42 (reproducibility)
- **Source**: integrated_optimal_lookup_table.csv

### Kernel Function (RBF)
The RBF kernel maps data to infinite-dimensional space:

$$K(x, x') = \exp(-\gamma \|x - x'\|^2)$$

Where:
- γ = 0.1 (controls influence of single training example)
- Higher γ = more complex decision boundary
- Lower γ = smoother predictions

### Hyperparameter Selection
Current values (C=100, gamma=0.1, epsilon=0.001) were chosen based on:
- Cross-validation experiments
- Balance between bias and variance
- Computational efficiency

**Future Work**: Grid search or Bayesian optimization for optimal hyperparameters

---

## Visualization

### 1. Predictions vs Actual (svr_predictions_vs_actual.png)
Scatter plots comparing SVR predictions to actual optimal values for:
- D₀: Moderate correlation (R² = 0.40)
- D₁: Poor correlation (R² = -0.20)
- D₂: Excellent correlation (R² = 0.93) ⭐
- Irms: Excellent correlation (R² = 0.99) ⭐

### 2. Power Trends (svr_power_trends.png)
Line plots showing how each parameter varies with power:
- Blue line: SVR predictions (smooth interpolation)
- Red markers: Training data (91 optimal points)
- Reveals mode transitions and non-linear behavior

---

## Files Generated

| File | Size | Description |
|------|------|-------------|
| `svr_model_D0.pkl` | 3.3 KB | D₀ prediction model |
| `svr_model_D1.pkl` | 3.1 KB | D₁ prediction model |
| `svr_model_D2.pkl` | 3.2 KB | D₂ prediction model |
| `svr_model_Irms_A.pkl` | 3.3 KB | Irms prediction model |
| `svr_scaler.pkl` | 623 B | Feature scaler (StandardScaler) |
| `svr_interpolated_lookup_table.csv` | 9.3 KB | 100 interpolated predictions |
| `svr_predictions_vs_actual.png` | 224 KB | Validation plots |
| `svr_power_trends.png` | 235 KB | Parameter trends visualization |

**Total Size**: ~480 KB (vs 2.8 MB for Random Forest artifacts)

---

## Conclusion

The SVR implementation provides a valuable alternative to Random Forest for TPS parameter prediction:

**Key Achievements:**
1. ⭐ **Superior D₂ prediction**: 93% test R² (vs RF's 59%)
2. ⭐ **Excellent Irms accuracy**: 98.6% test R² (matches RF)
3. 💾 **Compact model size**: 200× smaller than Random Forest
4. 🎯 **Good generalization**: Less overfitting on Irms and D₂

**Future Improvements:**
- Hyperparameter optimization for D₀ and D₁
- Try alternative kernels (polynomial, sigmoid)
- Feature engineering (add V₁, V₂, L as inputs)
- Ensemble methods combining RF and SVR strengths

---

**Author**: Harshit Singh  
**Project**: BTP - DAB Converter Optimization  
**Institution**: IIT Roorkee  
**Date**: November 2025  
**Reference**: Based on Tong et al. (2016) TPS control framework
