#!/usr/bin/env python3
"""
Export all project files with clear separators for easy copying
"""

import os
import glob

def export_files():
    """Export all project files with separators"""
    
    # List of files to export
    files_to_export = [
        'app.py',
        'test_app.py', 
        'setup.py',
        'start.sh',
        'README.md',
        'requirements.txt',
        'requirements_simple.txt',
        'utils/__init__.py',
        'utils/database.py',
        'utils/iot_simulator.py',
        'utils/crop_price_predictor.py',
        'utils/irrigation_controller.py',
        'utils/weather_api.py',
        'utils/market_data.py'
    ]
    
    print("=" * 80)
    print("SMART IRRIGATION SYSTEM - ALL FILES")
    print("=" * 80)
    print()
    
    for file_path in files_to_export:
        if os.path.exists(file_path):
            print(f"{'='*20} FILE: {file_path} {'='*20}")
            print()
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
            
            print()
            print(f"{'='*20} END OF {file_path} {'='*20}")
            print()
            print()
        else:
            print(f"File not found: {file_path}")
    
    print("=" * 80)
    print("ALL FILES EXPORTED")
    print("=" * 80)

if __name__ == "__main__":
    export_files()