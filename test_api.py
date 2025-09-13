#!/usr/bin/env python3
"""
Test API endpoints for Mutual Fund Portfolio Service
Tests both save and get functionality with real data
"""

import asyncio
import json
import requests
import time
from pathlib import Path
from typing import Dict, Any


class APITester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self) -> bool:
        """Test if API is healthy and connected"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"🏥 Health Check: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   🗄️  Database: {data['database']}")
                print(f"   📊 Total Portfolios: {data['total_portfolios']}")
                return True
            else:
                print(f"   ❌ Unhealthy: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            return False
    
    def test_root(self) -> bool:
        """Test root endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            print(f"\n🏠 Root Endpoint: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API: {data['message']}")
                print(f"   📋 Available endpoints: {len(data['endpoints'])}")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_save_portfolio(self, json_file: Path) -> str:
        """Test saving a portfolio"""
        try:
            print(f"\n💾 Testing Save Portfolio")
            print(f"   📁 Loading: {json_file}")
            
            # Load JSON data
            with open(json_file, 'r', encoding='utf-8') as f:
                portfolio_data = json.load(f)
            
            # Save portfolio via API
            response = self.session.post(
                f"{self.base_url}/portfolios",
                json=portfolio_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   📤 POST /portfolios: {response.status_code}")
            
            if response.status_code == 201:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   🆔 Portfolio ID: {data['data']['id']}")
                print(f"   📈 Fund: {data['data']['mutual_fund_name']}")
                print(f"   📅 Date: {data['data']['portfolio_date']}")
                print(f"   📊 Holdings: {data['data']['total_holdings']}")
                return data['data']['id']
            else:
                print(f"   ❌ Failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return None
    
    def test_get_portfolio(self, portfolio_id: str) -> bool:
        """Test getting a portfolio by ID"""
        try:
            print(f"\n📖 Testing Get Portfolio")
            print(f"   🆔 ID: {portfolio_id}")
            
            response = self.session.get(f"{self.base_url}/portfolios/{portfolio_id}")
            print(f"   📥 GET /portfolios/{portfolio_id[:8]}...: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   📈 Fund: {data['data']['mutual_fund_name']}")
                print(f"   📅 Date: {data['data']['portfolio_date']}")
                print(f"   📊 Holdings: {data['data']['total_holdings']}")
                print(f"   📋 Portfolio Data: {len(data['portfolio']['portfolio_holdings'])} holdings loaded")
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_list_portfolios(self) -> bool:
        """Test listing all portfolios"""
        try:
            print(f"\n📋 Testing List Portfolios")
            
            response = self.session.get(f"{self.base_url}/portfolios")
            print(f"   📥 GET /portfolios: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   📊 Count: {data['count']}")
                
                for i, portfolio in enumerate(data['data'], 1):
                    print(f"   {i}. {portfolio['fund_name']} ({portfolio['portfolio_date']}) - {portfolio['total_holdings']} holdings")
                
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_search_portfolios(self, fund_name: str) -> bool:
        """Test searching portfolios by fund name"""
        try:
            print(f"\n🔍 Testing Search Portfolios")
            print(f"   🎯 Fund: {fund_name}")
            
            response = self.session.get(
                f"{self.base_url}/portfolios/search",
                params={"fund_name": fund_name}
            )
            print(f"   📥 GET /portfolios/search: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   🔎 Query: {data['query']}")
                print(f"   📊 Results: {data['count']}")
                
                for i, portfolio in enumerate(data['data'], 1):
                    print(f"   {i}. {portfolio['fund_name']} ({portfolio['portfolio_date']}) - {portfolio['total_holdings']} holdings")
                
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_get_holdings_by_isin(self, isin_code: str) -> bool:
        """Test getting holdings by ISIN code"""
        try:
            print(f"\n🔍 Testing Get Holdings by ISIN")
            print(f"   🎯 ISIN: {isin_code}")
            
            response = self.session.get(f"{self.base_url}/holdings/{isin_code}")
            print(f"   📥 GET /holdings/{isin_code}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   📊 Holdings found: {data['count']}")
                
                for holding in data['data']:
                    print(f"   📈 {holding['fund_name']} - {holding['holding']['name_of_instrument']}")
                
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_get_fund_statistics(self, fund_name: str) -> bool:
        """Test getting fund statistics"""
        try:
            print(f"\n📊 Testing Get Fund Statistics")
            print(f"   🎯 Fund: {fund_name}")
            
            response = self.session.get(f"{self.base_url}/funds/{fund_name}/statistics")
            print(f"   📥 GET /funds/.../statistics: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                
                stats = data['statistics']
                print(f"   📊 Portfolio Count: {stats['portfolio_count']}")
                print(f"   📅 Date Range: {stats['earliest_date']} to {stats['latest_date']}")
                print(f"   📈 Holdings: {stats['min_holdings']} - {stats['max_holdings']} (avg: {stats['avg_holdings']})")
                
                return True
            else:
                print(f"   ❌ Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False


def main():
    """Run comprehensive API tests"""
    print("🚀 API Testing - Mutual Fund Portfolio Service")
    print("=" * 55)
    
    # Check if test data exists
    json_file = Path("data/mfextractedholdings/motilaloswalmf.json")
    if not json_file.exists():
        print(f"❌ Test data not found: {json_file}")
        return
    
    # Initialize tester
    tester = APITester()
    
    print("🔧 Starting API server test...")
    print("💡 Make sure to start the API server first:")
    print("   python -m am_api.api")
    print("   or")
    print("   uvicorn am_api.api:app --reload")
    
    # Wait for user to start server
    input("\n⏸️  Press Enter when API server is running...")
    
    # Test sequence
    tests_passed = 0
    total_tests = 0
    
    # 1. Health check
    total_tests += 1
    if tester.test_health():
        tests_passed += 1
    
    # 2. Root endpoint
    total_tests += 1
    if tester.test_root():
        tests_passed += 1
    
    # 3. Save portfolio
    total_tests += 1
    portfolio_id = tester.test_save_portfolio(json_file)
    if portfolio_id:
        tests_passed += 1
        
        # 4. Get portfolio by ID (only if save succeeded)
        total_tests += 1
        if tester.test_get_portfolio(portfolio_id):
            tests_passed += 1
    
    # 5. List portfolios
    total_tests += 1
    if tester.test_list_portfolios():
        tests_passed += 1
    
    # 6. Search portfolios
    total_tests += 1
    if tester.test_search_portfolios("Motilal Oswal Nifty Smallcap 250 Index Fund"):
        tests_passed += 1
    
    # 7. Get holdings by ISIN
    total_tests += 1
    if tester.test_get_holdings_by_isin("INE745G01035"):
        tests_passed += 1
    
    # 8. Get fund statistics
    total_tests += 1
    if tester.test_get_fund_statistics("Motilal Oswal Nifty Smallcap 250 Index Fund"):
        tests_passed += 1
    
    # Results
    print(f"\n🎯 Test Results")
    print("=" * 20)
    print(f"✅ Passed: {tests_passed}/{total_tests}")
    print(f"❌ Failed: {total_tests - tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 All tests passed! Your API is working perfectly!")
        print("\n📚 API Documentation:")
        print("   http://127.0.0.1:8000/docs (Swagger UI)")
        print("   http://127.0.0.1:8000/redoc (ReDoc)")
    else:
        print(f"\n⚠️  {total_tests - tests_passed} test(s) failed. Check the errors above.")


if __name__ == "__main__":
    main()