# Code Validation: Bugs & Fixes

## Critical Issues Found

---

## 🔴 Bug #1: Unverified Polynomial Fit for p*

### Location
`generate_zone_database.py` line ~10:
```python
def p_star_polynomial(m: float) -> float:
    """Polynomial fit from the paper (Eq. 15)."""
    return -1.9 * m**4 + 12.6 * m**3 - 30.9 * m**2 + 34.3 * m - 14.07
```

### Problem
- Coefficients are NOT explicitly provided in the paper
- This is a 4th-order **curve fit approximation** of the solution to Eq. (13a) and (14a)
- At m=1.3: returns p* ≈ **0.3825** (needs verification against paper)
- No source citation for where these coefficients come from

### What Should Happen
Paper states (Section II-E):
> "For m ∈ [0, 1], d₂* = 1 and the value of d₁* can be obtained by solution of: [Eq. 13a]"

This is a **6th-degree polynomial equation** that must be solved numerically:
```
(1 + m²)² × d₁*⁶ - 6m²(m²+1) × d₁*⁵ + ... = 0
```

Once d₁* is found, p* can be computed from:
```
p* = p_zone_v(m, d1*, d2*=1, δ*) 
   = 0.25 × m × π × [1 - (1-d₁*)² - (1-1)² - (1-δ*)²]
```

### Fix (Priority 1 - Critical)

**Option A: Use scipy.optimize.fsolve**
```python
from scipy.optimize import fsolve

def compute_p_star_accurate(m: float) -> float:
    """
    Solve Eq. (13a) exactly using numerical root-finding.
    Returns optimal p* at m for the design problem.
    """
    
    def eq_13a(d1):
        """6th-degree polynomial from paper Eq. 13a"""
        return (
            (1 + m**2)**2 * d1**6 
            - 6*m**2*(m**2+1) * d1**5 
            + 3*m**2*(4*m**2+1) * d1**4 
            - 2*m**2*(5*m**2+1) * d1**3 
            + 6*m**4 * d1**2 
            - m**6
        )
    
    # Initial guess
    d1_init = 0.5
    d1_star = fsolve(eq_13a, d1_init)[0]
    
    # Clamp to valid range
    d1_star = np.clip(d1_star, 0.01, 0.99)
    
    # Compute δ* using Eq. 13b
    delta_star = 1 - d1_star / m + np.sqrt(d1_star**2 - 2*d1_star + d1_star**2 / m**2)
    
    # Compute p* using zone V equation at optimal point
    p_star = 0.25 * m * np.pi * (
        1 - (1 - d1_star)**2 - (1 - 1)**2 - (1 - delta_star)**2
    )
    
    return p_star

# Verify at design point m=1.3
p_star_1p3 = compute_p_star_accurate(1.3)
print(f"p*(1.3) = {p_star_1p3:.6f}")  # Compare with paper figure
```

**Option B: Precompute lookup table**
```python
import numpy as np
from scipy.optimize import fsolve

# Precompute p* for common m values
m_values = np.linspace(0.5, 2.0, 100)
p_star_values = []

for m in m_values:
    # ... solve Eq. 13a/14a ...
    p_star_values.append(p_star)

# Create lookup with interpolation
from scipy.interpolate import interp1d
p_star_interp = interp1d(m_values, p_star_values, kind='cubic')

def design_n_l(v1, v2_min, fs, p_max, m_star):
    n = m_star * v1 / v2_min
    p_star = p_star_interp(m_star)  # Use interpolation instead of polynomial
    l = p_star * (v1**2) / (2 * np.pi * fs * p_max)
    return n, l, p_star
```

### Validation
After fix, cross-check with:
- Paper Figure 5 or Table II (if provided)
- Verify that p*(1.3) ≈ expected value from paper

---

## 🟡 Bug #2: Missing Power Feasibility Check

### Location
Both `generate_zone_database.py` and `build_optimized_dataset.py`

### Problem
Paper states (Section II-D):
> "For any given m and any arbitrary choice of L (provided p_max ≤ mπ/4 is ensured)..."

This is a **fundamental constraint** for the existence of a solution. Currently not checked!

### What Should Happen
For m=1.3:
```
max_p_allowed = m × π / 4 = 1.3 × π / 4 ≈ 1.0210 (scaled)
```

In actual power units:
```
P_max_feasible = (V1² / (2π × f_s × L)) × 1.0210
               = (200² / (2π × 100k × 10.089µH)) × 1.0210
               ≈ 6,450 W
```

Since design max is 3,500W, **we're safe**, but this should be explicitly validated.

### Fix (Priority 1 - Critical)

**In generate_zone_database.py:**
```python
def main():
    # ... existing code ...
    
    # ✅ ADD VALIDATION
    max_p_scaled = m * np.pi / 4
    print(f"Design validation: p_max_scaled = {max_p_scaled:.6f}")
    
    if args.p_max > (args.v1**2 / (2*np.pi*args.fs*args.l)) * max_p_scaled:
        print(f"⚠️  WARNING: p_max violates feasibility constraint!")
        print(f"   Max feasible power: {(args.v1**2 / (2*np.pi*args.fs*args.l)) * max_p_scaled:.1f}W")
        print(f"   Specified p_max: {args.p_max:.1f}W")
    
    # ✅ FILTER INFEASIBLE POINTS
    for v2 in v2_values:
        # ... existing zone masking code ...
        
        # After computing p_scaled for each zone:
        max_p_allowed = m * np.pi / 4
        
        rows_i = build_zone_rows(
            "I",
            m_i & (p_zone_i(...) <= max_p_allowed),  # ← ADD THIS CHECK
            # ... rest of code
        )
        
        rows_ii = build_zone_rows(
            "II",
            m_ii & (p_zone_ii(...) <= max_p_allowed),  # ← ADD THIS CHECK
            # ... rest of code
        )
        
        rows_v = build_zone_rows(
            "V",
            m_v & (p_zone_v(...) <= max_p_allowed),  # ← ADD THIS CHECK
            # ... rest of code
        )
```

### Impact
- **Current:** ~362k rows (may include unfeasible points)
- **After fix:** Fewer rows, but all guaranteed feasible
- **Users:** Will know their design is sound

---

## 🟡 Bug #3: Poor Variable Naming

### Location
All files use: `D0_delta`, `D1`, `D2`

### Problem
Creates confusion:
- `D0_delta` looks like it's a 4th parameter but it's actually the phase shift δ
- `D1` and `D2` match paper notation, but `D0_delta` doesn't
- Users might think `D0` is same as the mode numbers (Mode 1, 2, etc.)

### Example Confusion
```python
# Current (confusing):
row = {
    "D0_delta": 0.45,    # ← This is actually δ (phase shift), not D0
    "D1": 0.82,          # ← This is d1 (primary duty)
    "D2": 0.68,          # ← This is d2 (secondary duty)
}

# Correct naming:
row = {
    "delta": 0.45,       # OR "phase_shift" or "delta_phase"
    "d1_duty": 0.82,     # OR "d1" or "duty_primary"
    "d2_duty": 0.68,     # OR "d2" or "duty_secondary"
}
```

### Fix (Priority 2 - Important)

**Option A: Rename in CSV output** (minimal disruption)
```python
# In build_optimized_dataset.py, before saving CSV:
result = result.rename(columns={
    "D0_delta": "delta_phase_shift",
    "D1": "d1_primary_duty",
    "D2": "d2_secondary_duty",
})

# Also in generate_zone_database.py:
df = df.rename(columns={
    "D0_delta": "delta_phase_shift",
    "D1": "d1_primary_duty",
    "D2": "d2_secondary_duty",
})
```

**Option B: Semantic naming (clearer for domain experts)**
```python
columns = {
    "delta_phase_shift": "Phase shift between primary and secondary (Eq. δ)",
    "d1_primary_duty": "Primary voltage duty cycle (Eq. d₁)",
    "d2_secondary_duty": "Secondary voltage duty cycle (Eq. d₂)",
}
```

### Backward Compatibility
If existing code depends on old names, add a deprecation path:
```python
# keep old names as aliases
"D0_delta": "delta_phase_shift",
"D1": "d1_primary_duty",
"D2": "d2_secondary_duty",
```

---

## 🟠 Bug #4: No Explicit ZVS Soft-Switching Validation

### Location
`build_optimized_dataset.py` - final output doesn't include ZVS margin

### Problem
While zone classification ensures ZVS constraints are met, the output doesn't:
1. Explicitly verify soft-switching is satisfied
2. Provide margin information (how close to boundary?)
3. Warn if operating near constraint limits

### What Should Happen
Paper Table I specifies 4 constraints per zone. Final output should include:
```
"ZVS_Margin_Primary": computed margin for primary switch
"ZVS_Margin_Secondary": computed margin for secondary switch
"ZVS_Verified": Boolean (all constraints satisfied with margin > threshold)
```

### Fix (Priority 2 - Important)

```python
def compute_zvs_margins(row, m):
    """Compute ZVS soft-switching margins for a given operating point."""
    d1, d2, d0 = row['D1'], row['D2'], row['D0_delta']
    zone = row['Zone']
    
    margins = {}
    
    if zone == 'I':
        margins['c1'] = d1 - d2*m               # Should be > 0
        margins['c2'] = d0 - d2 + d2*m          # Should be > 0
        margins['c3'] = d2 + d0 - d2*m          # Should be < 0 (negate)
        margins['c3'] = -(d2 + d0 - d2*m)       # Now should be > 0
        min_margin = min(margins.values())
        margins['min_margin'] = min_margin
        margins['zvs_ok'] = min_margin > 0.01   # 1% margin threshold
        
    # Similar for zones II and V...
    
    return margins

# In build_optimized_dataset.py:
for idx, row in result.iterrows():
    m = row['m']
    zvs = compute_zvs_margins(row, m)
    result.loc[idx, 'ZVS_Min_Margin'] = zvs['min_margin']
    result.loc[idx, 'ZVS_Verified'] = zvs['zvs_ok']

# Save enhanced output
result.to_csv(out_path, index=False)
```

---

## 🟢 Minor Issues (Priority 3)

### Issue #5: No Zone Distribution Report
**Current:** Generates database but doesn't report zone statistics

**Fix:**
```python
print("\nZone distribution in final dataset:")
print(result["Zone"].value_counts().sort_index())
print(f"\nZone I:   {(result['Zone']=='I').sum()} rows ({100*(result['Zone']=='I').sum()/len(result):.1f}%)")
print(f"Zone II:  {(result['Zone']=='II').sum()} rows ({100*(result['Zone']=='II').sum()/len(result):.1f}%)")
print(f"Zone V:   {(result['Zone']=='V').sum()} rows ({100*(result['Zone']=='V').sum()/len(result):.1f}%)")
```

### Issue #6: No Warnings for Extreme Operating Points
**Current:** Silently handles points near power limits

**Fix:**
```python
if row['Power_W'] > 0.9 * args.p_max:
    print(f"⚠️  WARNING: Operating near power limit at P={row['Power_W']:.0f}W")
```

### Issue #7: Hard-coded m_star=1.3
**Better:** Make it a command-line parameter or read from paper reference

```python
parser.add_argument("--m-star", type=float, default=1.3,
                    help="Optimal voltage ratio from paper design (default: 1.3)")
```

---

## Summary: Severity Matrix

| Bug # | Title | Severity | Impact | Fix Complexity |
|-------|-------|----------|--------|----------------|
| 1 | Unverified polynomial | 🔴 HIGH | Wrong design params | Medium (numerical solving) |
| 2 | Missing feasibility check | 🔴 HIGH | Unfeasible points | Low (add 1 constraint) |
| 3 | Poor variable naming | 🟡 MEDIUM | User confusion | Low (rename columns) |
| 4 | No ZVS validation in output | 🟡 MEDIUM | Hidden margin info | Medium (compute & validate) |
| 5 | Zone statistics | 🟢 LOW | Missing insights | Low (add print statements) |
| 6 | No operation warnings | 🟢 LOW | Silent failures | Low (add if conditions) |
| 7 | Hard-coded m_star | 🟢 LOW | Limited flexibility | Low (add parameter) |

---

## Recommended Action Plan

**Week 1:**
1. ✅ Fix Bug #1 (polynomial) — implement scipy.optimize.fsolve solution
2. ✅ Fix Bug #2 (feasibility) — add constraint check to both scripts
3. ✅ Test with m ∈ [0.5, 2.0] range

**Week 2:**
4. ✅ Fix Bug #3 (naming) — rename columns, update documentation
5. ✅ Add Bug #4 (ZVS margins) — compute and export margins
6. ✅ Run full regression tests

**Ongoing:**
7. ✅ Add Bugs #5-7 (minor improvements)
8. ✅ Add comprehensive docstrings with paper references
9. ✅ Create unit tests for each function

