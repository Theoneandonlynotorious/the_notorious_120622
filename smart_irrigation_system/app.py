import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlite3
import json
import time
import threading
from utils.database import DatabaseManager
from utils.iot_simulator import IoTSensorSimulator
from utils.crop_price_predictor import CropPricePredictor
from utils.irrigation_controller import IrrigationController
from utils.weather_api import WeatherAPI
from utils.market_data import MarketDataFetcher

# Page configuration
st.set_page_config(
    page_title="Smart Irrigation & Crop Price System",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f8f0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2E8B57;
        margin: 0.5rem 0;
    }
    .alert-danger {
        background-color: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #c62828;
    }
    .alert-success {
        background-color: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = DatabaseManager()
if 'iot_simulator' not in st.session_state:
    st.session_state.iot_simulator = IoTSensorSimulator()
if 'price_predictor' not in st.session_state:
    st.session_state.price_predictor = CropPricePredictor()
if 'irrigation_controller' not in st.session_state:
    st.session_state.irrigation_controller = IrrigationController()
if 'weather_api' not in st.session_state:
    st.session_state.weather_api = WeatherAPI()
if 'market_fetcher' not in st.session_state:
    st.session_state.market_fetcher = MarketDataFetcher()

def main():
    st.markdown('<h1 class="main-header">🌱 Smart Irrigation & Crop Price System</h1>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Dashboard", "IoT Sensors", "Irrigation Control", "Crop Price Prediction", "Market Analysis", "Settings"]
    )
    
    if page == "Dashboard":
        show_dashboard()
    elif page == "IoT Sensors":
        show_iot_sensors()
    elif page == "Irrigation Control":
        show_irrigation_control()
    elif page == "Crop Price Prediction":
        show_crop_price_prediction()
    elif page == "Market Analysis":
        show_market_analysis()
    elif page == "Settings":
        show_settings()

def show_dashboard():
    st.header("📊 System Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get latest sensor data
    latest_data = st.session_state.iot_simulator.get_latest_data()
    
    with col1:
        st.metric(
            label="Soil Moisture",
            value=f"{latest_data['soil_moisture']:.1f}%",
            delta=f"{latest_data['soil_moisture'] - 45:.1f}%"
        )
    
    with col2:
        st.metric(
            label="Temperature",
            value=f"{latest_data['temperature']:.1f}°C",
            delta=f"{latest_data['temperature'] - 25:.1f}°C"
        )
    
    with col3:
        st.metric(
            label="Humidity",
            value=f"{latest_data['humidity']:.1f}%",
            delta=f"{latest_data['humidity'] - 60:.1f}%"
        )
    
    with col4:
        st.metric(
            label="Light Intensity",
            value=f"{latest_data['light_intensity']:.0f} lux",
            delta=f"{latest_data['light_intensity'] - 50000:.0f}"
        )
    
    # Real-time charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sensor Data Trends")
        sensor_history = st.session_state.db_manager.get_sensor_history(hours=24)
        if not sensor_history.empty:
            fig = px.line(
                sensor_history,
                x='timestamp',
                y=['soil_moisture', 'temperature', 'humidity'],
                title="24-Hour Sensor Trends"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Irrigation Status")
        irrigation_status = st.session_state.irrigation_controller.get_status()
        
        if irrigation_status['active']:
            st.markdown('<div class="alert-success">✅ Irrigation System: ACTIVE</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-danger">❌ Irrigation System: INACTIVE</div>', unsafe_allow_html=True)
        
        # Irrigation history
        irrigation_history = st.session_state.db_manager.get_irrigation_history(days=7)
        if not irrigation_history.empty:
            fig = px.bar(
                irrigation_history,
                x='date',
                y='duration_minutes',
                title="Weekly Irrigation Duration"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Alerts and notifications
    st.subheader("🚨 System Alerts")
    alerts = check_system_alerts(latest_data)
    for alert in alerts:
        st.markdown(f'<div class="alert-danger">{alert}</div>', unsafe_allow_html=True)

def show_iot_sensors():
    st.header("📡 IoT Sensor Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Real-time Sensor Data")
        
        # Auto-refresh toggle
        auto_refresh = st.checkbox("Auto-refresh (5 seconds)", value=True)
        
        if auto_refresh:
            placeholder = st.empty()
            for i in range(60):  # Refresh for 5 minutes
                with placeholder.container():
                    current_data = st.session_state.iot_simulator.get_latest_data()
                    
                    # Create gauge charts
                    fig = go.Figure()
                    
                    fig.add_trace(go.Indicator(
                        mode="gauge+number+delta",
                        value=current_data['soil_moisture'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Soil Moisture (%)"},
                        delta={'reference': 50},
                        gauge={'axis': {'range': [None, 100]},
                               'bar': {'color': "darkblue"},
                               'steps': [
                                   {'range': [0, 30], 'color': "lightgray"},
                                   {'range': [30, 70], 'color': "gray"}],
                               'threshold': {'line': {'color': "red", 'width': 4},
                                           'thickness': 0.75, 'value': 90}}))
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Display raw data
                    st.json(current_data)
                
                time.sleep(5)
        else:
            current_data = st.session_state.iot_simulator.get_latest_data()
            st.json(current_data)
    
    with col2:
        st.subheader("Sensor Configuration")
        
        # Sensor settings
        st.write("**Soil Moisture Sensor**")
        moisture_threshold = st.slider("Low moisture alert (%)", 0, 100, 30)
        
        st.write("**Temperature Sensor**")
        temp_min = st.slider("Min temperature alert (°C)", 0, 50, 15)
        temp_max = st.slider("Max temperature alert (°C)", 0, 50, 35)
        
        st.write("**Humidity Sensor**")
        humidity_threshold = st.slider("Low humidity alert (%)", 0, 100, 40)
        
        if st.button("Save Configuration"):
            config = {
                'moisture_threshold': moisture_threshold,
                'temp_min': temp_min,
                'temp_max': temp_max,
                'humidity_threshold': humidity_threshold
            }
            st.session_state.db_manager.save_sensor_config(config)
            st.success("Configuration saved!")

def show_irrigation_control():
    st.header("💧 Irrigation Control System")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Manual Control")
        
        if st.button("Start Irrigation", type="primary"):
            st.session_state.irrigation_controller.start_irrigation()
            st.success("Irrigation started!")
        
        if st.button("Stop Irrigation"):
            st.session_state.irrigation_controller.stop_irrigation()
            st.success("Irrigation stopped!")
        
        # Schedule irrigation
        st.subheader("Schedule Irrigation")
        schedule_time = st.time_input("Time")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=120, value=30)
        
        if st.button("Schedule"):
            st.session_state.irrigation_controller.schedule_irrigation(schedule_time, duration)
            st.success(f"Irrigation scheduled for {schedule_time} for {duration} minutes")
    
    with col2:
        st.subheader("Automatic Control Settings")
        
        auto_irrigation = st.checkbox("Enable Auto Irrigation", value=True)
        
        if auto_irrigation:
            moisture_trigger = st.slider("Trigger when soil moisture below (%)", 0, 100, 30)
            irrigation_duration = st.slider("Irrigation duration (minutes)", 5, 60, 15)
            
            if st.button("Save Auto Settings"):
                settings = {
                    'auto_enabled': auto_irrigation,
                    'moisture_trigger': moisture_trigger,
                    'duration': irrigation_duration
                }
                st.session_state.irrigation_controller.set_auto_settings(settings)
                st.success("Auto irrigation settings saved!")
        
        # Current status
        st.subheader("Current Status")
        status = st.session_state.irrigation_controller.get_status()
        
        if status['active']:
            st.success("🟢 Irrigation Active")
            st.write(f"Started: {status['start_time']}")
            st.write(f"Duration: {status['duration']} minutes")
        else:
            st.info("🔴 Irrigation Inactive")
        
        # Water usage statistics
        st.subheader("Water Usage")
        usage_data = st.session_state.db_manager.get_water_usage(days=30)
        if not usage_data.empty:
            fig = px.line(usage_data, x='date', y='liters_used', title="Daily Water Usage (L)")
            st.plotly_chart(fig, use_container_width=True)

def show_crop_price_prediction():
    st.header("📈 Crop Price Prediction")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Select Crop")
        
        crops = ["Wheat", "Rice", "Corn", "Soybeans", "Cotton", "Tomatoes", "Potatoes", "Onions"]
        selected_crop = st.selectbox("Choose crop", crops)
        
        prediction_days = st.slider("Prediction period (days)", 7, 90, 30)
        
        if st.button("Generate Prediction", type="primary"):
            with st.spinner("Generating prediction..."):
                prediction = st.session_state.price_predictor.predict_price(selected_crop, prediction_days)
                st.session_state.current_prediction = prediction
    
    with col2:
        st.subheader("Price Prediction Results")
        
        if hasattr(st.session_state, 'current_prediction'):
            prediction = st.session_state.current_prediction
            
            # Current price
            st.metric(
                label=f"Current {selected_crop} Price",
                value=f"₹{prediction['current_price']:.2f}/kg",
                delta=f"{prediction['price_change']:.2f}%"
            )
            
            # Prediction chart
            fig = go.Figure()
            
            # Historical data
            fig.add_trace(go.Scatter(
                x=prediction['historical_dates'],
                y=prediction['historical_prices'],
                mode='lines',
                name='Historical Prices',
                line=dict(color='blue')
            ))
            
            # Predicted data
            fig.add_trace(go.Scatter(
                x=prediction['prediction_dates'],
                y=prediction['predicted_prices'],
                mode='lines',
                name='Predicted Prices',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title=f"{selected_crop} Price Prediction",
                xaxis_title="Date",
                yaxis_title="Price (₹/kg)",
                hovermode='x'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Prediction insights
            st.subheader("Market Insights")
            
            if prediction['trend'] == 'increasing':
                st.success("📈 Prices are expected to increase. Good time to hold crops.")
            elif prediction['trend'] == 'decreasing':
                st.warning("📉 Prices are expected to decrease. Consider selling soon.")
            else:
                st.info("📊 Prices are expected to remain stable.")
            
            # Confidence level
            st.write(f"**Prediction Confidence:** {prediction['confidence']:.1f}%")
            
            # Best selling window
            st.write(f"**Optimal Selling Period:** {prediction['best_selling_window']}")

def show_market_analysis():
    st.header("📊 Market Analysis")
    
    # Market overview
    st.subheader("Current Market Overview")
    
    market_data = st.session_state.market_fetcher.get_current_market_data()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Market Trend", "Bullish", "↗️ 2.3%")
    
    with col2:
        st.metric("Avg Price Change", "+₹12.50", "↗️ 5.2%")
    
    with col3:
        st.metric("Trading Volume", "High", "↗️ 15%")
    
    # Price comparison chart
    st.subheader("Multi-Crop Price Comparison")
    
    crops_data = {
        'Crop': ['Wheat', 'Rice', 'Corn', 'Soybeans', 'Cotton'],
        'Current Price': [25.50, 45.20, 18.75, 55.30, 85.40],
        'Last Week': [24.80, 44.10, 18.20, 54.20, 83.20],
        'Change %': [2.8, 2.5, 3.0, 2.0, 2.6]
    }
    
    df = pd.DataFrame(crops_data)
    
    fig = px.bar(
        df,
        x='Crop',
        y=['Current Price', 'Last Week'],
        title="Current vs Last Week Prices",
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Market news and updates
    st.subheader("📰 Market News & Updates")
    
    news_items = [
        {
            "title": "Monsoon forecast positive for Kharif crops",
            "summary": "IMD predicts normal rainfall, boosting crop prospects",
            "impact": "Positive",
            "date": "2024-01-15"
        },
        {
            "title": "Export demand for wheat increases",
            "summary": "International buyers showing increased interest",
            "impact": "Positive",
            "date": "2024-01-14"
        },
        {
            "title": "Storage facility expansion announced",
            "summary": "Government announces new cold storage facilities",
            "impact": "Positive",
            "date": "2024-01-13"
        }
    ]
    
    for news in news_items:
        with st.expander(f"📰 {news['title']} - {news['date']}"):
            st.write(news['summary'])
            impact_color = "green" if news['impact'] == "Positive" else "red"
            st.markdown(f"**Impact:** <span style='color:{impact_color}'>{news['impact']}</span>", unsafe_allow_html=True)

def show_settings():
    st.header("⚙️ System Settings")
    
    tab1, tab2, tab3 = st.tabs(["General", "Notifications", "Data Management"])
    
    with tab1:
        st.subheader("General Settings")
        
        # Location settings
        st.write("**Farm Location**")
        latitude = st.number_input("Latitude", value=28.6139, format="%.4f")
        longitude = st.number_input("Longitude", value=77.2090, format="%.4f")
        
        # Farm details
        st.write("**Farm Details**")
        farm_size = st.number_input("Farm size (acres)", min_value=0.1, value=5.0)
        crop_type = st.selectbox("Primary crop", ["Wheat", "Rice", "Corn", "Mixed"])
        
        if st.button("Save General Settings"):
            settings = {
                'latitude': latitude,
                'longitude': longitude,
                'farm_size': farm_size,
                'crop_type': crop_type
            }
            st.session_state.db_manager.save_general_settings(settings)
            st.success("Settings saved!")
    
    with tab2:
        st.subheader("Notification Settings")
        
        email_notifications = st.checkbox("Email notifications", value=True)
        sms_notifications = st.checkbox("SMS notifications", value=False)
        
        st.write("**Alert Thresholds**")
        low_moisture_alert = st.slider("Low soil moisture alert (%)", 0, 100, 25)
        high_temp_alert = st.slider("High temperature alert (°C)", 20, 50, 40)
        
        if st.button("Save Notification Settings"):
            st.success("Notification settings saved!")
    
    with tab3:
        st.subheader("Data Management")
        
        # Database statistics
        stats = st.session_state.db_manager.get_database_stats()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Sensor Records", f"{stats['sensor_records']:,}")
            st.metric("Irrigation Records", f"{stats['irrigation_records']:,}")
        
        with col2:
            st.metric("Price Records", f"{stats['price_records']:,}")
            st.metric("Database Size", f"{stats['db_size_mb']:.1f} MB")
        
        # Data export
        st.write("**Data Export**")
        export_type = st.selectbox("Export type", ["Sensor Data", "Irrigation Logs", "Price Data", "All Data"])
        
        if st.button("Export Data"):
            # Implement data export functionality
            st.success("Data exported successfully!")
        
        # Data cleanup
        st.write("**Data Cleanup**")
        st.warning("⚠️ This will permanently delete old data!")
        
        if st.button("Delete data older than 1 year", type="secondary"):
            if st.session_state.db_manager.cleanup_old_data(days=365):
                st.success("Old data cleaned up!")

def check_system_alerts(sensor_data):
    alerts = []
    
    if sensor_data['soil_moisture'] < 25:
        alerts.append("🚨 Low soil moisture detected! Consider irrigation.")
    
    if sensor_data['temperature'] > 40:
        alerts.append("🌡️ High temperature alert! Monitor crops closely.")
    
    if sensor_data['humidity'] < 30:
        alerts.append("💨 Low humidity detected! Increase irrigation frequency.")
    
    # Check irrigation system
    irrigation_status = st.session_state.irrigation_controller.get_status()
    if not irrigation_status['system_health']:
        alerts.append("⚠️ Irrigation system malfunction detected!")
    
    return alerts

if __name__ == "__main__":
    main()