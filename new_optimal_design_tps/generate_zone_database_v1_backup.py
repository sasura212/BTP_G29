import argparse
from pathlib import Path

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# Paper-based design helpers
# -----------------------------------------------------------------------------
def p_star_polynomial(m: float) -> float:
    """Polynomial fit from the paper (Eq. 15)."""
    return -1.9 * m**4 + 12.6 * m**3 - 30.9 * m**2 + 34.3 * m - 14.07


def design_n_l(v1: float, v2_min: float, fs: float, p_max: float, m_star: float):
    """Compute n and L from paper design flow (Section II-F)."""
    n = m_star * v1 / v2_min
    p_star = p_star_polynomial(m_star)
    l = p_star * (v1**2) / (2 * np.pi * fs * p_max)
    return n, l, p_star


# -----------------------------------------------------------------------------
# Zone equations (from attached paper summary, Zones I, II, V)
# -----------------------------------------------------------------------------
def p_zone_i(m, d1, d2, d0):
    return 0.5 * m * np.pi * d0 * d2


def p_zone_ii(m, d1, d2, d0):
    return 0.5 * m * np.pi * d0 * d1


def p_zone_v(m, d1, d2, d0):
    return 0.25 * m * np.pi * (1 - (1 - d1) ** 2 - (1 - d2) ** 2 - (1 - d0) ** 2)


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


# -----------------------------------------------------------------------------
# ZVS/zone constraints (as provided in the paper table)
# -----------------------------------------------------------------------------
def mask_zone_i(m, d1, d2, d0):
    return (
        (d1 - d2 * m > 0)
        & (d0 - d2 + d2 * m > 0)
        & (d2 + d0 - d2 * m < 0)
    )


def mask_zone_ii(m, d1, d2, d0):
    return (
        (d1 - d2 * m < 0)
        & (d1 * m - d1 + m * d0 < 0)
        & (d1 - d1 * m + m * d0 > 0)
    )


def mask_zone_v(m, d1, d2, d0):
    return (
        (d1 - 2 * m + m * d0 + m * d1 > 0)
        & (d2 + d0 + m * d2 - 2 > 0)
        & (d0 - d2 + d2 * m > 0)
        & (d1 - d1 * m + m * d0 > 0)
    )


def build_zone_rows(zone_name, zone_mask, p_scaled, irms2_scaled, m, v2, v1, fs, l, n, d1, d2, d0):
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


def main():
    parser = argparse.ArgumentParser(description="Generate phase-shift lookup table using paper-based zone equations.")
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
    print("Paper-based zone database generation")
    print("=" * 80)
    print(f"Design point: m*={args.m_star:.4f}, p*(m*)={p_star:.6f}")
    print(f"Computed n={n:.6f}, L={l*1e6:.3f} uH")

    d_vals = np.arange(args.phase_step, 1.0, args.phase_step)
    d1g, d2g, d0g = np.meshgrid(d_vals, d_vals, d_vals, indexing="ij")

    all_rows = []
    v2_values = np.arange(args.v2_min, args.v2_max + 1e-12, args.v2_step)

    for v2 in v2_values:
        m = n * v2 / args.v1

        m_i = mask_zone_i(m, d1g, d2g, d0g)
        m_ii = mask_zone_ii(m, d1g, d2g, d0g)
        m_v = mask_zone_v(m, d1g, d2g, d0g)

        rows_i = build_zone_rows(
            "I",
            m_i,
            p_zone_i(m, d1g, d2g, d0g),
            irms2_zone_i(m, d1g, d2g, d0g),
            m,
            v2,
            args.v1,
            args.fs,
            l,
            n,
            d1g,
            d2g,
            d0g,
        )
        rows_ii = build_zone_rows(
            "II",
            m_ii,
            p_zone_ii(m, d1g, d2g, d0g),
            irms2_zone_ii(m, d1g, d2g, d0g),
            m,
            v2,
            args.v1,
            args.fs,
            l,
            n,
            d1g,
            d2g,
            d0g,
        )
        rows_v = build_zone_rows(
            "V",
            m_v,
            p_zone_v(m, d1g, d2g, d0g),
            irms2_zone_v(m, d1g, d2g, d0g),
            m,
            v2,
            args.v1,
            args.fs,
            l,
            n,
            d1g,
            d2g,
            d0g,
        )

        frames = [x for x in (rows_i, rows_ii, rows_v) if x is not None]
        if frames:
            one_v2 = pd.concat(frames, ignore_index=True)
            one_v2 = one_v2[(one_v2["Power_W"] >= 0) & (one_v2["Power_W"] <= args.p_max)]

            if one_v2.empty:
                print(f"V2={v2:.2f} V -> 0 valid rows (within power range)")
                continue

            all_rows.append(one_v2)
            print(f"V2={v2:.2f} V -> {len(one_v2)} valid rows")
        else:
            print(f"V2={v2:.2f} V -> 0 valid rows")

    if not all_rows:
        raise RuntimeError("No valid rows generated. Check constraints and settings.")

    df = pd.concat(all_rows, ignore_index=True)

    # Sort for faster downstream search
    df = df.sort_values(["V2_V", "Power_W", "Irms_A"]).reset_index(drop=True)
    df.to_csv(out_path, index=False)

    print("-" * 80)
    print(f"Saved: {out_path}")
    print(f"Rows: {len(df)}")
    print(f"Power range: {df['Power_W'].min():.2f} .. {df['Power_W'].max():.2f} W")
    print(f"Irms range: {df['Irms_A'].min():.4f} .. {df['Irms_A'].max():.4f} A")
    print("=" * 80)


if __name__ == "__main__":
    main()
