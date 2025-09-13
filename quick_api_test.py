#!/usr/bin/env python3
"""
Quick API Test - Test save and get functionality
"""

import requests
import json
from pathlib import Path

def test_api():
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Quick API Test")
    print("=" * 20)
    
    # Test health
    try:
        response = requests.get(f"{base_url}/health")
        print(f"🏥 Health: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database: {data['database']}")
            print(f"   Portfolios: {data['total_portfolios']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test save portfolio
    json_file = Path("data/mfextractedholdings/motilaloswalmf.json")
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                portfolio_data = json.load(f)
            
            response = requests.post(
                f"{base_url}/portfolios",
                json=portfolio_data
            )
            print(f"\n💾 Save Portfolio: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                portfolio_id = data['data']['id']
                print(f"   ✅ Saved: {data['data']['mutual_fund_name']}")
                print(f"   🆔 ID: {portfolio_id}")
                
                # Test get portfolio
                response = requests.get(f"{base_url}/portfolios/{portfolio_id}")
                print(f"\n📖 Get Portfolio: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Retrieved: {data['data']['mutual_fund_name']}")
                    print(f"   📊 Holdings: {data['data']['total_holdings']}")
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Portfolio test failed: {e}")
    
    # Test list portfolios
    try:
        response = requests.get(f"{base_url}/portfolios")
        print(f"\n📋 List Portfolios: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 Total: {data['count']}")
            for p in data['data']:
                print(f"   - {p['fund_name']} ({p['total_holdings']} holdings)")
    except Exception as e:
        print(f"❌ List test failed: {e}")
    
    print(f"\n🌐 API Documentation: {base_url}/docs")

if __name__ == "__main__":
    test_api()