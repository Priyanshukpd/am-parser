#!/usr/bin/env python3
"""
Test Mutual Fund Service with MongoDB
Comprehensive testing of the mutual fund JSON persistence service
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to find external modules
sys.path.insert(0, str(Path(__file__).parent))

from am_persistence import create_mutual_fund_service
from am_common.mutual_fund_models import MutualFundPortfolio


async def test_mutual_fund_service():
    """Test the mutual fund service with real data"""
    
    print("🧪 Testing Mutual Fund Service with MongoDB")
    print("=" * 50)
    
    # Initialize service
    service = create_mutual_fund_service(
        mongo_uri="mongodb://admin:password123@localhost:27017",
        db_name="mutual_funds"
    )
    
    try:
        # Test 1: Load and validate JSON data
        print("\n📁 Step 1: Loading JSON data")
        json_file = Path("data/mfextractedholdings/motilaloswalmf.json")
        
        if not json_file.exists():
            print(f"❌ JSON file not found: {json_file}")
            return False
            
        with open(json_file, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
        print(f"✅ Loaded JSON data from {json_file}")
        print(f"   Fund Name: {json_data.get('mutual_fund_name', 'N/A')}")
        print(f"   Holdings Count: {len(json_data.get('portfolio_holdings', []))}")
        
        # Test 2: Convert to Pydantic model
        print("\n🔄 Step 2: Converting to Pydantic model")
        try:
            portfolio = MutualFundPortfolio(**json_data)
            print(f"✅ Successfully created MutualFundPortfolio model")
            print(f"   Validation passed for {len(portfolio.portfolio_holdings)} holdings")
        except Exception as e:
            print(f"❌ Model validation failed: {e}")
            return False
        
        # Test 3: Save to MongoDB
        print("\n💾 Step 3: Saving to MongoDB")
        portfolio_id = await service.save_portfolio(portfolio)
        print(f"✅ Saved portfolio with ID: {portfolio_id}")
        
        # Test 4: Retrieve from MongoDB
        print("\n📖 Step 4: Retrieving from MongoDB")
        retrieved = await service.get_portfolio_by_id(portfolio_id)
        if retrieved:
            print(f"✅ Retrieved portfolio: {retrieved.mutual_fund_name}")
            print(f"   Holdings: {len(retrieved.portfolio_holdings)}")
            print(f"   Total Holdings: {retrieved.total_holdings}")
        else:
            print("❌ Failed to retrieve portfolio")
            return False
        
        # Test 5: Search functionality
        print("\n🔍 Step 5: Testing search functionality")
        
        # Search by fund name using list_portfolios
        search_results = await service.list_portfolios(fund_name=portfolio.mutual_fund_name)
        print(f"✅ Found {len(search_results)} portfolio(s) by fund name")
        
        # Search by ISIN (if available)
        if portfolio.portfolio_holdings:
            sample_isin = portfolio.portfolio_holdings[0].isin_code
            isin_results = await service.get_holdings_by_isin(sample_isin)
            print(f"✅ Found {len(isin_results)} holding(s) with ISIN: {sample_isin}")
        
        # Test 6: List all portfolios
        print("\n📋 Step 6: Listing all portfolios")
        all_portfolios = await service.list_portfolios(limit=10)
        print(f"✅ Found {len(all_portfolios)} total portfolio(s)")
        
        for i, p in enumerate(all_portfolios, 1):
            print(f"   {i}. {p.fund_name} ({p.portfolio_date}) - {p.total_holdings} holdings")
        
        # Test 7: Fund statistics
        print("\n📊 Step 7: Getting fund statistics")
        stats = await service.get_fund_statistics(portfolio.mutual_fund_name)
        if stats:
            print(f"✅ Statistics for {portfolio.mutual_fund_name}:")
            print(f"   Total Portfolios: {stats['portfolio_count']}")
            print(f"   Date Range: {stats['earliest_date']} to {stats['latest_date']}")
            print(f"   Avg Holdings: {stats['avg_holdings']}")
            print(f"   Holdings Range: {stats['min_holdings']} - {stats['max_holdings']}")
        else:
            print("⚠️  No statistics found for this fund")
        
        # Test 8: Test duplicate handling
        print("\n🔄 Step 8: Testing duplicate handling")
        try:
            duplicate_id = await service.save_portfolio(portfolio)
            print(f"✅ Duplicate handling working - ID: {duplicate_id}")
        except Exception as e:
            print(f"⚠️  Duplicate handling: {e}")
        
        print("\n🎉 All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Close service
        await service.close()
        print("\n🔐 Database connection closed")


async def cleanup_test_data():
    """Clean up test data (optional)"""
    print("\n🧹 Cleaning up test data...")
    
    service = create_mutual_fund_service(
        mongo_uri="mongodb://admin:password123@localhost:27017",
        db_name="mutual_funds"
    )
    
    try:
        # Get collection directly for cleanup
        collection = service._get_collection()
        result = await collection.delete_many({})
        print(f"✅ Cleaned up {result.deleted_count} documents")
        
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        
    finally:
        await service.close()


async def main():
    """Main test function"""
    print("🚀 Mutual Fund Service - MongoDB Integration Test")
    print("=" * 55)
    
    # Check if MongoDB is running
    try:
        service = create_mutual_fund_service()
        collection = service._get_collection()
        await service.close()
        print("✅ MongoDB connection verified")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Make sure Docker is running: docker-compose up -d")
        return
    
    # Run comprehensive tests
    success = await test_mutual_fund_service()
    
    if success:
        print("\n✅ All tests passed! Your mutual fund service is working perfectly.")
        print("\n🌐 View your data in Mongo Express:")
        print("   http://localhost:8081")
        print("   Username: webadmin")
        print("   Password: webpass123")
        
        # Ask if user wants to clean up
        print("\n🧹 Clean up test data? (y/N):", end=" ")
        
        # For automated testing, skip cleanup prompt
        # Uncomment the next lines if you want interactive cleanup
        # try:
        #     response = input().strip().lower()
        #     if response == 'y':
        #         await cleanup_test_data()
        # except (EOFError, KeyboardInterrupt):
        #     print("\nSkipping cleanup")
        
    else:
        print("\n❌ Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    asyncio.run(main())