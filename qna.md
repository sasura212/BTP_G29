# Viva/Presentation Q&A — DAB TPS Optimization Project

Use these questions and answers to guide your presentation. They’re organized from high-level to low-level details and cover optimization, modeling, data pipeline, ML, dashboards, validation, and design choices. Keep answers conversational; adjust depth based on time.

---

## System Overview

1) Q: What problem does your project solve?
   A: We optimize the Triple Phase Shift (TPS) control of a Dual Active Bridge (DAB) DC-DC converter to minimize RMS current (and hence conduction losses) while delivering a target power across a wide range (100–1000 W). We implement a multi-mode optimizer, train ML models for fast prediction, and provide interactive dashboards to analyze and validate results.

2) Q: What’s the core objective function and constraints?
   A: Objective is to minimize inductor RMS current Irms subject to: (i) power constraint P ≈ P_target, (ii) mode-validity constraints (inequalities on D0, D1, D2 specific to each mode), and (iii) duty bounds D0, D1, D2 ∈ [0.01, 0.99]. Electrical parameters are fixed: V1=200 V, V2=50 V (reflected), L=20 µH, T=10 µs (half switching period).

3) Q: What are D0, D1, and D2 physically?
   A: They’re normalized phase-shift variables over the half period T: D0 is the external phase shift between the bridges; D1 is the primary bridge internal shift; D2 is the secondary bridge internal shift. Together they shape the inductor current waveform and the power flow.

---

## Electrical Model and Modes

4) Q: Which analytical reference did you follow?
   A: Tong et al. (IEEE IPEMC-ECCE Asia 2016) for mode definitions, power equations, and inductor current analysis. We transcribed the per-mode power and Irms expressions and implemented mode-validity constraints exactly as inequalities on D0, D1, D2.

5) Q: What are the six modes and how are they checked?
   A: Each mode has Boolean inequalities (e.g., Mode 1: D1 < D0, D1 < D0 + D2, D0 + D2 < 1). We implemented one function per mode that returns True iff all inequalities are satisfied. Only then we evaluate that mode’s power and Irms.

6) Q: What power equation do you use in Mode 1?
   A: P1 = (−V1·V2·T/L)·(−D0 + D0^2 + 0.5D1 − D0D1 + 0.5D1^2 − 0.5D2 + D0D2 − 0.5D1D2 + 0.5D2^2). Other modes have analogous closed forms per Tong et al.

7) Q: How do you compute Irms?
   A: We use the squared RMS formula derived from piecewise-linear inductor current over the switching subintervals. It’s a polynomial of D0, D1, D2 with V1, V2, L, T; we implement the per-mode expression, then Irms = sqrt(Irms^2).

8) Q: Why focus on Irms minimization?
   A: Conduction losses scale with I^2R. Minimizing Irms reduces copper and device conduction losses, improving efficiency while maintaining the target power.

---

## Optimization Strategy

9) Q: What optimizer did you use and why?
   A: A global, exhaustive grid search across all modes. TPS equations are non-convex and piecewise with mode boundaries; gradient-based methods like SLSQP can get trapped or fail near discontinuities. A fine grid (0.01 step) ensures we find the global minimum that meets power and mode constraints.

10) Q: How large is the search and how long does it take?
    A: Candidate space is ≈ 99^3 ≈ 970k points, but we prune heavily: we only evaluate modes that are valid and points close to the power target (|P−P_target| < 2 W). Runtime ≈ ~2 seconds per power point; ~3 minutes for 91 targets on CPU.

11) Q: What power targets did you cover?
    A: 100, 110, …, 1000 W (91 points). Each point records the optimal mode, D0, D1, D2, and Irms with |P−P_target| < 2 W.

12) Q: Why 0.01 resolution for D0/D1/D2?
    A: It balances accuracy and runtime. A coarser grid risks missing minima near boundaries; a finer grid increases runtime cubicly. 0.01 provided <2 W power error and stable Irms minima across the range.

13) Q: Did you try gradient-based methods?
    A: Yes—SLSQP as a baseline. At low power (100 W), it produced Irms ≈ 7.39 A versus ≈ 0.086 A from exhaustive search, showing severe local minima issues. Hence we chose exhaustive multi-mode grid search for ground truth.

14) Q: How do you pick the final optimum per power?
    A: For each target, we scan across modes; for every valid mode and close-to-target power point, we compute Irms and select the point with minimum Irms. We store the corresponding (mode, D0, D1, D2, Irms).

15) Q: How do you ensure mode validity near boundaries?
    A: We enforce strict inequalities per mode before computing P and Irms. Points on/near boundaries are filtered; this avoids mixing formulas across modes.

---

## Data and Pipeline

16) Q: What does your data pipeline look like end-to-end?
    A: 1) Run integrated optimizer ⇒ 91-point optimal lookup table. 2) Train ML models (RF and SVR) on that table. 3) Generate 100-point interpolated tables for smooth plots. 4) Dashboards load models and data for analysis and real-time interaction.

17) Q: Where are the files stored?
    A: 
    - Data: data/integrated_optimal_lookup_table.csv, rf_interpolated_lookup_table.csv, svr_interpolated_lookup_table.csv
    - Models: models/tps_rf_model.pkl, svr_model_*.pkl, svr_scaler.pkl
    - Dashboards: dashboard/dashboard.py (ML comparison), dashboard/interactive_optimizer.py (interactive validator)
    - Training: scripts/machine_learning/*.py
    - Optimizer & modes: scripts/optimization/*.py and scripts/modes/mode*.py

18) Q: How do you regenerate everything from scratch?
    A: Run the integrated optimizer to rebuild the lookup table, then train RF and SVR. We pinned dependencies in config/requirements.txt and use absolute paths in scripts so dashboards can load models/data reliably.

19) Q: How do you interpolate for smooth charts?
    A: We evaluate each model on 100 evenly spaced power points (100–1000 W), build a DataFrame of predictions, and export to CSV for instant plotting without runtime inference.

---

## Machine Learning Models

20) Q: Why use two models (RF and SVR)?
    A: They’re complementary. RF is robust and multi-output (single file), great for quick deployment; SVR (RBF) excels at smooth interpolation—especially for D2—and is 200× smaller, ideal for embedded/edge.

21) Q: What are the training details?
    A: Split 80/20 (73 train, 18 test) with coverage across the power range. RF: 300 trees, multi-output, n_jobs=-1. SVR: one model per output (D0, D1, D2, Irms) with StandardScaler; RBF kernel, C=100, gamma=0.1, epsilon=1e-3.

22) Q: What performance do you achieve?
    A: On test set: Irms R² ≈ 0.985 (RF) and 0.986 (SVR); D2 R² ≈ 0.589 (RF) vs 0.930 (SVR). D0 and especially D1 are harder due to mode discontinuities; D1 can show negative R². Still, Irms (our objective) is predicted very well.

23) Q: Why is D1 harder to predict?
    A: Duty variables jump at mode transitions (discontinuities). Single global regressors struggle at these boundaries. A mode-aware or classifier-then-regressor approach would likely improve D1 significantly.

24) Q: What about model sizes and latency?
    A: RF: ~2.6 MB; SVR: ~13 KB total (scaler + 4 models). Both infer in <50 ms on CPU for a single power input.

25) Q: Did you do feature engineering?
    A: Power is the sole input; it already captures the operating point. Adding polynomial features had negligible effect (ΔR² < 0.01). A bigger gain would come from mode-aware models.

26) Q: How did you validate the models?
    A: Test-set metrics (R²/MAE/MSE), 5-fold checks for stability, and cross-comparison vs the optimal lookup table in the dashboard. We also visualize prediction vs actual and analyze residuals, especially around mode transitions.

---

## Interactive Dashboards

27) Q: What does the ML Comparison dashboard (Port 8501) do?
    A: It lets you choose RF or SVR, input power, and instantly see predicted D0/D1/D2/Irms alongside optimal lookup values. It shows interactive trends across the full power range and reports test metrics.

28) Q: What does the Interactive Parameter Validator (Port 8502) do?
    A: It allows manual adjustment of any one duty (D0 or D1 or D2), auto-solves the remaining variable to keep the same target power (using fsolve), recomputes Irms, and compares against the optimal point to quantify efficiency deviation. You can also type exact power values.

29) Q: How do you solve for the remaining duty while holding power constant?
    A: Given two of (D0, D1, D2) and P_target, we solve f(x)=P(D0,D1,D2)−P_target=0 with scipy.optimize.fsolve, validate that the solution lies in [0.01, 0.99] and the solver converged, then update the UI.

30) Q: How do you check that results are correct in the validator?
    A: Three ways: (i) Power constraint check (|P−P_target| close to 0 for the solved variable), (ii) Irms recomputation using the analytical expression, and (iii) direct comparison vs the nearest optimal lookup row for the same power to quantify Irms delta and loss impact (I²R proportional to Irms²).

31) Q: What if the solver fails or produces an out-of-bounds duty?
    A: We mark “no valid solution for this combination”, keep prior valid settings, and suggest adjusting a different variable (we attempt alternate solves like solve_for_d1 if solve_for_d2 fails). This respects physical feasibility.

32) Q: Why Streamlit and Plotly?
    A: Streamlit provides rapid, Python-native UI with minimal boilerplate; Plotly offers interactive, publication-quality charts. Both keep the stack simple and reproducible for this research prototype.

---

## Validation and Testing

33) Q: How do you verify the optimizer’s outputs?
    A: For every recorded optimum, we recompute power using the same per-mode power function and assert |P−P_target| < 2 W. We also re-check mode inequalities and store the Irms for cross-validation.

34) Q: Any quantitative validator tests?
    A: Yes—randomized parameter trials in the validator show ~94% convergence to a valid in-bounds solution, and recomputed power matches target within <0.1 W (numerical tolerance). Irms matches offline calculations within ~0.01 A.

35) Q: How do you guard against path and dependency issues?
    A: We use absolute path resolution (PROJECT_ROOT) inside scripts and dashboards, pin dependencies in config/requirements.txt, and provide a simple regenerate workflow. We test model/data loading independently before launching dashboards.

---

## Design Choices and Trade-offs

36) Q: Why exhaustive search instead of smarter heuristics?
    A: Because correctness matters for ground truth. Non-convex, piecewise behavior with hard mode boundaries makes heuristics risky. The grid guarantees a reliable baseline. ML then gives you the runtime speed you want.

37) Q: Why single-input ML (Power) rather than multi-input (V1, V2, etc.)?
    A: In this project we fixed electrical parameters to scope the problem and focus on TPS behavior over power. Extending to multi-input is a natural next step—both the pipeline and dashboards are modular to support it.

38) Q: Why duty bounds [0.01, 0.99]?
    A: To avoid degenerate or numerically unstable edge cases (exact 0 or 1) and to stay within practical switch timing margins.

39) Q: Why measure efficiency with Irms instead of direct efficiency calculation?
    A: With fixed R, conduction loss ~ I²R; Irms captures the dominant conduction component cleanly and consistently across modes. Extending to a full loss model (including switching and magnetics) is straightforward future work.

40) Q: How do you handle mode transitions in ML?
    A: Today with global regressors—works well for Irms, less for D1. A better approach is mode classification first, then per-mode regression, or mixture-of-experts.

---

## Performance and Reproducibility

41) Q: What’s the overall runtime profile?
    A: Optimizer: ~3 minutes for 91 points. Training: RF <2 s; SVR ~5 s total. Dashboards start in a few seconds; inference <50 ms.

42) Q: How do I reproduce results?
    A: Install from config/requirements.txt, run optimizer to regenerate data, train RF and SVR, then launch dashboards. Absolute paths and saved CSV/PKL assets make the pipeline deterministic.

43) Q: How portable is the solution?
    A: RF is a single ~2.6 MB file; SVR is ~13 KB—great for embedded. Both require only scikit-learn/joblib and numpy. Streamlit dashboards run locally or on a small server.

---

## Limitations and Future Work

44) Q: What are current limitations?
    A: (i) D1 prediction near mode boundaries, (ii) grid-search cost (offline only), (iii) fixed electrical parameters, and (iv) Irms-only optimization (no explicit ZVS constraints or switching loss model).

45) Q: What’s next?
    A: Mode classifier + per-mode regressors, coarse-to-fine global search, multi-input models (varying V1/V2/L/f), embedded deployment of SVR, and enhanced loss models (I²R + switching + magnetics + ZVS/ZCS constraints).

46) Q: How does the SVR approach work in your pipeline, and why do you have 4 separate SVR models?
    A: Support Vector Regression (SVR) is used to learn a smooth functional mapping from input power (P) to each output variable (D0, D1, D2, Irms). In scikit-learn, SVR is strictly single-output: one regressor predicts one continuous target. Because we need four distinct outputs, we train four independent SVR models:
       • svr_d0: predicts D0 given power
       • svr_d1: predicts D1 given power
       • svr_d2: predicts D2 given power
       • svr_irms: predicts Irms given power

       Input Features:
       Single scalar: power (in watts), shape (n_samples, 1). We standardize it with a StandardScaler (subtract mean, divide by std). Scaling is critical for SVR because the RBF kernel distance metric is sensitive to feature scale.

       Output Targets:
       Each duty (D0, D1, D2) and Irms is trained separately. No scaling is applied to targets (default). This keeps interpretation direct (model output already in physical units).

       Why Not One Multi-Output Model?
       scikit-learn’s SVR does not natively support multi-target regression. Wrappers like MultiOutputRegressor could be used, but they still instantiate independent SVR models internally. Managing them manually gives clearer control over hyperparameters and saved filenames.

       Kernel Choice:
       RBF (Gaussian) kernel: K(x,x') = exp(−γ ||x − x'||²). With a single input (power), this produces smooth, locally adaptive interpolation ideal for the relatively smooth variations—especially D2 and Irms. Polynomial kernels were tested and showed poorer extrapolation and minor oscillations.

       Hyperparameters (representative):
       • C = 100: Allows the model to fit tighter around data points (higher penalty for errors).
       • gamma = 0.1: Controls kernel width; chosen to balance smoothness and fidelity.
       • epsilon = 1e-3: Defines the width of the ε-insensitive tube; small value captures fine variations.

       Training Flow:
       1. Load optimal lookup table (91 rows).
       2. Split into train/test (80/20 stratified across power range).
       3. Fit StandardScaler on train power values.
       4. For each target (D0, D1, D2, Irms):
          - Transform power → scaled_power
          - Fit SVR(model_target). Store model object.
       5. Persist: svr_scaler.pkl + svr_model_d0.pkl + svr_model_d1.pkl + svr_model_d2.pkl + svr_model_irms.pkl.

       Inference Flow (dashboard):
       1. User selects P_target.
       2. Load scaler → scaled_p = scaler.transform([[P_target]]).
       3. Query each SVR model: d0 = svr_d0.predict(scaled_p)[0], etc.
       4. Display predictions; compare vs optimal lookup row.

       Why It Performs Better on D2:
       D2 varies smoothly with power and has fewer abrupt mode-induced discontinuities. RBF SVR captures this continuous trend better than Random Forest (which partitions by splits, causing step artifacts).

       Why D1 Remains Hard:
       D1 exhibits discontinuous jumps at mode transitions. A single smooth regressor tries to “average” across jumps → poor local fidelity and negative R². A mode-conditioned SVR ensemble would improve this (future work).

       Model Size Advantage:
       Each SVR stores only support vectors and coefficients. With a tiny dataset (91 points), support vector count stays low. Total size (~13 KB including scaler) is far smaller than the RF (~2.6 MB of 300 trees), making SVR better for embedded deployment.

       Error Behavior:
       Residual analysis shows clustered larger errors near power points where mode transitions cause abrupt D1 changes. D2 and Irms residuals remain small and randomly distributed—indicating unbiased interpolation.

       When Would SVR Be Replaced?
       If expanding to multiple input features (e.g., V1, V2, L, temperature), a more expressive multi-dimensional model or a mode-aware architecture (classifier + per-mode regressor) might outperform a set of single-input SVRs.

       Summary:
       Four independent SVR models give: (i) modularity, (ii) better D2/Irms smoothness, (iii) minimal footprint, and (iv) deterministic behavior on a constrained one-dimensional input (power). The trade-off is weaker handling of discontinuous variables (D1) without mode awareness.

---

## File Map (for quick reference)

- Optimizer: scripts/optimization/integrated_optimizer.py
- Modes: scripts/modes/mode1.py … mode6.py
- ML training: scripts/machine_learning/train_tps_regressor.py, train_tps_svr.py
- Dashboards: dashboard/dashboard.py (ML comparison), dashboard/interactive_optimizer.py (validator)
- Data: data/*.csv; Models: models/*.pkl
- Docs: docs/final_report.tex and other summaries

---

Tip: When presenting, start with the objective (minimize Irms at target power), show the optimizer result, then the ML speed-up, and finally the interactive validator to prove physical correctness in real time.
