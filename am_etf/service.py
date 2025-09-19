"""ETF persistence service"""
import sys
from pathlib import Path
from typing import List, Optional, Iterable
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from am_etf.models import ETFInstrument


class ETFService:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017", db_name: str = "etf_data"):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self._client = None
        self._db = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            import motor.motor_asyncio
            self._client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
            self._db = self._client[self.db_name]
            self._collection = self._db.etfs
            # Indexes for lookup & uniqueness
            self._collection.create_index("symbol")
            self._collection.create_index("isin")
            self._collection.create_index([("symbol", 1), ("isin", 1)], unique=True, sparse=True)
        return self._collection

    @property
    def collection(self):
        return self._get_collection()

    async def upsert_etf(self, etf: ETFInstrument):
        col = self._get_collection()
        identifier = {"symbol": etf.symbol}
        if etf.isin:
            identifier["isin"] = etf.isin
        
        # Prepare update document without created_at for $set
        doc = etf.to_mongo_document()
        doc.pop("created_at", None)  # Remove created_at from $set to avoid conflict
        doc["updated_at"] = datetime.utcnow()
        
        await col.update_one(
            identifier,
            {"$set": doc, "$setOnInsert": {"created_at": datetime.utcnow()}},
            upsert=True
        )

    async def bulk_upsert(self, instruments: Iterable[ETFInstrument]) -> int:
        count = 0
        for inst in instruments:
            await self.upsert_etf(inst)
            count += 1
        return count

    async def list(self, limit: int = 100) -> List[ETFInstrument]:
        col = self._get_collection()
        cursor = col.find().limit(limit)
        out = []
        async for doc in cursor:
            doc.pop("_id", None)
            out.append(ETFInstrument(**doc))
        return out

    async def get_by_symbol(self, symbol: str) -> Optional[ETFInstrument]:
        col = self._get_collection()
        doc = await col.find_one({"symbol": symbol})
        if doc:
            doc.pop("_id", None)
            return ETFInstrument(**doc)
        return None

    async def close(self):
        if self._client:
            self._client.close()


def create_etf_service(mongo_uri: str = "mongodb://localhost:27017", db_name: str = "etf_data") -> ETFService:
    return ETFService(mongo_uri, db_name)
