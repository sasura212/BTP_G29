"""
===========================================================
Triple Phase Shift (TPS) Optimization for Dual Active Bridge
===========================================================

Implements Tong et al. (2016) analytical method to minimize Irms
for a given target power level using closed-form equations and
Sequential Quadratic Programming (SLSQP) optimization.

This script sweeps power levels and computes the optimal D0, D1, D2
that minimize RMS current, storing results into a CSV lookup table.

Author: Harshit Singh (BTP Project, IIT Roorkee)
Date: November 2025
===========================================================
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize, NonlinearConstraint, Bounds


# === 1. System Constants ===
V1 = 200.0       # Primary DC voltage [V]
V2 = 50.0        # Secondary reflected DC voltage [V]
T = 1e-5         # Half switching period [s]
L = 20e-6        # Inductance [H]


# === 2. Objective Function: Irms ===
def Irms(x):
    """Compute RMS current based on Tong et al. (2016) analytical equations."""
    D0, D1, D2 = x

    try:
        term = (
            (0.125/3)*(V1**2) + (0.125/3)*(V2**2)
            + (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2
            - (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2
            - (0.5/3)*(0.25 - 1.5*(D0 + D2)**2 + (D0 + D2)**3)*V1*V2
            - (0.5/3)*(0.25 - 1.5*(D0 - D1)**2 + (D0 - D1)**3)*V1*V2
            - (0.5/3)*(0.25 - 1.5*(D0 + D2 - D1)**2 + (D0 + D2 - D1)**3)*V1*V2
            + (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
        )
        value = np.sqrt(((T/L)**2) * abs(term))
        if np.isnan(value) or value < 0:
            return 1e6  # Penalize invalid results
        return value
    except Exception:
        return 1e6


# === 3. Power Equation ===
def power_equation(x):
    """Analytical power equation for TPS control (Tong et al., Eq. 1)."""
    D0, D1, D2 = x
    return (-(V1*V2*T)/L) * (
        -D0 + D0**2 + 0.5*D1 - D0*D1 + 0.5*D1**2
        - 0.5*D2 + D0*D2 - 0.5*D1*D2 + 0.5*D2**2
    )


# === 4. Power Balance Constraint ===
def power_constraint(x, P_target):
    """Ensure the delivered power matches the target power."""
    return power_equation(x) - P_target


# === 5. Physical Mode Constraints ===
def physical_constraints(x):
    """Inequality constraints enforcing valid DAB operating modes."""
    D0, D1, D2 = x
    c1 = D1 - D0           # D1 < D0
    c2 = D1 - (D0 + D2)    # D1 < D0 + D2
    c3 = (D0 + D2) - 1.0   # D0 + D2 < 1
    return np.array([c1, c2, c3])


# === 6. Operating Mode Determination ===
def determine_mode(D0, D1, D2):
    """
    Determine operating mode based on Tong et al. (2016) Table I logic.
    Uses normalized duty ratios D0, D1, D2 (0–1 range).
    """
    phi = np.pi * abs(D0)
    D1r, D2r = np.pi * D1, np.pi * D2

    if phi <= D1r and phi <= D2r:
        return 1
    elif D2r < D1r and D2r <= phi <= D1r:
        return 2
    elif D1r < D2r and D1r <= phi <= D2r:
        return 3
    elif phi >= D1r and phi >= D2r and phi <= (D1r + D2r):
        return 4
    elif (D1r + D2r) <= phi <= (np.pi - D1r - D2r):
        return 5
    elif phi > (np.pi - D1r - D2r):
        return 6
    return 0  # Undefined / fallback


# === 7. Optimization Wrapper ===
def optimize_tps(P_target):
    """Run TPS optimization for a given target power level."""
    x0 = np.array([0.65, 0.32, 0.20])
    bounds = Bounds([0.01, 0.01, 0.01], [0.99, 0.99, 0.99])

    nlc_power = NonlinearConstraint(lambda x: power_constraint(x, P_target), 0.0, 0.0)
    nlc_phys = NonlinearConstraint(physical_constraints, -np.inf, 0.0)

    result = minimize(
        Irms,
        x0,
        method="SLSQP",
        bounds=bounds,
        constraints=[nlc_power, nlc_phys],
        options={"ftol": 1e-9, "disp": False, "maxiter": 500},
    )

    if not result.success:
        print(f"⚠️ Optimization failed at P={P_target:.2f} W: {result.message}")
    return result


# === 8. Power Sweep and Dataset Generation ===
powers = np.linspace(100, 1000, 20)  # Sweep from 100 W to 1 kW
results = []

print("===========================================================")
print(" Running TPS Optimization Sweep for DAB Converter")
print("===========================================================")

for P_target in powers:
    res = optimize_tps(P_target)
    D0, D1, D2 = res.x
    Irms_min = Irms(res.x)
    P_actual = power_equation(res.x)
    mode = determine_mode(D0, D1, D2)
    power_error = abs(P_actual - P_target) / P_target * 100  # Percentage error

    results.append([P_target, D0, D1, D2, Irms_min, P_actual, power_error, mode])
    print(f"P={P_target:.1f} W → D0={D0:.4f}, D1={D1:.4f}, D2={D2:.4f}, "
          f"Irms={Irms_min:.4f} A, P_actual={P_actual:.2f} W, Mode={mode}, Error={power_error:.3f}%")

# === 9. Save Results ===
df = pd.DataFrame(results, columns=["Power_W", "D0", "D1", "D2", "Irms_A", "P_actual_W", "Power_Error_%", "Mode"])
df.to_csv("optimized_lookup_table_tps.csv", index=False)

print("\n===========================================================")
print("✅ TPS Optimization Completed Successfully!")
print(f"Saved dataset: optimized_lookup_table_tps.csv ({len(df)} rows)")
print(f"Average Power Error: {df['Power_Error_%'].mean():.4f}%")
print("===========================================================")
