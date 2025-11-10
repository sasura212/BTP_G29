#!/usr/bin/env python3
"""
DAB Converter Optimal Control - Simple Interface
=================================================
Input: Power (W)
Output: Optimal D0, D1, D2, minimum Irms, and operating mode
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Setup paths
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from constants import L, f_s, V1_PRIMARY, V2_SECONDARY

# Page config
st.set_page_config(
    page_title="DAB Optimal Control",
    page_icon=" ",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .result-box {
        background: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin: 20px 0;
    }
    .big-number {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        margin: 10px 0;
    }
    .d0-number {
        font-size: 48px;
        font-weight: bold;
        color: #000000;
        text-align: center;
        margin: 10px 0;
    }
    .d1-number {
        font-size: 48px;
        font-weight: bold;
        color: #000000;
        text-align: center;
        margin: 10px 0;
    }
    .d2-number {
        font-size: 48px;
        font-weight: bold;
        color: #000000;
        text-align: center;
        margin: 10px 0;
    }
    .label {
        font-size: 14px;
        color: #000000;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    h1 {
        color: white !important;
        text-align: center;
    }
    .subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 18px;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_resource
def load_data():
    try:
        df = pd.read_csv(os.path.join(project_root, 'data/optimized_lookup_table.csv'))
        return df, True
    except:
        return None, False

df_opt, loaded = load_data()

# Header
st.title("DAB Converter Optimal Control")
st.markdown('<p class="subtitle">Find Optimal Control Parameters for Minimum RMS Current</p>', unsafe_allow_html=True)

if not loaded:
    st.error("Data not found. Run generate_data.py first.")
    st.stop()

# System info (collapsible)
with st.expander("System Parameters"):
    col1, col2, col3 = st.columns(3)
    col1.write(f"**L:** {L*1e6:.1f} µH")
    col2.write(f"**f_s:** {f_s/1e3:.0f} kHz")
    col3.write(f"**V1/V2:** {V1_PRIMARY}/{V2_SECONDARY}V")

st.markdown("---")

# Input section
st.markdown("### 🔌 Enter Power Requirement")

col1, col2 = st.columns([3, 1])

with col1:
    power = st.number_input(
        "Power (W)",
        min_value=0.0,
        max_value=5000.0,
        value=1000.0,
        step=50.0
    )

with col2:
    st.write("")
    st.write("")
    go = st.button("Find", type="primary", use_container_width=True)

# Results
if go or power:
    # Find closest match based on ACTUAL power (not requested)
    df_opt['power_diff'] = abs(df_opt['Power_actual_W'] - power)
    idx = df_opt['power_diff'].idxmin()
    r = df_opt.loc[idx]
    
    st.markdown("---")
    st.markdown("Optimal Solution")
    
    # Power matching
    col1, col2 = st.columns(2)
    col1.metric("Requested", f"{power:.1f} W")
    col2.metric("Matched", f"{r['Power_actual_W']:.1f} W", 
                f"{abs(r['Power_actual_W']-power):.1f}W")
    
    st.markdown("---")
    
    # Main results - Duty cycles
    st.markdown("Control Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="label">D₀ (Phase Shift)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="d0-number">{r["D0_opt"]:.3f}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="label">D₁ (Primary)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="d1-number">{r["D1_opt"]:.3f}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="label">D₂ (Secondary)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="d2-number">{r["D2_opt"]:.3f}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Performance metrics
    st.markdown("Performance")
    col1, col2 = st.columns(2)
    
    col1.metric("Min RMS Current", f"{r['Irms_opt_A']:.3f} A", 
                help="Optimized inductor RMS current")
    col2.metric("Operating Mode", f"Mode {int(r['Mode'])}", 
                help="DAB operating mode (1-6)")
    
    # Summary
    st.markdown("---")
    st.success(f"""
    **Solution:** For **{power:.0f}W**, use D₀={r['D0_opt']:.3f}, D₁={r['D1_opt']:.3f}, D₂={r['D2_opt']:.3f}  
    → Achieves **{r['Irms_opt_A']:.3f}A** RMS current in **Mode {int(r['Mode'])}**
    """)

st.markdown("---")
st.caption("DAB Optimal Control | BTP G29 | IIT Roorkee")
