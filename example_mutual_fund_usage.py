#!/usr/bin/env python3
"""
Example usage of MutualFundService
Shows how to load JSON data and persist to MongoDB
"""

import json
import asyncio
from pathlib import Path

# Import the models and service
from am_common import MutualFundPortfolio
from am_persistence import create_mutual_fund_service


async def example_usage():
    """Example of using MutualFundService"""
    
    # 1. Load JSON data
    json_file = Path("data/mfextractedholdings/motilaloswalmf.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 2. Convert to Pydantic model
    portfolio = MutualFundPortfolio(**data)
    
    print(f"📋 Portfolio: {portfolio.mutual_fund_name}")
    print(f"📅 Date: {portfolio.portfolio_date}")
    print(f"📊 Holdings: {len(portfolio.portfolio_holdings)}")
    
    # 3. Create service and save to MongoDB
    service = create_mutual_fund_service(
        mongo_uri="mongodb://localhost:27017",
        db_name="mutual_funds"
    )
    
    try:
        # Save portfolio
        portfolio_id = await service.save_portfolio(portfolio)
        print(f"✅ Saved with ID: {portfolio_id}")
        
        # Retrieve it back
        retrieved = await service.get_portfolio(
            portfolio.mutual_fund_name,
            portfolio.portfolio_date
        )
        
        if retrieved:
            print(f"✅ Retrieved successfully: {len(retrieved.portfolio_holdings)} holdings")
        
        # Get statistics
        stats = await service.get_fund_statistics(portfolio.mutual_fund_name)
        print(f"📊 Fund statistics: {stats}")
        
        # Search by ISIN
        if portfolio.portfolio_holdings:
            sample_isin = portfolio.portfolio_holdings[0].isin_code
            isin_results = await service.get_holdings_by_isin(sample_isin)
            print(f"🔍 ISIN {sample_isin} found in {len(isin_results)} portfolio(s)")
        
    except ImportError:
        print("❌ MongoDB support requires 'motor' package")
        print("💡 Install with: pip install motor")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await service.close()


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_usage())
