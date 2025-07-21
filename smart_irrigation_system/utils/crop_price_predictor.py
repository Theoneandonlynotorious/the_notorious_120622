import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import requests
import json
import warnings
warnings.filterwarnings('ignore')

class CropPricePredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.crop_data = {}
        self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Initialize with sample historical data for demonstration"""
        crops = ["Wheat", "Rice", "Corn", "Soybeans", "Cotton", "Tomatoes", "Potatoes", "Onions"]
        
        # Generate sample historical data for each crop
        for crop in crops:
            dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
            
            # Create realistic price trends with seasonality
            base_price = {
                "Wheat": 25, "Rice": 45, "Corn": 18, "Soybeans": 55,
                "Cotton": 85, "Tomatoes": 35, "Potatoes": 20, "Onions": 30
            }[crop]
            
            # Add seasonal variations and trends
            prices = []
            for i, date in enumerate(dates):
                # Seasonal component
                seasonal = 5 * np.sin(2 * np.pi * date.dayofyear / 365)
                
                # Trend component
                trend = 0.01 * i  # Slight upward trend
                
                # Random noise
                noise = np.random.normal(0, 2)
                
                # Market events (random spikes/drops)
                if np.random.random() < 0.05:  # 5% chance of market event
                    event = np.random.choice([-10, 10])  # Price shock
                else:
                    event = 0
                
                price = base_price + seasonal + trend + noise + event
                prices.append(max(price, base_price * 0.5))  # Minimum price floor
            
            self.crop_data[crop] = pd.DataFrame({
                'date': dates,
                'price': prices,
                'volume': np.random.normal(1000, 200, len(dates)),
                'weather_factor': np.random.normal(1, 0.2, len(dates)),
                'demand_factor': np.random.normal(1, 0.15, len(dates))
            })
    
    def prepare_features(self, data):
        """Prepare features for machine learning model"""
        df = data.copy()
        
        # Time-based features
        df['day_of_year'] = df['date'].dt.dayofyear
        df['month'] = df['date'].dt.month
        df['quarter'] = df['date'].dt.quarter
        df['year'] = df['date'].dt.year
        
        # Price-based features
        df['price_lag_1'] = df['price'].shift(1)
        df['price_lag_7'] = df['price'].shift(7)
        df['price_lag_30'] = df['price'].shift(30)
        
        # Moving averages
        df['price_ma_7'] = df['price'].rolling(window=7).mean()
        df['price_ma_30'] = df['price'].rolling(window=30).mean()
        
        # Price volatility
        df['price_volatility'] = df['price'].rolling(window=7).std()
        
        # Price momentum
        df['price_momentum'] = df['price'] / df['price_ma_30'] - 1
        
        # Volume features
        df['volume_ma_7'] = df['volume'].rolling(window=7).mean()
        df['volume_ratio'] = df['volume'] / df['volume_ma_7']
        
        # External factors
        df['weather_impact'] = df['weather_factor']
        df['demand_impact'] = df['demand_factor']
        
        # Drop NaN values
        df = df.dropna()
        
        return df
    
    def train_model(self, crop_name):
        """Train prediction model for a specific crop"""
        if crop_name not in self.crop_data:
            raise ValueError(f"No data available for crop: {crop_name}")
        
        # Prepare data
        data = self.prepare_features(self.crop_data[crop_name])
        
        # Define features and target
        feature_columns = [
            'day_of_year', 'month', 'quarter', 'year',
            'price_lag_1', 'price_lag_7', 'price_lag_30',
            'price_ma_7', 'price_ma_30', 'price_volatility', 'price_momentum',
            'volume_ma_7', 'volume_ratio', 'weather_impact', 'demand_impact'
        ]
        
        X = data[feature_columns]
        y = data['price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=False
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Random Forest model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Store model and scaler
        self.models[crop_name] = model
        self.scalers[crop_name] = scaler
        
        return {
            'mae': mae,
            'r2_score': r2,
            'feature_importance': dict(zip(feature_columns, model.feature_importances_))
        }
    
    def predict_price(self, crop_name, prediction_days=30):
        """Predict crop prices for the next N days"""
        if crop_name not in self.crop_data:
            # Train model if not exists
            self.train_model(crop_name)
        
        if crop_name not in self.models:
            self.train_model(crop_name)
        
        model = self.models[crop_name]
        scaler = self.scalers[crop_name]
        
        # Get recent data
        recent_data = self.crop_data[crop_name].tail(60).copy()
        prepared_data = self.prepare_features(recent_data)
        
        # Generate future dates
        last_date = recent_data['date'].iloc[-1]
        future_dates = pd.date_range(
            start=last_date + timedelta(days=1),
            periods=prediction_days,
            freq='D'
        )
        
        # Predict future prices
        predictions = []
        current_data = prepared_data.iloc[-1:].copy()
        
        feature_columns = [
            'day_of_year', 'month', 'quarter', 'year',
            'price_lag_1', 'price_lag_7', 'price_lag_30',
            'price_ma_7', 'price_ma_30', 'price_volatility', 'price_momentum',
            'volume_ma_7', 'volume_ratio', 'weather_impact', 'demand_impact'
        ]
        
        for i, future_date in enumerate(future_dates):
            # Update time-based features
            current_data['day_of_year'] = future_date.dayofyear
            current_data['month'] = future_date.month
            current_data['quarter'] = future_date.quarter
            current_data['year'] = future_date.year
            
            # Prepare features
            X_pred = current_data[feature_columns].values
            X_pred_scaled = scaler.transform(X_pred)
            
            # Make prediction
            predicted_price = model.predict(X_pred_scaled)[0]
            predictions.append(predicted_price)
            
            # Update lagged features for next prediction
            if i == 0:
                current_data['price_lag_1'] = predicted_price
            elif i >= 6:
                current_data['price_lag_7'] = predictions[i-6]
            elif i >= 29:
                current_data['price_lag_30'] = predictions[i-29]
        
        # Calculate prediction metrics
        current_price = recent_data['price'].iloc[-1]
        price_change = ((predictions[-1] - current_price) / current_price) * 100
        
        # Determine trend
        if predictions[-1] > predictions[0] * 1.05:
            trend = 'increasing'
        elif predictions[-1] < predictions[0] * 0.95:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Calculate confidence (simplified)
        price_volatility = np.std(predictions)
        confidence = max(50, min(95, 100 - price_volatility * 2))
        
        # Find optimal selling window
        max_price_idx = np.argmax(predictions)
        best_selling_window = f"Day {max_price_idx + 1} to {min(max_price_idx + 7, len(predictions))}"
        
        return {
            'crop_name': crop_name,
            'current_price': current_price,
            'predicted_prices': predictions,
            'prediction_dates': future_dates.tolist(),
            'historical_dates': recent_data['date'].tolist(),
            'historical_prices': recent_data['price'].tolist(),
            'price_change': price_change,
            'trend': trend,
            'confidence': confidence,
            'best_selling_window': best_selling_window,
            'prediction_summary': {
                'min_price': min(predictions),
                'max_price': max(predictions),
                'avg_price': np.mean(predictions),
                'volatility': price_volatility
            }
        }
    
    def get_market_insights(self, crop_name):
        """Get market insights for a specific crop"""
        if crop_name not in self.crop_data:
            return None
        
        data = self.crop_data[crop_name]
        recent_data = data.tail(30)
        
        insights = {
            'current_price': recent_data['price'].iloc[-1],
            'price_trend_30d': (recent_data['price'].iloc[-1] - recent_data['price'].iloc[0]) / recent_data['price'].iloc[0] * 100,
            'volatility_30d': recent_data['price'].std(),
            'avg_volume_30d': recent_data['volume'].mean(),
            'price_range_30d': {
                'min': recent_data['price'].min(),
                'max': recent_data['price'].max()
            }
        }
        
        return insights
    
    def compare_crops(self, crops_list):
        """Compare multiple crops for investment decisions"""
        comparison = {}
        
        for crop in crops_list:
            if crop in self.crop_data:
                prediction = self.predict_price(crop, 30)
                insights = self.get_market_insights(crop)
                
                comparison[crop] = {
                    'current_price': prediction['current_price'],
                    'predicted_change_30d': prediction['price_change'],
                    'trend': prediction['trend'],
                    'confidence': prediction['confidence'],
                    'volatility': insights['volatility_30d'],
                    'recommendation': self._get_recommendation(prediction, insights)
                }
        
        return comparison
    
    def _get_recommendation(self, prediction, insights):
        """Generate investment recommendation"""
        if prediction['trend'] == 'increasing' and prediction['confidence'] > 70:
            return "Strong Buy"
        elif prediction['trend'] == 'increasing' and prediction['confidence'] > 50:
            return "Buy"
        elif prediction['trend'] == 'decreasing' and prediction['confidence'] > 70:
            return "Sell"
        elif prediction['trend'] == 'decreasing' and prediction['confidence'] > 50:
            return "Consider Selling"
        else:
            return "Hold"
    
    def save_model(self, crop_name, filepath):
        """Save trained model to file"""
        if crop_name in self.models:
            model_data = {
                'model': self.models[crop_name],
                'scaler': self.scalers[crop_name],
                'crop_name': crop_name
            }
            joblib.dump(model_data, filepath)
            return True
        return False
    
    def load_model(self, filepath):
        """Load trained model from file"""
        try:
            model_data = joblib.load(filepath)
            crop_name = model_data['crop_name']
            self.models[crop_name] = model_data['model']
            self.scalers[crop_name] = model_data['scaler']
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def update_with_real_data(self, crop_name, new_data):
        """Update model with new real market data"""
        if crop_name not in self.crop_data:
            self.crop_data[crop_name] = pd.DataFrame()
        
        # Append new data
        self.crop_data[crop_name] = pd.concat([
            self.crop_data[crop_name], 
            new_data
        ]).drop_duplicates().sort_values('date').reset_index(drop=True)
        
        # Retrain model with updated data
        return self.train_model(crop_name)

# Market Data Fetcher for real-time data
class RealTimeMarketData:
    def __init__(self):
        self.api_endpoints = {
            'agmarknet': 'https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070',
            'commodity_api': 'https://commodities-api.com/api/latest'
        }
    
    def fetch_agmarknet_data(self, commodity, market=None):
        """Fetch data from AgMarkNet (Indian agricultural markets)"""
        try:
            # This would require actual API key and proper endpoint
            # For demonstration, returning sample data
            sample_data = {
                'commodity': commodity,
                'market': market or 'Delhi',
                'price': np.random.uniform(20, 100),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'unit': 'per kg'
            }
            return sample_data
        except Exception as e:
            print(f"Error fetching AgMarkNet data: {e}")
            return None
    
    def fetch_global_commodity_prices(self, commodity):
        """Fetch global commodity prices"""
        try:
            # This would require actual API integration
            # For demonstration, returning sample data
            sample_data = {
                'commodity': commodity,
                'price_usd': np.random.uniform(100, 500),
                'change_24h': np.random.uniform(-5, 5),
                'volume': np.random.uniform(1000000, 10000000),
                'timestamp': datetime.now().isoformat()
            }
            return sample_data
        except Exception as e:
            print(f"Error fetching global commodity data: {e}")
            return None