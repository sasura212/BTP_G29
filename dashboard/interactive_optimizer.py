"""
Interactive TPS Parameter Optimizer Dashboard
Allows manual adjustment of D0, D1, D2 to see real-time effects on power and Irms
Compares with optimal values
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
from scipy.optimize import fsolve

# Get paths
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DASHBOARD_DIR)
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Page configuration
st.set_page_config(
    page_title="Interactive TPS Optimizer",
    page_icon="🎛️",
    layout="wide"
)

# ============================================================================
# Constants
# ============================================================================
V1 = 200.0      # Primary DC voltage [V]
V2 = 50.0       # Secondary reflected DC voltage [V]
T = 1e-5        # Half switching period [s]
L = 20e-6       # Inductance [H]

# ============================================================================
# Power and Irms Calculation Functions
# ============================================================================

def calculate_power(D0, D1, D2):
    """Calculate power using TPS equation (Mode 1 approximation)"""
    return (-(V1*V2*T)/L) * (
        -D0 + D0**2 + 0.5*D1 - D0*D1 + 0.5*D1**2 -
        0.5*D2 + D0*D2 - 0.5*D1*D2 + 0.5*D2**2
    )

def calculate_irms(D0, D1, D2):
    """Calculate RMS current using TPS equation"""
    try:
        irms_squared = (T/L)**2 * (
            (0.125/3)*(V1**2) + (0.125/3)*(V2**2) +
            (0.5/3)*(0.25 - 1.5*D1**2 + D1**3)*V1**2 -
            (0.5/3)*(0.25 - 1.5*D0**2 + D0**3)*V1*V2 -
            (0.5/3)*(0.25 - 1.5*(D0 + D2)**2 + (D0 + D2)**3)*V1*V2 -
            (0.5/3)*(0.25 - 1.5*(D0 - D1)**2 + (D0 - D1)**3)*V1*V2 -
            (0.5/3)*(0.25 - 1.5*(D0 + D2 - D1)**2 + (D0 + D2 - D1)**3)*V1*V2 +
            (0.5/3)*(0.25 - 1.5*D2**2 + D2**3)*V2**2
        )
        return np.sqrt(abs(irms_squared))
    except:
        return 0.0

def solve_for_d2(D0, D1, target_power):
    """Solve for D2 given D0, D1, and target power"""
    def equation(D2):
        return calculate_power(D0, D1, D2) - target_power
    
    try:
        # Try to find D2 in valid range [0.01, 0.99]
        D2_solution = fsolve(equation, 0.1, full_output=True)
        D2 = D2_solution[0][0]
        
        # Check if solution is valid
        if 0.01 <= D2 <= 0.99 and D2_solution[2] == 1:
            return D2
        else:
            return None
    except:
        return None

def solve_for_d1(D0, D2, target_power):
    """Solve for D1 given D0, D2, and target power"""
    def equation(D1):
        return calculate_power(D0, D1, D2) - target_power
    
    try:
        D1_solution = fsolve(equation, 0.5, full_output=True)
        D1 = D1_solution[0][0]
        
        if 0.01 <= D1 <= 0.99 and D1_solution[2] == 1:
            return D1
        else:
            return None
    except:
        return None

def solve_for_d0(D1, D2, target_power):
    """Solve for D0 given D1, D2, and target power"""
    def equation(D0):
        return calculate_power(D0, D1, D2) - target_power
    
    try:
        D0_solution = fsolve(equation, 0.5, full_output=True)
        D0 = D0_solution[0][0]
        
        if 0.01 <= D0 <= 0.99 and D0_solution[2] == 1:
            return D0
        else:
            return None
    except:
        return None

# ============================================================================
# Load Optimal Lookup Table
# ============================================================================
@st.cache_data
def load_optimal_data():
    """Load the optimal lookup table"""
    try:
        df = pd.read_csv(os.path.join(DATA_DIR, 'integrated_optimal_lookup_table.csv'))
        return df
    except:
        return None

optimal_df = load_optimal_data()

# ============================================================================
# Header
# ============================================================================
st.title("🎛️ Interactive TPS Parameter Optimizer")
st.markdown("### Adjust duty cycles and see real-time effects on power and RMS current")
st.markdown("---")

# ============================================================================
# Sidebar - System Parameters
# ============================================================================
st.sidebar.header("⚙️ System Parameters")
st.sidebar.markdown(f"""
- **Primary Voltage (V₁):** {V1} V
- **Secondary Voltage (V₂):** {V2} V
- **Inductance (L):** {L*1e6:.0f} µH
- **Switching Frequency:** {1/(2*T)/1000:.0f} kHz
- **Half Period (T):** {T*1e6:.0f} µs
""")

st.sidebar.markdown("---")
st.sidebar.header("📖 How to Use")
st.sidebar.markdown("""
1. **Select target power** (100-1000W)
2. **Choose which parameter to adjust**
3. **Use the slider** to change the value
4. **Other parameters auto-adjust** to maintain power
5. **Compare Irms** with optimal value
""")

# ============================================================================
# Main Interface
# ============================================================================

# Step 1: Select Target Power
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    target_power = st.slider(
        "🎯 Target Power (W)",
        min_value=100.0,
        max_value=1000.0,
        value=500.0,
        step=10.0,
        key="power_slider"
    )

with col2:
    # Input field for precise power entry
    input_power = st.number_input(
        "Or enter exact value:",
        min_value=100.0,
        max_value=1000.0,
        value=target_power,
        step=1.0,
        key="power_input"
    )
    
    # Use input value if it differs from slider
    if input_power != target_power:
        target_power = input_power

with col3:
    st.metric("Selected Power", f"{target_power:.1f} W")

# Get optimal values for this power
if optimal_df is not None:
    # Find closest power point
    closest_idx = (optimal_df['Power_Target_W'] - target_power).abs().idxmin()
    optimal_row = optimal_df.iloc[closest_idx]
    
    optimal_D0 = optimal_row['D0']
    optimal_D1 = optimal_row['D1']
    optimal_D2 = optimal_row['D2']
    optimal_Irms = optimal_row['Irms_A']
    optimal_mode = optimal_row.get('Mode', 'N/A')
else:
    # Default values if no optimal data
    optimal_D0 = 0.7
    optimal_D1 = 0.7
    optimal_D2 = 0.1
    optimal_Irms = 10.0
    optimal_mode = 'N/A'

st.markdown("---")

# Step 2: Choose which parameter to adjust
st.subheader("🔧 Adjust Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    adjust_param = st.radio(
        "Which parameter to adjust?",
        ["D₀", "D₁", "D₂"],
        horizontal=True
    )

# Initialize session state for parameters
if 'current_D0' not in st.session_state:
    st.session_state.current_D0 = optimal_D0
if 'current_D1' not in st.session_state:
    st.session_state.current_D1 = optimal_D1
if 'current_D2' not in st.session_state:
    st.session_state.current_D2 = optimal_D2

st.markdown("---")

# Step 3: Adjust the selected parameter
col1, col2 = st.columns([3, 2])

with col1:
    if adjust_param == "D₀":
        adjusted_D0 = st.slider(
            "Adjust D₀ (External Phase Shift)",
            min_value=0.01,
            max_value=0.99,
            value=float(st.session_state.current_D0),
            step=0.01,
            key="slider_d0"
        )
        
        # Keep D1 fixed, solve for D2
        fixed_D1 = st.session_state.current_D1
        solved_D2 = solve_for_d2(adjusted_D0, fixed_D1, target_power)
        
        if solved_D2 is not None:
            st.session_state.current_D0 = adjusted_D0
            st.session_state.current_D1 = fixed_D1
            st.session_state.current_D2 = solved_D2
            solution_found = True
        else:
            # Try solving for D1 instead
            fixed_D2 = st.session_state.current_D2
            solved_D1 = solve_for_d1(adjusted_D0, fixed_D2, target_power)
            
            if solved_D1 is not None:
                st.session_state.current_D0 = adjusted_D0
                st.session_state.current_D1 = solved_D1
                st.session_state.current_D2 = fixed_D2
                solution_found = True
            else:
                solution_found = False
    
    elif adjust_param == "D₁":
        adjusted_D1 = st.slider(
            "Adjust D₁ (Primary Bridge Internal Phase Shift)",
            min_value=0.01,
            max_value=0.99,
            value=float(st.session_state.current_D1),
            step=0.01,
            key="slider_d1"
        )
        
        # Keep D0 fixed, solve for D2
        fixed_D0 = st.session_state.current_D0
        solved_D2 = solve_for_d2(fixed_D0, adjusted_D1, target_power)
        
        if solved_D2 is not None:
            st.session_state.current_D0 = fixed_D0
            st.session_state.current_D1 = adjusted_D1
            st.session_state.current_D2 = solved_D2
            solution_found = True
        else:
            solution_found = False
    
    else:  # D₂
        adjusted_D2 = st.slider(
            "Adjust D₂ (Secondary Bridge Internal Phase Shift)",
            min_value=0.01,
            max_value=0.99,
            value=float(st.session_state.current_D2),
            step=0.01,
            key="slider_d2"
        )
        
        # Keep D0 fixed, solve for D1
        fixed_D0 = st.session_state.current_D0
        solved_D1 = solve_for_d1(fixed_D0, adjusted_D2, target_power)
        
        if solved_D1 is not None:
            st.session_state.current_D0 = fixed_D0
            st.session_state.current_D1 = solved_D1
            st.session_state.current_D2 = adjusted_D2
            solution_found = True
        else:
            solution_found = False

with col2:
    if solution_found:
        st.success("✅ Valid solution found!")
    else:
        st.error("❌ No valid solution for this combination")

# Calculate current power and Irms
current_D0 = st.session_state.current_D0
current_D1 = st.session_state.current_D1
current_D2 = st.session_state.current_D2

current_power = calculate_power(current_D0, current_D1, current_D2)
current_Irms = calculate_irms(current_D0, current_D1, current_D2)

st.markdown("---")

# Step 4: Display Results
st.subheader("📊 Results Comparison")

# Create comparison table
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Parameter")
    st.markdown("**D₀**")
    st.markdown("**D₁**")
    st.markdown("**D₂**")
    st.markdown("**Power**")
    st.markdown("**Irms**")
    st.markdown("**Mode**")

with col2:
    st.markdown("#### Current Values")
    st.markdown(f"`{current_D0:.4f}`")
    st.markdown(f"`{current_D1:.4f}`")
    st.markdown(f"`{current_D2:.4f}`")
    st.markdown(f"`{current_power:.2f} W`")
    st.markdown(f"**`{current_Irms:.2f} A`**")
    st.markdown(f"`Manual`")

with col3:
    st.markdown("#### Optimal Values")
    st.markdown(f"`{optimal_D0:.4f}`")
    st.markdown(f"`{optimal_D1:.4f}`")
    st.markdown(f"`{optimal_D2:.4f}`")
    st.markdown(f"`{target_power:.2f} W`")
    st.markdown(f"**`{optimal_Irms:.2f} A`**")
    st.markdown(f"`Mode {optimal_mode}`")

with col4:
    st.markdown("#### Difference")
    d0_diff = current_D0 - optimal_D0
    d1_diff = current_D1 - optimal_D1
    d2_diff = current_D2 - optimal_D2
    power_diff = current_power - target_power
    irms_diff = current_Irms - optimal_Irms
    
    st.markdown(f"`{d0_diff:+.4f}`")
    st.markdown(f"`{d1_diff:+.4f}`")
    st.markdown(f"`{d2_diff:+.4f}`")
    st.markdown(f"`{power_diff:+.2f} W`")
    
    if irms_diff > 0:
        st.markdown(f"**:red[`{irms_diff:+.2f} A`]**")
    else:
        st.markdown(f"**:green[`{irms_diff:+.2f} A`]**")
    st.markdown("`-`")

# Irms comparison metric
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Current Irms",
        f"{current_Irms:.2f} A",
        delta=f"{irms_diff:+.2f} A vs optimal",
        delta_color="inverse"
    )

with col2:
    st.metric(
        "Optimal Irms",
        f"{optimal_Irms:.2f} A"
    )

with col3:
    efficiency_loss = (irms_diff / optimal_Irms) * 100 if optimal_Irms > 0 else 0
    st.metric(
        "Efficiency Impact",
        f"{abs(efficiency_loss):.1f}%",
        delta="Higher losses" if irms_diff > 0 else "Better efficiency",
        delta_color="inverse" if irms_diff > 0 else "normal"
    )

st.markdown("---")

# Step 5: Visualization
st.subheader("📈 Visual Comparison")

# Create radar chart for parameter comparison
fig = go.Figure()

categories = ['D₀', 'D₁', 'D₂', 'Irms (×0.1)']

fig.add_trace(go.Scatterpolar(
    r=[current_D0, current_D1, current_D2, current_Irms * 0.1],
    theta=categories,
    fill='toself',
    name='Current',
    line_color='#FF6B6B'
))

fig.add_trace(go.Scatterpolar(
    r=[optimal_D0, optimal_D1, optimal_D2, optimal_Irms * 0.1],
    theta=categories,
    fill='toself',
    name='Optimal',
    line_color='#4ECDC4'
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 1]
        )
    ),
    showlegend=True,
    title="Parameter Comparison (Radar Chart)",
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Bar chart for Irms comparison
col1, col2 = st.columns(2)

with col1:
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        x=['Current', 'Optimal'],
        y=[current_Irms, optimal_Irms],
        marker_color=['#FF6B6B', '#4ECDC4'],
        text=[f'{current_Irms:.2f} A', f'{optimal_Irms:.2f} A'],
        textposition='auto',
    ))
    
    fig_bar.update_layout(
        title="RMS Current Comparison",
        yaxis_title="Irms (A)",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    # Power losses comparison (I²R losses proportional to Irms²)
    current_losses = current_Irms**2
    optimal_losses = optimal_Irms**2
    losses_increase = ((current_losses - optimal_losses) / optimal_losses) * 100
    
    fig_losses = go.Figure()
    
    fig_losses.add_trace(go.Bar(
        x=['Current', 'Optimal'],
        y=[current_losses, optimal_losses],
        marker_color=['#FF6B6B', '#4ECDC4'],
        text=[f'{current_losses:.1f}', f'{optimal_losses:.1f}'],
        textposition='auto',
    ))
    
    fig_losses.update_layout(
        title=f"Relative Losses (I²R) - {losses_increase:+.1f}% difference",
        yaxis_title="Losses (A²)",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig_losses, use_container_width=True)

# Reset button
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    if st.button("🔄 Reset to Optimal", type="primary"):
        st.session_state.current_D0 = optimal_D0
        st.session_state.current_D1 = optimal_D1
        st.session_state.current_D2 = optimal_D2
        st.rerun()

with col2:
    if st.button("📋 Copy Values"):
        st.code(f"D0 = {current_D0:.4f}\nD1 = {current_D1:.4f}\nD2 = {current_D2:.4f}\nIrms = {current_Irms:.2f} A")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <small>Interactive TPS Parameter Optimizer | Adjust duty cycles and compare with optimal values</small>
</div>
""", unsafe_allow_html=True)
