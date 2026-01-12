"""Market and market data models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Market(BaseModel):
    """Polymarket prediction market."""

    # Identification
    market_id: str = Field(..., description="Unique market identifier")
    question: str = Field(..., description="Market question")
    description: str = Field(..., description="Detailed market description")

    # Metadata
    end_date: Optional[datetime] = Field(None, description="Market resolution date")
    active: bool = Field(True, description="Whether market is active")

    # Token IDs
    yes_token_id: str = Field(..., description="YES token ID")
    no_token_id: str = Field(..., description="NO token ID")

    # Categories (for filtering)
    tags: list[str] = Field(default_factory=list, description="Market category tags")

    # Cache metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class MarketData(BaseModel):
    """Current price data for a market."""

    # Identification
    market_id: str = Field(..., description="Market identifier")

    # Prices
    yes_price: float = Field(..., ge=0.0, le=1.0, description="Current YES price")
    no_price: float = Field(..., ge=0.0, le=1.0, description="Current NO price")

    # Spread
    bid_price: Optional[float] = Field(None, ge=0.0, le=1.0, description="Highest bid price")
    ask_price: Optional[float] = Field(None, ge=0.0, le=1.0, description="Lowest ask price")

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(default="polymarket_gamma", description="Data source")

    @property
    def spread(self) -> float:
        """Calculate bid-ask spread."""
        if self.bid_price is not None and self.ask_price is not None:
            return self.ask_price - self.bid_price
        return 0.0

    @property
    def implied_probability(self) -> float:
        """Calculate implied probability from yes price."""
        return self.yes_price

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
