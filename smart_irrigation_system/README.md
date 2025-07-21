# 🌱 Smart Irrigation & Crop Price Prediction System

A comprehensive IoT-based smart irrigation system with integrated crop price prediction using machine learning and real-time market data analysis.

## 🚀 Features

### Smart Irrigation System
- **Real-time IoT Sensor Monitoring**: Soil moisture, temperature, humidity, pH, and nutrient levels
- **Automated Irrigation Control**: Intelligent scheduling based on sensor data and weather conditions
- **Manual Override**: Complete manual control with emergency stop functionality
- **Water Usage Tracking**: Monitor and optimize water consumption
- **System Health Monitoring**: Real-time diagnostics and alerts
- **Weather Integration**: Weather-based irrigation recommendations

### Crop Price Prediction
- **Machine Learning Models**: Random Forest and Linear Regression for price forecasting
- **Real-time Market Data**: Integration with agricultural market APIs
- **Price Trend Analysis**: Historical data analysis and seasonal patterns
- **Market Comparison**: Multi-market price comparison and arbitrage opportunities
- **Investment Recommendations**: Buy/sell/hold recommendations based on predictions

### User Interface
- **Modern Streamlit Dashboard**: Interactive web interface
- **Real-time Data Visualization**: Charts, graphs, and live sensor data
- **Mobile-Responsive Design**: Works on desktop, tablet, and mobile
- **Multi-page Navigation**: Organized sections for different functionalities
- **Custom Alerts**: Configurable notifications and warnings

## 📋 Requirements

- Python 3.8+
- Streamlit
- Pandas, NumPy
- Scikit-learn
- Plotly
- SQLite3
- MQTT (for real IoT devices)

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd smart_irrigation_system
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the application**:
```bash
streamlit run app.py
```

4. **Access the dashboard**:
Open your browser and go to `http://localhost:8501`

## 📁 Project Structure

```
smart_irrigation_system/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # Project documentation
├── data/                          # Database and data files
│   └── smart_irrigation.db        # SQLite database
├── utils/                         # Utility modules
│   ├── __init__.py
│   ├── database.py                # Database management
│   ├── iot_simulator.py           # IoT sensor simulation
│   ├── crop_price_predictor.py    # ML price prediction
│   ├── irrigation_controller.py   # Irrigation automation
│   ├── weather_api.py             # Weather data integration
│   └── market_data.py             # Market data fetching
├── models/                        # Trained ML models
├── static/                        # Static assets
│   ├── css/
│   ├── js/
│   └── images/
└── config/                        # Configuration files
```

## 🎯 Usage

### Dashboard Overview
The main dashboard provides:
- Real-time sensor readings
- System status indicators
- Irrigation control buttons
- Water usage statistics
- Price prediction charts
- Market analysis

### IoT Sensor Management
- View real-time sensor data
- Configure sensor thresholds
- Monitor sensor health
- Export sensor data

### Irrigation Control
- Manual start/stop irrigation
- Schedule automated irrigation
- Set automatic triggers
- Monitor water usage
- View irrigation history

### Crop Price Prediction
- Select crops for prediction
- Set prediction timeframes
- View price trends and forecasts
- Get buy/sell recommendations
- Compare market prices

### Market Analysis
- Real-time market overview
- Multi-crop price comparison
- Market news and updates
- Seasonal price patterns
- Supply/demand analysis

## 🔧 Configuration

### Sensor Settings
Configure sensor thresholds in the Settings page:
- Soil moisture alerts
- Temperature ranges
- Humidity thresholds
- pH level monitoring

### Irrigation Settings
Customize irrigation parameters:
- Moisture trigger levels
- Default irrigation duration
- Maximum daily sessions
- Water flow rates

### Price Prediction Settings
Adjust ML model parameters:
- Prediction timeframes
- Confidence thresholds
- Market data sources
- Alert configurations

## 📊 Data Sources

### IoT Sensors (Simulated)
- Soil moisture sensors
- Temperature sensors
- Humidity sensors
- Light intensity sensors
- pH sensors
- NPK nutrient sensors

### Weather Data
- OpenWeatherMap API (configurable)
- Local weather stations
- Satellite data integration

### Market Data
- AgMarkNet (Indian agricultural markets)
- Commodity APIs
- International market feeds
- Government price data

## 🤖 Machine Learning Models

### Price Prediction Models
- **Random Forest Regressor**: Primary prediction model
- **Linear Regression**: Baseline comparison
- **Feature Engineering**: Time-series, seasonal, and market factors
- **Model Validation**: Cross-validation and performance metrics

### Features Used
- Historical prices
- Seasonal patterns
- Weather data
- Market volume
- Supply/demand factors
- Economic indicators

## 🌐 IoT Integration

### MQTT Support
For real IoT devices, the system supports MQTT:
```python
# Configure MQTT broker
broker_host = "localhost"
broker_port = 1883

# Topics
sensors/soil_moisture
sensors/temperature
sensors/humidity
control/irrigation
```

### Sensor Hardware Compatibility
- Arduino-based sensors
- Raspberry Pi controllers
- ESP32/ESP8266 modules
- Commercial IoT sensors

## 📈 Performance Metrics

### Irrigation Efficiency
- Water usage optimization
- Crop yield improvement
- Energy consumption reduction
- Automated vs manual sessions

### Prediction Accuracy
- Mean Absolute Error (MAE)
- R-squared scores
- Prediction confidence levels
- Backtesting results

## 🚨 Alerts and Notifications

### System Alerts
- Low soil moisture
- High temperature warnings
- System malfunctions
- Irrigation failures

### Price Alerts
- Target price reached
- Significant price changes
- Market opportunities
- Seasonal recommendations

## 🔐 Security Features

- Input validation
- SQL injection prevention
- Data encryption (configurable)
- User authentication (extensible)
- API key management

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Test coverage includes:
- Unit tests for all modules
- Integration tests
- Performance benchmarks
- Data validation tests

## 📱 Mobile Support

The dashboard is fully responsive and works on:
- Desktop browsers
- Tablets
- Mobile phones
- Progressive Web App (PWA) ready

## 🔄 Data Export/Import

### Export Options
- CSV format for spreadsheet analysis
- JSON format for data exchange
- PDF reports (configurable)
- API endpoints for integration

### Import Options
- Historical price data
- Sensor calibration data
- Weather data
- Market data feeds

## 🌍 Scalability

### Multi-Farm Support
- Farm location management
- Separate sensor networks
- Independent irrigation systems
- Consolidated reporting

### Cloud Deployment
- Docker containerization
- AWS/Azure deployment
- Database scaling
- Load balancing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the FAQ section
- Contact the development team

## 🔮 Future Enhancements

### Planned Features
- AI-powered crop recommendations
- Drone integration for aerial monitoring
- Blockchain for supply chain tracking
- Mobile app development
- Advanced analytics dashboard
- Integration with farm management systems

### Research Areas
- Computer vision for crop health monitoring
- Predictive maintenance for irrigation equipment
- Climate change impact modeling
- Precision agriculture techniques

## 📚 Documentation

Detailed documentation available in the `/docs` folder:
- API documentation
- Installation guides
- Configuration tutorials
- Troubleshooting guides
- Best practices

## 🏆 Acknowledgments

- OpenWeatherMap for weather data
- AgMarkNet for market data
- Streamlit for the web framework
- Scikit-learn for ML capabilities
- The open-source community

---

**Built with ❤️ for sustainable agriculture and smart farming**