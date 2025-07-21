import random
import time
import threading
from datetime import datetime, timedelta
import json
import numpy as np

class IoTSensorSimulator:
    def __init__(self):
        self.running = False
        self.current_data = {
            'soil_moisture': 45.0,
            'temperature': 25.0,
            'humidity': 60.0,
            'light_intensity': 50000,
            'ph_level': 7.0,
            'nitrogen': 50,
            'phosphorus': 30,
            'potassium': 40,
            'timestamp': datetime.now()
        }
        self.data_history = []
        self.simulation_thread = None
        self.start_simulation()
    
    def start_simulation(self):
        """Start the sensor data simulation"""
        if not self.running:
            self.running = True
            self.simulation_thread = threading.Thread(target=self._simulate_sensors, daemon=True)
            self.simulation_thread.start()
    
    def stop_simulation(self):
        """Stop the sensor data simulation"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join()
    
    def _simulate_sensors(self):
        """Simulate sensor readings with realistic variations"""
        while self.running:
            # Simulate time-based variations
            hour = datetime.now().hour
            
            # Soil moisture (affected by irrigation and evaporation)
            base_moisture = 45
            if 6 <= hour <= 18:  # Daytime evaporation
                moisture_trend = -0.5
            else:  # Nighttime retention
                moisture_trend = 0.1
            
            self.current_data['soil_moisture'] += random.uniform(-1, 1) + moisture_trend
            self.current_data['soil_moisture'] = max(10, min(90, self.current_data['soil_moisture']))
            
            # Temperature (follows daily cycle)
            base_temp = 25 + 10 * np.sin((hour - 6) * np.pi / 12)  # Peak at 2 PM
            self.current_data['temperature'] = base_temp + random.uniform(-3, 3)
            self.current_data['temperature'] = max(5, min(45, self.current_data['temperature']))
            
            # Humidity (inversely related to temperature)
            base_humidity = 80 - (self.current_data['temperature'] - 20) * 2
            self.current_data['humidity'] = base_humidity + random.uniform(-10, 10)
            self.current_data['humidity'] = max(20, min(95, self.current_data['humidity']))
            
            # Light intensity (follows sun cycle)
            if 6 <= hour <= 18:
                base_light = 80000 * np.sin((hour - 6) * np.pi / 12)
            else:
                base_light = 0
            
            self.current_data['light_intensity'] = max(0, base_light + random.uniform(-5000, 5000))
            
            # pH level (relatively stable with small variations)
            self.current_data['ph_level'] += random.uniform(-0.1, 0.1)
            self.current_data['ph_level'] = max(5.5, min(8.5, self.current_data['ph_level']))
            
            # Nutrient levels (NPK - slowly decrease over time)
            nutrients = ['nitrogen', 'phosphorus', 'potassium']
            for nutrient in nutrients:
                self.current_data[nutrient] += random.uniform(-0.5, 0.2)  # Slight depletion
                self.current_data[nutrient] = max(0, min(100, self.current_data[nutrient]))
            
            # Update timestamp
            self.current_data['timestamp'] = datetime.now()
            
            # Store in history (keep last 1000 readings)
            self.data_history.append(self.current_data.copy())
            if len(self.data_history) > 1000:
                self.data_history.pop(0)
            
            time.sleep(5)  # Update every 5 seconds
    
    def get_latest_data(self):
        """Get the latest sensor readings"""
        return self.current_data.copy()
    
    def get_historical_data(self, hours=24):
        """Get historical sensor data"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        filtered_data = [
            data for data in self.data_history 
            if data['timestamp'] >= cutoff_time
        ]
        return filtered_data
    
    def simulate_irrigation_effect(self, duration_minutes=30):
        """Simulate the effect of irrigation on soil moisture"""
        def irrigation_effect():
            # Gradually increase soil moisture over irrigation duration
            moisture_increase = 40  # Maximum increase
            steps = duration_minutes * 12  # 5-second intervals
            increase_per_step = moisture_increase / steps
            
            for _ in range(steps):
                if self.running:
                    self.current_data['soil_moisture'] += increase_per_step
                    self.current_data['soil_moisture'] = min(90, self.current_data['soil_moisture'])
                    time.sleep(5)
        
        # Run irrigation effect in a separate thread
        irrigation_thread = threading.Thread(target=irrigation_effect, daemon=True)
        irrigation_thread.start()
    
    def add_sensor_noise(self, noise_level=1.0):
        """Add noise to sensor readings (for testing purposes)"""
        for key in ['soil_moisture', 'temperature', 'humidity']:
            if key in self.current_data:
                noise = random.uniform(-noise_level, noise_level)
                self.current_data[key] += noise
    
    def simulate_sensor_malfunction(self, sensor_type, duration_seconds=60):
        """Simulate sensor malfunction"""
        def malfunction():
            original_value = self.current_data[sensor_type]
            # Set to unrealistic value
            if sensor_type == 'soil_moisture':
                self.current_data[sensor_type] = -1  # Invalid reading
            elif sensor_type == 'temperature':
                self.current_data[sensor_type] = 999  # Invalid reading
            
            time.sleep(duration_seconds)
            self.current_data[sensor_type] = original_value
        
        malfunction_thread = threading.Thread(target=malfunction, daemon=True)
        malfunction_thread.start()
    
    def calibrate_sensor(self, sensor_type, calibration_offset):
        """Apply calibration offset to sensor"""
        if sensor_type in self.current_data:
            self.current_data[sensor_type] += calibration_offset
    
    def get_sensor_status(self):
        """Get the status of all sensors"""
        status = {}
        
        # Check if readings are within normal ranges
        status['soil_moisture'] = 'OK' if 0 <= self.current_data['soil_moisture'] <= 100 else 'ERROR'
        status['temperature'] = 'OK' if -10 <= self.current_data['temperature'] <= 50 else 'ERROR'
        status['humidity'] = 'OK' if 0 <= self.current_data['humidity'] <= 100 else 'ERROR'
        status['light_intensity'] = 'OK' if self.current_data['light_intensity'] >= 0 else 'ERROR'
        status['ph_level'] = 'OK' if 0 <= self.current_data['ph_level'] <= 14 else 'ERROR'
        
        return status
    
    def export_data_to_json(self, filename=None):
        """Export sensor data to JSON file"""
        if filename is None:
            filename = f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        export_data = []
        for data_point in self.data_history:
            data_copy = data_point.copy()
            data_copy['timestamp'] = data_copy['timestamp'].isoformat()
            export_data.append(data_copy)
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return filename
    
    def load_data_from_json(self, filename):
        """Load sensor data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Convert timestamp strings back to datetime objects
            for data_point in data:
                data_point['timestamp'] = datetime.fromisoformat(data_point['timestamp'])
            
            self.data_history = data
            if data:
                self.current_data = data[-1].copy()
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

# MQTT Integration (for real IoT devices)
class MQTTSensorClient:
    def __init__(self, broker_host="localhost", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.connected = False
        
    def connect(self):
        """Connect to MQTT broker"""
        try:
            import paho.mqtt.client as mqtt
            
            self.client = mqtt.Client()
            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message
            
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            return True
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            return False
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            self.connected = True
            # Subscribe to sensor topics
            topics = [
                "sensors/soil_moisture",
                "sensors/temperature",
                "sensors/humidity",
                "sensors/light_intensity",
                "sensors/ph_level",
                "sensors/nutrients"
            ]
            for topic in topics:
                client.subscribe(topic)
        else:
            print(f"MQTT connection failed with code {rc}")
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Process sensor data from real IoT devices
            print(f"Received data from {topic}: {payload}")
            
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def publish_control_command(self, device, command):
        """Send control commands to IoT devices"""
        if self.connected and self.client:
            topic = f"control/{device}"
            self.client.publish(topic, json.dumps(command))
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False