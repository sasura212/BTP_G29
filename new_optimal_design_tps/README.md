# New Paper-Aligned DAB Optimization Pipeline

This folder is isolated from the old codebase and implements a fresh, two-stage optimization
pipeline for a **Dual Active Bridge (DAB) DC-DC converter** using Triple Phase Shift (TPS)
modulation. The approach is derived directly from the research paper included in the repo
(`Optimal_Design_DAB_Converter.md` / `Optimal_design.pdf`).

---

## What the pipeline does — overview

```
generate_zone_database.py
       |
       |  sweeps all (D1, D2, D0) combinations, classifies each point
       |  into a zone, computes scaled power & Irms, converts to real units
       v
data/phase_shift_zone_database.csv   (millions of candidate operating points)
       |
build_optimized_dataset.py
       |
       |  for every (V2 voltage, target power) pair, picks the candidate
       |  that delivers the right power with the lowest transformer RMS current
       v
data/optimized_operating_points.csv  (one best row per (V2, P_target) pair)
```

`run_pipeline.py` simply calls both scripts in sequence with sensible defaults.

---

## Base converter parameters

| Parameter | Value |
|-----------|-------|
| Switching frequency `fs` | 100 kHz |
| Fixed DC bus voltage `V1` | 200 V |
| Battery voltage `V2` range | 45 V – 55 V |
| Maximum power `P_max` | 3 500 W |
| Design ratio `m*` | 1.3 |

---

## File-by-file explanation

### 1. `generate_zone_database.py`

**Purpose:** Build a comprehensive lookup table of *every feasible operating point* for the
DAB converter under TPS modulation.

**What it does, step by step:**

1. **Design `n` and `L` from the paper (Section II-F).**
   - `n = m* × V1 / V2_min` — transformer turns ratio chosen so the converter operates at
     the optimal normalized voltage ratio `m*` at the worst-case (lowest) battery voltage.
   - `L` is computed from the polynomial fit `p*(m*)` (Equation 15 of the paper):
     `p*(m*) = -1.9m⁴ + 12.6m³ - 30.9m² + 34.3m - 14.07`
     then `L = p*(m*) × V1² / (2π × fs × P_max)`.
   These two values fix the hardware and remain constant throughout the sweep.

2. **Sweep all TPS phase-shift combinations.**
   Three duty-cycle / phase-shift variables `D1`, `D2`, `D0(delta)` are each swept from
   `phase_step` to 1 in increments of `phase_step` (default 0.01), forming a 3-D grid of
   ~99³ ≈ 970 000 candidate points per `V2` voltage.

3. **Classify each point into a Zone (I, II, or V).**
   Each zone corresponds to a different current waveform shape on the transformer.
   Membership is determined by the sign of three algebraic inequalities derived from the
   paper's ZVS/operating-region table:
   - **Zone I** (`mask_zone_i`): `d1 - d2·m > 0`, `d0 - d2 + d2·m > 0`, `d2 + d0 - d2·m < 0`
   - **Zone II** (`mask_zone_ii`): `d1 - d2·m < 0`, `d1·m - d1 + m·d0 < 0`, `d1 - d1·m + m·d0 > 0`
   - **Zone V** (`mask_zone_v`): four combined inequalities ensuring both bridges operate
     in a favorable regime for full ZVS.

4. **Compute scaled power `p` and scaled RMS current `i_rms` for valid points.**
   Each zone has its own analytical formula (from the paper) for the normalized power
   transfer `p` and the normalized RMS current squared `i_rms²`:
   - Zone I: `p = 0.5·m·π·D0·D2`
   - Zone II: `p = 0.5·m·π·D0·D1`
   - Zone V: `p = 0.25·m·π·(1 - (1-D1)² - (1-D2)² - (1-D0)²)`
   RMS expressions are polynomial functions of `(m, D1, D2, D0)` — see `irms2_zone_*`.

5. **Convert to real physical units.**
   - `Power_W = (V1² / (2π·fs·L)) × p_scaled`
   - `Irms_A  = (V1  / (2π·fs·L)) × sqrt(irms2_scaled)`

6. **Filter and save.**
   Only points where `0 ≤ Power_W ≤ P_max` are kept. The result is sorted by
   `[V2_V, Power_W, Irms_A]` and saved to `data/phase_shift_zone_database.csv`.

**Key CLI arguments:**

| Argument | Default | Meaning |
|----------|---------|---------|
| `--v1` | 200 | DC bus voltage (V) |
| `--fs` | 100 000 | Switching frequency (Hz) |
| `--p-max` | 3500 | Maximum power (W) |
| `--v2-min` | 45 | Minimum battery voltage (V) |
| `--v2-max` | 55 | Maximum battery voltage (V) |
| `--v2-step` | 1.0 | Step between V2 values (V) |
| `--m-star` | 1.3 | Optimal normalized voltage ratio |
| `--phase-step` | 0.01 | Grid resolution for D1, D2, D0 |
| `--out` | `data/phase_shift_zone_database.csv` | Output path |

---

### 2. `build_optimized_dataset.py`

**Purpose:** Reduce the large zone database to a *single optimal operating point per
(V2, target power) pair* by minimizing transformer RMS current.

**What it does, step by step:**

1. **Load the zone database** produced by `generate_zone_database.py`.

2. **Define target power values** — a uniform grid from `power_min` to `power_max` with
   step `power_step` (e.g. 0 W, 10 W, 20 W, … 3 500 W).

3. **For each `V2` voltage, for each target power `P_target`:**

   a. **Within-tolerance search:** collect all candidate rows where
      `|Power_W - P_target| ≤ power_tolerance` (default ±2 W).
      Among those, pick the row with the **smallest `Irms_A`** — this is the
      minimum-loss operating point for that exact power level.

   b. **Fallback — nearest power:** if no candidate falls within tolerance, find the
      single closest achievable power in the database and pick the minimum-`Irms_A`
      row at that power.
      - If the nearest power is still further than `max_nearest_error` W away, the
        target is marked `Zone = NO_SOLUTION` with NaN phase-shift values.

4. **Sort and save** the result to `data/optimized_operating_points.csv`.

5. **Print a summary** — total input/output rows, average and worst power error, and
   a count of how many operating points fall into each zone.

**Key CLI arguments:**

| Argument | Default | Meaning |
|----------|---------|---------|
| `--in` | `data/phase_shift_zone_database.csv` | Input database |
| `--out` | `data/optimized_operating_points.csv` | Output path |
| `--power-min` | 0 | Lowest target power (W) |
| `--power-max` | 3500 | Highest target power (W) |
| `--power-step` | 10 | Step between targets (W) |
| `--power-tolerance` | 2 | ±tolerance for "exact" match (W) |
| `--max-nearest-error` | 100 | Max fallback error before NO_SOLUTION (W) |

---

### 3. `run_pipeline.py`

A thin convenience wrapper that calls both scripts in the correct order with the
recommended defaults. Run it from the repository root:

```bash
python3 new_optimal_design_tps/run_pipeline.py
```

---

## Running the pipeline manually

```bash
# Step 1 – generate the zone database (~few minutes for phase-step=0.01)
python3 new_optimal_design_tps/generate_zone_database.py \
  --phase-step 0.01 \
  --v2-step 1.0

# Step 2 – build the optimized operating-point table
python3 new_optimal_design_tps/build_optimized_dataset.py \
  --power-min 0 \
  --power-max 3500 \
  --power-step 10 \
  --power-tolerance 2 \
  --max-nearest-error 100
```

---

## Output columns (final dataset — `optimized_operating_points.csv`)

| Column | Description |
|--------|-------------|
| `Power_Target_W` | Requested power setpoint (W) |
| `V2_V` | Battery-side voltage (V) |
| `D0_delta` | TPS outer phase shift |
| `D1` | Primary bridge duty cycle / phase shift |
| `D2` | Secondary bridge duty cycle / phase shift |
| `Zone` | Operating zone (I, II, V, or NO_SOLUTION) |
| `Irms_A` | Transformer RMS current at this point (A) |
| `Power_Actual_W` | True power delivered by the chosen point (W) |
| `Power_Error_W` | `|Power_Actual_W - Power_Target_W|` (W) |
| `m` | Normalized voltage ratio `n·V2/V1` |
| `p_scaled` | Normalized (per-unit) power |
| `n` | Transformer turns ratio |
| `L_H` | Series inductance (H) |

Rows where no feasible solution is close enough have:
- `Zone = NO_SOLUTION`
- `D0_delta`, `D1`, `D2`, `Irms_A`, `Power_Actual_W` all set to NaN
