"""ETF domain models"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ETFInstrument(BaseModel):
    symbol: str = Field(..., description="Ticker / trading symbol")
    name: str = Field(..., description="ETF name")
    asset_class: Optional[str] = None
    market_cap_category: Optional[str] = None
    isin: Optional[str] = Field(None, description="ISIN code if available")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_mongo_document(self):
        doc = self.dict()
        return doc
