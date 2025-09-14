#!/usr/bin/env python3
"""
Simple upload test using requests without starting conflicting server
"""

import requests
import json
import time
import sys

def test_upload():
    """Test upload to the running API server"""
    
    print("🚀 Testing Upload to Database")
    print("=" * 40)
    
    # API endpoint
    api_url = "http://127.0.0.1:8000/upload/excel"
    
    # File to upload
    file_path = "data/samples/motilal-hy-portfolio-march-2025.xlsx"
    
    print(f"📁 File: {file_path}")
    print(f"🌐 API: {api_url}")
    
    try:
        # Test if API is running
        health_response = requests.get("http://127.0.0.1:8000/", timeout=5)
        if health_response.status_code != 200:
            print("❌ API server is not running!")
            print("   Please start it with: python start_api.py")
            return
            
        print("✅ API server is running")
        
        # Prepare upload
        with open(file_path, 'rb') as f:
            files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
            data = {
                'parse_method': 'together',
                'together_api_key': 'bff39f38ee07df9a08ff8d2e7279b9d7223ab3f283a30bc39590d36f77dbd2fd'
            }
            
            print("\n📤 Uploading...")
            response = requests.post(api_url, files=files, data=data, timeout=60)
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS! Portfolio saved to database!")
                print(f"   Message: {result.get('message', 'Done')}")
                
                if 'portfolio_ids' in result:
                    print(f"   Created {len(result['portfolio_ids'])} portfolios:")
                    for pid in result['portfolio_ids']:
                        print(f"     - {pid}")
                        
                # Now check database
                print("\n🔍 Checking database...")
                time.sleep(1)
                
                list_response = requests.get("http://127.0.0.1:8000/portfolios/", timeout=10)
                if list_response.status_code == 200:
                    portfolios = list_response.json()
                    print(f"✅ Found {len(portfolios)} portfolios in database!")
                    
                    for i, portfolio in enumerate(portfolios[-2:], 1):  # Show last 2
                        print(f"\n📋 Portfolio {i}:")
                        print(f"   ID: {portfolio.get('_id', 'Unknown')}")
                        print(f"   Fund: {portfolio.get('mutual_fund_name', 'Unknown')}")
                        print(f"   Date: {portfolio.get('portfolio_date', 'Unknown')}")
                        print(f"   Holdings: {portfolio.get('total_holdings', 0)}")
                        
                else:
                    print("❌ Could not check database")
                    
            else:
                print(f"❌ Upload failed: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server!")
        print("   Please start it with: python start_api.py")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_upload()