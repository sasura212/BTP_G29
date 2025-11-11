"""
===========================================================
Random Forest Regressor Training for TPS Parameter Prediction
===========================================================

Trains a Random Forest model to predict optimal D0, D1, D2, and Irms
from target power level using the integrated optimal lookup table.

Author: Harshit Singh (BTP Project, IIT Roorkee)
Date: November 2025
===========================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import joblib

print("=" * 70)
print("TPS RANDOM FOREST REGRESSOR TRAINING")
print("=" * 70)

# ============================================================================
# 1. Load and Prepare Data
# ============================================================================
print("\n📂 Loading dataset...")
df = pd.read_csv('integrated_optimal_lookup_table.csv')

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
# 2. Split Dataset
# ============================================================================
print("\n🔀 Splitting dataset...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"   ✓ Training samples: {len(X_train)}")
print(f"   ✓ Test samples: {len(X_test)}")

# ============================================================================
# 3. Train Random Forest Model
# ============================================================================
print("\n🌲 Training Random Forest Regressor...")
print("   Parameters: n_estimators=300, max_depth=None, random_state=42")

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    random_state=42,
    n_jobs=-1,
    verbose=0
)

model.fit(X_train, y_train)
print("   ✓ Model training complete!")

# ============================================================================
# 4. Evaluate Performance
# ============================================================================
print("\n📊 Evaluating model performance...")

# Predictions
y_train_pred = model.predict(X_train)
y_test_pred = model.predict(X_test)

# R² scores
train_r2 = r2_score(y_train, y_train_pred)
test_r2 = r2_score(y_test, y_test_pred)

print(f"\n   Train R²: {train_r2:.6f}")
print(f"   Test R²:  {test_r2:.6f}")

# Per-output metrics
target_names = ['D0', 'D1', 'D2', 'Irms_A']
print("\n   Per-output R² scores:")
for i, name in enumerate(target_names):
    train_r2_i = r2_score(y_train[:, i], y_train_pred[:, i])
    test_r2_i = r2_score(y_test[:, i], y_test_pred[:, i])
    mae_i = mean_absolute_error(y_test[:, i], y_test_pred[:, i])
    rmse_i = np.sqrt(mean_squared_error(y_test[:, i], y_test_pred[:, i]))
    print(f"      {name:8s}: Train R²={train_r2_i:.6f}, Test R²={test_r2_i:.6f}, "
          f"MAE={mae_i:.6f}, RMSE={rmse_i:.6f}")

# ============================================================================
# 5. Visualization
# ============================================================================
print("\n📈 Generating prediction plots...")

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
fig.suptitle('Random Forest: Predicted vs Actual', fontsize=16, fontweight='bold')

for i, (ax, name) in enumerate(zip(axes.flat, target_names)):
    # Plot test predictions
    ax.scatter(y_test[:, i], y_test_pred[:, i], alpha=0.6, s=50, 
               label='Test', color='blue', edgecolors='black', linewidth=0.5)
    
    # Perfect prediction line
    min_val = min(y_test[:, i].min(), y_test_pred[:, i].min())
    max_val = max(y_test[:, i].max(), y_test_pred[:, i].max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    # Labels and formatting
    ax.set_xlabel(f'Actual {name}', fontsize=11, fontweight='bold')
    ax.set_ylabel(f'Predicted {name}', fontsize=11, fontweight='bold')
    ax.set_title(f'{name} (Test R²={r2_score(y_test[:, i], y_test_pred[:, i]):.4f})', 
                 fontsize=12)
    ax.legend(loc='best')
    ax.grid(True, alpha=0.3)
    
plt.tight_layout()
plt.savefig('rf_predictions_vs_actual.png', dpi=150, bbox_inches='tight')
print("   ✓ Saved plot: rf_predictions_vs_actual.png")

# ============================================================================
# 6. Save Model
# ============================================================================
print("\n💾 Saving trained model...")
joblib.dump(model, 'tps_rf_model.pkl')
print("   ✓ Model saved: tps_rf_model.pkl")

# ============================================================================
# 7. Generate Interpolated Predictions
# ============================================================================
print("\n🔮 Generating interpolated predictions...")

# Create fine-grained power values
power_values = np.linspace(100, 1000, 100).reshape(-1, 1)
predictions = model.predict(power_values)

# Create DataFrame
interpolated_df = pd.DataFrame({
    'Power_W': power_values.flatten(),
    'D0_pred': predictions[:, 0],
    'D1_pred': predictions[:, 1],
    'D2_pred': predictions[:, 2],
    'Irms_pred': predictions[:, 3]
})

interpolated_df.to_csv('rf_interpolated_lookup_table.csv', index=False)
print(f"   ✓ Generated {len(interpolated_df)} interpolated points")
print("   ✓ Saved: rf_interpolated_lookup_table.csv")

# ============================================================================
# 8. Feature Importance
# ============================================================================
print("\n🎯 Feature Importance:")
feature_importance = model.feature_importances_
print(f"   Power_Target_W: {feature_importance[0]:.6f}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("✅ MODEL TRAINING COMPLETE")
print("=" * 70)
print(f"   Model performance: Test R² = {test_r2:.6f}")
print(f"   Saved files:")
print(f"      • tps_rf_model.pkl (trained model)")
print(f"      • rf_interpolated_lookup_table.csv (100 interpolated points)")
print(f"      • rf_predictions_vs_actual.png (visualization)")
print("\n   Usage example:")
print("      import joblib")
print("      model = joblib.load('tps_rf_model.pkl')")
print("      D0, D1, D2, Irms = model.predict([[500]])[0]  # Predict for 500W")
print("=" * 70)
