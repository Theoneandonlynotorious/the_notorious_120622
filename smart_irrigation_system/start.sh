#!/bin/bash

echo "🌱 Starting Smart Irrigation & Crop Price Prediction System..."
echo "================================================================"

# Add local bin to PATH for streamlit
export PATH="$HOME/.local/bin:$PATH"

# Check if streamlit is available
if ! command -v streamlit &> /dev/null; then
    echo "⚠️  Streamlit not found in PATH. Using python3 -m streamlit..."
    python3 -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0
else
    echo "✅ Starting Streamlit application..."
    streamlit run app.py --server.port 8501 --server.address 0.0.0.0
fi