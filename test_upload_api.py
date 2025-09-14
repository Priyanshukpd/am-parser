#!/usr/bin/env python3
"""
Test script for the file upload and processing API
"""

import requests
import json
import time
from pathlib import Path


API_BASE_URL = "http://127.0.0.1:8000"
EXCEL_FILE_PATH = "data/samples/c45b0-copy-of-motilal-hy-portfolio-march-2025.xlsx"
TOGETHER_API_KEY = "bff39f38ee07df9a08ff8d2e7279b9d7223ab3f283a30bc39590d36f77dbd2fd"


def test_upload_flow():
    """Test the complete upload and processing flow"""
    print("🚀 Testing File Upload and Processing API")
    print("=" * 60)
    
    # Step 1: Upload Excel file
    print("📤 Step 1: Uploading Excel file...")
    upload_response = upload_excel_file()
    if not upload_response:
        return False
    
    file_id = upload_response["file_id"]
    print(f"✅ File uploaded successfully with ID: {file_id}")
    
    # Step 2: Process Excel file (split into sheets)
    print("\n🔄 Step 2: Processing Excel file (splitting into sheets)...")
    process_response = process_excel_file(file_id)
    if not process_response:
        return False
    
    print("✅ Processing started successfully")
    
    # Step 3: Wait for processing to complete and check status
    print("\n⏳ Step 3: Waiting for processing to complete...")
    file_status = wait_for_processing(file_id)
    if not file_status:
        return False
    
    # Step 4: Parse individual sheets
    print("\n🧠 Step 4: Parsing individual sheets with Together AI...")
    sheet_files = file_status.get("sheet_files", [])
    if not sheet_files:
        print("❌ No sheet files found")
        return False
    
    print(f"Found {len(sheet_files)} sheet files")
    
    # Parse first sheet as example
    first_sheet = sheet_files[0]
    sheet_id = first_sheet["file_id"]
    sheet_name = first_sheet["sheet_name"]
    
    print(f"📊 Parsing sheet: {sheet_name} (ID: {sheet_id})")
    parse_response = parse_sheet(sheet_id, "together", TOGETHER_API_KEY)
    if not parse_response:
        return False
    
    print("✅ Sheet parsing started successfully")
    
    # Step 5: Check final results
    print("\n⏳ Step 5: Waiting for parsing to complete...")
    time.sleep(10)  # Wait for parsing
    
    final_status = get_file_status(file_id)
    if final_status:
        print("\n📊 Final Status Summary:")
        print(f"   Main file: {final_status['file_info']['original_filename']}")
        print(f"   Status: {final_status['file_info']['status']}")
        print(f"   Total sheets: {len(final_status['sheet_files'])}")
        
        for sheet in final_status['sheet_files']:
            status_icon = "✅" if sheet['status'] == 'parsed' else "⏳" if sheet['status'] == 'processing' else "❌"
            print(f"   {status_icon} {sheet['sheet_name']}: {sheet['status']}")
            if sheet.get('processing_metadata'):
                metadata = sheet['processing_metadata']
                print(f"      - Portfolio: {metadata.get('mutual_fund_name', 'Unknown')}")
                print(f"      - Holdings: {metadata.get('holdings_count', 0)}")
    
    return True


def upload_excel_file():
    """Upload Excel file"""
    try:
        with open(EXCEL_FILE_PATH, "rb") as f:
            files = {"file": (Path(EXCEL_FILE_PATH).name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            data = {"auto_process": "false"}  # We'll process manually for testing
            
            response = requests.post(f"{API_BASE_URL}/upload", files=files, data=data)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Upload failed: {response.status_code} - {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None


def process_excel_file(file_id):
    """Process Excel file to split into sheets"""
    try:
        response = requests.post(f"{API_BASE_URL}/process/{file_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Processing failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return None


def wait_for_processing(file_id, timeout=30):
    """Wait for file processing to complete"""
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = get_file_status(file_id)
        if status:
            file_status = status["file_info"]["status"]
            print(f"   Current status: {file_status}")
            
            if file_status == "completed":
                return status
            elif file_status == "failed":
                print(f"❌ Processing failed: {status['file_info'].get('error_message', 'Unknown error')}")
                return None
        
        time.sleep(2)
    
    print("⏰ Timeout waiting for processing")
    return None


def get_file_status(file_id):
    """Get file status"""
    try:
        response = requests.get(f"{API_BASE_URL}/files/{file_id}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Status check failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return None


def parse_sheet(sheet_id, method, api_key):
    """Parse individual sheet"""
    try:
        data = {
            "method": method,
            "api_key": api_key
        }
        
        response = requests.post(f"{API_BASE_URL}/parse/{sheet_id}", data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Parsing failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Parsing error: {e}")
        return None


def list_all_files():
    """List all uploaded files"""
    try:
        response = requests.get(f"{API_BASE_URL}/files")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ List files failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ List files error: {e}")
        return None


def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ API is healthy - Database: {health_data['database']}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


if __name__ == "__main__":
    print("🧪 File Upload API Test Suite")
    print("=" * 60)
    
    # Check if API is running
    if not test_api_health():
        print("\n💡 Make sure the API server is running:")
        print("   python start_api.py")
        exit(1)
    
    # Check if Excel file exists
    if not Path(EXCEL_FILE_PATH).exists():
        print(f"❌ Excel file not found: {EXCEL_FILE_PATH}")
        exit(1)
    
    # Run the complete test flow
    success = test_upload_flow()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        
        # Show all files
        print("\n📋 All uploaded files:")
        files_response = list_all_files()
        if files_response:
            for file_info in files_response["files"][:5]:  # Show first 5
                print(f"   📄 {file_info['original_filename']} ({file_info['status']})")
    else:
        print("❌ Some tests failed")