"""CLI for fetching and storing ETF holdings in dedicated collection"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from am_etf.holdings_service import ETFHoldingsService
from am_etf.service import ETFService


async def fetch_equity_holdings():
    """Fetch holdings for a few equity ETFs and store in dedicated collection"""
    
    holdings_service = ETFHoldingsService()
    etf_service = ETFService()
    
    # Get a couple of equity ETFs to test with
    equity_etfs = await etf_service.get_etfs_by_asset_class("Equity")
    
    if not equity_etfs:
        print("❌ No equity ETFs found in database")
        return
    
    print(f"📊 Found {len(equity_etfs)} equity ETFs")
    
    # Process first 2 equity ETFs
    processed = 0
    for etf in equity_etfs[:2]:
        if etf.isin:
            print(f"\n🔄 Processing {etf.symbol} ({etf.isin})")
            success = await holdings_service.fetch_and_store_holdings_for_isin(
                isin=etf.isin,
                symbol=etf.symbol,
                etf_name=etf.name
            )
            if success:
                processed += 1
            
            # Add delay between requests
            await asyncio.sleep(1)
    
    print(f"\n✅ Successfully processed holdings for {processed} equity ETFs")
    
    # Show stats
    stats = await holdings_service.get_holdings_stats()
    print(f"📊 Holdings Collection Stats: {stats}")
    
    # Show stored holdings
    print("\n📋 Recently stored holdings:")
    all_holdings = await holdings_service.list_all_holdings(limit=5)
    for holdings_data in all_holdings:
        print(f"  • {holdings_data.symbol} ({holdings_data.isin}): {holdings_data.total_holdings} holdings")
        if holdings_data.holdings:
            # Show top 3 holdings
            for i, holding in enumerate(holdings_data.holdings[:3]):
                print(f"    {i+1}. {holding.stock_name}: {holding.percentage}%")
    
    await holdings_service.close()
    await etf_service.close()


async def query_holdings():
    """Query and display stored holdings"""
    holdings_service = ETFHoldingsService()
    
    stats = await holdings_service.get_holdings_stats()
    print(f"📊 Holdings Collection Stats: {stats}")
    
    all_holdings = await holdings_service.list_all_holdings(limit=10)
    
    if not all_holdings:
        print("No holdings data found in etf_holdings collection")
        return
    
    for holdings_data in all_holdings:
        print(f"\n🎯 ETF: {holdings_data.symbol} ({holdings_data.etf_name})")
        print(f"   ISIN: {holdings_data.isin}")
        print(f"   Total Holdings: {holdings_data.total_holdings}")
        print(f"   Fetched: {holdings_data.fetched_at}")
        
        if holdings_data.holdings:
            print("   Top Holdings:")
            for i, holding in enumerate(holdings_data.holdings[:5]):
                print(f"     {i+1}. {holding.stock_name}: {holding.percentage}%")
    
    await holdings_service.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "query":
        asyncio.run(query_holdings())
    else:
        asyncio.run(fetch_equity_holdings())