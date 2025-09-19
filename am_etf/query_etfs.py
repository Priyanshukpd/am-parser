"""Query script to check ETF data with holdings"""
import asyncio
from am_etf.service import create_etf_service


async def show_etf_data():
    service = create_etf_service(
        mongo_uri="mongodb://admin:password123@localhost:27017",
        db_name="etf_data"
    )
    
    try:
        # Get ETFs with holdings
        etfs_with_holdings = await service.get_etfs_with_holdings(limit=10)
        
        print(f"📊 Found {len(etfs_with_holdings)} ETFs with holdings data:\n")
        
        for etf in etfs_with_holdings:
            print(f"🏷️  {etf.symbol}: {etf.name}")
            print(f"   ISIN: {etf.isin}")
            print(f"   Asset Class: {etf.asset_class}")
            print(f"   Market Cap Category: {etf.market_cap_category}")
            
            if etf.holdings:
                print(f"   Holdings: {len(etf.holdings)} stocks")
                print("   Top 5 Holdings:")
                for i, holding in enumerate(etf.holdings[:5]):
                    print(f"     {i+1}. {holding.stock_name}: {holding.percentage}%")
            print()
            
        # Show summary stats
        total_etfs = await service.collection.count_documents({})
        etfs_with_holdings_count = await service.collection.count_documents({"holdings": {"$exists": True, "$ne": None}})
        
        print(f"📈 Summary:")
        print(f"   Total ETFs in database: {total_etfs}")
        print(f"   ETFs with holdings data: {etfs_with_holdings_count}")
        print(f"   Coverage: {etfs_with_holdings_count/total_etfs*100:.1f}%")
        
    finally:
        await service.close()


if __name__ == "__main__":
    asyncio.run(show_etf_data())