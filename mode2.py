"""
-------------------------------------------------------------------------
Mode 2: Power and Irms Dataset Generator
-------------------------------------------------------------------------
Iterates through duty cycles (D0, D1, D2) to generate Power and Irms values
for Mode 2 operational constraints.

Constraints:
- 0 < D1 < D0 < 1
- 1 < D0 + D2 < 1 + D1
-------------------------------------------------------------------------
"""

import numpy as np
import pandas as pd

# --- Given Constants ---
V1 = 200.0          # V1' in Volts
V2 = 50.0           # V2' in Volts
T = 1e-5            # Switching period in Seconds (10 microseconds)
L = 20e-6           # Inductance in Henry

# --- Simulation Parameters ---
step_size = 0.05
duty_cycles = np.arange(0.01, 1.0, step_size)

# --- Data Initialization ---
results = []

print('Generating dataset for Mode 2... This might take a moment.')

# --- Main Loop to Generate Data ---
for D0 in duty_cycles:
    for D1 in duty_cycles:
        for D2 in duty_cycles:
            
            # --- Constraint Checking for Mode 2 ---
            if (D1 < D0) and ((D0 + D2) > 1) and ((D0 + D2) < (1 + D1)):
                
                # --- Power Calculation for Mode 2 ---
                power = (V1*V2*T/L) * (
                    -0.5 + 0.5*D0**2 + 0.5*D1 - D0*D1 + 
                    0.5*D1**2 + 0.5*D2 - 0.5*D1*D2
                )
                
                # --- Irms Calculation for Mode 2 ---
                irms_squared = (T**2/L**2) * (
                    (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
                    (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
                    (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
                    (0.5/3)*(0.25 - 1.5*(2-D0-D2)**2 + (2-D0-D2)**3)*V1*V2 -
                    (0.5/3)*(0.25 - 1.5*(D0-D1)**2 + (D0-D1)**3)*V1*V2 -
                    (0.5/3)*(0.25 - 1.5*(D0+D2-D1)**2 + (D0+D2-D1)**3)*V1*V2 +
                    (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
                )

                Irms = np.sqrt(abs(irms_squared))
                
                # Store the valid data point
                results.append([D0, D1, D2, power, Irms])

print(f'Dataset generation complete. Found {len(results)} valid points.')
print('Now printing the data...\n')

# Convert to DataFrame
df = pd.DataFrame(results, columns=['D0', 'D1', 'D2', 'Power_W', 'Irms_A'])

# --- Print Data ---
if df.empty:
    print('No valid data points found. Try adjusting the step size or constraints.')
else:
    print('------------------------------------------------------------')
    print('  D0\t\t  D1\t\t  D2\t\t Power (W)\t   Irms (A)')
    print('------------------------------------------------------------')
    for _, row in df.iterrows():
        print(f"{row['D0']:.4f}\t\t{row['D1']:.4f}\t\t{row['D2']:.4f}\t\t"
              f"{row['Power_W']:8.2f}\t\t{row['Irms_A']:8.4f}")
    print('------------------------------------------------------------')
    
    # --- Print Irms Range ---
    print(f"\n--- Irms Value Range (Mode 2) ---")
    print(f"Minimum Irms: {df['Irms_A'].min():.4f} A")
    print(f"Maximum Irms: {df['Irms_A'].max():.4f} A")
    print('---------------------------------')
    
    print('\nData printing complete.')
    
    # --- Save to CSV ---
    df.to_csv('mode2_dataset.csv', index=False)
    print('Dataset saved to mode2_dataset.csv')