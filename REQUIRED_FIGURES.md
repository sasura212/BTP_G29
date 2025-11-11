# Required Figures for Final Report

This document lists all the figure placeholders in `final_report.tex` and what content should be included in each.

---

## Figure 1: Circuit Diagram (Already Exists)
**Filename:** `simulink_model.png`  
**Label:** `fig_dab`  
**Caption:** "Circuit Diagram of a Dual Active Bridge (DAB) Converter."

**Content:** 
- Already exists in your files
- Shows the DAB circuit with two H-bridges, transformer, and series inductor

**Status:** ✅ Ready

---

## Figure 2: Optimization Results ⚠️ NEW
**Filename:** `optimization_results.png`  
**Label:** `fig_optimization`  
**Caption:** "Optimal duty cycles and Irms vs power across all operating modes. The fine grid resolution captures mode transitions and achieves consistent power accuracy <2W."

**Required Content:**
1. **Top subplot:** D0, D1, D2 vs Power (100-1000W)
   - Three lines showing how duty cycles vary with power
   - Color-coded for each parameter
   - Show mode transitions (different regions)
   
2. **Bottom subplot:** Irms vs Power
   - Show the non-linear increase from 0.086A @ 100W to ~22A @ 1000W
   - Highlight mode regions with different colors/shading

**How to Generate:**
```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('integrated_optimal_lookup_table.csv')

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

# Top: Duty cycles
ax1.plot(df['Power_Target_W'], df['D0'], 'b-', label='D₀', linewidth=2)
ax1.plot(df['Power_Target_W'], df['D1'], 'g-', label='D₁', linewidth=2)
ax1.plot(df['Power_Target_W'], df['D2'], 'r-', label='D₂', linewidth=2)
ax1.set_xlabel('Power (W)')
ax1.set_ylabel('Duty Cycle')
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.set_title('Optimal Duty Cycles vs Power')

# Bottom: Irms
ax2.plot(df['Power_Target_W'], df['Irms_A'], 'purple', linewidth=2.5)
ax2.set_xlabel('Power (W)')
ax2.set_ylabel('Irms (A)')
ax2.grid(True, alpha=0.3)
ax2.set_title('Minimum RMS Current vs Power')

plt.tight_layout()
plt.savefig('optimization_results.png', dpi=300, bbox_inches='tight')
```

---

## Figure 3: ML Comparison ⚠️ NEW
**Filename:** `ml_comparison.png`  
**Label:** `fig_ml_comparison`  
**Caption:** "Predicted vs actual values for both Random Forest and SVR models. SVR shows superior D₂ correlation while both excel at Irms prediction."

**Required Content:**
2×2 subplot grid showing scatter plots:
- **Row 1:** D0 predictions (RF vs SVR)
- **Row 2:** D2 predictions (RF vs SVR)
- Each subplot: predicted vs actual with perfect prediction line
- Annotate with R² values

**How to Generate:**
```python
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import joblib

# Load data
df = pd.read_csv('integrated_optimal_lookup_table.csv')
rf_model = joblib.load('tps_rf_model.pkl')
svr_scaler = joblib.load('svr_scaler.pkl')
svr_d0 = joblib.load('svr_model_D0.pkl')
svr_d2 = joblib.load('svr_model_D2.pkl')

# Predictions
X = df[['Power_Target_W']].values
X_scaled = svr_scaler.transform(X)
rf_pred = rf_model.predict(X)
svr_d0_pred = svr_d0.predict(X_scaled)
svr_d2_pred = svr_d2.predict(X_scaled)

fig, axes = plt.subplots(2, 2, figsize=(10, 10))

# D0 - RF
axes[0,0].scatter(df['D0'], rf_pred[:,0], alpha=0.6, s=50)
axes[0,0].plot([0,1], [0,1], 'r--', lw=2)
axes[0,0].set_title('D₀: Random Forest (R²=0.686)')
axes[0,0].set_xlabel('Actual D₀')
axes[0,0].set_ylabel('Predicted D₀')
axes[0,0].grid(True, alpha=0.3)

# D0 - SVR
axes[0,1].scatter(df['D0'], svr_d0_pred, alpha=0.6, s=50, color='green')
axes[0,1].plot([0,1], [0,1], 'r--', lw=2)
axes[0,1].set_title('D₀: SVR (R²=0.401)')
axes[0,1].set_xlabel('Actual D₀')
axes[0,1].set_ylabel('Predicted D₀')
axes[0,1].grid(True, alpha=0.3)

# D2 - RF
axes[1,0].scatter(df['D2'], rf_pred[:,2], alpha=0.6, s=50)
axes[1,0].plot([0,1], [0,1], 'r--', lw=2)
axes[1,0].set_title('D₂: Random Forest (R²=0.589)')
axes[1,0].set_xlabel('Actual D₂')
axes[1,0].set_ylabel('Predicted D₂')
axes[1,0].grid(True, alpha=0.3)

# D2 - SVR
axes[1,1].scatter(df['D2'], svr_d2_pred, alpha=0.6, s=50, color='green')
axes[1,1].plot([0,1], [0,1], 'r--', lw=2)
axes[1,1].set_title('D₂: SVR (R²=0.930) ⭐')
axes[1,1].set_xlabel('Actual D₂')
axes[1,1].set_ylabel('Predicted D₂')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('ml_comparison.png', dpi=300, bbox_inches='tight')
```

---

## Figure 4: Dashboard Screenshot ⚠️ NEW
**Filename:** `dashboard_screenshot.png`  
**Label:** `fig_dashboard`  
**Caption:** "Dashboard interface showing model selection, three-way comparison table, and interactive parameter trend visualizations. Users can switch between RF and SVR in real-time."

**Required Content:**
Screenshot of the actual dashboard showing:
1. Model selection radio buttons (top)
2. Power input slider
3. Three-way comparison table
4. Interactive charts

**How to Generate:**
1. Make sure dashboard is running: `python3 -m streamlit run dashboard.py`
2. Open browser at `http://localhost:8501`
3. Select a power value (e.g., 500W)
4. Take screenshot showing full interface
5. Crop to remove browser chrome
6. Save as `dashboard_screenshot.png`

**Alternative (if screenshot not available):**
Create a mockup diagram showing the dashboard layout with labeled components.

---

## Figure 5: Future Architecture ⚠️ NEW
**Filename:** `future_architecture.png`  
**Label:** `fig_future`  
**Caption:** "Proposed hybrid architecture combining RF and SVR strengths with mode classification layer for improved D₁ prediction."

**Required Content:**
Block diagram showing:
```
Input (Power) 
    ↓
┌───────────────────────┐
│  Mode Classifier      │
│  (Neural Network)     │
└───────────┬───────────┘
            ↓
    Mode Information
            ↓
┌───────────────────────────────────────┐
│  Hybrid Parameter Predictor           │
│  • RF Model → D₀ (best R²)            │
│  • SVR Model → D₂, Irms (best R²)     │
│  • Mode-Specific Regressor → D₁       │
└───────────┬───────────────────────────┘
            ↓
    D₀, D₁, D₂, Irms
```

**How to Generate:**
Create a simple block diagram using:
- PowerPoint/Keynote
- draw.io
- TikZ (LaTeX)
- Python matplotlib with boxes and arrows

---

## Summary Checklist

- [x] **Figure 1:** Circuit diagram (simulink_model.png) - Already exists
- [ ] **Figure 2:** Optimization results (optimization_results.png) - CREATE THIS
- [ ] **Figure 3:** ML comparison (ml_comparison.png) - CREATE THIS
- [ ] **Figure 4:** Dashboard screenshot (dashboard_screenshot.png) - SCREENSHOT
- [ ] **Figure 5:** Future architecture (future_architecture.png) - CREATE DIAGRAM

---

## Quick Generation Script

Run this to generate Figures 2 and 3:

```bash
cd /workspaces/BTP_G29
python3 << 'EOF'
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import joblib

# Load data
df = pd.read_csv('integrated_optimal_lookup_table.csv')

# ========== FIGURE 2: Optimization Results ==========
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

# Top: Duty cycles
ax1.plot(df['Power_Target_W'], df['D0'], 'b-', label='D₀', linewidth=2)
ax1.plot(df['Power_Target_W'], df['D1'], 'g-', label='D₁', linewidth=2)
ax1.plot(df['Power_Target_W'], df['D2'], 'r-', label='D₂', linewidth=2)
ax1.set_xlabel('Power (W)', fontsize=11)
ax1.set_ylabel('Duty Cycle', fontsize=11)
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_title('Optimal Duty Cycles vs Power', fontsize=12, fontweight='bold')

# Bottom: Irms
ax2.plot(df['Power_Target_W'], df['Irms_A'], 'purple', linewidth=2.5)
ax2.set_xlabel('Power (W)', fontsize=11)
ax2.set_ylabel('Irms (A)', fontsize=11)
ax2.grid(True, alpha=0.3)
ax2.set_title('Minimum RMS Current vs Power', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('optimization_results.png', dpi=300, bbox_inches='tight')
print("✓ Created: optimization_results.png")

# ========== FIGURE 3: ML Comparison ==========
rf_model = joblib.load('tps_rf_model.pkl')
svr_scaler = joblib.load('svr_scaler.pkl')
svr_d0 = joblib.load('svr_model_D0.pkl')
svr_d2 = joblib.load('svr_model_D2.pkl')

X = df[['Power_Target_W']].values
X_scaled = svr_scaler.transform(X)
rf_pred = rf_model.predict(X)
svr_d0_pred = svr_d0.predict(X_scaled)
svr_d2_pred = svr_d2.predict(X_scaled)

fig, axes = plt.subplots(2, 2, figsize=(10, 10))

# D0 - RF
axes[0,0].scatter(df['D0'], rf_pred[:,0], alpha=0.6, s=40, edgecolors='black', linewidth=0.5)
axes[0,0].plot([0,1], [0,1], 'r--', lw=2)
axes[0,0].set_title('D₀: Random Forest (R²=0.686)', fontsize=11, fontweight='bold')
axes[0,0].set_xlabel('Actual D₀', fontsize=10)
axes[0,0].set_ylabel('Predicted D₀', fontsize=10)
axes[0,0].grid(True, alpha=0.3)

# D0 - SVR
axes[0,1].scatter(df['D0'], svr_d0_pred, alpha=0.6, s=40, color='green', edgecolors='black', linewidth=0.5)
axes[0,1].plot([0,1], [0,1], 'r--', lw=2)
axes[0,1].set_title('D₀: SVR (R²=0.401)', fontsize=11, fontweight='bold')
axes[0,1].set_xlabel('Actual D₀', fontsize=10)
axes[0,1].set_ylabel('Predicted D₀', fontsize=10)
axes[0,1].grid(True, alpha=0.3)

# D2 - RF
axes[1,0].scatter(df['D2'], rf_pred[:,2], alpha=0.6, s=40, edgecolors='black', linewidth=0.5)
axes[1,0].plot([0,1], [0,1], 'r--', lw=2)
axes[1,0].set_title('D₂: Random Forest (R²=0.589)', fontsize=11, fontweight='bold')
axes[1,0].set_xlabel('Actual D₂', fontsize=10)
axes[1,0].set_ylabel('Predicted D₂', fontsize=10)
axes[1,0].grid(True, alpha=0.3)

# D2 - SVR
axes[1,1].scatter(df['D2'], svr_d2_pred, alpha=0.6, s=40, color='green', edgecolors='black', linewidth=0.5)
axes[1,1].plot([0,1], [0,1], 'r--', lw=2)
axes[1,1].set_title('D₂: SVR (R²=0.930) ⭐', fontsize=11, fontweight='bold')
axes[1,1].set_xlabel('Actual D₂', fontsize=10)
axes[1,1].set_ylabel('Predicted D₂', fontsize=10)
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('ml_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Created: ml_comparison.png")

print("\n✅ All figures generated successfully!")
EOF
```

---

## Notes

- All figures should be at least 300 DPI for publication quality
- Use consistent fonts and colors across all figures
- Include grid lines for readability
- Label axes clearly with units
- Use bold/larger fonts for titles
- Save as PNG format (or EPS for LaTeX if preferred)
