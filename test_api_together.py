#!/usr/bin/env python3
"""
Test Together AI API integration
"""

import requests
import json
import time
from pathlib import Path

API_BASE_URL = "http://127.0.0.1:8000"
TOGETHER_API_KEY = "bff39f38ee07df9a08ff8d2e7279b9d7223ab3f283a30bc39590d36f77dbd2fd"

def test_api_upload_with_together():
    """Test API upload with Together AI parsing"""
    print("🧪 Testing API Upload with Together AI Parsing")
    print("=" * 60)
    
    # File to upload
    file_path = Path("data/samples/c45b0-copy-of-motilal-hy-portfolio-march-2025.xlsx")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
        
    print(f"📂 File to upload: {file_path}")
    
    # Prepare the request
    url = f"{API_BASE_URL}/portfolios/upload"
    
    # Open file and prepare form data
    with open(file_path, 'rb') as f:
        files = {
            'file': (file_path.name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        }
        
        data = {
            'method': 'together',
            'sheet_name': 'YO17',
            'api_key': TOGETHER_API_KEY
        }
        
        print(f"🚀 Uploading to: {url}")
        print(f"📋 Method: together")
        print(f"📄 Sheet: YO17")
        
        try:
            # Make the request
            response = requests.post(url, files=files, data=data, timeout=120)
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                
                # Print summary
                portfolio = result.get('portfolio', {})
                print(f"\n📊 Portfolio Summary:")
                print(f"   🆔 ID: {result.get('id', 'Unknown')}")
                print(f"   📈 Fund: {portfolio.get('mutual_fund_name', 'Unknown')}")
                print(f"   📅 Date: {portfolio.get('portfolio_date', 'Unknown')}")
                print(f"   🔢 Holdings: {portfolio.get('total_holdings', 0)}")
                print(f"   📋 Actual holdings count: {len(portfolio.get('portfolio_holdings', []))}")
                
                # Print first few holdings
                holdings = portfolio.get('portfolio_holdings', [])
                if holdings:
                    print(f"\n🔍 Sample holdings:")
                    for i, holding in enumerate(holdings[:5], 1):
                        name = holding.get('name_of_instrument', 'Unknown')
                        percentage = holding.get('percentage_to_nav', 'N/A')
                        print(f"   {i}. {name} ({percentage})")
                    
                    if len(holdings) > 5:
                        print(f"   ... and {len(holdings) - 5} more")
                
                return result.get('id')
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"🐛 Error details: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"🐛 Error text: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return False

def test_api_get_portfolio(portfolio_id):
    """Test API get portfolio by ID"""
    print(f"\n🧪 Testing API Get Portfolio (ID: {portfolio_id})")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/portfolios/{portfolio_id}"
    
    try:
        response = requests.get(url)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            portfolio = response.json()
            print("✅ Get portfolio successful!")
            
            print(f"\n📊 Retrieved Portfolio:")
            print(f"   📈 Fund: {portfolio.get('mutual_fund_name', 'Unknown')}")
            print(f"   📅 Date: {portfolio.get('portfolio_date', 'Unknown')}")
            print(f"   🔢 Holdings: {portfolio.get('total_holdings', 0)}")
            print(f"   📋 Actual holdings count: {len(portfolio.get('portfolio_holdings', []))}")
            
            return True
        else:
            print(f"❌ Get portfolio failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_api_list_portfolios():
    """Test API list all portfolios"""
    print(f"\n🧪 Testing API List All Portfolios")
    print("=" * 60)
    
    url = f"{API_BASE_URL}/portfolios/"
    
    try:
        response = requests.get(url)
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            portfolios = response.json()
            print("✅ List portfolios successful!")
            
            print(f"\n📊 Total portfolios: {len(portfolios)}")
            
            for i, portfolio in enumerate(portfolios, 1):
                print(f"   {i}. {portfolio.get('mutual_fund_name', 'Unknown')} ({portfolio.get('portfolio_date', 'Unknown')})")
            
            return True
        else:
            print(f"❌ List portfolios failed: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Together AI API Integration Tests")
    print("=" * 60)
    
    # Test 1: Upload with Together AI
    portfolio_id = test_api_upload_with_together()
    
    if portfolio_id:
        # Test 2: Get the uploaded portfolio
        test_api_get_portfolio(portfolio_id)
        
        # Test 3: List all portfolios
        test_api_list_portfolios()
        
        print("\n" + "=" * 60)
        print("🎉 All API tests completed successfully!")
        print(f"📊 Portfolio ID for further testing: {portfolio_id}")
    else:
        print("\n" + "=" * 60)
        print("❌ API upload test failed")

if __name__ == "__main__":
    main()