# -------------------------------------------------------------------------
# Script to Generate and Print Power and Irms Data for Mode 5
# -------------------------------------------------------------------------
# This script iterates through duty cycles (D0, D1, D2) to generate a
# dataset for Power and Irms values based on the specific equations and
# constraints for Mode 5.
# -------------------------------------------------------------------------

import numpy as np

# --- Given Constants ---
V1 = 200          # V1' in Volts
V2 = 50           # V2' in Volts
T = 1e-5          # Switching period in Seconds (10 microseconds)
L = 20e-6         # Inductance in Henry

# --- Simulation Parameters ---
# Define the step size for iterating through duty cycles.
# A smaller step size creates a more detailed dataset but takes longer.
step_size = 0.05
duty_cycles = np.arange(0.01, 1.0, step_size)

# --- Data Initialization ---
results = []

print('Generating dataset for Mode 5... This might take a moment.')

# --- Main Loop to Generate Data ---
# Iterate through all combinations of D0, D1, and D2.
for D0 in duty_cycles:
    for D1 in duty_cycles:
        for D2 in duty_cycles:
            
            # --- Constraint Checking for Mode 5 ---
            # Conditions: 0 < D0 < D1 < 1 && D1 < D0 + D2 < 1
            if (D0 < D1) and (D1 < (D0 + D2)) and ((D0 + D2) < 1):
                
                # --- Power Calculation for Mode 5 (Corrected based on user-provided formula) ---
                power = (-(V1*V2*T)/L) * (-D0 + 0.5*D0**2 + 0.5*D1 - 0.5*D2 + D0*D2 - 0.5*D1*D2 + 0.5*D2**2)
                
                # --- Irms Calculation for Mode 5 ---
                # x(1) = D0, x(2) = D1, x(3) = D2
                irms_squared = (T**2/L**2) * (
                    (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
                    (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
                    (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
                    (0.5/3)*(0.25 - 1.5*(D0+D2)**2 + (D0+D2)**3)*V1*V2 -
                    (0.5/3)*(0.25 - 1.5*(D1-D0)**2 + (D1-D0)**3)*V1*V2 -
                    (0.5/3)*(0.25 - 1.5*(D0+D2-D1)**2 + (D0+D2-D1)**3)*V1*V2 +
                    (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2 )

                Irms = np.sqrt(irms_squared)
                
                # Store the valid data point
                results.append([D0, D1, D2, power, Irms])

print(f'Dataset generation complete. Found {len(results)} valid points.')
print('Now printing the data...\n')

# Convert the list to a numpy array for easier processing
dataSet = np.array(results)

# --- Print Data to Command Window ---
if len(dataSet) == 0:
    print('No valid data points found. Try adjusting the step size or constraints.')
else:
    # Print header
    print('------------------------------------------------------------')
    print('  D0\t\t  D1\t\t  D2\t\t Power (W)\t   Irms (A)')
    print('------------------------------------------------------------')

    # Loop through the dataset and print each row
    for i in range(dataSet.shape[0]):
        print(f'{dataSet[i,0]:.4f}\t\t{dataSet[i,1]:.4f}\t\t{dataSet[i,2]:.4f}\t\t{dataSet[i,3]:8.2f}\t\t{dataSet[i,4]:8.4f}')
    print('------------------------------------------------------------')

    # --- Print Irms Range ---
    min_irms = np.min(dataSet[:, 4])
    max_irms = np.max(dataSet[:, 4])
    print('\n--- Irms Value Range (Mode 5) ---')
    print(f'Minimum Irms: {min_irms:.4f} A')
    print(f'Maximum Irms: {max_irms:.4f} A')
    print('---------------------------------')

    print('\nData printing complete.')

    # --- Optional: Save to CSV ---
    # Uncomment the following lines to save the generated data to a CSV file.
    # import pandas as pd
    # df = pd.DataFrame(dataSet, columns=['D0', 'D1', 'D2', 'Power_W', 'Irms_A'])
    # df.to_csv('power_irms_dataset_mode5.csv', index=False)
    # print('Dataset saved to power_irms_dataset_mode5.csv')