# New Paper-Aligned DAB Optimization Pipeline

This folder is isolated from the old codebase and implements a fresh flow based on the attached research paper:

1. Generate a phase-shift database by sweeping `D0(delta)`, `D1`, `D2`.
2. Classify feasible points into Zone I / II / V using the paper constraints.
3. Compute scaled power `p`, scaled RMS `i_rms`, and then actual `Power_W`, `Irms_A`.
4. For each target power and each battery voltage (`V2`), pick the minimum `Irms` candidate within tolerance.

## Base setup used

- Switching frequency: 100 kHz
- Power range: 0 to 3.5 kW
- Fixed voltage `V1`: 200 V
- Battery voltage `V2`: 45 to 55 V

## Files

- `generate_zone_database.py` -> creates `data/phase_shift_zone_database.csv`
- `build_optimized_dataset.py` -> creates `data/optimized_operating_points.csv`

## Run

```bash
python3 new_optimal_design_tps/generate_zone_database.py \
  --phase-step 0.01 \
  --v2-step 1.0

python3 new_optimal_design_tps/build_optimized_dataset.py \
  --power-min 0 \
  --power-max 3500 \
  --power-step 10 \
  --power-tolerance 2 \
  --max-nearest-error 100
```

## Output columns (final dataset)

- `Power_Target_W`
- `V2_V`
- `D0_delta`, `D1`, `D2`
- `Zone`
- `Irms_A`
- `Power_Actual_W`
- `Power_Error_W`
- `m`, `p_scaled`, `n`, `L_H`

If no feasible point is close enough, the row is marked with:

- `Zone = NO_SOLUTION`
- `D0_delta`, `D1`, `D2`, `Irms_A` as empty values
