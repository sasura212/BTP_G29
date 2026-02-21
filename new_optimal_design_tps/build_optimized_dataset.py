import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def optimize_points(df: pd.DataFrame, power_values, tolerance_w: float, max_nearest_error_w: float | None):
    out_rows = []

    v2_values = sorted(df["V2_V"].unique())

    for v2 in v2_values:
        df_v2 = df[df["V2_V"] == v2]

        for p_target in power_values:
            candidates = df_v2[(df_v2["Power_W"] >= p_target - tolerance_w) & (df_v2["Power_W"] <= p_target + tolerance_w)]

            if not candidates.empty:
                best = candidates.loc[candidates["Irms_A"].idxmin()]
            else:
                # Fallback: nearest power, then minimum Irms among ties
                d = (df_v2["Power_W"] - p_target).abs()
                nearest_err = d.min()

                if max_nearest_error_w is not None and nearest_err > max_nearest_error_w:
                    out_rows.append(
                        {
                            "Power_Target_W": p_target,
                            "V2_V": v2,
                            "D0_delta": np.nan,
                            "D1": np.nan,
                            "D2": np.nan,
                            "Zone": "NO_SOLUTION",
                            "Irms_A": np.nan,
                            "Power_Actual_W": np.nan,
                            "Power_Error_W": nearest_err,
                            "m": np.nan,
                            "p_scaled": np.nan,
                            "n": np.nan,
                            "L_H": np.nan,
                        }
                    )
                    continue

                nearest = df_v2[d == nearest_err]
                best = nearest.loc[nearest["Irms_A"].idxmin()]

            out_rows.append(
                {
                    "Power_Target_W": p_target,
                    "V2_V": best["V2_V"],
                    "D0_delta": best["D0_delta"],
                    "D1": best["D1"],
                    "D2": best["D2"],
                    "Zone": best["Zone"],
                    "Irms_A": best["Irms_A"],
                    "Power_Actual_W": best["Power_W"],
                    "Power_Error_W": abs(best["Power_W"] - p_target),
                    "m": best["m"],
                    "p_scaled": best["p_scaled"],
                    "n": best["n"],
                    "L_H": best["L_H"],
                }
            )

    return pd.DataFrame(out_rows)


def main():
    parser = argparse.ArgumentParser(description="Build final optimized operating-point dataset from zone database.")
    parser.add_argument("--in", dest="in_csv", type=str, default="new_optimal_design_tps/data/phase_shift_zone_database.csv")
    parser.add_argument("--out", type=str, default="new_optimal_design_tps/data/optimized_operating_points.csv")
    parser.add_argument("--power-min", type=float, default=0.0)
    parser.add_argument("--power-max", type=float, default=3500.0)
    parser.add_argument("--power-step", type=float, default=10.0)
    parser.add_argument("--power-tolerance", type=float, default=2.0)
    parser.add_argument("--max-nearest-error", type=float, default=100.0)
    args = parser.parse_args()

    in_path = Path(args.in_csv)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not in_path.exists():
        raise FileNotFoundError(f"Input database not found: {in_path}")

    df = pd.read_csv(in_path)

    power_values = np.arange(args.power_min, args.power_max + 1e-12, args.power_step)

    max_nearest_error = None if args.max_nearest_error < 0 else args.max_nearest_error
    result = optimize_points(df, power_values, args.power_tolerance, max_nearest_error)
    result = result.sort_values(["V2_V", "Power_Target_W"]).reset_index(drop=True)
    result.to_csv(out_path, index=False)

    print("=" * 80)
    print("Final optimized dataset generated")
    print("=" * 80)
    print(f"Input rows: {len(df)}")
    print(f"Output rows: {len(result)}")
    print(f"Saved: {out_path}")
    print(f"Average |Power error|: {result['Power_Error_W'].mean():.3f} W")
    print(f"Worst |Power error|: {result['Power_Error_W'].max():.3f} W")
    print("Zone distribution:")
    print(result["Zone"].value_counts().sort_index())
    print("=" * 80)


if __name__ == "__main__":
    main()
