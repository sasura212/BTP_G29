# DAB Triple Phase Shift (TPS) Optimization Project

## Overview
This project implements optimal control parameter selection for Dual Active Bridge (DAB) converters using Triple Phase Shift (TPS) modulation, based on Tong et al. (2016) analytical methods.

## Project Structure

```
BTP_G29/
├── dataset_generator.py          # SLSQP optimization-based approach
├── integrated_optimizer.py       # Multi-mode grid-search approach ⭐
├── mode1.py ... mode6.py         # Individual mode dataset generators (all 6 modes)
├── optimized_lookup_table_tps.csv          # SLSQP results
├── integrated_optimal_lookup_table.csv     # Grid-search results
└── requirements.txt
```

## Key Scripts

### 1. **`integrated_optimizer.py`** ⭐ (Recommended)
Exhaustive multi-mode grid-search for global optimum.

**Pros:**
- Searches ALL modes simultaneously
- Finds global optimum (with fine grid)
- No local minima issues

```bash
# Full run (20 points, step=0.01, ~10 minutes)
python3 integrated_optimizer.py

# Quick test (5 points)
python3 integrated_optimizer.py --test
```

**Output:** `integrated_optimal_lookup_table.csv`

---

### 2. **`dataset_generator.py`** (Fast Alternative)
Uses scipy SLSQP optimizer with analytical gradients.

**Pros:**
- Fast (< 1 second for 20 points)
- Continuous solution space

**Cons:**
- May miss global optimum

```bash
python3 dataset_generator.py
```

**Output:** `optimized_lookup_table_tps.csv`

---

### 3. **`mode1.py` ... `mode6.py`** (Educational)
Generate complete datasets for individual operating modes.

```bash
python3 mode1.py  # Creates mode1_dataset.csv
```

---

## Installation

```bash
pip install -r requirements.txt
```

Dependencies: `numpy`, `pandas`, `scipy`, `tqdm`

---

## Operating Modes

| Mode | Constraints | Power Range |
|------|------------|-------------|
| 1 | D1 < D0, D1 < D0+D2, D0+D2 < 1 | High |
| 2 | D1 < D0, 1 < D0+D2 < 1+D1 | Low-Med |
| 3 | D1 < D0, 1+D1 < D0+D2 < 2 | Low |
| 4 | D0 < D1, 0 < D0+D2 < D1 | Medium |
| 6 | D0 < D1, 1 < D0+D2 < 1+D1 | Low |

---

## System Parameters

- V1 = 200 V, V2 = 50 V
- T = 10 μs, L = 20 μH
- Power: 100 – 1000 W

---

## Citation

Based on: Tong et al. (2016), "Analytical Model for Triple Phase Shift Control for DAB Converters"

---

## Author

Harshit Singh | BTP Project, IIT Roorkee | November 2025

