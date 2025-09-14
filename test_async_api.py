#!/usr/bin/env python3
"""
Test script to upload Excel file using async API
"""
import requests
import json
import time

def test_async_upload():
    """Test the async Excel upload endpoint"""
    
    # Test file path
    test_file = "data/samples/motilal-hy-portfolio-march-2025.xlsx"
    
    # Upload endpoint
    url = "http://localhost:8000/jobs/upload-excel-async"
    
    try:
        print("🚀 Testing async Excel upload...")
        
        # Prepare the file upload
        with open(test_file, 'rb') as f:
            files = {
                'file': ('motilal-hy-portfolio-march-2025.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {
                'parse_method': 'together'
            }
            
            # Make the request
            response = requests.post(url, files=files, data=data)
            
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            print(f"✅ Job submitted successfully!")
            print(f"📋 Job ID: {job_id}")
            print(f"🔍 Status: {result.get('status')}")
            print(f"📝 Message: {result.get('message')}")
            
            # Check job status
            print("\n🔍 Checking job status...")
            status_url = f"http://localhost:8000/jobs/{job_id}/status"
            
            for i in range(10):  # Check for up to 10 iterations
                time.sleep(2)  # Wait 2 seconds between checks
                status_response = requests.get(status_url)
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"⏱️  Check {i+1}: Status = {status_data.get('status')}, Progress = {status_data.get('progress', {}).get('percentage', 0)}%")
                    
                    if status_data.get('status') in ['completed', 'failed']:
                        print(f"\n🎯 Final Status: {status_data.get('status')}")
                        if status_data.get('status') == 'completed':
                            print("✅ Job completed successfully!")
                            if 'result' in status_data:
                                result_data = status_data['result']
                                print(f"📊 Parsed portfolios: {len(result_data.get('parsed_portfolios', []))}")
                                for portfolio in result_data.get('parsed_portfolios', []):
                                    print(f"  - {portfolio.get('sheet_name')}: {portfolio.get('mutual_fund_name')} ({portfolio.get('total_holdings')} holdings)")
                        else:
                            print("❌ Job failed!")
                            print(f"❌ Error: {status_data.get('error')}")
                        break
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    break
            else:
                print("⏰ Timeout waiting for job completion")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_async_upload()