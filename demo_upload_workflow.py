#!/usr/bin/env python3
"""
Demo script showing complete upload workflow:
1. Upload Excel file via API
2. File gets processed by Together AI LLM
3. Portfolio gets saved to MongoDB
4. Verify portfolio exists in database
"""

import requests
import json
import time

def demo_upload_workflow():
    """Demonstrate the complete upload to database workflow"""
    
    print("🚀 Starting Upload to Database Demo")
    print("=" * 50)
    
    # API endpoint
    api_url = "http://127.0.0.1:8000/upload/excel"
    
    # File to upload
    file_path = "data/samples/motilal-hy-portfolio-march-2025.xlsx"
    
    print(f"📁 Uploading file: {file_path}")
    print(f"🌐 API endpoint: {api_url}")
    
    # Prepare the upload request
    with open(file_path, 'rb') as f:
        files = {'file': (file_path, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        
        # Request data - using Together AI for parsing
        data = {
            'parse_method': 'together',
            'together_api_key': 'bff39f38ee07df9a08ff8d2e7279b9d7223ab3f283a30bc39590d36f77dbd2fd'
        }
        
        print("\n📤 Making upload request...")
        print(f"   Parse method: {data['parse_method']}")
        print(f"   API key: {data['together_api_key'][:20]}...")
        
        try:
            response = requests.post(api_url, files=files, data=data, timeout=30)
            
            print(f"\n📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"   Message: {result.get('message', 'No message')}")
                
                # Show the portfolio IDs that were created
                if 'portfolio_ids' in result:
                    print(f"   Created {len(result['portfolio_ids'])} portfolios:")
                    for pid in result['portfolio_ids']:
                        print(f"     - {pid}")
                    return result['portfolio_ids']
                else:
                    print("   No portfolio IDs returned")
                    return []
                    
            else:
                print(f"❌ Upload failed with status {response.status_code}")
                print(f"   Error: {response.text}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return []

def check_portfolios_in_db():
    """Check what portfolios exist in the database"""
    
    print("\n🔍 Checking portfolios in database...")
    
    # Use the portfolio list API endpoint
    list_url = "http://127.0.0.1:8000/portfolios/"
    
    try:
        response = requests.get(list_url, timeout=10)
        
        if response.status_code == 200:
            portfolios = response.json()
            print(f"✅ Found {len(portfolios)} portfolios in database:")
            
            for portfolio in portfolios:
                print(f"\n📋 Portfolio: {portfolio.get('_id', 'No ID')}")
                print(f"   Fund: {portfolio.get('mutual_fund_name', 'Unknown')}")
                print(f"   Date: {portfolio.get('portfolio_date', 'Unknown')}")
                print(f"   Holdings: {portfolio.get('total_holdings', 0)}")
                
                # Show first few holdings if available
                holdings = portfolio.get('holdings', [])
                if holdings:
                    print(f"   Sample holdings:")
                    for holding in holdings[:3]:
                        print(f"     - {holding.get('company_name', 'Unknown')}: {holding.get('percentage', 0):.2f}%")
                    if len(holdings) > 3:
                        print(f"     ... and {len(holdings) - 3} more")
                        
        else:
            print(f"❌ Failed to get portfolios: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    # Run the complete demo
    portfolio_ids = demo_upload_workflow()
    
    # Wait a moment for processing
    if portfolio_ids:
        print("\n⏳ Waiting 2 seconds for database persistence...")
        time.sleep(2)
    
    # Check the database
    check_portfolios_in_db()
    
    print("\n🎉 Demo complete!")
    print("\nTo see the portfolios, you can also:")
    print("   1. Visit http://127.0.0.1:8000/docs for API documentation")
    print("   2. Use the /portfolios/ endpoint to list all portfolios")
    print("   3. Use mongo-express at http://127.0.0.1:8081 (admin/password123)")