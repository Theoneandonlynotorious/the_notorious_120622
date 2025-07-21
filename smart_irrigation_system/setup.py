#!/usr/bin/env python3
"""
Setup script for Smart Irrigation & Crop Price Prediction System
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "data",
        "models",
        "static/css",
        "static/js", 
        "static/images",
        "config",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   Created: {directory}")
    
    print("✅ Directories created successfully")

def initialize_database():
    """Initialize the SQLite database"""
    print("🗃️ Initializing database...")
    try:
        from utils.database import DatabaseManager
        db_manager = DatabaseManager()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def create_config_file():
    """Create default configuration file"""
    print("⚙️ Creating configuration file...")
    
    config_content = """# Smart Irrigation System Configuration

# Database Configuration
DATABASE_PATH = "data/smart_irrigation.db"

# API Keys (replace with your actual keys)
OPENWEATHER_API_KEY = "your_openweather_api_key_here"
AGMARKNET_API_KEY = "your_agmarknet_api_key_here"

# MQTT Configuration (for real IoT devices)
MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
MQTT_USERNAME = ""
MQTT_PASSWORD = ""

# System Settings
DEFAULT_FARM_LATITUDE = 28.6139
DEFAULT_FARM_LONGITUDE = 77.2090
DEFAULT_FARM_SIZE_ACRES = 5.0

# Irrigation Settings
DEFAULT_MOISTURE_TRIGGER = 30
DEFAULT_IRRIGATION_DURATION = 15
DEFAULT_WATER_FLOW_RATE = 10

# Alert Settings
EMAIL_NOTIFICATIONS = True
SMS_NOTIFICATIONS = False
ALERT_EMAIL = "your_email@example.com"

# Logging Settings
LOG_LEVEL = "INFO"
LOG_FILE = "logs/irrigation_system.log"

# Security Settings
SESSION_SECRET_KEY = "your_secret_key_here"
ENABLE_AUTHENTICATION = False

# Performance Settings
SENSOR_UPDATE_INTERVAL = 5  # seconds
WEATHER_UPDATE_INTERVAL = 3600  # seconds (1 hour)
PRICE_UPDATE_INTERVAL = 86400  # seconds (24 hours)
"""
    
    config_path = "config/settings.py"
    with open(config_path, "w") as f:
        f.write(config_content)
    
    print(f"✅ Configuration file created: {config_path}")

def create_sample_data():
    """Create sample data for demonstration"""
    print("📊 Creating sample data...")
    try:
        from utils.database import DatabaseManager
        from utils.iot_simulator import IoTSensorSimulator
        from datetime import datetime, timedelta
        import random
        
        db_manager = DatabaseManager()
        
        # Create sample sensor data for the last 7 days
        for i in range(7 * 24):  # 7 days, hourly data
            timestamp = datetime.now() - timedelta(hours=i)
            sample_data = {
                'soil_moisture': random.uniform(20, 80),
                'temperature': random.uniform(15, 40),
                'humidity': random.uniform(30, 90),
                'light_intensity': random.uniform(0, 100000),
                'ph_level': random.uniform(6.0, 8.0),
                'nitrogen': random.uniform(20, 80),
                'phosphorus': random.uniform(15, 60),
                'potassium': random.uniform(25, 70)
            }
            
            # Insert into database (you would modify this to use actual timestamp)
            # db_manager.insert_sensor_data(sample_data)
        
        # Create sample irrigation logs
        for i in range(10):
            start_time = datetime.now() - timedelta(days=random.randint(1, 7))
            end_time = start_time + timedelta(minutes=random.randint(10, 60))
            duration = (end_time - start_time).total_seconds() / 60
            water_used = duration * 10  # 10 liters per minute
            
            db_manager.insert_irrigation_log(
                start_time, end_time, duration, water_used, 
                "Automatic irrigation", False
            )
        
        print("✅ Sample data created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def create_startup_script():
    """Create startup script for easy launching"""
    print("🚀 Creating startup script...")
    
    # Windows batch file
    windows_script = """@echo off
echo Starting Smart Irrigation System...
cd /d "%~dp0"
streamlit run app.py
pause
"""
    
    with open("start_windows.bat", "w") as f:
        f.write(windows_script)
    
    # Unix shell script
    unix_script = """#!/bin/bash
echo "Starting Smart Irrigation System..."
cd "$(dirname "$0")"
streamlit run app.py
"""
    
    with open("start_unix.sh", "w") as f:
        f.write(unix_script)
    
    # Make Unix script executable
    try:
        os.chmod("start_unix.sh", 0o755)
    except:
        pass  # Windows doesn't support chmod
    
    print("✅ Startup scripts created")

def run_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running setup verification tests...")
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: Import main modules
    try:
        from utils.database import DatabaseManager
        from utils.iot_simulator import IoTSensorSimulator
        from utils.crop_price_predictor import CropPricePredictor
        from utils.irrigation_controller import IrrigationController
        from utils.weather_api import WeatherAPI
        from utils.market_data import MarketDataFetcher
        print("   ✅ Module imports successful")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Module import failed: {e}")
    
    # Test 2: Database connection
    try:
        db_manager = DatabaseManager()
        stats = db_manager.get_database_stats()
        print("   ✅ Database connection successful")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
    
    # Test 3: IoT simulator
    try:
        iot_sim = IoTSensorSimulator()
        data = iot_sim.get_latest_data()
        print("   ✅ IoT simulator working")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ IoT simulator failed: {e}")
    
    # Test 4: Price predictor
    try:
        predictor = CropPricePredictor()
        prediction = predictor.predict_price("Wheat", 7)
        print("   ✅ Price predictor working")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Price predictor failed: {e}")
    
    # Test 5: Irrigation controller
    try:
        controller = IrrigationController()
        status = controller.get_status()
        print("   ✅ Irrigation controller working")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Irrigation controller failed: {e}")
    
    print(f"🧪 Tests completed: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def main():
    """Main setup function"""
    print("🌱 Smart Irrigation & Crop Price Prediction System Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Create directories
    create_directories()
    
    # Initialize database
    if not initialize_database():
        return False
    
    # Create configuration file
    create_config_file()
    
    # Create sample data
    create_sample_data()
    
    # Create startup scripts
    create_startup_script()
    
    # Run verification tests
    tests_passed = run_tests()
    
    print("\n" + "=" * 60)
    if tests_passed:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Edit config/settings.py with your API keys")
        print("2. Run 'streamlit run app.py' to start the application")
        print("3. Open http://localhost:8501 in your browser")
        print("\nAlternatively, use the startup scripts:")
        print("- Windows: double-click start_windows.bat")
        print("- Linux/Mac: ./start_unix.sh")
    else:
        print("⚠️ Setup completed with some issues")
        print("Please check the error messages above and resolve them")
    
    return tests_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)