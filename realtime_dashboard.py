"""
Real-time Model Performance Dashboard
Displays live metrics, feature importances, and predictions
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Bitcoin ML - Real-time Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .title-large {
        font-size: 28px;
        font-weight: bold;
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("# 📊 Bitcoin Price Prediction - Real-time Dashboard")
st.markdown("---")

# Initialize session state for data persistence
if 'metrics_history' not in st.session_state:
    st.session_state.metrics_history = []

# Paths (resolve relative to this file so they work inside the container)
BASE_DIR = Path(__file__).resolve().parent
METRICS_FILE = BASE_DIR / "model_metrics.txt"
PREDICTIONS_LOG = BASE_DIR / "predictions_log.json"
METRICS_HISTORY_FILE = BASE_DIR / "metrics_history.json"

def load_current_metrics():
    """Load the latest model metrics from file"""
    try:
        if METRICS_FILE.exists():
            with METRICS_FILE.open('r') as f:
                content = f.read()
                metrics = {}
                for line in content.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metrics[key.strip()] = value.strip()
                return metrics
    except Exception as e:
        st.warning(f"Error loading metrics: {e}")
    return None

def load_metrics_history():
    """Load historical metrics data"""
    try:
        if METRICS_HISTORY_FILE.exists():
            with METRICS_HISTORY_FILE.open('r') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Error loading history: {e}")
    return []

def parse_metrics(metrics_dict):
    """Parse metrics dictionary"""
    parsed = {
        'model': metrics_dict.get('Model', 'GBTRegressor'),
        'rmse': float(metrics_dict.get('RMSE', 0)),
        'mae': float(metrics_dict.get('MAE', 0)),
        'trees': int(metrics_dict.get('Trees', 0)),
        'batch': int(metrics_dict.get('Batch', 0)),
    }
    
    # Parse feature importances
    try:
        features_str = metrics_dict.get('Feature Importances', '[]')
        # Clean the string
        features_str = features_str.replace('[', '').replace(']', '').strip()
        if features_str:
            parsed['feature_importances'] = [float(x.strip()) for x in features_str.split(',')]
        else:
            parsed['feature_importances'] = [0, 0, 0, 0]
    except:
        parsed['feature_importances'] = [0, 0, 0, 0]
    
    return parsed

# Sidebar Controls
st.sidebar.title("⚙️ Dashboard Controls")
refresh_interval = st.sidebar.slider(
    "Refresh interval (seconds)",
    min_value=1,
    max_value=60,
    value=5
)
auto_refresh = st.sidebar.checkbox("Enable Auto-refresh", value=True)

# Create placeholder for metrics
metrics_placeholder = st.empty()
charts_placeholder = st.empty()

# Main loop
while True:
    # Load metrics
    metrics = load_current_metrics()
    history = load_metrics_history()
    
    with metrics_placeholder.container():
        # Metrics Section
        if metrics:
            parsed = parse_metrics(metrics)
            
            # Top row - Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "📈 RMSE",
                    f"{parsed['rmse']:.2f}",
                    delta=None,
                    delta_color="inverse"
                )
            
            with col2:
                st.metric(
                    "📊 MAE",
                    f"{parsed['mae']:.2f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "🌳 Decision Trees",
                    f"{parsed['trees']}",
                    delta=None
                )
            
            with col4:
                st.metric(
                    "📦 Latest Batch",
                    f"{parsed['batch']}",
                    delta=None
                )
            
            st.markdown("---")
            
            # Feature Importances
            st.subheader("🎯 Feature Importances")
            feature_names = ["Open", "High", "Low", "Volume"]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        x=feature_names,
                        y=parsed['feature_importances'],
                        marker=dict(
                            color=parsed['feature_importances'],
                            colorscale='Viridis'
                        ),
                        text=[f"{v:.4f}" for v in parsed['feature_importances']],
                        textposition='auto'
                    )
                ])
                fig.update_layout(
                    title="Feature Importance Scores",
                    xaxis_title="Features",
                    yaxis_title="Importance",
                    showlegend=False,
                    height=350,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.write("**Top Features:**")
                feature_importance_df = pd.DataFrame({
                    'Feature': feature_names,
                    'Importance': parsed['feature_importances']
                }).sort_values('Importance', ascending=False)
                
                for idx, row in feature_importance_df.iterrows():
                    st.write(f"• **{row['Feature']}**: {row['Importance']:.4f}")
            
            st.markdown("---")
        else:
            st.info("⏳ Waiting for model metrics... Make sure spark_realtime_ml.py is running")
    
    with charts_placeholder.container():
        # Historical Performance
        if history:
            st.subheader("📉 Model Performance Over Time")
            
            df_history = pd.DataFrame(history)
            
            # Metrics over time
            col1, col2 = st.columns(2)
            
            with col1:
                fig_rmse = go.Figure()
                fig_rmse.add_trace(go.Scatter(
                    x=df_history.get('batch', []),
                    y=df_history.get('rmse', []),
                    mode='lines+markers',
                    name='RMSE',
                    line=dict(color='#ff7f0e', width=3),
                    fill='tozeroy'
                ))
                fig_rmse.update_layout(
                    title="RMSE Over Batches",
                    xaxis_title="Batch Number",
                    yaxis_title="RMSE",
                    height=350,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_rmse, use_container_width=True)
            
            with col2:
                fig_mae = go.Figure()
                fig_mae.add_trace(go.Scatter(
                    x=df_history.get('batch', []),
                    y=df_history.get('mae', []),
                    mode='lines+markers',
                    name='MAE',
                    line=dict(color='#2ca02c', width=3),
                    fill='tozeroy'
                ))
                fig_mae.update_layout(
                    title="MAE Over Batches",
                    xaxis_title="Batch Number",
                    yaxis_title="MAE",
                    height=350,
                    hovermode='x unified'
                )
                st.plotly_chart(fig_mae, use_container_width=True)
        
        # System Info
        st.subheader("ℹ️ System Information")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with col2:
            st.write(f"**Dashboard**: Real-time Monitoring")
        
        with col3:
            st.write(f"**Total Batches Processed**: {len(history)}")
    
    # Control refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()
    else:
        st.info("Auto-refresh is disabled. Click the button below to refresh manually.")
        if st.button("🔄 Refresh Now"):
            st.rerun()
        break
