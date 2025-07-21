import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os

class DatabaseManager:
    def __init__(self, db_path="data/smart_irrigation.db"):
        self.db_path = db_path
        self.ensure_directory()
        self.init_database()
    
    def ensure_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sensor data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                soil_moisture REAL,
                temperature REAL,
                humidity REAL,
                light_intensity REAL,
                ph_level REAL,
                nitrogen REAL,
                phosphorus REAL,
                potassium REAL
            )
        ''')
        
        # Irrigation logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS irrigation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                end_time DATETIME,
                duration_minutes INTEGER,
                water_used_liters REAL,
                trigger_reason TEXT,
                manual_override BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Crop price data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crop_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                crop_name TEXT,
                price_per_kg REAL,
                market_location TEXT,
                source TEXT
            )
        ''')
        
        # System settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                id INTEGER PRIMARY KEY,
                setting_key TEXT UNIQUE,
                setting_value TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Weather data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_speed REAL,
                precipitation REAL,
                weather_condition TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_sensor_data(self, data):
        """Insert sensor data into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data 
            (soil_moisture, temperature, humidity, light_intensity, ph_level, nitrogen, phosphorus, potassium)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['soil_moisture'],
            data['temperature'],
            data['humidity'],
            data['light_intensity'],
            data.get('ph_level', 7.0),
            data.get('nitrogen', 50),
            data.get('phosphorus', 30),
            data.get('potassium', 40)
        ))
        
        conn.commit()
        conn.close()
    
    def get_sensor_history(self, hours=24):
        """Get sensor data history"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM sensor_data 
            WHERE timestamp >= datetime('now', '-{} hours')
            ORDER BY timestamp DESC
        '''.format(hours)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def insert_irrigation_log(self, start_time, end_time, duration, water_used, reason, manual=False):
        """Insert irrigation log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO irrigation_logs 
            (start_time, end_time, duration_minutes, water_used_liters, trigger_reason, manual_override)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (start_time, end_time, duration, water_used, reason, manual))
        
        conn.commit()
        conn.close()
    
    def get_irrigation_history(self, days=7):
        """Get irrigation history"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT DATE(start_time) as date, 
                   SUM(duration_minutes) as duration_minutes,
                   SUM(water_used_liters) as water_used
            FROM irrigation_logs 
            WHERE start_time >= datetime('now', '-{} days')
            GROUP BY DATE(start_time)
            ORDER BY date DESC
        '''.format(days)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def get_water_usage(self, days=30):
        """Get water usage statistics"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT DATE(start_time) as date, 
                   SUM(water_used_liters) as liters_used
            FROM irrigation_logs 
            WHERE start_time >= datetime('now', '-{} days')
            GROUP BY DATE(start_time)
            ORDER BY date
        '''.format(days)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def insert_crop_price(self, date, crop_name, price, market_location, source):
        """Insert crop price data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO crop_prices 
            (date, crop_name, price_per_kg, market_location, source)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, crop_name, price, market_location, source))
        
        conn.commit()
        conn.close()
    
    def get_crop_price_history(self, crop_name, days=90):
        """Get crop price history"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM crop_prices 
            WHERE crop_name = ? AND date >= date('now', '-{} days')
            ORDER BY date
        '''.format(days)
        
        df = pd.read_sql_query(query, conn, params=(crop_name,))
        conn.close()
        
        return df
    
    def save_setting(self, key, value):
        """Save system setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO system_settings (setting_key, setting_value)
            VALUES (?, ?)
        ''', (key, json.dumps(value)))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key, default=None):
        """Get system setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT setting_value FROM system_settings WHERE setting_key = ?', (key,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return json.loads(result[0])
        return default
    
    def save_sensor_config(self, config):
        """Save sensor configuration"""
        self.save_setting('sensor_config', config)
    
    def save_general_settings(self, settings):
        """Save general settings"""
        self.save_setting('general_settings', settings)
    
    def get_database_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Count records in each table
        cursor.execute('SELECT COUNT(*) FROM sensor_data')
        stats['sensor_records'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM irrigation_logs')
        stats['irrigation_records'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM crop_prices')
        stats['price_records'] = cursor.fetchone()[0]
        
        # Get database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size_bytes = cursor.fetchone()[0]
        stats['db_size_mb'] = size_bytes / (1024 * 1024)
        
        conn.close()
        
        return stats
    
    def cleanup_old_data(self, days=365):
        """Clean up old data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete old sensor data
            cursor.execute('''
                DELETE FROM sensor_data 
                WHERE timestamp < datetime('now', '-{} days')
            '''.format(days))
            
            # Delete old irrigation logs
            cursor.execute('''
                DELETE FROM irrigation_logs 
                WHERE start_time < datetime('now', '-{} days')
            '''.format(days))
            
            # Delete old crop prices
            cursor.execute('''
                DELETE FROM crop_prices 
                WHERE date < date('now', '-{} days')
            '''.format(days))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error cleaning up data: {e}")
            return False