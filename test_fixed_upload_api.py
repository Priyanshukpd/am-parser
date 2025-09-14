#!/usr/bin/env python3
"""
Test the fixed upload API with complete workflow
"""
import asyncio
import sys
from pathlib import Path
import io

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from am_api.api import app


async def test_fixed_upload_api():
    """Test the complete upload API workflow"""
    print("🧪 Testing Fixed Upload API")
    print("=" * 50)
    
    # Create test client
    client = TestClient(app)
    
    # Test file path
    test_file_path = Path("data/samples/motilal-hy-portfolio-march-2025.xlsx")
    
    if not test_file_path.exists():
        print(f"❌ Test file not found: {test_file_path}")
        return
    
    try:
        # Read the Excel file
        with open(test_file_path, "rb") as f:
            file_content = f.read()
        
        print(f"📁 Testing with file: {test_file_path.name}")
        print(f"📊 File size: {len(file_content):,} bytes")
        
        # Prepare the request
        files = {
            "file": (test_file_path.name, io.BytesIO(file_content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        }
        data = {
            "parse_method": "manual"
        }
        
        print("\n🚀 Sending request to /upload/excel...")
        
        # Make the request
        response = client.post("/upload/excel", files=files, data=data)
        
        print(f"📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API call successful!")
            print(f"📋 Summary:")
            print(f"   Main file: {result['summary']['original_filename']}")
            print(f"   Total sheets: {result['summary']['total_sheets']}")
            print(f"   Successfully parsed: {result['summary']['successfully_parsed']}")
            print(f"   Parsing errors: {result['summary']['parsing_errors']}")
            print(f"   Parse method: {result['summary']['parse_method']}")
            
            if result.get('parsed_portfolios'):
                print(f"\n📊 Parsed Portfolios:")
                for i, portfolio in enumerate(result['parsed_portfolios'], 1):
                    print(f"   {i}. {portfolio['sheet_name']}: {portfolio['mutual_fund_name']}")
                    print(f"      Holdings: {portfolio['total_holdings']}")
                    print(f"      Date: {portfolio['portfolio_date']}")
            
            if result.get('parsing_errors'):
                print(f"\n⚠️ Parsing Errors:")
                for i, error in enumerate(result['parsing_errors'], 1):
                    print(f"   {i}. {error['sheet_name']}: {error['error']}")
            
            print(f"\n🎉 Complete workflow test successful!")
            
        else:
            print(f"❌ API call failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail.get('detail', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_fixed_upload_api())