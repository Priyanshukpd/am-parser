#!/usr/bin/env python3
"""Quick ETF data verification script"""
import asyncio
from am_etf.service import create_etf_service

async def main():
    service = create_etf_service(
        mongo_uri="mongodb://admin:password123@localhost:27017", 
        db_name="etf_data"
    )
    
    # Get total count
    collection = service.collection
    total = await collection.count_documents({})
    print(f"Total ETF records: {total}")
    
    # Sample records
    print("\nSample ETF records:")
    etfs = await service.list(limit=5)
    for etf in etfs:
        print(f"- {etf.symbol}: {etf.name} ({etf.asset_class}, {etf.market_cap_category})")
    
    # Check for duplicates by symbol
    print("\nDuplicate check:")
    pipeline = [
        {"$group": {"_id": "$symbol", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    async for doc in collection.aggregate(pipeline):
        print(f"Symbol '{doc['_id']}' appears {doc['count']} times")
    
    # Asset class breakdown
    print("\nAsset class breakdown:")
    pipeline = [
        {"$group": {"_id": "$asset_class", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    async for doc in collection.aggregate(pipeline):
        asset_class = doc['_id'] or "Unknown"
        print(f"- {asset_class}: {doc['count']} ETFs")
    
    await service.close()

if __name__ == "__main__":
    asyncio.run(main())