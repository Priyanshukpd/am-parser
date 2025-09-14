#!/usr/bin/env python3
"""
Comprehensive test script to demonstrate async vs sync processing
This script shows the clear difference between immediate async responses 
vs blocking sync responses for Excel file processing.
"""
import requests
import json
import time
import threading
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_FILE = "data/samples/motilal-hy-portfolio-march-2025.xlsx"

def print_timestamp(message):
    """Print message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_sync_processing():
    """Test the synchronous endpoint - this will block until processing is done"""
    print_timestamp("🔄 Starting SYNCHRONOUS processing test...")
    start_time = time.time()
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {
                'file': ('motilal-hy-portfolio-march-2025.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {'parse_method': 'together'}
            
            print_timestamp("📤 Sending request to /upload/excel (SYNC)...")
            response = requests.post(f"{BASE_URL}/upload/excel", files=files, data=data)
            
        end_time = time.time()
        processing_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print_timestamp(f"✅ SYNC processing completed in {processing_time:.2f} seconds")
            print_timestamp(f"📊 Parsed {len(result.get('parsed_portfolios', []))} portfolios")
            return processing_time
        else:
            print_timestamp(f"❌ SYNC request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_timestamp(f"❌ SYNC test error: {e}")
        return None

def test_async_processing():
    """Test the asynchronous endpoint - this returns immediately with job ID"""
    print_timestamp("🚀 Starting ASYNCHRONOUS processing test...")
    start_time = time.time()
    
    try:
        with open(TEST_FILE, 'rb') as f:
            files = {
                'file': ('motilal-hy-portfolio-march-2025.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            data = {
                'parse_method': 'together',
                'webhook_url': 'http://httpbin.org/post'  # Test webhook
            }
            
            print_timestamp("📤 Sending request to /jobs/upload-excel-async (ASYNC)...")
            response = requests.post(f"{BASE_URL}/jobs/upload-excel-async", files=files, data=data)
            
        immediate_response_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            job_id = result.get('job_id')
            
            print_timestamp(f"✅ ASYNC request returned IMMEDIATELY in {immediate_response_time:.2f} seconds")
            print_timestamp(f"📋 Job ID: {job_id}")
            print_timestamp(f"🔍 Status: {result.get('status')}")
            
            # Now monitor the job progress
            return monitor_job_progress(job_id, start_time)
            
        else:
            print_timestamp(f"❌ ASYNC request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print_timestamp(f"❌ ASYNC test error: {e}")
        return None

def monitor_job_progress(job_id, start_time):
    """Monitor job progress and show real-time updates"""
    print_timestamp(f"👀 Monitoring job progress for {job_id}...")
    
    max_checks = 30  # Maximum number of status checks
    check_interval = 2  # Seconds between checks
    
    for i in range(max_checks):
        try:
            response = requests.get(f"{BASE_URL}/jobs/{job_id}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                status = status_data.get('status')
                progress = status_data.get('progress', {})
                percentage = progress.get('percentage', 0)
                
                elapsed = time.time() - start_time
                print_timestamp(f"📊 Check {i+1}: Status={status}, Progress={percentage}%, Elapsed={elapsed:.1f}s")
                
                if status == 'completed':
                    total_time = time.time() - start_time
                    print_timestamp(f"🎉 ASYNC job completed! Total time: {total_time:.2f} seconds")
                    
                    # Get the final result
                    result_response = requests.get(f"{BASE_URL}/jobs/{job_id}/result")
                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        portfolios = result_data.get('parsed_portfolios', [])
                        print_timestamp(f"📊 Final result: {len(portfolios)} portfolios parsed")
                        for portfolio in portfolios:
                            print_timestamp(f"  - {portfolio.get('sheet_name')}: {portfolio.get('mutual_fund_name')}")
                    
                    return total_time
                    
                elif status == 'failed':
                    print_timestamp(f"❌ ASYNC job failed: {status_data.get('error')}")
                    return None
                    
                elif status in ['in-progress', 'queued']:
                    time.sleep(check_interval)
                    continue
                    
            else:
                print_timestamp(f"❌ Status check failed: {response.status_code}")
                break
                
        except Exception as e:
            print_timestamp(f"❌ Error checking status: {e}")
            break
    
    print_timestamp("⏰ Timeout waiting for job completion")
    return None

def test_api_endpoints():
    """Test various API endpoints to show functionality"""
    print_timestamp("🔍 Testing API endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{BASE_URL}/")
        print_timestamp(f"✅ Health check: {response.status_code}")
    except:
        print_timestamp("❌ Server not responding")
        return False
    
    # Test job listing
    try:
        response = requests.get(f"{BASE_URL}/jobs/")
        if response.status_code == 200:
            jobs = response.json()
            print_timestamp(f"📋 Found {len(jobs)} existing jobs")
        else:
            print_timestamp(f"⚠️ Job listing returned: {response.status_code}")
    except Exception as e:
        print_timestamp(f"❌ Error testing job listing: {e}")
    
    return True

def main():
    """Main test function"""
    print("=" * 80)
    print("🧪 ASYNC vs SYNC PROCESSING COMPARISON TEST")
    print("=" * 80)
    print()
    
    # Test if server is running
    if not test_api_endpoints():
        print_timestamp("❌ Server tests failed. Make sure uvicorn server is running.")
        return
    
    print()
    print("📝 This test demonstrates the key difference:")
    print("   • SYNC: API blocks until processing is complete (1-3 minutes)")
    print("   • ASYNC: API returns immediately, processing happens in background")
    print()
    
    # Test async processing first
    print("🚀 PART 1: ASYNC PROCESSING")
    print("-" * 50)
    async_time = test_async_processing()
    
    print()
    print("⏱️ PART 2: SYNC PROCESSING (for comparison)")
    print("-" * 50)
    sync_time = test_sync_processing()
    
    print()
    print("=" * 80)
    print("📊 COMPARISON RESULTS:")
    print("=" * 80)
    
    if async_time and sync_time:
        print(f"🚀 ASYNC total time: {async_time:.2f} seconds")
        print(f"🔄 SYNC blocking time: {sync_time:.2f} seconds")
        print()
        print("✅ KEY BENEFITS OF ASYNC:")
        print(f"   • API responds immediately (not blocked for {sync_time:.1f} seconds)")
        print("   • Can handle multiple concurrent requests")
        print("   • Real-time progress monitoring")
        print("   • Webhook notifications on completion")
        print("   • No API timeouts for large files")
    else:
        print("⚠️ Could not complete comparison - check server logs")
    
    print()
    print("🎯 For files with 50+ sheets (50-150 minutes processing):")
    print("   • SYNC: API would timeout or block for hours")
    print("   • ASYNC: Immediate response + background processing")

if __name__ == "__main__":
    main()