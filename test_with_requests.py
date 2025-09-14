#!/usr/bin/env python3
"""
Simple test using requests to avoid FastAPI TestClient issues
"""
import requests
import sys
from pathlib import Path

def test_api_with_requests():
    """Test the API using requests library"""
    print("🧪 Testing API with requests")
    print("=" * 40)
    
    # Test file path
    test_file_path = Path("data/samples/motilal-hy-portfolio-march-2025.xlsx")
    
    if not test_file_path.exists():
        print(f"❌ Test file not found: {test_file_path}")
        return
    
    try:
        # Test basic connectivity first
        print("🔗 Testing basic connectivity...")
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            print("✅ API server is responding")
        else:
            print(f"❌ API server not responding: {response.status_code}")
            return
        
        # Test file upload
        print(f"📤 Testing file upload...")
        with open(test_file_path, "rb") as f:
            files = {"file": (test_file_path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"parse_method": "manual"}
            
            response = requests.post("http://127.0.0.1:8000/upload/excel", files=files, data=data)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("🎉 SUCCESS! Complete workflow working!")
            print(f"📋 Summary:")
            print(f"   File: {result['summary']['original_filename']}")
            print(f"   Sheets: {result['summary']['total_sheets']}")
            print(f"   Parsed: {result['summary']['successfully_parsed']}")
            print(f"   Errors: {result['summary']['parsing_errors']}")
            
            if result.get('parsed_portfolios'):
                print(f"\n📊 Parsed Portfolios:")
                for portfolio in result['parsed_portfolios']:
                    print(f"   • {portfolio['sheet_name']}: {portfolio['mutual_fund_name']}")
                    print(f"     Holdings: {portfolio['total_holdings']}")
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            try:
                error = response.json()
                print(f"   Error: {error.get('detail', response.text)}")
            except:
                print(f"   Raw response: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_with_requests()