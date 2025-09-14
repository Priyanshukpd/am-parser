#!/usr/bin/env python3
"""
Debug script to test portfolio saving and retrieval
"""
import asyncio
from am_persistence.mutual_fund_service import MutualFundService
from am_common.mutual_fund_models import MutualFundPortfolio, Holding

async def test_portfolio_operations():
    """Test saving and retrieving a portfolio"""
    
    # Create a test portfolio
    test_holdings = [
        Holding(
            name_of_instrument="Test Company 1",
            isin_code="TEST001",
            percentage_to_nav="10.5%"
        ),
        Holding(
            name_of_instrument="Test Company 2", 
            isin_code="TEST002",
            percentage_to_nav="20.0%"
        )
    ]
    
    test_portfolio = MutualFundPortfolio(
        mutual_fund_name="Test Fund",
        portfolio_date="2025-01-01",
        total_holdings=2,
        portfolio_holdings=test_holdings
    )
    
    # Initialize service with proper authentication
    service = MutualFundService(
        mongo_uri="mongodb://admin:password123@localhost:27017",
        db_name="mutual_funds"
    )
    
    # Test custom ID
    custom_id = "test-portfolio-123"
    
    try:
        print("🧪 Testing portfolio save with custom ID...")
        saved_id = await service.save_portfolio_with_id(test_portfolio, custom_id)
        print(f"✅ Saved portfolio with ID: {saved_id}")
        
        print("🔍 Testing portfolio retrieval...")
        retrieved = await service.get_portfolio_by_id(saved_id)
        
        if retrieved:
            print(f"✅ Successfully retrieved portfolio: {retrieved.mutual_fund_name}")
            print(f"📊 Holdings count: {retrieved.total_holdings}")
            print(f"🏢 First holding: {retrieved.portfolio_holdings[0].name_of_instrument}")
        else:
            print("❌ Failed to retrieve portfolio")
            
        # Test direct MongoDB query
        collection = service._get_collection()
        doc = await collection.find_one({"_id": custom_id})
        if doc:
            print(f"✅ Direct MongoDB query found document: {doc.get('mutual_fund_name')}")
        else:
            print("❌ Direct MongoDB query found no document")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(test_portfolio_operations())