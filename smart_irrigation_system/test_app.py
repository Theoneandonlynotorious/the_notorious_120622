#!/usr/bin/env python3
"""
Simple test script to verify the Smart Irrigation System works
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        from sklearn.ensemble import RandomForestRegressor
        print("✅ Scikit-learn imported successfully")
    except ImportError as e:
        print(f"❌ Scikit-learn import failed: {e}")
        return False
    
    return True

def test_utility_modules():
    """Test if utility modules can be imported"""
    print("\nTesting utility modules...")
    
    try:
        from utils.database import DatabaseManager
        print("✅ DatabaseManager imported successfully")
        
        # Test database initialization
        db = DatabaseManager()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ DatabaseManager test failed: {e}")
        return False
    
    try:
        from utils.iot_simulator import IoTSensorSimulator
        print("✅ IoTSensorSimulator imported successfully")
        
        # Test sensor simulation
        iot = IoTSensorSimulator()
        data = iot.get_latest_data()
        print(f"✅ Sensor data generated: {list(data.keys())}")
    except Exception as e:
        print(f"❌ IoTSensorSimulator test failed: {e}")
        return False
    
    try:
        from utils.crop_price_predictor import CropPricePredictor
        print("✅ CropPricePredictor imported successfully")
        
        # Test price prediction
        predictor = CropPricePredictor()
        prediction = predictor.predict_price("Wheat", 7)
        print(f"✅ Price prediction generated for Wheat")
    except Exception as e:
        print(f"❌ CropPricePredictor test failed: {e}")
        return False
    
    try:
        from utils.irrigation_controller import IrrigationController
        print("✅ IrrigationController imported successfully")
        
        # Test irrigation controller
        controller = IrrigationController()
        status = controller.get_status()
        print(f"✅ Irrigation status retrieved")
    except Exception as e:
        print(f"❌ IrrigationController test failed: {e}")
        return False
    
    try:
        from utils.weather_api import WeatherAPI
        print("✅ WeatherAPI imported successfully")
        
        # Test weather data
        weather = WeatherAPI()
        current = weather.get_current_weather()
        print(f"✅ Weather data retrieved")
    except Exception as e:
        print(f"❌ WeatherAPI test failed: {e}")
        return False
    
    try:
        from utils.market_data import MarketDataFetcher
        print("✅ MarketDataFetcher imported successfully")
        
        # Test market data
        market = MarketDataFetcher()
        data = market.get_current_market_data()
        print(f"✅ Market data retrieved")
    except Exception as e:
        print(f"❌ MarketDataFetcher test failed: {e}")
        return False
    
    return True

def main():
    print("🌱 Smart Irrigation & Crop Price Prediction System - Test Suite")
    print("=" * 70)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed!")
        return False
    
    # Test utility modules
    if not test_utility_modules():
        print("\n❌ Utility module tests failed!")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 All tests passed! The system is ready to use.")
    print("\nTo start the application:")
    print("1. Run: python3 -m streamlit run app.py")
    print("2. Open your browser to: http://localhost:8501")
    print("\nNote: Add /home/ubuntu/.local/bin to PATH for streamlit command")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)