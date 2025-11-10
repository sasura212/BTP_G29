"""
constants.py - Project Constants and Parameters
===============================================

This file contains all the constants, parameters, and configuration values
for the DAB Converter Optimization project.

References:
- Tong et al. (2016): "Power flow and inductor current analysis of PWM control for DAB"
- BTP_G29 Project Report, IIT Roorkee
"""

import numpy as np

# ============================================================================
# CONVERTER PARAMETERS (from Tong et al. 2016 and BTP Project)
# ============================================================================

# Inductor
L = 50e-6  # Inductance (Henry) - reduced for higher power capability

# Transformer
TRANSFORMER_RATIO = 1.0  # n = primary/secondary turns ratio

# Voltages (increased for 5kW operation)
V1_PRIMARY = 200.0  # Primary side voltage (Volts) - typical for 5kW EV charger

# IMPORTANT: Avoid algebraic degeneracy at k==1.0
# When k = V2/V1 = 1.0 exactly, Tong et al. RMS formulas contain terms like (1-k)
# and (1-k)^2 that vanish, leaving polynomials that can be negative in some regions.
# A small offset (2%) is physically realistic (tolerances, voltage drops) and
# removes the mathematical degeneracy while producing nearly identical results.
V2_SECONDARY = 196.0  # 0.98 * V1 - small offset to avoid k=1 degeneracy

# Switching
f_s = 20e3  # Switching frequency (Hz)
T_s = 1 / f_s  # Switching period (seconds)
T_half = T_s / 2  # Half switching period (seconds)

# ============================================================================
# CONTROL PARAMETERS
# ============================================================================

# Phase Shift Ranges (normalized: 0 to 1)
D0_MIN, D0_MAX = 0.0, 1.0  # External phase shift (between bridges)
D1_MIN, D1_MAX = 0.0, 1.0  # Internal phase shift (primary bridge)
D2_MIN, D2_MAX = 0.0, 1.0  # Internal phase shift (secondary bridge)

# Resolution for sweep/optimization
D_RESOLUTION = 0.05  # Step size for parameter sweep (coarse: 0.1, fine: 0.05)

# ============================================================================
# SIMULATION PARAMETERS
# ============================================================================

# Power range for optimization
P_MIN = 100  # Minimum power (Watts)
P_MAX = 10000  # Maximum power (Watts)

# Data generation parameters
DATA_POINTS_PER_MODE = 100  # Number of sweep points per mode
NUM_MODES = 6  # Six operating modes as per Tong et al.

# ============================================================================
# OPERATING MODES (from Tong et al. 2016)
# ============================================================================

MODE_DEFINITIONS = {
    1: {
        "name": "Mode 1",
        "condition": "0 < D1 < D0 < 1 and D1 < D0 + D2 < 1",
        "description": "Leading bridge controls primary current rise"
    },
    2: {
        "name": "Mode 2",
        "condition": "0 < D1 < D0 < 1 and 1 < D0 + D2 < 1 + D1",
        "description": "Transition mode between Modes 1 and 3"
    },
    3: {
        "name": "Mode 3",
        "condition": "0 < D1 < D0 < 1 and 1 + D1 < D0 + D2 < 2",
        "description": "Lagging bridge controls current decay"
    },
    4: {
        "name": "Mode 4",
        "condition": "0 < D0 < D1 < 1 and 0 < D0 + D2 < D1",
        "description": "Reverse power flow - Mode 4"
    },
    5: {
        "name": "Mode 5",
        "condition": "0 < D0 < D1 < 1 and D1 < D0 + D2 < 1",
        "description": "Reverse power flow - Mode 5"
    },
    6: {
        "name": "Mode 6",
        "condition": "0 < D0 < D1 < 1 and 1 < D0 + D2 < 1 + D1",
        "description": "Reverse power flow - Mode 6"
    }
}

# ============================================================================
# OPTIMIZATION PARAMETERS
# ============================================================================

# Optimization method
OPTIMIZER_METHOD = "SLSQP"  # Sequential Least Squares Programming
OPTIMIZATION_TOLERANCE = 1e-6

# Constraint tolerance
POWER_CONSTRAINT_TOLERANCE = 0.01  # Percentage tolerance for power constraint

# Initial guess strategy
INITIAL_GUESS_METHOD = "data_based"  # "random", "sps", or "data_based"

# ============================================================================
# MACHINE LEARNING PARAMETERS
# ============================================================================

# Model type
ML_MODEL_TYPE = "MLPRegressor"  # Neural Network

# Neural network architecture
ML_HIDDEN_LAYERS = (128, 64, 32)  # Layer sizes
ML_ACTIVATION = "relu"
ML_MAX_ITERATIONS = 1000
ML_LEARNING_RATE = 0.001
ML_RANDOM_STATE = 42

# Train/test split
ML_TEST_SIZE = 0.2
ML_VALIDATION_SIZE = 0.1

# ============================================================================
# NUMERICAL CONSTANTS
# ============================================================================

PI = np.pi
EPSILON = 1e-12  # Small value to avoid division by zero

# ============================================================================
# EFFICIENCY CALCULATION
# ============================================================================

# Parasitic resistance (ESR) for loss calculation
ESR_PRIMARY = 0.1  # Ohms (estimate from typical MOSFETs + PCB traces)
ESR_SECONDARY = 0.1  # Ohms

# ============================================================================
# PLOTTING DEFAULTS
# ============================================================================

PLOT_RESOLUTION_3D = 30  # Resolution for 3D surface plots
PLOT_DPI = 150
PLOT_FIGSIZE = (12, 8)

# ============================================================================
# FILE PATHS
# ============================================================================

DATA_DIR = "./data/"
MODEL_DIR = "./models/"
NOTEBOOK_DIR = "./notebooks/"
FIGURE_DIR = "./figures/"

# ============================================================================
# REFERENCES
# ============================================================================

REFERENCES = """
[1] Tong, A., Hang, L., Li, G., Guo, Y., Zou, Y., Chen, J., Li, J., Zhuang, J., & Li, S. (2016).
    Power flow and inductor current analysis of PWM control for dual active bridge converter.
    IEEE IPEMC-ECCE Asia, 2016.

[2] Zhao, B., et al. (2013).
    Current-stress-optimized switching strategy of isolated bidirectional DC/DC converter 
    with dual-phase-shift control.
    IEEE Transactions on Industrial Electronics, 60(10), 4458-4467.

[3] Kheraluwala, M. N., Gascoigne, R. W., Divan, D. M., & Baumann, E. D. (1992).
    Performance characterization of a high-power dual active bridge dc-to-dc converter.
    IEEE Transactions on Industry Applications, 28(6), 1294-1301.

[4] BTP_G29 Project Report (2025).
    Optimal PWM Control of Dual Active Bridge Converters for EV Charging Applications.
    Indian Institute of Technology Roorkee.
    Authors: Harshit Singh, Jatin Singal, Karthik Ayangar.
"""

if __name__ == "__main__":
    print("DAB Converter Optimization Constants")
    print("=" * 50)
    print(f"Inductance: {L*1e6:.1f} µH")
    print(f"Switching Frequency: {f_s/1e3:.0f} kHz")
    print(f"Primary Voltage: {V1_PRIMARY:.1f} V")
    print(f"Secondary Voltage: {V2_SECONDARY:.1f} V")
    print(f"Transformer Ratio: {TRANSFORMER_RATIO:.2f}")
    print("=" * 50)
