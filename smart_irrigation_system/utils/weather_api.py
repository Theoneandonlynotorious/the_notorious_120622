import requests
import json
from datetime import datetime, timedelta
import random

class WeatherAPI:
    def __init__(self, api_key=None):
        self.api_key = api_key or "demo_key"  # Use demo key for simulation
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
        
    def get_current_weather(self, lat=28.6139, lon=77.2090):
        """Get current weather data"""
        try:
            # For demonstration, return simulated weather data
            # In production, use actual API call
            current_weather = self._simulate_current_weather()
            return current_weather
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return self._get_fallback_weather()
    
    def get_weather_forecast(self, lat=28.6139, lon=77.2090, days=5):
        """Get weather forecast"""
        try:
            # For demonstration, return simulated forecast data
            forecast = self._simulate_weather_forecast(days)
            return forecast
        except Exception as e:
            print(f"Error fetching forecast data: {e}")
            return self._get_fallback_forecast(days)
    
    def _simulate_current_weather(self):
        """Simulate current weather data"""
        hour = datetime.now().hour
        
        # Simulate temperature based on time of day
        if 6 <= hour <= 18:  # Daytime
            temp = random.uniform(25, 40)
        else:  # Nighttime
            temp = random.uniform(15, 25)
        
        # Simulate other weather parameters
        humidity = random.uniform(40, 80)
        pressure = random.uniform(1000, 1020)
        wind_speed = random.uniform(0, 15)
        
        # Simulate weather conditions
        conditions = ["clear", "partly_cloudy", "cloudy", "rain", "thunderstorm"]
        weights = [0.4, 0.3, 0.2, 0.08, 0.02]  # Probability weights
        weather_condition = random.choices(conditions, weights=weights)[0]
        
        # Simulate precipitation
        if weather_condition in ["rain", "thunderstorm"]:
            precipitation = random.uniform(0.1, 10.0)
        else:
            precipitation = 0.0
        
        return {
            "timestamp": datetime.now(),
            "temperature": round(temp, 1),
            "humidity": round(humidity, 1),
            "pressure": round(pressure, 1),
            "wind_speed": round(wind_speed, 1),
            "precipitation": round(precipitation, 2),
            "weather_condition": weather_condition,
            "description": self._get_weather_description(weather_condition),
            "visibility": random.uniform(5, 15),
            "uv_index": max(0, min(11, random.uniform(0, 8) if 6 <= hour <= 18 else 0))
        }
    
    def _simulate_weather_forecast(self, days):
        """Simulate weather forecast data"""
        forecast = []
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            
            # Simulate daily weather
            day_weather = {
                "date": date.date(),
                "temp_max": random.uniform(30, 42),
                "temp_min": random.uniform(18, 25),
                "humidity": random.uniform(45, 85),
                "precipitation": random.uniform(0, 5) if random.random() < 0.3 else 0,
                "wind_speed": random.uniform(2, 12),
                "weather_condition": random.choice(["clear", "partly_cloudy", "cloudy", "rain"]),
                "precipitation_probability": random.uniform(0, 100)
            }
            
            day_weather["description"] = self._get_weather_description(day_weather["weather_condition"])
            forecast.append(day_weather)
        
        return forecast
    
    def _get_weather_description(self, condition):
        """Get weather description from condition"""
        descriptions = {
            "clear": "Clear sky",
            "partly_cloudy": "Partly cloudy",
            "cloudy": "Cloudy",
            "rain": "Light rain",
            "thunderstorm": "Thunderstorm"
        }
        return descriptions.get(condition, "Unknown")
    
    def _get_fallback_weather(self):
        """Get fallback weather data when API fails"""
        return {
            "timestamp": datetime.now(),
            "temperature": 25.0,
            "humidity": 60.0,
            "pressure": 1013.0,
            "wind_speed": 5.0,
            "precipitation": 0.0,
            "weather_condition": "clear",
            "description": "Clear sky",
            "visibility": 10.0,
            "uv_index": 3.0
        }
    
    def _get_fallback_forecast(self, days):
        """Get fallback forecast data when API fails"""
        forecast = []
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            forecast.append({
                "date": date.date(),
                "temp_max": 30.0,
                "temp_min": 20.0,
                "humidity": 60.0,
                "precipitation": 0.0,
                "wind_speed": 5.0,
                "weather_condition": "clear",
                "description": "Clear sky",
                "precipitation_probability": 10.0
            })
        return forecast
    
    def get_irrigation_recommendation(self, lat=28.6139, lon=77.2090):
        """Get irrigation recommendation based on weather"""
        current_weather = self.get_current_weather(lat, lon)
        forecast = self.get_weather_forecast(lat, lon, 3)
        
        recommendation = {
            "should_irrigate": True,
            "confidence": 50,
            "reason": "Normal irrigation schedule",
            "timing": "morning",
            "duration_adjustment": 0
        }
        
        # Check current weather conditions
        if current_weather["precipitation"] > 5:
            recommendation.update({
                "should_irrigate": False,
                "confidence": 90,
                "reason": "Heavy rainfall detected",
                "timing": "skip",
                "duration_adjustment": 0
            })
        elif current_weather["weather_condition"] == "rain":
            recommendation.update({
                "should_irrigate": False,
                "confidence": 80,
                "reason": "Rain in progress",
                "timing": "skip",
                "duration_adjustment": 0
            })
        
        # Check forecast for next 24 hours
        rain_expected = any(day["precipitation"] > 2 for day in forecast[:1])
        if rain_expected:
            recommendation.update({
                "should_irrigate": False,
                "confidence": 75,
                "reason": "Rain expected within 24 hours",
                "timing": "postpone",
                "duration_adjustment": 0
            })
        
        # Check temperature and humidity
        if current_weather["temperature"] > 35 and current_weather["humidity"] < 40:
            recommendation.update({
                "should_irrigate": True,
                "confidence": 85,
                "reason": "High temperature and low humidity",
                "timing": "early_morning",
                "duration_adjustment": 20  # Increase duration by 20%
            })
        
        # Check wind conditions
        if current_weather["wind_speed"] > 10:
            recommendation.update({
                "timing": "early_morning",
                "duration_adjustment": recommendation["duration_adjustment"] + 10,
                "reason": recommendation["reason"] + " + windy conditions"
            })
        
        return recommendation
    
    def get_evapotranspiration_estimate(self, lat=28.6139, lon=77.2090):
        """Estimate evapotranspiration rate"""
        current_weather = self.get_current_weather(lat, lon)
        
        # Simplified Penman-Monteith equation estimation
        temp = current_weather["temperature"]
        humidity = current_weather["humidity"]
        wind_speed = current_weather["wind_speed"]
        
        # Basic ET calculation (mm/day)
        et_rate = (0.0023 * (temp + 17.8) * 
                  ((100 - humidity) / 100) * 
                  (1 + 0.1 * wind_speed))
        
        return {
            "et_rate_mm_per_day": round(et_rate, 2),
            "water_requirement_liters_per_sqm": round(et_rate / 10, 3),
            "recommended_irrigation_duration": round(et_rate * 2, 0),  # minutes
            "factors": {
                "temperature_effect": temp / 30,
                "humidity_effect": (100 - humidity) / 100,
                "wind_effect": 1 + (wind_speed / 50)
            }
        }
    
    def get_weather_alerts(self, lat=28.6139, lon=77.2090):
        """Get weather alerts and warnings"""
        current_weather = self.get_current_weather(lat, lon)
        forecast = self.get_weather_forecast(lat, lon, 3)
        
        alerts = []
        
        # Temperature alerts
        if current_weather["temperature"] > 40:
            alerts.append({
                "type": "heat_wave",
                "severity": "high",
                "message": "Extreme heat warning - increase irrigation frequency",
                "action": "Irrigate early morning and evening"
            })
        elif current_weather["temperature"] > 35:
            alerts.append({
                "type": "high_temperature",
                "severity": "medium",
                "message": "High temperature alert - monitor soil moisture",
                "action": "Consider additional irrigation"
            })
        
        # Precipitation alerts
        heavy_rain_forecast = any(day["precipitation"] > 10 for day in forecast)
        if heavy_rain_forecast:
            alerts.append({
                "type": "heavy_rain",
                "severity": "medium",
                "message": "Heavy rain expected - suspend irrigation",
                "action": "Cancel scheduled irrigation for next 24-48 hours"
            })
        
        # Wind alerts
        if current_weather["wind_speed"] > 15:
            alerts.append({
                "type": "high_wind",
                "severity": "medium",
                "message": "High wind conditions - irrigation efficiency reduced",
                "action": "Use drip irrigation or irrigate during calm periods"
            })
        
        # Humidity alerts
        if current_weather["humidity"] < 30:
            alerts.append({
                "type": "low_humidity",
                "severity": "medium",
                "message": "Very low humidity - increased water loss",
                "action": "Increase irrigation frequency and duration"
            })
        
        return alerts
    
    def get_seasonal_recommendations(self, month=None):
        """Get seasonal irrigation recommendations"""
        if month is None:
            month = datetime.now().month
        
        seasonal_advice = {
            # Winter months (Dec, Jan, Feb)
            12: {"season": "Winter", "irrigation_frequency": "Low", "best_time": "Mid-day", "notes": "Reduce irrigation, avoid frost periods"},
            1: {"season": "Winter", "irrigation_frequency": "Low", "best_time": "Mid-day", "notes": "Minimal irrigation needed, protect from frost"},
            2: {"season": "Winter", "irrigation_frequency": "Low", "best_time": "Mid-day", "notes": "Gradually increase as temperature rises"},
            
            # Spring months (Mar, Apr, May)
            3: {"season": "Spring", "irrigation_frequency": "Medium", "best_time": "Morning", "notes": "Increase irrigation for growing season"},
            4: {"season": "Spring", "irrigation_frequency": "Medium", "best_time": "Morning", "notes": "Monitor for dry spells"},
            5: {"season": "Spring", "irrigation_frequency": "High", "best_time": "Early morning", "notes": "Peak growing season, ensure adequate water"},
            
            # Summer months (Jun, Jul, Aug)
            6: {"season": "Summer", "irrigation_frequency": "High", "best_time": "Early morning", "notes": "Hot weather, increase frequency"},
            7: {"season": "Summer", "irrigation_frequency": "Very High", "best_time": "Early morning/Evening", "notes": "Peak summer, avoid midday irrigation"},
            8: {"season": "Summer", "irrigation_frequency": "Very High", "best_time": "Early morning/Evening", "notes": "Continue intensive irrigation"},
            
            # Monsoon/Fall months (Sep, Oct, Nov)
            9: {"season": "Monsoon", "irrigation_frequency": "Variable", "best_time": "As needed", "notes": "Reduce based on rainfall"},
            10: {"season": "Post-monsoon", "irrigation_frequency": "Medium", "best_time": "Morning", "notes": "Resume regular irrigation"},
            11: {"season": "Fall", "irrigation_frequency": "Medium", "best_time": "Morning", "notes": "Prepare for winter reduction"}
        }
        
        return seasonal_advice.get(month, seasonal_advice[1])
    
    def calculate_water_savings(self, weather_data, irrigation_schedule):
        """Calculate potential water savings based on weather"""
        savings = {
            "total_scheduled_water": 0,
            "weather_adjusted_water": 0,
            "water_saved": 0,
            "savings_percentage": 0,
            "cost_savings": 0  # Assuming cost per liter
        }
        
        # This would integrate with actual irrigation scheduling
        # For demonstration, calculate estimated savings
        
        base_water_per_session = 100  # liters
        sessions_per_week = 7
        
        savings["total_scheduled_water"] = base_water_per_session * sessions_per_week
        
        # Adjust based on weather
        rain_days = sum(1 for day in weather_data if day.get("precipitation", 0) > 5)
        hot_days = sum(1 for day in weather_data if day.get("temp_max", 25) > 35)
        
        # Skip irrigation on rainy days
        water_saved_rain = rain_days * base_water_per_session
        
        # Increase irrigation on hot days
        extra_water_hot = hot_days * (base_water_per_session * 0.2)
        
        savings["weather_adjusted_water"] = (
            savings["total_scheduled_water"] - 
            water_saved_rain + 
            extra_water_hot
        )
        
        savings["water_saved"] = savings["total_scheduled_water"] - savings["weather_adjusted_water"]
        
        if savings["total_scheduled_water"] > 0:
            savings["savings_percentage"] = (
                savings["water_saved"] / savings["total_scheduled_water"]
            ) * 100
        
        # Assuming water cost (₹ per liter)
        water_cost_per_liter = 0.05
        savings["cost_savings"] = savings["water_saved"] * water_cost_per_liter
        
        return savings