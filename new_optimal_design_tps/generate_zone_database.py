"""
Generate phase-shift lookup table using paper-based zone equations.

Based on: Das & Basu, "Optimal Design of a Dual-Active-Bridge DC–DC Converter,"
IEEE Trans. Ind. Electron., 2021.

Key changes vs v1:
  - Non-strict inequalities on zone masks (captures boundary points)
  - Analytical optimal path from Table III (fills zone-boundary gaps)
  - Focused d1=1 sweep for Zone V transition region
  - Proper documentation of why Zone II is empty for m > 1
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


# =============================================================================
# Paper-based design helpers
# =============================================================================

def p_star_polynomial(m: float) -> float:
    """Polynomial fit for p*(m) from the paper (Eq. 15)."""
    return -1.9 * m**4 + 12.6 * m**3 - 30.9 * m**2 + 34.3 * m - 14.07


def design_n_l(v1: float, v2_min: float, fs: float, p_max: float, m_star: float):
    """Compute transformer turns ratio n and inductance L (Section II-F)."""
    n = m_star * v1 / v2_min
    p_star = p_star_polynomial(m_star)
    l = p_star * (v1**2) / (2 * np.pi * fs * p_max)
    return n, l, p_star


def compute_pc1(m: float) -> float:
    """Critical power boundary pc1 (Table II).

    Below pc1 the optimal path lies on the Zone I/II boundary.
    """
    if m > 1:
        return np.pi * (m - 1) / (2 * m)
    else:
        return np.pi * m**2 * (1 - m) / 2


def compute_pc2(m: float) -> float:
    """Critical power boundary pc2 (Table II).

    Above pc2 the optimal path is SPS (d1=d2=1).
    """
    if m > 1:
        return m * np.pi / 2 * (1 - m**2 + m * np.sqrt(m**2 - 1))
    else:
        return (1 - m**2) * np.pi / (2 * m) * (-1 + 1 / np.sqrt(1 - m**2))


# =============================================================================
# Zone power equations (Eq. 8)
# =============================================================================

def p_zone_i(m, d1, d2, d0):
    return 0.5 * m * np.pi * d0 * d2


def p_zone_ii(m, d1, d2, d0):
    return 0.5 * m * np.pi * d0 * d1


def p_zone_v(m, d1, d2, d0):
    return 0.25 * m * np.pi * (1 - (1 - d1) ** 2 - (1 - d2) ** 2 - (1 - d0) ** 2)


# =============================================================================
# Zone Irms^2 equations (Eq. 9)
# =============================================================================

def irms2_zone_i(m, d1, d2, d0):
    return (np.pi**2 / 12.0) * (
        -2 * d1**3
        + 3 * d1**2 * d2 * m
        + 3 * d1**2
        - 6 * d1 * d2 * m
        - 2 * d2**3 * m**2
        + d2**3 * m
        + 3 * d2**2 * m**2
        + 3 * d2 * d0**2 * m
    )


def irms2_zone_ii(m, d1, d2, d0):
    return (np.pi**2 / 12.0) * (
        d1**3 * m
        - 2 * d1**3
        + 3 * d1**2
        + 3 * d1 * d2**2 * m
        - 6 * d1 * d2 * m
        + 3 * d1 * d0**2 * m
        - 2 * d2**3 * m**2
        + 3 * d2**2 * m**2
    )


def irms2_zone_v(m, d1, d2, d0):
    return (np.pi**2 / 12.0) * (
        -2 * d1**3
        - 3 * d1**2 * d0 * m
        + 3 * d1**2 * m
        + 3 * d1**2
        + 6 * d1 * d0 * m
        - 6 * d1 * m
        - 2 * d2**3 * m**2
        - 3 * d2**2 * d0 * m
        + 3 * d2**2 * m**2
        + 3 * d2**2 * m
        + 6 * d2 * d0 * m
        - 6 * d2 * m
        - d0**3 * m
        + 3 * d0**2 * m
        - 6 * d0 * m
        + 4 * m
    )


# =============================================================================
# ZVS constraint masks (Table I) — NON-STRICT inequalities
#
# Using >= / <= instead of > / < so that boundary points (where the
# optimal trajectory lives) are included.
#
# Note: Zone II ZVS is infeasible for m > 1 because constraints 2 & 3
# require m*delta < d1*(1-m) < 0 AND m*delta > d1*(m-1) > 0 simultaneously.
# This is mathematically impossible when m > 1 and delta > 0.
# =============================================================================

def mask_zone_i(m, d1, d2, d0):
    return (
        (d1 - d2 * m >= 0)
        & (d0 - d2 + d2 * m >= 0)
        & (d2 + d0 - d2 * m <= 0)
    )


def mask_zone_ii(m, d1, d2, d0):
    return (
        (d1 - d2 * m <= 0)
        & (d1 * m - d1 + m * d0 <= 0)
        & (d1 - d1 * m + m * d0 >= 0)
    )


def mask_zone_v(m, d1, d2, d0):
    return (
        (d1 - 2 * m + m * d0 + m * d1 >= 0)
        & (d2 + d0 + m * d2 - 2 >= 0)
        & (d0 - d2 + d2 * m >= 0)
        & (d1 - d1 * m + m * d0 >= 0)
    )


# =============================================================================
# Analytical optimal modulation path (Table III)
# =============================================================================

def generate_analytical_optimal(m, v1, v2, fs, l, n, p_max_w, n_points=1000):
    """Generate points along the paper's analytical optimal modulation path.

    For m > 1 (our case for all V2 in [45,55]):
      Region 1  [0, pc1]:      d1 = m·d2,  δ = (m-1)·d2     (Zone I/II boundary)
      Region 3  [pc2, mπ/4]:   d1 = 1, d2 = 1, δ from SPS    (Zone V / SPS)

    Region 2 [pc1, pc2] is covered by the grid sweep (d1≈1, Zone V interior).
    """
    scale_p = v1**2 / (2 * np.pi * fs * l)
    scale_i = v1 / (2 * np.pi * fs * l)
    p_limit = min(p_max_w / scale_p, m * np.pi / 4)
    pc1 = compute_pc1(m)
    pc2 = compute_pc2(m)

    frames = []

    # ---- Region 1: Zone I/II boundary, p in (0, pc1] ----
    r1_max = min(pc1, p_limit)
    if r1_max > 0 and m > 1:
        p_arr = np.linspace(1e-6, r1_max, n_points)
        d2_arr = np.sqrt(2 * p_arr / (np.pi * m * (m - 1)))
        d1_arr = m * d2_arr
        delta_arr = (m - 1) * d2_arr

        valid = (d1_arr <= 1) & (d2_arr <= 1) & (delta_arr <= 1) & (d1_arr > 0)
        d1_v = d1_arr[valid]
        d2_v = d2_arr[valid]
        delta_v = delta_arr[valid]
        p_v = p_arr[valid]

        # Use Zone I Irms formula (valid on the boundary, continuous from Zone I)
        irms2_v = irms2_zone_i(m, d1_v, d2_v, delta_v)
        ok = irms2_v >= 0

        if np.any(ok):
            irms_s = np.sqrt(irms2_v[ok])
            frames.append(pd.DataFrame({
                "V2_V": v2, "m": m, "n": n, "L_H": l,
                "D0_delta": delta_v[ok], "D1": d1_v[ok], "D2": d2_v[ok],
                "Zone": "I", "p_scaled": p_v[ok],
                "Irms_scaled": irms_s,
                "Power_W": scale_p * p_v[ok],
                "Irms_A": scale_i * irms_s,
            }))

    # ---- Region 1 for m <= 1 (not used in current design, included for generality) ----
    if r1_max > 0 and m <= 1:
        p_arr = np.linspace(1e-6, r1_max, n_points)
        d1_arr = np.sqrt(2 * p_arr / ((1 - m) * np.pi))
        d2_arr = d1_arr / m   # d1 = m*d2 → d2 = d1/m  (on I/II boundary)
        delta_arr = (1 - m) * d2_arr

        valid = (d1_arr <= 1) & (d2_arr <= 1) & (delta_arr <= 1) & (d1_arr > 0)
        d1_v = d1_arr[valid]
        d2_v = d2_arr[valid]
        delta_v = delta_arr[valid]
        p_v = p_arr[valid]

        irms2_v = irms2_zone_i(m, d1_v, d2_v, delta_v)
        ok = irms2_v >= 0

        if np.any(ok):
            irms_s = np.sqrt(irms2_v[ok])
            frames.append(pd.DataFrame({
                "V2_V": v2, "m": m, "n": n, "L_H": l,
                "D0_delta": delta_v[ok], "D1": d1_v[ok], "D2": d2_v[ok],
                "Zone": "I", "p_scaled": p_v[ok],
                "Irms_scaled": irms_s,
                "Power_W": scale_p * p_v[ok],
                "Irms_A": scale_i * irms_s,
            }))

    # ---- Region 3: SPS (d1=1, d2=1), p in (pc2, mπ/4] ----
    if pc2 < p_limit:
        p_arr = np.linspace(pc2 + 1e-6, p_limit, n_points)
        arg = 1 - 4 * p_arr / (m * np.pi)
        valid = arg >= 0
        p_v = p_arr[valid]
        delta_v = 1 - np.sqrt(arg[valid])
        d1_v = np.ones_like(delta_v)
        d2_v = np.ones_like(delta_v)

        irms2_v = irms2_zone_v(m, d1_v, d2_v, delta_v)
        ok = irms2_v >= 0

        if np.any(ok):
            irms_s = np.sqrt(irms2_v[ok])
            frames.append(pd.DataFrame({
                "V2_V": v2, "m": m, "n": n, "L_H": l,
                "D0_delta": delta_v[ok], "D1": d1_v[ok], "D2": d2_v[ok],
                "Zone": "V", "p_scaled": p_v[ok],
                "Irms_scaled": irms_s,
                "Power_W": scale_p * p_v[ok],
                "Irms_A": scale_i * irms_s,
            }))

    return pd.concat(frames, ignore_index=True) if frames else None


# =============================================================================
# Focused d1=1 sweep for Zone V transition region
# =============================================================================

def generate_d1_fixed_sweep(m, v1, v2, fs, l, n, p_max_w, d1_fixed=1.0, step=0.005):
    """Fine 2-D sweep with d1 fixed at 1.0.

    This fills the Region 2 gap (pc1 to pc2) where the optimal path
    has d1=1 and d2, delta varying inside Zone V.
    """
    scale_p = v1**2 / (2 * np.pi * fs * l)
    scale_i = v1 / (2 * np.pi * fs * l)
    p_limit = min(p_max_w / scale_p, m * np.pi / 4)

    d_vals = np.arange(step, 1.0 + 1e-12, step)
    d2g, d0g = np.meshgrid(d_vals, d_vals, indexing="ij")
    d1g = np.full_like(d2g, d1_fixed)

    zv_mask = mask_zone_v(m, d1g, d2g, d0g)
    p_scaled = p_zone_v(m, d1g, d2g, d0g)
    irms2_scaled = irms2_zone_v(m, d1g, d2g, d0g)

    valid = zv_mask & (p_scaled > 0) & (p_scaled <= p_limit) & (irms2_scaled >= 0)
    if not np.any(valid):
        return None

    p_v = p_scaled[valid]
    irms_s = np.sqrt(irms2_scaled[valid])

    return pd.DataFrame({
        "V2_V": v2, "m": m, "n": n, "L_H": l,
        "D0_delta": d0g[valid], "D1": d1g[valid], "D2": d2g[valid],
        "Zone": "V", "p_scaled": p_v,
        "Irms_scaled": irms_s,
        "Power_W": scale_p * p_v,
        "Irms_A": scale_i * irms_s,
    })


def generate_zone_v_boundary(m, v1, v2, fs, l, n, p_max_w, n_points=500):
    """Trace the Zone V entry boundary (minimum-power Zone V points).

    At d1=1, sweeps d2 from 1/m to 1 and uses the minimum delta that
    satisfies all Zone V constraints.  This produces the lowest-power
    Zone V operating points, closing the gap between Zone I max (=pc1)
    and the coarser grid's Zone V min.
    """
    scale_p = v1**2 / (2 * np.pi * fs * l)
    scale_i = v1 / (2 * np.pi * fs * l)
    p_limit = min(p_max_w / scale_p, m * np.pi / 4)

    d1 = 1.0
    d2_vals = np.linspace(max(1.0 / m, 0.01), 1.0, n_points)

    rows_d1 = []
    rows_d2 = []
    rows_d0 = []
    rows_p = []
    rows_irms2 = []

    for d2 in d2_vals:
        # Minimum delta from Zone V constraints with d1=1:
        #   (1+m) + m*delta >= 2m  →  delta >= (m-1)/m
        #   (1+m)*d2 + delta >= 2  →  delta >= 2 - (1+m)*d2
        #   d1*(1-m) + m*delta >= 0 →  delta >= (m-1)/m
        delta_min = max((m - 1) / m, 2 - (1 + m) * d2, 0.001)

        # Sweep a small range above delta_min for coverage near boundary
        for delta in np.linspace(delta_min, min(delta_min + 0.03, 1.0), 15):
            c1 = d1 * (1 + m) + m * delta >= 2 * m
            c2 = (1 + m) * d2 + delta >= 2
            c3 = delta + d2 * (m - 1) >= 0
            c4 = d1 * (1 - m) + m * delta >= 0
            if not (c1 and c2 and c3 and c4):
                continue

            p = p_zone_v(m, d1, d2, delta)
            if p <= 0 or p > p_limit:
                continue
            irms2 = irms2_zone_v(m, d1, d2, delta)
            if irms2 < 0:
                continue

            rows_d1.append(d1)
            rows_d2.append(d2)
            rows_d0.append(delta)
            rows_p.append(p)
            rows_irms2.append(irms2)

    if not rows_p:
        return None

    p_arr = np.array(rows_p)
    irms_s = np.sqrt(np.array(rows_irms2))
    return pd.DataFrame({
        "V2_V": v2, "m": m, "n": n, "L_H": l,
        "D0_delta": rows_d0, "D1": rows_d1, "D2": rows_d2,
        "Zone": "V", "p_scaled": p_arr,
        "Irms_scaled": irms_s,
        "Power_W": scale_p * p_arr,
        "Irms_A": scale_i * irms_s,
    })


# =============================================================================
# Grid sweep helpers
# =============================================================================

def build_zone_rows(zone_name, zone_mask, p_scaled, irms2_scaled, m, v2, v1, fs, l, n, d1, d2, d0):
    """Build a dataframe of valid zone operating points from a grid sweep."""
    valid = zone_mask & (p_scaled > 0) & (irms2_scaled >= 0)
    if not np.any(valid):
        return None

    p_valid = p_scaled[valid]
    irms_scaled = np.sqrt(irms2_scaled[valid])

    power_w = (v1**2 / (2 * np.pi * fs * l)) * p_valid
    irms_a = (v1 / (2 * np.pi * fs * l)) * irms_scaled

    return pd.DataFrame(
        {
            "V2_V": np.full(p_valid.size, v2),
            "m": np.full(p_valid.size, m),
            "n": np.full(p_valid.size, n),
            "L_H": np.full(p_valid.size, l),
            "D0_delta": d0[valid],
            "D1": d1[valid],
            "D2": d2[valid],
            "Zone": np.full(p_valid.size, zone_name),
            "p_scaled": p_valid,
            "Irms_scaled": irms_scaled,
            "Power_W": power_w,
            "Irms_A": irms_a,
        }
    )


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate phase-shift lookup table using paper-based zone equations."
    )
    parser.add_argument("--v1", type=float, default=200.0)
    parser.add_argument("--fs", type=float, default=100_000.0)
    parser.add_argument("--p-max", type=float, default=3500.0)
    parser.add_argument("--v2-min", type=float, default=45.0)
    parser.add_argument("--v2-max", type=float, default=55.0)
    parser.add_argument("--v2-step", type=float, default=1.0)
    parser.add_argument("--m-star", type=float, default=1.3)
    parser.add_argument("--phase-step", type=float, default=0.01)
    parser.add_argument("--out", type=str, default="new_optimal_design_tps/data/phase_shift_zone_database.csv")
    args = parser.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    n, l, p_star = design_n_l(args.v1, args.v2_min, args.fs, args.p_max, args.m_star)

    print("=" * 80)
    print("Paper-based zone database generation (v2 – with analytical path)")
    print("=" * 80)
    print(f"Design point: m*={args.m_star:.4f}, p*(m*)={p_star:.6f}")
    print(f"Computed n={n:.6f}, L={l*1e6:.3f} uH")

    d_vals = np.arange(args.phase_step, 1.0, args.phase_step)
    d1g, d2g, d0g = np.meshgrid(d_vals, d_vals, d_vals, indexing="ij")

    all_rows = []
    v2_values = np.arange(args.v2_min, args.v2_max + 1e-12, args.v2_step)

    for v2 in v2_values:
        m = n * v2 / args.v1
        pc1 = compute_pc1(m)
        pc2 = compute_pc2(m)
        scale_p = args.v1**2 / (2 * np.pi * args.fs * l)
        pc1_w = scale_p * pc1
        pc2_w = scale_p * pc2

        # ---- 3-D grid sweep (Zones I, II, V) ----
        m_i = mask_zone_i(m, d1g, d2g, d0g)
        m_ii = mask_zone_ii(m, d1g, d2g, d0g)
        m_v = mask_zone_v(m, d1g, d2g, d0g)

        rows_i = build_zone_rows(
            "I", m_i, p_zone_i(m, d1g, d2g, d0g),
            irms2_zone_i(m, d1g, d2g, d0g),
            m, v2, args.v1, args.fs, l, n, d1g, d2g, d0g,
        )
        rows_ii = build_zone_rows(
            "II", m_ii, p_zone_ii(m, d1g, d2g, d0g),
            irms2_zone_ii(m, d1g, d2g, d0g),
            m, v2, args.v1, args.fs, l, n, d1g, d2g, d0g,
        )
        rows_v = build_zone_rows(
            "V", m_v, p_zone_v(m, d1g, d2g, d0g),
            irms2_zone_v(m, d1g, d2g, d0g),
            m, v2, args.v1, args.fs, l, n, d1g, d2g, d0g,
        )

        # ---- Analytical optimal path (Table III, fills boundary gaps) ----
        rows_analytical = generate_analytical_optimal(
            m, args.v1, v2, args.fs, l, n, args.p_max
        )

        # ---- Focused d1=1 sweep (fills Zone V transition region) ----
        rows_d1_fixed = generate_d1_fixed_sweep(
            m, args.v1, v2, args.fs, l, n, args.p_max
        )

        # ---- Zone V boundary curve (fills gap at pc1 transition) ----
        rows_zv_boundary = generate_zone_v_boundary(
            m, args.v1, v2, args.fs, l, n, args.p_max
        )

        frames = [x for x in (rows_i, rows_ii, rows_v, rows_analytical, rows_d1_fixed, rows_zv_boundary) if x is not None]
        if frames:
            one_v2 = pd.concat(frames, ignore_index=True)
            one_v2 = one_v2[(one_v2["Power_W"] >= 0) & (one_v2["Power_W"] <= args.p_max)]

            if one_v2.empty:
                print(f"  V2={v2:.1f} V  m={m:.4f}  pc1={pc1_w:.0f} W  pc2={pc2_w:.0f} W  -> 0 rows")
                continue

            all_rows.append(one_v2)
            zones = one_v2["Zone"].value_counts()
            zone_str = ", ".join(f"{z}:{c}" for z, c in sorted(zones.items()))
            print(
                f"  V2={v2:.1f} V  m={m:.4f}  pc1={pc1_w:.0f} W  pc2={pc2_w:.0f} W  "
                f"-> {len(one_v2)} rows  [{zone_str}]"
            )
        else:
            print(f"  V2={v2:.1f} V  m={m:.4f}  -> 0 valid rows")

    if not all_rows:
        raise RuntimeError("No valid rows generated. Check constraints and settings.")

    df = pd.concat(all_rows, ignore_index=True)

    # Drop exact duplicates (grid + analytical overlap)
    df = df.drop_duplicates(subset=["V2_V", "D1", "D2", "D0_delta", "Zone"]).reset_index(drop=True)

    # Sort for faster downstream search
    df = df.sort_values(["V2_V", "Power_W", "Irms_A"]).reset_index(drop=True)
    df.to_csv(out_path, index=False)

    print("-" * 80)
    print(f"Saved: {out_path}")
    print(f"Total rows: {len(df)}")
    print(f"Power range: {df['Power_W'].min():.2f} .. {df['Power_W'].max():.2f} W")
    print(f"Irms range: {df['Irms_A'].min():.4f} .. {df['Irms_A'].max():.4f} A")
    print(f"\nZone distribution:")
    print(df["Zone"].value_counts().sort_index().to_string())
    print("=" * 80)


if __name__ == "__main__":
    main()
