

import numpy as np
import pandas as pd
from tqdm import tqdm

# === System Constants ===
V1 = 200.0
V2 = 50.0
T = 1e-5
L = 20e-6

# === Simulation Parameters ===
step_size = 0.01  # Finer resolution for better accuracy
duty_cycles = np.arange(0.01, 1.0, step_size)
power_tolerance = 2.0  # Watts - tighter power matching


# === Mode-Specific Constraint Checkers ===
def is_valid_mode1(D0, D1, D2):
    """Mode 1: D1 < D0, D1 < D0+D2, D0+D2 < 1"""
    return (D1 < D0) and (D1 < (D0 + D2)) and ((D0 + D2) < 1)


def is_valid_mode2(D0, D1, D2):
    """Mode 2: D1 < D0, 1 < D0+D2 < 1+D1"""
    return (D1 < D0) and ((D0 + D2) > 1) and ((D0 + D2) < (1 + D1))


def is_valid_mode3(D0, D1, D2):
    """Mode 3: D1 < D0, 1+D1 < D0+D2 < 2"""
    return (D1 < D0) and ((D0 + D2) > (1 + D1)) and ((D0 + D2) < 2)


def is_valid_mode4(D0, D1, D2):
    """Mode 4: D0 < D1, 0 < D0+D2 < D1"""
    return (D0 < D1) and (D1 < 1) and ((D0 + D2) > 0) and ((D0 + D2) < D1)


def is_valid_mode5(D0, D1, D2):
    """Mode 5: D0 < D1, D1 < D0+D2 < 1"""
    return (D0 < D1) and (D1 < (D0 + D2)) and ((D0 + D2) < 1)


def is_valid_mode6(D0, D1, D2):
    """Mode 6: D0 < D1, 1 < D0+D2 < 1+D1"""
    return (D0 < D1) and ((D0 + D2) > 1) and ((D0 + D2) < (1 + D1))


# === Mode-Specific Power Equations ===
def power_mode1(D0, D1, D2):
    """Generic TPS power equation"""
    return (-(V1*V2*T)/L) * (
        -D0 + D0**2 + 0.5*D1 - D0*D1 + 0.5*D1**2 -
        0.5*D2 + D0*D2 - 0.5*D1*D2 + 0.5*D2**2
    )


def power_mode2(D0, D1, D2):
    """Mode 2 power equation"""
    return (V1*V2*T/L) * (
        -0.5 + 0.5*D0**2 + 0.5*D1 - D0*D1 + 
        0.5*D1**2 + 0.5*D2 - 0.5*D1*D2
    )


def power_mode3(D0, D1, D2):
    """Mode 3 power equation"""
    return (V1*V2*T/L) * (
        -1 + D0 - 0.5*D1 + 1.5*D2 - 
        D0*D2 + 0.5*D1*D2 - 0.5*D2**2
    )


def power_mode4(D0, D1, D2):
    """Mode 4 power equation"""
    return (-(V1*V2*T)/L) * (
        -D0 + 0.5*D1 + D0*D1 - 0.5*D1**2 - 
        0.5*D2 + 0.5*D1*D2
    )


def power_mode5(D0, D1, D2):
    """Mode 5 power equation"""
    return (-(V1*V2*T)/L) * (
        -D0 + 0.5*D0**2 + 0.5*D1 - 0.5*D2 + 
        D0*D2 - 0.5*D1*D2 + 0.5*D2**2
    )


def power_mode6(D0, D1, D2):
    """Mode 6 power equation"""
    return (-(V1*V2*T)/L) * (
        -0.5 + 0.5*D1 + 0.5*D2 - 0.5*D1*D2
    )


# === Universal Irms Calculation ===
def calculate_irms_mode1(D0, D1, D2):
    """Irms for Mode 1"""
    irms_squared = (T/L)**2 * (
        (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
        (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
        (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0+D2)**2 + (D0+D2)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0-D1)**2 + (D0-D1)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0+D2-D1)**2 + (D0+D2-D1)**3)*V1*V2 +
        (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
    )
    return np.sqrt(abs(irms_squared))


def calculate_irms_mode2(D0, D1, D2):
    """Irms for Mode 2"""
    irms_squared = (T**2/L**2) * (
        (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
        (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
        (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(2-D0-D2)**2 + (2-D0-D2)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0-D1)**2 + (D0-D1)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0+D2-D1)**2 + (D0+D2-D1)**3)*V1*V2 +
        (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
    )
    return np.sqrt(abs(irms_squared))


def calculate_irms_mode3(D0, D1, D2):
    """Irms for Mode 3"""
    irms_squared = (T**2/L**2) * (
        (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
        (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
        (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(2-D0-D2)**2 + (2-D0-D2)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0-D1)**2 + (D0-D1)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(2-D0-D1+D2)**2 + (2-D0-D1+D2)**3)*V1*V2 +
        (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
    )
    return np.sqrt(abs(irms_squared))


def calculate_irms_mode4(D0, D1, D2):
    """Irms for Mode 4"""
    irms_squared = (T**2/L**2) * (
        (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
        (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
        (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0+D2)**2 + (D0+D2)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D1-D0)**2 + (D1-D0)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D1-D0-D2)**2 + (D1-D0-D2)**3)*V1*V2 +
        (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
    )
    return np.sqrt(abs(irms_squared))


def calculate_irms_mode5(D0, D1, D2):
    """Irms for Mode 5"""
    irms_squared = (T**2/L**2) * (
        (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
        (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
        (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0+D2)**2 + (D0+D2)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D1-D0)**2 + (D1-D0)**3)*V1*V2 -
        (0.5/3)*(0.25 - 1.5*(D0+D2-D1)**2 + (D0+D2-D1)**3)*V1*V2 +
        (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
    )
    return np.sqrt(abs(irms_squared))


def calculate_irms_mode6(D0, D1, D2):
    """Irms for Mode 6"""
    irms_squared = (T**2/L**2) * (
        (1/24)*(V1**2) + (1/24)*(V2**2) +
        (1/6)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
        (1/6)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
        (1/6)*(0.25 - 1.5*(2-D0-D2)**2 + (2-D0-D2)**3)*V1*V2 -
        (1/6)*(0.25 - 1.5*(D1-D0)**2 + (D1-D0)**3)*V1*V2 +
        (1/6)*(0.25 - 1.5*(D0+D2-D1)**2 + (D0+D2-D1)**3)*V1*V2 +
        (1/6)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
    )
    return np.sqrt(abs(irms_squared))


# === Mode Configuration ===
MODES = {
    1: {
        'constraint': is_valid_mode1,
        'power': power_mode1,
        'irms': calculate_irms_mode1
    },
    2: {
        'constraint': is_valid_mode2,
        'power': power_mode2,
        'irms': calculate_irms_mode2
    },
    3: {
        'constraint': is_valid_mode3,
        'power': power_mode3,
        'irms': calculate_irms_mode3
    },
    4: {
        'constraint': is_valid_mode4,
        'power': power_mode4,
        'irms': calculate_irms_mode4
    },
    5: {
        'constraint': is_valid_mode5,
        'power': power_mode5,
        'irms': calculate_irms_mode5
    },
    6: {
        'constraint': is_valid_mode6,
        'power': power_mode6,
        'irms': calculate_irms_mode6
    }
}


def find_optimal_for_power(P_target):
    """
    For a given target power, search all modes and return the
    (D0, D1, D2, mode) combination with minimum Irms.
    """
    candidates = []
    
    # Search all modes
    for mode_num, mode_funcs in MODES.items():
        for D0 in duty_cycles:
            for D1 in duty_cycles:
                for D2 in duty_cycles:
                    
                    # Check if this combination is valid for this mode
                    if not mode_funcs['constraint'](D0, D1, D2):
                        continue
                    
                    # Calculate power
                    P_actual = mode_funcs['power'](D0, D1, D2)
                    
                    # Check if power matches target (within tolerance)
                    if abs(P_actual - P_target) > power_tolerance:
                        continue
                    
                    # Calculate Irms
                    Irms = mode_funcs['irms'](D0, D1, D2)
                    
                    # Store candidate
                    candidates.append({
                        'D0': D0,
                        'D1': D1,
                        'D2': D2,
                        'Mode': mode_num,
                        'Power_W': P_actual,
                        'Irms_A': Irms,
                        'Power_Error_W': abs(P_actual - P_target)
                    })
    
    if not candidates:
        return None
    
    # Find the candidate with minimum Irms
    best = min(candidates, key=lambda x: x['Irms_A'])
    return best


# === Main Execution ===
if __name__ == "__main__":
    import sys
    
    # Check for test mode
    test_mode = '--test' in sys.argv
    
    # Define power sweep range
    if test_mode:
        power_targets = np.array([100, 300, 500, 700, 1000])
        print("🧪 TEST MODE: Running with 5 power points only")
    else:
        # Full lookup table: 100W to 1000W in steps of 10W (91 points)
        power_targets = np.arange(100, 1001, 10)
    
    print("=" * 70)
    print(" Integrated Multi-Mode TPS Optimization")
    print("=" * 70)
    print(f"Power range: {power_targets[0]:.0f} - {power_targets[-1]:.0f} W")
    print(f"Step size: {step_size}")
    print(f"Power tolerance: ±{power_tolerance} W")
    print(f"Searching across Modes: {list(MODES.keys())}")
    print("=" * 70)
    print()
    
    results = []
    
    for P_target in tqdm(power_targets, desc="Optimizing"):
        optimal = find_optimal_for_power(P_target)
        
        if optimal is None:
            print(f"⚠️  No valid solution found for P={P_target:.1f} W")
            continue
        
        results.append([
            P_target,
            optimal['D0'],
            optimal['D1'],
            optimal['D2'],
            optimal['Irms_A'],
            optimal['Power_W'],
            optimal['Power_Error_W'],
            optimal['Mode']
        ])
        
        print(f"P={P_target:6.1f} W → Mode {optimal['Mode']} | "
              f"D0={optimal['D0']:.4f}, D1={optimal['D1']:.4f}, D2={optimal['D2']:.4f} | "
              f"Irms={optimal['Irms_A']:6.4f} A | Error={optimal['Power_Error_W']:.2f} W")
    
    # Create DataFrame and save
    df = pd.DataFrame(results, columns=[
        'Power_Target_W', 'D0', 'D1', 'D2', 'Irms_A', 
        'Power_Actual_W', 'Power_Error_W', 'Mode'
    ])
    
    df.to_csv('integrated_optimal_lookup_table.csv', index=False)
    
    print("\n" + "=" * 70)
    print("✅ Optimization Complete!")
    print("=" * 70)
    print(f"Total solutions found: {len(df)}")
    print(f"Average Irms: {df['Irms_A'].mean():.4f} A")
    print(f"Min Irms: {df['Irms_A'].min():.4f} A @ {df.loc[df['Irms_A'].idxmin(), 'Power_Target_W']:.0f} W")
    print(f"Max Irms: {df['Irms_A'].max():.4f} A @ {df.loc[df['Irms_A'].idxmax(), 'Power_Target_W']:.0f} W")
    print(f"Average Power Error: {df['Power_Error_W'].mean():.4f} W")
    print(f"\nMode distribution:")
    print(df['Mode'].value_counts().sort_index())
    print(f"\nSaved to: integrated_optimal_lookup_table.csv")
    print("=" * 70)
