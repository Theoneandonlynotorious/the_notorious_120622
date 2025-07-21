import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import random
from bs4 import BeautifulSoup

class MarketDataFetcher:
    def __init__(self):
        self.api_endpoints = {
            'agmarknet': 'https://agmarknet.gov.in/',
            'commodity_api': 'https://commodities-api.com/api/',
            'yahoo_finance': 'https://finance.yahoo.com/',
            'investing_com': 'https://www.investing.com/commodities/'
        }
        
        # Sample market data for demonstration
        self.sample_markets = [
            "Delhi", "Mumbai", "Kolkata", "Chennai", "Bangalore", 
            "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
        ]
        
        self.crop_categories = {
            "Cereals": ["Wheat", "Rice", "Corn", "Barley", "Oats"],
            "Pulses": ["Chickpea", "Lentils", "Black Gram", "Green Gram"],
            "Oilseeds": ["Soybeans", "Mustard", "Sunflower", "Groundnut"],
            "Cash Crops": ["Cotton", "Sugarcane", "Tobacco"],
            "Vegetables": ["Tomatoes", "Onions", "Potatoes", "Cabbage"],
            "Fruits": ["Apples", "Bananas", "Oranges", "Grapes"]
        }
    
    def get_current_market_data(self):
        """Get current market overview"""
        try:
            # For demonstration, return simulated market data
            # In production, this would fetch from real APIs
            return self._simulate_market_overview()
        except Exception as e:
            print(f"Error fetching market data: {e}")
            return self._get_fallback_market_data()
    
    def fetch_crop_prices(self, crop_name, market=None, days=30):
        """Fetch crop prices from various sources"""
        try:
            # Simulate fetching from multiple sources
            agmarknet_data = self._fetch_agmarknet_prices(crop_name, market, days)
            commodity_data = self._fetch_commodity_api_prices(crop_name, days)
            
            # Combine and process data
            combined_data = self._combine_price_data(agmarknet_data, commodity_data)
            return combined_data
            
        except Exception as e:
            print(f"Error fetching crop prices: {e}")
            return self._get_fallback_crop_prices(crop_name, days)
    
    def _simulate_market_overview(self):
        """Simulate current market overview"""
        return {
            "market_status": "Open",
            "overall_trend": random.choice(["Bullish", "Bearish", "Stable"]),
            "total_volume": random.uniform(10000, 50000),
            "active_markets": len(self.sample_markets),
            "price_changes": {
                "gainers": random.randint(15, 25),
                "losers": random.randint(10, 20),
                "unchanged": random.randint(5, 15)
            },
            "top_commodities": self._get_top_commodities(),
            "market_news": self._get_market_news(),
            "timestamp": datetime.now()
        }
    
    def _get_top_commodities(self):
        """Get top performing commodities"""
        commodities = []
        all_crops = [crop for category in self.crop_categories.values() for crop in category]
        
        for i in range(5):
            crop = random.choice(all_crops)
            commodities.append({
                "name": crop,
                "price": round(random.uniform(20, 100), 2),
                "change": round(random.uniform(-10, 15), 2),
                "change_percent": round(random.uniform(-8, 12), 2),
                "volume": random.randint(1000, 10000)
            })
        
        return commodities
    
    def _get_market_news(self):
        """Get simulated market news"""
        news_templates = [
            "Weather conditions favorable for {crop} harvest",
            "Export demand increases for {crop}",
            "Government announces minimum support price for {crop}",
            "Storage facilities expand in {market} region",
            "New farming techniques boost {crop} yield"
        ]
        
        news = []
        for i in range(3):
            template = random.choice(news_templates)
            crop = random.choice([crop for category in self.crop_categories.values() for crop in category])
            market = random.choice(self.sample_markets)
            
            news.append({
                "headline": template.format(crop=crop, market=market),
                "impact": random.choice(["Positive", "Negative", "Neutral"]),
                "timestamp": datetime.now() - timedelta(hours=random.randint(1, 24))
            })
        
        return news
    
    def _fetch_agmarknet_prices(self, crop_name, market, days):
        """Simulate fetching from AgMarkNet"""
        # In real implementation, this would use AgMarkNet API
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        base_price = random.uniform(20, 100)
        prices = []
        
        for date in dates:
            # Simulate price variations
            daily_change = random.uniform(-5, 5)
            price = max(base_price * 0.5, base_price + daily_change)
            base_price = price
            
            prices.append({
                "date": date,
                "crop": crop_name,
                "market": market or random.choice(self.sample_markets),
                "price": round(price, 2),
                "unit": "per kg",
                "source": "AgMarkNet"
            })
        
        return pd.DataFrame(prices)
    
    def _fetch_commodity_api_prices(self, crop_name, days):
        """Simulate fetching from commodity API"""
        # In real implementation, this would use commodity APIs
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        base_price_usd = random.uniform(0.5, 2.0)  # USD per kg
        prices = []
        
        for date in dates:
            daily_change = random.uniform(-0.1, 0.1)
            price_usd = max(base_price_usd * 0.5, base_price_usd + daily_change)
            price_inr = price_usd * 83  # Convert to INR (approximate rate)
            base_price_usd = price_usd
            
            prices.append({
                "date": date,
                "crop": crop_name,
                "price_usd": round(price_usd, 3),
                "price_inr": round(price_inr, 2),
                "exchange_rate": 83,
                "source": "CommodityAPI"
            })
        
        return pd.DataFrame(prices)
    
    def _combine_price_data(self, agmarknet_data, commodity_data):
        """Combine price data from multiple sources"""
        combined = {
            "domestic_prices": agmarknet_data,
            "international_prices": commodity_data,
            "price_correlation": self._calculate_price_correlation(agmarknet_data, commodity_data),
            "arbitrage_opportunities": self._find_arbitrage_opportunities(agmarknet_data)
        }
        
        return combined
    
    def _calculate_price_correlation(self, domestic_data, international_data):
        """Calculate correlation between domestic and international prices"""
        if len(domestic_data) > 0 and len(international_data) > 0:
            # Merge data on date
            merged = pd.merge(
                domestic_data[['date', 'price']], 
                international_data[['date', 'price_inr']], 
                on='date', 
                how='inner'
            )
            
            if len(merged) > 1:
                correlation = merged['price'].corr(merged['price_inr'])
                return round(correlation, 3)
        
        return None
    
    def _find_arbitrage_opportunities(self, market_data):
        """Find price differences between markets"""
        if len(market_data) == 0:
            return []
        
        # Group by date and find price differences
        opportunities = []
        latest_date = market_data['date'].max()
        latest_data = market_data[market_data['date'] == latest_date]
        
        if len(latest_data) > 1:
            min_price = latest_data['price'].min()
            max_price = latest_data['price'].max()
            price_diff = max_price - min_price
            
            if price_diff > min_price * 0.1:  # 10% difference threshold
                min_market = latest_data[latest_data['price'] == min_price]['market'].iloc[0]
                max_market = latest_data[latest_data['price'] == max_price]['market'].iloc[0]
                
                opportunities.append({
                    "buy_market": min_market,
                    "sell_market": max_market,
                    "buy_price": min_price,
                    "sell_price": max_price,
                    "profit_margin": round(price_diff, 2),
                    "profit_percentage": round((price_diff / min_price) * 100, 2)
                })
        
        return opportunities
    
    def get_price_alerts(self, crop_name, target_price, alert_type="above"):
        """Set up price alerts for crops"""
        current_prices = self.fetch_crop_prices(crop_name, days=1)
        alerts = []
        
        if not current_prices["domestic_prices"].empty:
            latest_price = current_prices["domestic_prices"]["price"].iloc[-1]
            
            if alert_type == "above" and latest_price >= target_price:
                alerts.append({
                    "type": "price_target_reached",
                    "message": f"{crop_name} price reached ₹{latest_price}/kg (target: ₹{target_price}/kg)",
                    "current_price": latest_price,
                    "target_price": target_price,
                    "timestamp": datetime.now()
                })
            elif alert_type == "below" and latest_price <= target_price:
                alerts.append({
                    "type": "price_drop_alert",
                    "message": f"{crop_name} price dropped to ₹{latest_price}/kg (alert: ₹{target_price}/kg)",
                    "current_price": latest_price,
                    "target_price": target_price,
                    "timestamp": datetime.now()
                })
        
        return alerts
    
    def get_seasonal_price_patterns(self, crop_name, years=3):
        """Analyze seasonal price patterns"""
        # Simulate historical data for seasonal analysis
        seasonal_data = {}
        
        for month in range(1, 13):
            month_prices = []
            for year in range(years):
                # Simulate seasonal price variations
                if crop_name in ["Wheat", "Rice"]:
                    # Harvest seasons affect prices
                    if month in [4, 5, 11, 12]:  # Harvest months
                        base_price = random.uniform(20, 30)
                    else:
                        base_price = random.uniform(30, 45)
                elif crop_name in ["Tomatoes", "Onions"]:
                    # More volatile vegetables
                    base_price = random.uniform(15, 80)
                else:
                    base_price = random.uniform(25, 60)
                
                month_prices.append(base_price)
            
            seasonal_data[month] = {
                "month": month,
                "avg_price": round(np.mean(month_prices), 2),
                "min_price": round(np.min(month_prices), 2),
                "max_price": round(np.max(month_prices), 2),
                "volatility": round(np.std(month_prices), 2)
            }
        
        # Find best and worst months
        avg_prices = [data["avg_price"] for data in seasonal_data.values()]
        best_month = min(seasonal_data.keys(), key=lambda x: seasonal_data[x]["avg_price"])
        worst_month = max(seasonal_data.keys(), key=lambda x: seasonal_data[x]["avg_price"])
        
        return {
            "seasonal_data": seasonal_data,
            "best_buying_month": best_month,
            "best_selling_month": worst_month,
            "price_volatility": round(np.std(avg_prices), 2),
            "seasonal_trend": "Stable" if np.std(avg_prices) < 5 else "Volatile"
        }
    
    def get_market_comparison(self, crop_name, markets=None):
        """Compare prices across different markets"""
        if markets is None:
            markets = random.sample(self.sample_markets, 5)
        
        comparison = []
        
        for market in markets:
            prices = self._fetch_agmarknet_prices(crop_name, market, 7)
            if not prices.empty:
                avg_price = prices["price"].mean()
                price_trend = "Up" if prices["price"].iloc[-1] > prices["price"].iloc[0] else "Down"
                
                comparison.append({
                    "market": market,
                    "current_price": round(prices["price"].iloc[-1], 2),
                    "avg_price_7d": round(avg_price, 2),
                    "price_trend": price_trend,
                    "volatility": round(prices["price"].std(), 2),
                    "volume": random.randint(100, 1000)  # Simulated volume
                })
        
        # Sort by current price
        comparison.sort(key=lambda x: x["current_price"])
        
        return comparison
    
    def get_supply_demand_analysis(self, crop_name):
        """Analyze supply and demand factors"""
        analysis = {
            "supply_factors": {
                "production_estimate": random.uniform(80, 120),  # % of normal
                "weather_impact": random.choice(["Positive", "Negative", "Neutral"]),
                "area_under_cultivation": random.uniform(90, 110),  # % of last year
                "yield_per_hectare": random.uniform(85, 115),  # % of average
                "storage_levels": random.uniform(70, 130)  # % of capacity
            },
            "demand_factors": {
                "domestic_consumption": random.uniform(95, 105),  # % of normal
                "export_demand": random.uniform(80, 120),  # % of last year
                "industrial_usage": random.uniform(90, 110),  # % of normal
                "government_procurement": random.uniform(85, 115),  # % of target
                "price_elasticity": random.uniform(0.3, 0.8)
            },
            "market_sentiment": random.choice(["Bullish", "Bearish", "Neutral"]),
            "price_forecast": {
                "short_term": random.choice(["Increase", "Decrease", "Stable"]),
                "medium_term": random.choice(["Increase", "Decrease", "Stable"]),
                "long_term": random.choice(["Increase", "Decrease", "Stable"])
            }
        }
        
        return analysis
    
    def export_market_data(self, data, filename=None):
        """Export market data to CSV/JSON"""
        if filename is None:
            filename = f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            if isinstance(data, pd.DataFrame):
                data.to_csv(f"{filename}.csv", index=False)
                return f"{filename}.csv"
            else:
                with open(f"{filename}.json", 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                return f"{filename}.json"
        except Exception as e:
            print(f"Error exporting data: {e}")
            return None
    
    def _get_fallback_market_data(self):
        """Fallback market data when APIs fail"""
        return {
            "market_status": "Unknown",
            "overall_trend": "Stable",
            "total_volume": 25000,
            "active_markets": 10,
            "price_changes": {"gainers": 20, "losers": 15, "unchanged": 10},
            "top_commodities": [],
            "market_news": [],
            "timestamp": datetime.now()
        }
    
    def _get_fallback_crop_prices(self, crop_name, days):
        """Fallback crop prices when APIs fail"""
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        base_price = 50  # Default price
        
        domestic_prices = pd.DataFrame([
            {
                "date": date,
                "crop": crop_name,
                "market": "Delhi",
                "price": base_price,
                "unit": "per kg",
                "source": "Fallback"
            } for date in dates
        ])
        
        international_prices = pd.DataFrame([
            {
                "date": date,
                "crop": crop_name,
                "price_usd": base_price / 83,
                "price_inr": base_price,
                "exchange_rate": 83,
                "source": "Fallback"
            } for date in dates
        ])
        
        return {
            "domestic_prices": domestic_prices,
            "international_prices": international_prices,
            "price_correlation": None,
            "arbitrage_opportunities": []
        }