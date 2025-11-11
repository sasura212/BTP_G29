
import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="TPS DAB Optimizer",
    page_icon="⚡",
    layout="wide"
)

# ============================================================================
# Constants
# ============================================================================
V1 = 200.0      # Primary DC voltage [V]
V2 = 50.0       # Secondary reflected DC voltage [V]
T = 1e-5        # Half switching period [s]
L = 20e-6       # Inductance [H]
f = 1 / (2 * T) # Switching frequency [Hz]

# ============================================================================
# Load Models and Data
# ============================================================================
@st.cache_resource
def load_rf_model():
    """Load the trained Random Forest model"""
    try:
        model = joblib.load('tps_rf_model.pkl')
        return model
    except FileNotFoundError:
        return None

@st.cache_resource
def load_svr_models():
    """Load the trained SVR models and scaler"""
    try:
        scaler = joblib.load('svr_scaler.pkl')
        models = {
            'D0': joblib.load('svr_model_D0.pkl'),
            'D1': joblib.load('svr_model_D1.pkl'),
            'D2': joblib.load('svr_model_D2.pkl'),
            'Irms_A': joblib.load('svr_model_Irms_A.pkl')
        }
        return scaler, models
    except FileNotFoundError:
        return None, None

@st.cache_data
def load_lookup_table():
    """Load the integrated optimal lookup table"""
    try:
        df = pd.read_csv('integrated_optimal_lookup_table.csv')
        return df
    except FileNotFoundError:
        st.warning("⚠️ Lookup table not found. Some features will be limited.")
        return None

@st.cache_data
def load_rf_interpolated():
    """Load Random Forest interpolated predictions"""
    try:
        df = pd.read_csv('rf_interpolated_lookup_table.csv')
        return df
    except FileNotFoundError:
        return None

@st.cache_data
def load_svr_interpolated():
    """Load SVR interpolated predictions"""
    try:
        df = pd.read_csv('svr_interpolated_lookup_table.csv')
        return df
    except FileNotFoundError:
        return None

# Load models and data
rf_model = load_rf_model()
svr_scaler, svr_models = load_svr_models()
lookup_df = load_lookup_table()
rf_interp_df = load_rf_interpolated()
svr_interp_df = load_svr_interpolated()

# Check if at least one model is available
if rf_model is None and svr_models is None:
    st.error("❌ No models found! Please run train_tps_regressor.py or train_tps_svr.py first.")
    st.stop()

# ============================================================================
# Header
# ============================================================================
st.title("⚡ Triple Phase Shift (TPS) DAB Converter Optimizer")
st.markdown("### Optimal Control Parameter Prediction using Machine Learning")
st.markdown("---")

# ============================================================================
# Model Selection
# ============================================================================
st.subheader("🤖 Select Prediction Model")

available_models = []
if rf_model is not None:
    available_models.append("Random Forest")
if svr_models is not None:
    available_models.append("Support Vector Regression (SVR)")

if len(available_models) == 0:
    st.error("No models available!")
    st.stop()

selected_model = st.radio(
    "Choose ML Model:",
    options=available_models,
    horizontal=True,
    help="Select which machine learning model to use for predictions"
)

st.markdown("---")

# ============================================================================
# Sidebar - System Parameters
# ============================================================================
st.sidebar.header("📊 System Parameters")
st.sidebar.markdown("**DAB Converter Specifications**")
st.sidebar.markdown(f"""
- **Primary Voltage (V₁):** {V1:.1f} V
- **Secondary Voltage (V₂):** {V2:.1f} V
- **Inductance (L):** {L*1e6:.1f} µH
- **Switching Frequency (f):** {f/1000:.1f} kHz
- **Half Period (T):** {T*1e6:.1f} µs
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Operating Range**")
st.sidebar.markdown(f"""
- **Power:** 100 - 1000 W
- **D₀, D₁, D₂:** 0.01 - 0.99
- **Modes:** 1, 2, 3, 4, 5, 6
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Model Information**")

if selected_model == "Random Forest":
    st.sidebar.markdown(f"""
    - **Algorithm:** Random Forest
    - **Estimators:** 300 trees
    - **Training Data:** 91 points
    - **Test R² (Irms):** 0.985
    - **Test R² (D0):** 0.686
    - **Test R² (D2):** 0.589
    """)
else:  # SVR
    st.sidebar.markdown(f"""
    - **Algorithm:** Support Vector Regression
    - **Kernel:** RBF (Radial Basis Function)
    - **Training Data:** 91 points
    - **Test R² (Irms):** 0.986
    - **Test R² (D0):** 0.401
    - **Test R² (D2):** 0.930
    """)

# ============================================================================
# Main Dashboard - Power Input
# ============================================================================
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🎯 Target Power Selection")
    
    # Slider for power input
    power_input = st.slider(
        "Select Target Power (W)",
        min_value=100,
        max_value=1000,
        value=500,
        step=10,
        help="Slide to select the desired output power"
    )
    
    # Alternative: Number input
    power_manual = st.number_input(
        "Or enter power manually (W)",
        min_value=100.0,
        max_value=1000.0,
        value=float(power_input),
        step=1.0,
        help="Type exact power value"
    )
    
    # Use manual input if different from slider
    if power_manual != power_input:
        power_input = power_manual

with col2:
    st.subheader("📈 Current Power")
    st.metric(
        label="Target Power",
        value=f"{power_input:.1f} W",
        delta=f"{(power_input/1000)*100:.1f}% of max"
    )

st.markdown("---")

# ============================================================================
# Prediction
# ============================================================================
st.subheader(f"🔮 Predicted Optimal Parameters ({selected_model})")

# Make prediction based on selected model
if selected_model == "Random Forest":
    prediction = rf_model.predict([[power_input]])[0]
    D0_pred, D1_pred, D2_pred, Irms_pred = prediction
else:  # SVR
    # Scale the input
    power_scaled = svr_scaler.transform([[power_input]])
    # Predict each parameter
    D0_pred = svr_models['D0'].predict(power_scaled)[0]
    D1_pred = svr_models['D1'].predict(power_scaled)[0]
    D2_pred = svr_models['D2'].predict(power_scaled)[0]
    Irms_pred = svr_models['Irms_A'].predict(power_scaled)[0]

# Display predictions in columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="D₀ (Duty Cycle 1)",
        value=f"{D0_pred:.4f}",
        help="Primary-to-secondary phase shift"
    )

with col2:
    st.metric(
        label="D₁ (Duty Cycle 2)",
        value=f"{D1_pred:.4f}",
        help="Inner phase shift (primary bridge)"
    )

with col3:
    st.metric(
        label="D₂ (Duty Cycle 3)",
        value=f"{D2_pred:.4f}",
        help="Inner phase shift (secondary bridge)"
    )

with col4:
    st.metric(
        label="Minimum Irms",
        value=f"{Irms_pred:.2f} A",
        help="Predicted minimum RMS current"
    )

# ============================================================================
# Comparison with Lookup Table and Other Model (if available)
# ============================================================================
if lookup_df is not None:
    st.markdown("---")
    st.subheader("📋 Model Comparison Table")
    
    # Find closest power in lookup table
    closest_idx = (lookup_df['Power_Target_W'] - power_input).abs().idxmin()
    closest_row = lookup_df.iloc[closest_idx]
    
    # Prepare comparison data
    comparison_data = {
        'Parameter': ['D₀', 'D₁', 'D₂', 'Irms'],
        f'{selected_model}': [
            f"{D0_pred:.4f}", 
            f"{D1_pred:.4f}", 
            f"{D2_pred:.4f}", 
            f"{Irms_pred:.4f} A"
        ]
    }
    
    # Add other model predictions if available
    if selected_model == "Random Forest" and svr_models is not None:
        # Get SVR predictions
        power_scaled = svr_scaler.transform([[power_input]])
        svr_D0 = svr_models['D0'].predict(power_scaled)[0]
        svr_D1 = svr_models['D1'].predict(power_scaled)[0]
        svr_D2 = svr_models['D2'].predict(power_scaled)[0]
        svr_Irms = svr_models['Irms_A'].predict(power_scaled)[0]
        
        comparison_data['SVR'] = [
            f"{svr_D0:.4f}",
            f"{svr_D1:.4f}",
            f"{svr_D2:.4f}",
            f"{svr_Irms:.4f} A"
        ]
    elif selected_model == "Support Vector Regression (SVR)" and rf_model is not None:
        # Get RF predictions
        rf_pred = rf_model.predict([[power_input]])[0]
        comparison_data['Random Forest'] = [
            f"{rf_pred[0]:.4f}",
            f"{rf_pred[1]:.4f}",
            f"{rf_pred[2]:.4f}",
            f"{rf_pred[3]:.4f} A"
        ]
    
    # Add lookup table data
    comparison_data['Lookup Table'] = [
        f"{closest_row['D0']:.4f}",
        f"{closest_row['D1']:.4f}",
        f"{closest_row['D2']:.4f}",
        f"{closest_row['Irms_A']:.4f} A"
    ]
    
    # Add mode info separately
    comparison_df = pd.DataFrame(comparison_data)
    
    # Display comparison table
    st.dataframe(comparison_df, hide_index=True, width='stretch')
    
    # Show lookup table info
    st.caption(f"Lookup Table data point: {closest_row['Power_Target_W']:.0f}W, Mode {int(closest_row['Mode'])}")
    
    # Show error if power matches exactly
    if abs(closest_row['Power_Target_W'] - power_input) < 0.1:
        error_d0 = abs(D0_pred - closest_row['D0'])
        error_d1 = abs(D1_pred - closest_row['D1'])
        error_d2 = abs(D2_pred - closest_row['D2'])
        error_irms = abs(Irms_pred - closest_row['Irms_A'])
        
        st.info(f"""
        **{selected_model} Prediction Error vs Lookup Table:**  
        D₀: {error_d0:.4f} | D₁: {error_d1:.4f} | D₂: {error_d2:.4f} | Irms: {error_irms:.4f} A
        """)

# ============================================================================
# Visualization - Power vs Parameters
# ============================================================================
st.markdown("---")
st.subheader("📊 Parameter Trends Across Power Range")

# Get the appropriate interpolated dataframe
if selected_model == "Random Forest" and rf_interp_df is not None:
    interp_df = rf_interp_df
    interp_label = "RF Prediction"
elif selected_model == "Support Vector Regression (SVR)" and svr_interp_df is not None:
    interp_df = svr_interp_df
    interp_label = "SVR Prediction"
else:
    interp_df = None
    interp_label = "Prediction"

if interp_df is not None or lookup_df is not None:
    # Create interactive plot for duty cycles
    fig = go.Figure()
    
    # Add interpolated predictions if available
    if interp_df is not None:
        fig.add_trace(go.Scatter(
            x=interp_df['Power_W'],
            y=interp_df['D0_pred'],
            mode='lines',
            name=f'D₀ ({interp_label})',
            line=dict(color='blue', width=2, dash='solid'),
            opacity=0.7
        ))
        
        fig.add_trace(go.Scatter(
            x=interp_df['Power_W'],
            y=interp_df['D1_pred'],
            mode='lines',
            name=f'D₁ ({interp_label})',
            line=dict(color='green', width=2, dash='solid'),
            opacity=0.7
        ))
        
        fig.add_trace(go.Scatter(
            x=interp_df['Power_W'],
            y=interp_df['D2_pred'],
            mode='lines',
            name=f'D₂ ({interp_label})',
            line=dict(color='red', width=2, dash='solid'),
            opacity=0.7
        ))
    
    # Add lookup table data as reference points
    if lookup_df is not None:
        fig.add_trace(go.Scatter(
            x=lookup_df['Power_Target_W'],
            y=lookup_df['D0'],
            mode='markers',
            name='D₀ (Optimal)',
            marker=dict(color='blue', size=6, symbol='circle'),
            opacity=0.5
        ))
        
        fig.add_trace(go.Scatter(
            x=lookup_df['Power_Target_W'],
            y=lookup_df['D1'],
            mode='markers',
            name='D₁ (Optimal)',
            marker=dict(color='green', size=6, symbol='circle'),
            opacity=0.5
        ))
        
        fig.add_trace(go.Scatter(
            x=lookup_df['Power_Target_W'],
            y=lookup_df['D2'],
            mode='markers',
            name='D₂ (Optimal)',
            marker=dict(color='red', size=6, symbol='circle'),
            opacity=0.5
        ))
    
    # Add current prediction point
    fig.add_trace(go.Scatter(
        x=[power_input],
        y=[D0_pred],
        mode='markers',
        name='Current D₀',
        marker=dict(color='blue', size=15, symbol='star', line=dict(color='white', width=2))
    ))
    
    fig.add_trace(go.Scatter(
        x=[power_input],
        y=[D1_pred],
        mode='markers',
        name='Current D₁',
        marker=dict(color='green', size=15, symbol='star', line=dict(color='white', width=2))
    ))
    
    fig.add_trace(go.Scatter(
        x=[power_input],
        y=[D2_pred],
        mode='markers',
        name='Current D₂',
        marker=dict(color='red', size=15, symbol='star', line=dict(color='white', width=2))
    ))
    
    fig.update_layout(
        title=f'Duty Cycles vs Power ({selected_model})',
        xaxis_title='Power (W)',
        yaxis_title='Duty Cycle Value',
        hovermode='x unified',
        height=450
    )
    
    st.plotly_chart(fig, width='stretch')
    
    # Irms vs Power plot
    fig2 = go.Figure()
    
    # Add interpolated predictions if available
    if interp_df is not None:
        fig2.add_trace(go.Scatter(
            x=interp_df['Power_W'],
            y=interp_df['Irms_pred'],
            mode='lines',
            name=f'Irms ({interp_label})',
            line=dict(color='purple', width=3),
            opacity=0.8
        ))
    
    # Add lookup table data
    if lookup_df is not None:
        fig2.add_trace(go.Scatter(
            x=lookup_df['Power_Target_W'],
            y=lookup_df['Irms_A'],
            mode='markers',
            name='Irms (Optimal)',
            marker=dict(color='purple', size=6, symbol='circle'),
            opacity=0.5
        ))
    
    # Add current prediction
    fig2.add_trace(go.Scatter(
        x=[power_input],
        y=[Irms_pred],
        mode='markers',
        name='Current Prediction',
        marker=dict(color='orange', size=15, symbol='star', line=dict(color='white', width=2))
    ))
    
    fig2.update_layout(
        title=f'RMS Current vs Power ({selected_model})',
        xaxis_title='Power (W)',
        yaxis_title='Irms (A)',
        hovermode='x unified',
        height=450
    )
    
    st.plotly_chart(fig2, width='stretch')

# ============================================================================
# Footer
# ============================================================================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666;'>
    <p><strong>TPS DAB Converter Optimizer</strong> | BTP Project, IIT Roorkee | November 2025</p>
    <p>Powered by {selected_model} | Based on Tong et al. (2016)</p>
</div>
""", unsafe_allow_html=True)
