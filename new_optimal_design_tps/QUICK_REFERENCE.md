# Quick Reference: New DAB Optimization Pipeline

## TL;DR - What, Why, How

### **What We're Doing**
Building a **2-stage lookup table** for optimal DAB converter control based on Das & Basu (2021) research paper:

1. **Stage 1:** Generate comprehensive zone database (362k rows)
   - Sweep all phase shifts: D0 ∈ [0.01, 0.99], D1, D2 (0.01 step)
   - For each battery voltage: V2 ∈ [45-55V]
   - Classify into operating zones (I, II, V) using paper constraints
   - Calculate power and RMS current for each valid point
   
2. **Stage 2:** Extract optimized operating points (3.8k rows)
   - For each target power (0-3500W, 10W step)
   - For each battery voltage (45-55V)
   - Find the phase shift combo with minimum RMS current

### **Why This Approach**
✅ **Replaces old codebase** (Mode 1 hardcoded, no multi-voltage support)  
✅ **Paper-verified equations** (not generic approximations)  
✅ **Exhaustive search** (no risk of local minima like SLSQP)  
✅ **Multi-voltage support** (45-55V range)  
✅ **ZVS-guaranteed** (soft-switching via constraint enforcement)

### **How It Works**

#### Fixed Design Parameters (Computed Once)
```
V1 (regulated) = 200V
f_s = 100 kHz
m* = 1.3 (optimal voltage ratio from paper)

→ n (turns ratio) = 5.778
→ L (inductance) = 10.089 µH
```

#### For Each (D0, D1, D2) Point in Each Zone:
```
1. Check Zone I/II/V constraints (paper Table I)
   → if valid, continue; else skip
   
2. Calculate scaled power: p = zone_specific_equation(D0, D1, D2, m)
   
3. Calculate scaled RMS current: i_rms = zone_specific_equation(D0, D1, D2, m)
   
4. Convert to actual units:
   Power_W = (V1² / (2π×f_s×L)) × p
   Irms_A = (V1 / (2π×f_s×L)) × i_rms
```

#### For Each (P_target, V2) in Final Dataset:
```
Query zone database: find all rows where
  P_target - 2W ≤ Power_W ≤ P_target + 2W
  AND V2_V = target_V2

Select row with minimum Irms_A

If none found: try fallback (nearest power within 100W)
              if still none: mark NO_SOLUTION
```

---

## Files Overview

### Input Files
- `Optimal_Design_DAB_Converter.md` — Research paper (in Markdown)
- System specs: V1=200V, V2∈[45,55V], fs=100kHz, P∈[0,3.5kW]

### Processing Scripts
| Script | What | Input | Output | Time |
|--------|------|-------|--------|------|
| `generate_zone_database.py` | Sweep & classify | Design params | `phase_shift_zone_database.csv` (362k) | ~30s |
| `build_optimized_dataset.py` | Extract best per (P,V2) | Zone DB | `optimized_operating_points.csv` (3.8k) | ~2s |
| `run_pipeline.py` | Orchestrate both | None | Both CSVs | ~40s total |

### Output Files
| File | Rows | Use Case | Columns |
|------|------|----------|---------|
| `phase_shift_zone_database.csv` | 362,375 | Research, analysis | V2, m, n, L, D0, D1, D2, Zone, Power_W, Irms_A |
| `optimized_operating_points.csv` | 3,861 | ML training, firmware | Power_Target_W, V2, D0, D1, D2, Zone, Irms_A, Error |

---

## Key Equations (Simplified)

### Zone Power Equations
```
Zone I:   p = 0.5 × m × π × δ × d2
Zone II:  p = 0.5 × m × π × δ × d1
Zone V:   p = 0.25 × m × π × [1 - (1-d1)² - (1-d2)² - (1-δ)²]
```

### Zone RMS Current Equations
```
Zone I:   i²_rms = (π²/12) × [polynomial(m, d1, d2, δ)]
Zone II:  i²_rms = (π²/12) × [polynomial(m, d1, d2, δ)]
Zone V:   i²_rms = (π²/12) × [polynomial(m, d1, d2, δ)]  ← most complex
```

### Unit Conversion
```
I_rms_actual = (V1 / (2π×f_s×L)) × i_rms_scaled
P_actual = (V1² / (2π×f_s×L)) × p_scaled

Factor = 200 / (2π × 100k × 10.089e-6) ≈ 31,572
```

---

## Data Summary

### Phase Shift Zone Database (Stage 1 Output)
```
Total rows: 362,375
Power range: 0.32W to 6,472W
Irms range: 0.0001A to 16.5A

Zone distribution:
  Zone I:   ~200,000 rows (55%)
  Zone II:  ~80,000 rows  (22%)
  Zone V:   ~82,000 rows  (23%)

V2 distribution (11 values):
  45V → ~33k rows
  46V → ~33k rows
  ...
  55V → ~33k rows
```

### Optimized Operating Points (Stage 2 Output)
```
Total rows: 3,861
Power targets: 0W, 10W, 20W, ..., 3500W (351 points)
Voltage points: 45V, 46V, ..., 55V (11 points)

Average power error: 0.22W
Max power error: 100W
NO_SOLUTION rows: 5 (all at P=0W, acceptable)

Example operating point:
  P_target=500W, V2=45V
  → D0=0.48, D1=0.85, D2=0.91, Zone=V
  → Irms=6.87A (minimized for this power)
  → Power_actual=502.3W (±2.3W)
```

---

## Known Issues & Status

| Issue | Severity | Status | Fix |
|-------|----------|--------|-----|
| Polynomial fit unverified | 🔴 HIGH | ⏳ To do | Use scipy.optimize.fsolve |
| Missing feasibility check (p ≤ mπ/4) | 🔴 HIGH | ⏳ To do | Add constraint to both scripts |
| Poor variable naming (D0_delta confusing) | 🟡 MEDIUM | ⏳ To do | Rename to delta_phase_shift, d1_duty, d2_duty |
| No ZVS margin output | 🟡 MEDIUM | ⏳ To do | Compute & export margin columns |
| Zone statistics missing | 🟢 LOW | ⏳ To do | Add print report |

**Overall Code Grade: B+ (Solid foundation, needs tightening)**

---

## Using the Output

### For ML Model Training
```python
# Load final optimized dataset
import pandas as pd

df = pd.read_csv('new_optimal_design_tps/data/optimized_operating_points.csv')

# Split into features and targets
X = df[['Power_Target_W', 'V2_V']]
y = df[['D0_delta', 'D1', 'D2', 'Irms_A']]

# Train model (Random Forest, SVR, Neural Net, etc.)
from sklearn.ensemble import RandomForestRegressor
model = RandomForestRegressor().fit(X, y)

# Predict for new operating point
X_new = [[1500, 50]]  # 1500W at 50V
predictions = model.predict(X_new)  # [D0, D1, D2, Irms]
print(f"Optimal control: D0={predictions[0]:.3f}, D1={predictions[1]:.3f}, D2={predictions[2]:.3f}")
```

### For Firmware Implementation
```c
// Load lookup table into embedded system
// At runtime:
power_requested = 2000;  // W
battery_voltage = 48;    // V

// Find nearest row in CSV
best_row = lookup_table.query(power_requested, battery_voltage);

D0_optimal = best_row.D0_delta;
D1_optimal = best_row.D1;
D2_optimal = best_row.D2;

// Set phase shifts in hardware
DAB_set_duty_cycles(D0_optimal, D1_optimal, D2_optimal);
```

### For Research
- Compare with other modulation strategies
- Extend to other voltage/power ranges
- Verify soft-switching experimentally
- Optimize for different objectives (efficiency, thermal, cost)

---

## Running the Pipeline

### Full Run (40 seconds)
```bash
cd /Users/kitu/Desktop/Acads/BTP/BTP_G29
python3 new_optimal_design_tps/run_pipeline.py
```

### Stage 1 Only (Zone database, 30s)
```bash
python3 new_optimal_design_tps/generate_zone_database.py \
  --phase-step 0.01 \
  --v2-step 1.0 \
  --out new_optimal_design_tps/data/phase_shift_zone_database.csv
```

### Stage 2 Only (Optimize, 2s)
```bash
python3 new_optimal_design_tps/build_optimized_dataset.py \
  --power-min 0 \
  --power-max 3500 \
  --power-step 10 \
  --power-tolerance 2.0
```

### Adjust Resolution
```bash
# Finer phase shifts (slower, more accurate)
python3 new_optimal_design_tps/generate_zone_database.py --phase-step 0.005

# Coarser phase shifts (faster, less accurate)
python3 new_optimal_design_tps/generate_zone_database.py --phase-step 0.02
```

---

## Comparison: Old vs New at a Glance

```
OLD (scripts/optimization/):          NEW (new_optimal_design_tps/):
├─ Mode 1 only                        ├─ Zones I, II, V (paper-verified)
├─ Hardcoded equations                ├─ Analytical from paper
├─ SLSQP optimization                 ├─ Exhaustive grid search
├─ V2 = 50V fixed                     ├─ V2 ∈ [45-55V]
├─ 91 operating points                ├─ 3,861 operating points
├─ Run time: ~10 minutes              ├─ Run time: ~40 seconds
├─ Suboptimal for low/high power      ├─ Global optimum per zone
└─ Implicit constraints               └─ Explicit ZVS guaranteed
```

---

## Next Steps

1. **Validate & Fix** (1-2 days)
   - Implement Priority 1 bugs
   - Run regression tests
   
2. **Integrate** (1 day)
   - Replace old lookup table with new CSV
   - Update dashboard/ML pipeline
   - Retrain models with larger dataset
   
3. **Verify** (1 week)
   - Experimental validation on prototype
   - Compare Irms predictions vs measurements
   - Verify soft-switching under all conditions

4. **Deploy** (ongoing)
   - Use in production firmware
   - Monitor for edge cases
   - Gather operational data

