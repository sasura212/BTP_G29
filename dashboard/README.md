# TPS DAB Converter Dashboard

## Quick Start

### 1. Run the Dashboard

```bash
python3 -m streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### 2. Using the Dashboard

**Main Features:**
- **Power Selection**: Use the slider or number input to select target power (100-1000W)
- **Instant Predictions**: View optimal D₀, D₁, D₂, and minimum Irms
- **System Parameters**: Sidebar shows all DAB converter constants (V₁, V₂, L, f)
- **Comparison**: See how ML predictions compare with lookup table values
- **Visualizations**: Interactive plots showing parameter trends across power range

**Sidebar Information:**
- Primary Voltage (V₁): 200 V
- Secondary Voltage (V₂): 50 V
- Inductance (L): 20 µH
- Switching Frequency (f): 50 kHz
- Half Period (T): 10 µs

### 3. Features

✅ **Real-time prediction** using trained Random Forest model  
✅ **Interactive sliders** for power selection  
✅ **Visual comparison** with optimal lookup table  
✅ **Dynamic charts** showing trends  
✅ **System parameters** always visible in sidebar  

### 4. Example Usage

1. Move the slider to 500W
2. View predicted optimal parameters:
   - D₀ ≈ 0.75
   - D₁ ≈ 0.74
   - D₂ ≈ 0.03
   - Irms ≈ 11.47 A
3. Compare with lookup table values
4. View position on parameter trend charts

### 5. Files Required

The dashboard needs these files in the same directory:
- `dashboard.py` - Main dashboard script
- `tps_rf_model.pkl` - Trained Random Forest model
- `integrated_optimal_lookup_table.csv` - Reference lookup table

### 6. Dependencies

```bash
pip install streamlit plotly pandas numpy joblib
```

Or install all from requirements:
```bash
pip install -r requirements.txt
```

### 7. Troubleshooting

**Dashboard won't start:**
```bash
# Check if streamlit is installed
python3 -m streamlit --version

# Reinstall if needed
pip install streamlit --upgrade
```

**Model file not found:**
```bash
# Train the model first
python3 train_tps_regressor.py
```

**Port already in use:**
```bash
# Use a different port
python3 -m streamlit run dashboard.py --server.port 8502
```

### 8. Access in Codespaces

If running in GitHub Codespaces:
1. Dashboard will auto-forward port 8501
2. Click the "Open in Browser" notification
3. Or go to Ports tab and click the Local Address

---

**Author:** Harshit Singh  
**Project:** BTP DAB Converter Optimization  
**Date:** November 2025
