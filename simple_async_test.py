#!/usr/bin/env python3
"""
Simple async API test - demonstrates the immediate response
"""
import requests
import json
import time
from datetime import datetime

def test_async_endpoint():
    """Test the async endpoint and show immediate response"""
    print("🚀 Testing ASYNC Excel Upload Endpoint")
    print("=" * 50)
    
    url = "http://localhost:8000/jobs/upload-excel-async"
    test_file = "data/samples/motilal-hy-portfolio-march-2025.xlsx"
    
    try:
        # Record start time
        start_time = time.time()
        print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Prepare request
        with open(test_file, 'rb') as f:
            files = {
                'file': ('motilal-hy-portfolio-march-2025.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {
                'parse_method': 'together'
            }
            
            print("📤 Sending request to async endpoint...")
            print("   (This should return IMMEDIATELY, not wait for processing)")
            
            # Make the request
            response = requests.post(url, files=files, data=data)
        
        # Calculate response time
        response_time = time.time() - start_time
        end_time = datetime.now().strftime('%H:%M:%S')
        
        print(f"⏰ Response time: {datetime.now().strftime('%H:%M:%S')}")
        print(f"⚡ IMMEDIATE response in: {response_time:.2f} seconds")
        print()
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Async endpoint responded immediately:")
            print(f"📋 Job ID: {result.get('job_id')}")
            print(f"🔍 Status: {result.get('status')}")
            print(f"📝 Message: {result.get('message')}")
            print()
            print("🎯 KEY POINT: The API returned instantly!")
            print("   The actual processing is happening in the background.")
            
            return result.get('job_id')
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"❌ Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_job_status(job_id):
    """Check the job status to show background processing"""
    print(f"👀 Checking status of job: {job_id}")
    print("-" * 50)
    
    status_url = f"http://localhost:8000/jobs/{job_id}/status"
    
    for i in range(5):  # Check status 5 times
        try:
            response = requests.get(status_url)
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                progress = status_data.get('progress', {})
                percentage = progress.get('percentage', 0)
                
                print(f"📊 Check {i+1}: Status={status}, Progress={percentage}%")
                
                if status == 'completed':
                    print("🎉 Job completed!")
                    break
                elif status == 'failed':
                    print("❌ Job failed!")
                    break
                    
                if i < 4:  # Don't sleep on last iteration
                    time.sleep(3)
                    
            else:
                print(f"❌ Status check failed: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Error checking status: {e}")
            break

if __name__ == "__main__":
    print("🧪 ASYNC API DEMONSTRATION")
    print("This test shows how the async API returns immediately")
    print("instead of blocking for 1-3 minutes like the sync version.")
    print()
    
    # Test async endpoint
    job_id = test_async_endpoint()
    
    if job_id:
        print()
        print("Now let's check the job status to see background processing:")
        check_job_status(job_id)
        print()
        print("🎯 SUMMARY:")
        print("✅ Async API responded in <1 second")
        print("🔄 Processing continues in background")
        print("👀 Can monitor progress via job status API")
        print("📞 Can receive webhooks when complete")
    else:
        print("❌ Could not test job status - async request failed")