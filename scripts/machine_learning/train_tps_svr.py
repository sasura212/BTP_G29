"""
===========================================================
Support Vector Regression (SVR) Training for TPS Parameter Prediction
===========================================================

Trains separate SVR models to predict optimal D0, D1, D2, and Irms
from target power level using the integrated optimal lookup table.

Author: Harshit Singh (BTP Project, IIT Roorkee)
Date: November 2025
===========================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib
import os

# Get project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

print("=" * 70)
print("TPS SUPPORT VECTOR REGRESSION (SVR) TRAINING")
print("=" * 70)

# ============================================================================
# 1. Load and Prepare Data
# ============================================================================
print("\n📂 Loading dataset...")
df = pd.read_csv(os.path.join(PROJECT_ROOT, 'data', 'integrated_optimal_lookup_table.csv'))

# Sort by power and drop NaNs
df = df.sort_values('Power_Target_W').dropna()

print(f"   ✓ Loaded {len(df)} data points")
print(f"   ✓ Power range: {df['Power_Target_W'].min():.0f}W to {df['Power_Target_W'].max():.0f}W")

# Define features (X) and targets (y)
X = df[['Power_Target_W']].values
y = df[['D0', 'D1', 'D2', 'Irms_A']].values

print(f"   ✓ Feature shape: {X.shape}")
print(f"   ✓ Target shape: {y.shape}")

# ============================================================================
# 2. Feature Scaling (Important for SVR!)
# ============================================================================
print("\n🔧 Scaling features...")
scaler_X = StandardScaler()
X_scaled = scaler_X.fit_transform(X)
print("   ✓ Power values scaled to zero mean and unit variance")

# ============================================================================
# 3. Split Dataset
# ============================================================================
print("\n🔀 Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42
)

print(f"   ✓ Training samples: {len(X_train)}")
print(f"   ✓ Test samples: {len(X_test)}")

# ============================================================================
# 4. Train Separate SVR Models for Each Output
# ============================================================================
target_names = ['D0', 'D1', 'D2', 'Irms_A']
models = {}

print("\n🤖 Training SVR models...")
print("   Parameters: kernel='rbf', C=100, gamma=0.1, epsilon=0.001")
print()

for i, target in enumerate(target_names):
    print(f"   Training SVR for {target}...")
    
    # Create and train SVR model
    model = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.001)
    model.fit(X_train, y_train[:, i])
    
    # Make predictions
    y_train_pred = model.predict(X_train)
    y_test_pred = model.predict(X_test)
    
    # Calculate R² scores
    train_r2 = r2_score(y_train[:, i], y_train_pred)
    test_r2 = r2_score(y_test[:, i], y_test_pred)
    
    # Calculate additional metrics
    mae = mean_absolute_error(y_test[:, i], y_test_pred)
    rmse = np.sqrt(mean_squared_error(y_test[:, i], y_test_pred))
    
    print(f"      Train R² = {train_r2:.6f}")
    print(f"      Test R²  = {test_r2:.6f}")
    print(f"      MAE      = {mae:.6f}")
    print(f"      RMSE     = {rmse:.6f}")
    
    # Store model
    models[target] = model
    
    # Save model
    filename = os.path.join(PROJECT_ROOT, 'models', f"svr_model_{target}.pkl")
    joblib.dump(model, filename)
    print(f"      ✓ Saved: models/svr_model_{target}.pkl")
    print()

# Save the scaler as well
joblib.dump(scaler_X, os.path.join(PROJECT_ROOT, 'models', 'svr_scaler.pkl'))
print("   ✓ Saved: models/svr_scaler.pkl (feature scaler)")

# ============================================================================
# 5. Calculate Overall Performance
# ============================================================================
print("\n📊 Overall Model Performance:")

# Predict all outputs on test set
y_test_pred_all = np.column_stack([
    models[target].predict(X_test) for target in target_names
])

overall_train_r2 = np.mean([
    r2_score(y_train[:, i], models[target].predict(X_train))
    for i, target in enumerate(target_names)
])
overall_test_r2 = np.mean([
    r2_score(y_test[:, i], y_test_pred_all[:, i])
    for i in range(len(target_names))
])

print(f"   Average Train R²: {overall_train_r2:.6f}")
print(f"   Average Test R²:  {overall_test_r2:.6f}")

# ============================================================================
# 6. Generate Interpolated Predictions
# ============================================================================
print("\n🔮 Generating interpolated predictions...")

# Create fine-grained power values
power_values = np.linspace(100, 1000, 100).reshape(-1, 1)
power_values_scaled = scaler_X.transform(power_values)

# Predict each output
predictions = {}
for target in target_names:
    predictions[target] = models[target].predict(power_values_scaled)

# Create DataFrame
interpolated_df = pd.DataFrame({
    'Power_W': power_values.flatten(),
    'D0_pred': predictions['D0'],
    'D1_pred': predictions['D1'],
    'D2_pred': predictions['D2'],
    'Irms_pred': predictions['Irms_A']
})

interpolated_df.to_csv(os.path.join(PROJECT_ROOT, 'data', 'svr_interpolated_lookup_table.csv'), index=False)
print(f"   ✓ Generated {len(interpolated_df)} interpolated points")
print("   ✓ Saved: data/svr_interpolated_lookup_table.csv")

# ============================================================================
# 7. Visualization
# ============================================================================
print("\n📈 Generating prediction plots...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Support Vector Regression: Predicted vs Actual', 
             fontsize=16, fontweight='bold')

for i, (ax, target) in enumerate(zip(axes.flat, target_names)):
    # Predict on test set
    y_pred = models[target].predict(X_test)
    
    # Plot test predictions
    ax.scatter(y_test[:, i], y_pred, alpha=0.7, s=60, 
               label='Test', color='green', edgecolors='black', linewidth=0.5)
    
    # Perfect prediction line
    min_val = min(y_test[:, i].min(), y_pred.min())
    max_val = max(y_test[:, i].max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2.5, 
            label='Perfect Prediction')
    
    # Labels and formatting
    ax.set_xlabel(f'Actual {target}', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'Predicted {target}', fontsize=12, fontweight='bold')
    
    test_r2 = r2_score(y_test[:, i], y_pred)
    ax.set_title(f'{target} (Test R²={test_r2:.4f})', fontsize=13)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    
plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, 'figures', 'svr_predictions_vs_actual.png'), dpi=150, bbox_inches='tight')
print("   ✓ Saved plot: figures/svr_predictions_vs_actual.png")

# ============================================================================
# 8. Additional Visualization: Power vs Predictions
# ============================================================================
print("\n📊 Generating power vs prediction trends...")

fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle('SVR Predictions vs Power Level', 
              fontsize=16, fontweight='bold')

pred_cols = ['D0_pred', 'D1_pred', 'D2_pred', 'Irms_pred']
data_cols = ['D0', 'D1', 'D2', 'Irms_A']

for i, (ax, target, pred_col, data_col) in enumerate(zip(axes2.flat, target_names, pred_cols, data_cols)):
    # Plot interpolated predictions
    ax.plot(interpolated_df['Power_W'], 
            interpolated_df[pred_col], 
            'b-', linewidth=2, label='SVR Prediction')
    
    # Plot actual training data
    ax.scatter(df['Power_Target_W'], df[data_col], 
               alpha=0.5, s=40, color='red', 
               label='Training Data', edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('Power (W)', fontsize=12, fontweight='bold')
    ax.set_ylabel(f'{target}', fontsize=12, fontweight='bold')
    ax.set_title(f'{target} vs Power', fontsize=13)
    ax.legend(loc='best', fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(os.path.join(PROJECT_ROOT, 'figures', 'svr_power_trends.png'), dpi=150, bbox_inches='tight')
print("   ✓ Saved plot: figures/svr_power_trends.png")

# ============================================================================
# 9. Performance Summary Table
# ============================================================================
print("\n" + "=" * 70)
print("📋 PERFORMANCE SUMMARY")
print("=" * 70)

print("\n{:<12} {:<15} {:<15} {:<12} {:<12}".format(
    "Output", "Train R²", "Test R²", "MAE", "RMSE"
))
print("-" * 70)

for i, target in enumerate(target_names):
    y_train_pred = models[target].predict(X_train)
    y_test_pred = models[target].predict(X_test)
    
    train_r2 = r2_score(y_train[:, i], y_train_pred)
    test_r2 = r2_score(y_test[:, i], y_test_pred)
    mae = mean_absolute_error(y_test[:, i], y_test_pred)
    rmse = np.sqrt(mean_squared_error(y_test[:, i], y_test_pred))
    
    print("{:<12} {:<15.6f} {:<15.6f} {:<12.6f} {:<12.6f}".format(
        target, train_r2, test_r2, mae, rmse
    ))

print("-" * 70)
print("{:<12} {:<15.6f} {:<15.6f}".format(
    "AVERAGE", overall_train_r2, overall_test_r2
))

# ============================================================================
# 10. Final Summary
# ============================================================================
print("\n" + "=" * 70)
print("✅ SVR MODEL TRAINING COMPLETE")
print("=" * 70)
print(f"   Average Test R²: {overall_test_r2:.6f}")
print(f"\n   Saved files:")
print(f"      • svr_model_D0.pkl")
print(f"      • svr_model_D1.pkl")
print(f"      • svr_model_D2.pkl")
print(f"      • svr_model_Irms_A.pkl")
print(f"      • svr_scaler.pkl (feature scaler)")
print(f"      • svr_interpolated_lookup_table.csv (100 interpolated points)")
print(f"      • svr_predictions_vs_actual.png (validation plots)")
print(f"      • svr_power_trends.png (power vs prediction trends)")
print("\n   Usage example:")
print("      import joblib, numpy as np")
print("      scaler = joblib.load('svr_scaler.pkl')")
print("      model_D0 = joblib.load('svr_model_D0.pkl')")
print("      power_scaled = scaler.transform([[500]])")
print("      D0 = model_D0.predict(power_scaled)[0]  # Predict for 500W")
print("=" * 70)
print("\n✅ SVR interpolation complete")
print("Interpolated dataset saved as svr_interpolated_lookup_table.csv")
print("=" * 70)
