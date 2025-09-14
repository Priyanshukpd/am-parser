"""
Mutual Fund Persistence Service - Handle MongoDB operations for mutual fund data
"""
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add parent directory to path to find external modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from am_common.mutual_fund_models import MutualFundPortfolio, PortfolioSummary, Holding


class MutualFundService:
    """
    Service class for handling mutual fund portfolio operations
    Accepts MutualFundPortfolio model objects and handles persistence
    """
    
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "mutual_funds"):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self._client = None
        self._db = None
        self._collection = None
    
    def _get_collection(self):
        """Lazy initialization of MongoDB connection"""
        if self._collection is None:
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                
                # Configure client with authentication if credentials are in URI
                if "@" in self.mongo_uri:
                    # URI contains credentials
                    self._client = AsyncIOMotorClient(self.mongo_uri)
                else:
                    # Try without auth first, then with default Docker credentials
                    try:
                        self._client = AsyncIOMotorClient(self.mongo_uri)
                        # Test connection
                        import asyncio
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # We're in an async context, defer the connection test
                            pass
                        else:
                            loop.run_until_complete(self._client.server_info())
                    except Exception:
                        # Try with Docker default credentials
                        auth_uri = self.mongo_uri.replace("mongodb://", "mongodb://admin:password123@")
                        self._client = AsyncIOMotorClient(auth_uri)
                
                self._db = self._client[self.db_name]
                self._collection = self._db.portfolios
            except ImportError:
                raise ImportError(
                    "MongoDB support requires 'motor' package. "
                    "Install with: pip install motor"
                )
        return self._collection
    
    @property
    def database(self):
        """Get the database instance"""
        self._get_collection()  # Ensure database is initialized
        return self._db
    
    async def save_portfolio(self, portfolio: MutualFundPortfolio) -> str:
        """
        Save a mutual fund portfolio to MongoDB
        
        Args:
            portfolio: MutualFundPortfolio model instance
            
        Returns:
            str: MongoDB document ID
        """
        collection = self._get_collection()
        
        # Convert to MongoDB document
        doc = portfolio.to_mongo_document()
        doc["updated_at"] = datetime.now().isoformat()
        
        # Check if portfolio already exists (by fund name and date)
        existing = await collection.find_one({
            "mutual_fund_name": portfolio.mutual_fund_name,
            "portfolio_date": portfolio.portfolio_date
        })
        
        if existing:
            # Update existing document
            result = await collection.replace_one(
                {"_id": existing["_id"]}, 
                doc
            )
            return str(existing["_id"])
        else:
            # Insert new document
            result = await collection.insert_one(doc)
            return str(result.inserted_id)
    
    async def save_portfolio_with_id(self, portfolio: MutualFundPortfolio, custom_id: str) -> str:
        """
        Save a mutual fund portfolio with a specific custom ID (to match sheet ID)
        
        Args:
            portfolio: MutualFundPortfolio model instance
            custom_id: Custom ID to use (e.g., sheet file ID)
            
        Returns:
            str: The custom ID used for the document
        """
        collection = self._get_collection()
        
        # Convert to MongoDB document
        doc = portfolio.to_mongo_document()
        doc["updated_at"] = datetime.now().isoformat()
        doc["_id"] = custom_id  # Use custom ID instead of auto-generated ObjectId
        doc["sheet_id"] = custom_id  # Also store as separate field for queries
        
        try:
            # Try to insert with custom ID
            await collection.insert_one(doc)
            print(f"✅ Portfolio inserted with custom ID: {custom_id}")
            return custom_id
        except Exception as e:
            # If ID already exists, update the document
            if "duplicate key" in str(e).lower():
                doc.pop("_id")  # Remove _id for update
                result = await collection.replace_one(
                    {"_id": custom_id}, 
                    doc
                )
                print(f"✅ Portfolio updated with custom ID: {custom_id}")
                return custom_id
            else:
                # If other error, fall back to auto-generated ID
                print(f"⚠️ Custom ID failed, using auto-generated: {e}")
                doc.pop("_id", None)
                result = await collection.insert_one(doc)
                return str(result.inserted_id)
    
    async def get_portfolio(self, fund_name: str, portfolio_date: str) -> Optional[MutualFundPortfolio]:
        """
        Retrieve a portfolio by fund name and date
        
        Args:
            fund_name: Name of the mutual fund
            portfolio_date: Portfolio date string
            
        Returns:
            MutualFundPortfolio instance or None if not found
        """
        collection = self._get_collection()
        
        doc = await collection.find_one({
            "mutual_fund_name": fund_name,
            "portfolio_date": portfolio_date
        })
        
        if doc:
            # Remove MongoDB _id field before creating model
            doc.pop("_id", None)
            return MutualFundPortfolio(**doc)
        return None
    
    async def get_portfolio_by_id(self, portfolio_id: str) -> Optional[MutualFundPortfolio]:
        """
        Retrieve a portfolio by MongoDB document ID (supports both ObjectId and custom string IDs)
        
        Args:
            portfolio_id: MongoDB document ID (ObjectId string or custom string)
            
        Returns:
            MutualFundPortfolio instance or None if not found
        """
        collection = self._get_collection()
        
        try:
            # First try as string ID (for custom IDs)
            doc = await collection.find_one({"_id": portfolio_id})
            if doc:
                doc.pop("_id", None)
                return MutualFundPortfolio(**doc)
            
            # If not found, try as ObjectId (for auto-generated IDs)
            from bson import ObjectId
            try:
                doc = await collection.find_one({"_id": ObjectId(portfolio_id)})
                if doc:
                    doc.pop("_id", None)
                    return MutualFundPortfolio(**doc)
            except Exception:
                pass
                
        except Exception:
            pass
        return None
    
    async def list_portfolios(self, fund_name: Optional[str] = None, limit: int = 50) -> List[PortfolioSummary]:
        """
        List portfolios with optional filtering
        
        Args:
            fund_name: Optional fund name filter
            limit: Maximum number of results
            
        Returns:
            List of PortfolioSummary objects
        """
        collection = self._get_collection()
        
        query = {}
        if fund_name:
            query["mutual_fund_name"] = {"$regex": fund_name, "$options": "i"}
        
        cursor = collection.find(query).limit(limit).sort("updated_at", -1)
        
        summaries = []
        async for doc in cursor:
            doc.pop("_id", None)
            portfolio = MutualFundPortfolio(**doc)
            summary = PortfolioSummary.from_portfolio(portfolio)
            summaries.append(summary)
        
        return summaries
    
    async def delete_portfolio(self, fund_name: str, portfolio_date: str) -> bool:
        """
        Delete a portfolio by fund name and date
        
        Args:
            fund_name: Name of the mutual fund
            portfolio_date: Portfolio date string
            
        Returns:
            True if deleted, False if not found
        """
        collection = self._get_collection()
        
        result = await collection.delete_one({
            "mutual_fund_name": fund_name,
            "portfolio_date": portfolio_date
        })
        
        return result.deleted_count > 0
    
    async def get_holdings_by_isin(self, isin_code: str) -> List[Dict[str, Any]]:
        """
        Find all portfolios containing a specific ISIN
        
        Args:
            isin_code: ISIN code to search for
            
        Returns:
            List of portfolios containing the ISIN with holding details
        """
        collection = self._get_collection()
        
        # MongoDB aggregation to find portfolios with specific ISIN
        pipeline = [
            {"$match": {"portfolio_holdings.isin_code": isin_code}},
            {"$project": {
                "mutual_fund_name": 1,
                "portfolio_date": 1,
                "total_holdings": 1,
                "matching_holding": {
                    "$filter": {
                        "input": "$portfolio_holdings",
                        "cond": {"$eq": ["$$this.isin_code", isin_code]}
                    }
                }
            }}
        ]
        
        results = []
        async for doc in collection.aggregate(pipeline):
            results.append({
                "fund_name": doc["mutual_fund_name"],
                "portfolio_date": doc["portfolio_date"],
                "total_holdings": doc["total_holdings"],
                "holding": doc["matching_holding"][0] if doc["matching_holding"] else None
            })
        
        return results
    
    async def get_fund_statistics(self, fund_name: str) -> Dict[str, Any]:
        """
        Get statistics for a specific fund across all portfolio dates
        
        Args:
            fund_name: Name of the mutual fund
            
        Returns:
            Dictionary with fund statistics
        """
        collection = self._get_collection()
        
        pipeline = [
            {"$match": {"mutual_fund_name": fund_name}},
            {"$group": {
                "_id": "$mutual_fund_name",
                "portfolio_count": {"$sum": 1},
                "latest_date": {"$max": "$portfolio_date"},
                "earliest_date": {"$min": "$portfolio_date"},
                "avg_holdings": {"$avg": "$total_holdings"},
                "max_holdings": {"$max": "$total_holdings"},
                "min_holdings": {"$min": "$total_holdings"}
            }}
        ]
        
        async for doc in collection.aggregate(pipeline):
            return {
                "fund_name": doc["_id"],
                "portfolio_count": doc["portfolio_count"],
                "latest_date": doc["latest_date"],
                "earliest_date": doc["earliest_date"],
                "avg_holdings": round(doc["avg_holdings"], 1),
                "max_holdings": doc["max_holdings"],
                "min_holdings": doc["min_holdings"]
            }
        
        return {}
    
    async def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()


# Factory function for easy instantiation
def create_mutual_fund_service(mongo_uri: str = "mongodb://localhost:27017", 
                              db_name: str = "mutual_funds") -> MutualFundService:
    """
    Factory function to create MutualFundService instance
    
    Args:
        mongo_uri: MongoDB connection URI
        db_name: Database name
        
    Returns:
        MutualFundService instance
    """
    return MutualFundService(mongo_uri, db_name)
