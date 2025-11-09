# Optimal PWM Control of Dual Active Bridge Converters for EV Charging Applications

**BTP Project | IIT Roorkee | Department of Electrical Engineering**

**Authors:** Harshit Singh (22115065), Jatin Singal (22115074), Karthik Ayangar (22115080)

**Course:** EEN-400A

---

## 📋 Project Overview

This project develops a **data-driven optimization framework** for Pulse-Width Modulation (PWM) control of Dual Active Bridge (DAB) converters in multi-port EV charging stations. The objective is to dynamically adjust the converter's phase-shift parameters (D₀, D₁, D₂) in real-time to:

1. Meet variable power demands
2. Minimize inductor RMS current (Irms)
3. Reduce conduction losses
4. Maximize overall efficiency across all operating conditions

### Key Innovation

Traditional DAB converters use **Single Phase Shift (SPS)** control, which is simple but inefficient under variable loads. This project implements **Triple Phase Shift (TPS)** control with optimization to minimize RMS current, achieving superior efficiency across power ranges.

---

## 🎯 Project Objectives

**Primary Objective:**
$$\text{Minimize: } I_{rms}(D_0, D_1, D_2)$$
$$\text{Subject to: } P(D_0, D_1, D_2) = P_{req}(t)$$

Where:
- **D₀**: External phase shift (between primary and secondary bridges)
- **D₁**: Internal phase shift of primary bridge
- **D₂**: Internal phase shift of secondary bridge
- **Irms**: Inductor RMS current (causes conduction losses)
- **P_req**: Required instantaneous power output

---

## 📁 Project Structure

```
/BTP-DAB-Optimization
│
├── docs/                          # Research papers and project reports
│   ├── BTP_G29.pdf
│   ├── Power_flow_and_inductor_current_analysis.pdf
│   └── BTP_Presentation.pdf
│
├── notebooks/                     # Jupyter notebooks for analysis
│   ├── 01_Analytical_Model.ipynb
│   ├── 02_Data_Generation.ipynb
│   ├── 03_Optimization.ipynb
│   └── 04_ML_Model.ipynb
│
├── scripts/                       # Executable Python scripts
│   └── 05_Dashboard.py
│
├── data/                          # Generated datasets
│   ├── dab_data.csv               # Raw simulation data
│   └── optimized_lookup_table.csv # Final control mapping
│
├── models/                        # Trained ML models
│   └── model.pkl
│
├── constants.py                   # Project constants and parameters
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🧬 Development Stages

### **Stage 1: Analytical Model** (`01_Analytical_Model.ipynb`)

**Objective:** Extract and implement analytical equations from Tong et al. (2016).

**Outputs:**
- Symbolic expressions for Power: $P(D_0, D_1, D_2)$
- Symbolic expressions for Inductor RMS: $I_{rms}(D_0, D_1, D_2)$
- Six operating modes classification
- Verification plots

**Key Equations (from Tong et al. 2016):**

For each of 6 modes, power and RMS current are expressed analytically:

$$P = \frac{V_1 V_2}{L} \cdot f(D_0, D_1, D_2) \text{ [depends on mode]}$$

$$I_{rms} = \sqrt{\frac{1}{T_s} \int_0^{T_s} i_L^2(t) \, dt}$$

Where the inductor current $i_L(t)$ is a superposition of triangular waves controlled by D₀, D₁, D₂.

---

### **Stage 2: Data Generation** (`02_Data_Generation.ipynb`)

**Objective:** Simulate 2-level DAB converter and generate training data.

**Process:**
1. Sweep through D₀, D₁, D₂ parameter space
2. For each combination, compute:
   - Power transfer (P)
   - Inductor RMS current (Irms)
   - Operating mode classification
3. Save to `dab_data.csv`

**Output Format:**
```
D0, D1, D2, Mode, Power_W, Irms_A
0.1, 0.05, 0.1, 1, 500, 2.34
0.1, 0.05, 0.15, 1, 520, 2.41
...
```

**Size:** ~20,000 data points covering feasible operating regions

---

### **Stage 3: Optimization** (`03_Optimization.ipynb`)

**Objective:** Solve the optimization problem for given power demands.

**Algorithm:**
1. For each P_req in range [P_min, P_max]:
   - Initialize from data-based guess
   - Minimize Irms subject to P(D₀, D₁, D₂) = P_req
   - Use scipy.optimize.minimize (SLSQP method)
2. Store optimal (D₀*, D₁*, D₂*) → `optimized_lookup_table.csv`

**Output Format:**
```
Power_req_W, D0_opt, D1_opt, D2_opt, Irms_opt, Mode_opt
100, 0.15, 0.08, 0.12, 0.95, 1
200, 0.22, 0.12, 0.18, 1.32, 1
...
```

**Validation:** Verify P(D₀*, D₁*, D₂*) ≈ P_req with <1% error

---

### **Stage 4: Machine Learning** (`04_ML_Model.ipynb`)

**Objective:** Train neural network for fast, real-time inference.

**Model:**
- **Input:** Power request (P_req), Voltage ratio (k)
- **Output:** Optimal parameters (D₀*, D₁*, D₂*)
- **Architecture:** MLP with layers (2 → 128 → 64 → 32 → 3)
- **Training:** 80% data, 20% test, 10% validation

**Performance:**
- Mean Squared Error (MSE) < 1e-4
- Prediction time: <1ms per sample

**Export:** `models/model.pkl`

---

### **Stage 5: Dashboard & Visualization** (`05_Dashboard.py`)

**Objective:** Interactive visualization and control demonstration.

**Features:**
1. **3D Surfaces:**
   - Power vs (D₀, D₁, D₂)
   - Irms vs (D₀, D₁, D₂)
   - Efficiency landscape

2. **Control Mapping:**
   - Optimal (D₀, D₁, D₂) for any P_req
   - Mode transitions
   - SPS vs. TPS comparison

3. **Dynamic Simulation:**
   - Real-time power profile input
   - Adaptive control response
   - Loss and efficiency tracking

**Run Dashboard:**
```bash
streamlit run scripts/05_Dashboard.py
```

---

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository:**
   ```bash
   cd /workspaces/BTP_G29
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python constants.py
   ```

---

## 📊 Quick Start

### Run All Stages Sequentially

1. **Stage 1 - Analytical Model:**
   ```bash
   jupyter notebook notebooks/01_Analytical_Model.ipynb
   ```

2. **Stage 2 - Data Generation:**
   ```bash
   jupyter notebook notebooks/02_Data_Generation.ipynb
   ```

3. **Stage 3 - Optimization:**
   ```bash
   jupyter notebook notebooks/03_Optimization.ipynb
   ```

4. **Stage 4 - Machine Learning:**
   ```bash
   jupyter notebook notebooks/04_ML_Model.ipynb
   ```

5. **Stage 5 - Dashboard:**
   ```bash
   streamlit run scripts/05_Dashboard.py
   ```

### Generate All Results (Quick Mode)

```bash
python run_pipeline.py --quick
```

---

## 📈 Expected Results

### Efficiency Improvement

| Control Strategy | Efficiency @ 50% Load | Efficiency @ 100% Load |
|------------------|----------------------|----------------------|
| SPS              | 85%                  | 92%                  |
| TPS (Optimized)  | 94%                  | 97%                  |

### RMS Current Reduction

- **SPS:** Irms = 10A (avg) @ 5kW
- **TPS (Optimized):** Irms = 6.5A (avg) @ 5kW → **35% reduction**

### ML Model Performance

- **Training MSE:** <1e-4
- **Inference Time:** <1ms
- **Prediction Accuracy:** ±2% on test set

---

## 🧮 Key Equations Reference

### DAB Converter Power Transfer (Tong et al. 2016)

For Mode 1 (0 < D₁ < D₀ < 1, D₁ < D₀ + D₂ < 1):

$$P = \frac{V_1^2}{2\pi f_s L} [2kφ(1-D_2) - k(D_1^2 + D_2^2 - φ^2 - 2D_1φ)]$$

### Inductor RMS Current

$$I_{rms} = \sqrt{\frac{1}{T} \int_0^T i_L^2(t) \, dt}$$

Where $i_L(t)$ is composed of triangular waveforms shaped by D₀, D₁, D₂.

### Conduction Loss

$$P_{loss} = I_{rms}^2 \cdot R_{esr}$$

Thus, minimizing Irms directly reduces losses.

---

## 📚 References

### Primary References

1. **Tong et al. (2016):** "Power flow and inductor current analysis of PWM control for Dual Active Bridge Converter," IEEE IPEMC-ECCE Asia.
   - Provides the analytical framework for 6-mode operation
   - Defines equations for P and Irms

2. **Zhao et al. (2013):** "Current-stress-optimized switching strategy of isolated bidirectional DC/DC converter with dual-phase-shift control," IEEE Transactions on Industrial Electronics.
   - Motivation for current stress optimization

3. **Kheraluwala et al. (1992):** "Performance characterization of a high-power dual active bridge dc-to-dc converter," IEEE Transactions on Industry Applications.
   - Original DAB topology paper

### Project Report

4. **BTP_G29 (2025):** "Optimal PWM Control of Dual Active Bridge Converters for EV Charging Applications," IIT Roorkee.
   - Complete project documentation
   - Simulation results and implementation details

---

## 🔬 Theoretical Background

### Why DAB for EV Charging?

| Feature              | Benefit for EV Charging |
|----------------------|-------------------------|
| Bidirectional Flow   | Enables Vehicle-to-Grid (V2G) |
| Galvanic Isolation   | Safety, no ground loops |
| Soft Switching (ZVS) | Low EMI, high efficiency |
| High Power Density   | Compact fast-charging stations |
| Modularity          | Scales to multi-port systems |

### The Variable Load Problem

Traditional DAB converters:
- Designed for **fixed nominal power**
- Use pre-set phase shifts (D₀, D₁, D₂)
- Lose efficiency under **variable loads** (typical in charging stations)
- Experience high **circulating currents** and **loss of soft switching**

Our Solution:
- **Real-time, adaptive control** using optimization
- **Minimize Irms** for every power demand
- Maintain **high efficiency across all loads**
- Ready for **ML-based fast inference**

---

## 🎓 Learning Outcomes

By completing this project, you will understand:

1. **Power Electronics:**
   - DAB converter topology and operation
   - Phase-shift modulation and multi-level control
   - Soft-switching and zero-voltage-switching (ZVS)

2. **Control Theory:**
   - Optimization problem formulation
   - Constrained optimization (SLSQP)
   - Real-time parameter adaptation

3. **Data Science & ML:**
   - Dataset generation and preprocessing
   - Neural network regression
   - Model validation and inference

4. **EV Charging Infrastructure:**
   - Multi-port charging challenges
   - State-of-charge (SoC) dynamics
   - Efficiency and thermal management

---

## 🤝 Contributing

To add features or improvements:

1. Create a new branch: `git checkout -b feature/your-feature`
2. Make changes and test thoroughly
3. Commit with clear messages: `git commit -m "Add feature description"`
4. Push and create a pull request

---

## 📝 License

This project is part of the BTP curriculum at IIT Roorkee.

---

## ✉️ Contact

**Project Authors:**
- Harshit Singh (22115065) — [email protected]
- Jatin Singal (22115074) — [email protected]
- Karthik Ayangar (22115080) — [email protected]

**Advisor:** [Advisor Name], Department of Electrical Engineering, IIT Roorkee

---

## 📅 Project Timeline

- **Phase 1 (Sep-Oct 2024):** Literature review, theoretical analysis ✓
- **Phase 2 (Oct-Nov 2024):** Simulation, data generation ✓
- **Phase 3 (Nov 2024):** Optimization algorithm, lookup table generation
- **Phase 4 (Nov-Dec 2024):** ML integration, dashboard development
- **Phase 5 (Dec 2024):** Final testing, documentation, presentation

---

**Last Updated:** November 2024
**Status:** In Development
