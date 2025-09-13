"""
Demo script for Mutual Fund Service
Shows how to load JSON data, convert to models, and persist to MongoDB
"""
import json
import asyncio
import sys
from pathlib import Path

# Add parent directory to path to find external modules
sys.path.insert(0, str(Path(__file__).parent))

from am_common.mutual_fund_models import MutualFundPortfolio, Holding
from am_persistence.mutual_fund_service import create_mutual_fund_service


async def demo_mutual_fund_service():
    """Demonstrate the mutual fund service with real data"""
    
    print("🚀 Mutual Fund Service Demo")
    print("=" * 40)
    
    # Load sample data
    sample_file = Path("data/mfextractedholdings/motilaloswalmf.json")
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return
    
    print(f"📁 Loading data from: {sample_file}")
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to Pydantic model
    print("📋 Converting to Pydantic model...")
    portfolio = MutualFundPortfolio(**data)
    
    print(f"✅ Loaded portfolio: {portfolio.mutual_fund_name}")
    print(f"📅 Date: {portfolio.portfolio_date}")
    print(f"📊 Total holdings: {portfolio.total_holdings}")
    print(f"🔗 Actual holdings loaded: {len(portfolio.portfolio_holdings)}")
    
    # Create service instance
    print("\n🔌 Connecting to MongoDB...")
    service = create_mutual_fund_service()
    
    try:
        # Save to MongoDB
        print("💾 Saving to MongoDB...")
        portfolio_id = await service.save_portfolio(portfolio)
        print(f"✅ Saved with ID: {portfolio_id}")
        
        # Retrieve from MongoDB
        print("\n📖 Retrieving from MongoDB...")
        retrieved = await service.get_portfolio(
            portfolio.mutual_fund_name, 
            portfolio.portfolio_date
        )
        
        if retrieved:
            print(f"✅ Retrieved: {retrieved.mutual_fund_name}")
            print(f"📊 Holdings: {len(retrieved.portfolio_holdings)}")
        
        # List portfolios
        print("\n📝 Listing all portfolios...")
        summaries = await service.list_portfolios()
        print(f"✅ Found {len(summaries)} portfolio(s)")
        
        for summary in summaries:
            print(f"  - {summary.fund_name} ({summary.portfolio_date})")
            print(f"    Holdings: {summary.total_holdings}, Total %: {summary.total_percentage:.2f}%")
        
        # Search by ISIN
        if portfolio.portfolio_holdings:
            sample_isin = portfolio.portfolio_holdings[0].isin_code
            print(f"\n🔍 Searching for ISIN: {sample_isin}")
            
            isin_results = await service.get_holdings_by_isin(sample_isin)
            print(f"✅ Found in {len(isin_results)} portfolio(s)")
            
            for result in isin_results:
                if result["holding"]:
                    print(f"  - {result['fund_name']}: {result['holding']['name_of_instrument']}")
                    print(f"    Allocation: {result['holding']['percentage_to_nav']}")
        
        # Get fund statistics
        print(f"\n📊 Statistics for {portfolio.mutual_fund_name}...")
        stats = await service.get_fund_statistics(portfolio.mutual_fund_name)
        
        if stats:
            print(f"✅ Portfolio versions: {stats['portfolio_count']}")
            print(f"📅 Date range: {stats['earliest_date']} to {stats['latest_date']}")
            print(f"📊 Holdings range: {stats['min_holdings']} - {stats['max_holdings']} (avg: {stats['avg_holdings']})")
        
    except ImportError as e:
        print(f"❌ MongoDB dependency missing: {e}")
        print("💡 Install with: pip install motor")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await service.close()
    
    print("\n✨ Demo complete!")


def demo_model_conversion():
    """Demonstrate model conversion without MongoDB"""
    print("\n🔄 Model Conversion Demo (No MongoDB)")
    print("=" * 45)
    
    sample_file = Path("data/mfextractedholdings/motilaloswalmf.json")
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Convert to model
    portfolio = MutualFundPortfolio(**data)
    
    print(f"✅ Portfolio model created:")
    print(f"  Fund: {portfolio.mutual_fund_name}")
    print(f"  Date: {portfolio.portfolio_date}")
    print(f"  Holdings: {len(portfolio.portfolio_holdings)}")
    
    # Convert to MongoDB document
    mongo_doc = portfolio.to_mongo_document()
    print(f"\n📄 MongoDB document prepared:")
    print(f"  Keys: {list(mongo_doc.keys())}")
    print(f"  Document size: {len(json.dumps(mongo_doc))} characters")
    
    # Create summary
    summary = portfolio.portfolio_holdings[0]
    print(f"\n🏆 Top holding:")
    print(f"  Name: {summary.name_of_instrument}")
    print(f"  ISIN: {summary.isin_code}")
    print(f"  Allocation: {summary.percentage_to_nav}")


if __name__ == "__main__":
    # Run model conversion demo (always works)
    demo_model_conversion()
    
    # Run MongoDB demo (requires motor package)
    print("\n" + "="*50)
    try:
        asyncio.run(demo_mutual_fund_service())
    except ImportError:
        print("\n💡 To run MongoDB demo, install: pip install motor")
    except Exception as e:
        print(f"\n❌ MongoDB demo failed: {e}")
        print("💡 Make sure MongoDB is running on localhost:27017")
