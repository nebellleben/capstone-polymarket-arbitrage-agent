"""Market impact assessment model."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from pydantic import HttpUrl


class PriceDirection(str, Enum):
    """Expected price direction."""

    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"


class MarketImpact(BaseModel):
    """Assessment of news impact on a market."""

    # Identification
    id: str = Field(..., description="Unique impact identifier")
    news_url: HttpUrl = Field(..., description="Related news article")
    market_id: str = Field(..., description="Affected market")

    # AI reasoning results
    relevance: float = Field(
        ..., ge=0.0, le=1.0, description="Relevance score (0-1)"
    )
    direction: PriceDirection = Field(..., description="Expected price direction")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in assessment (0-1)"
    )
    reasoning: str = Field(
        ..., min_length=10, max_length=1000, description="Explanation of the impact"
    )

    # Expected price change
    expected_magnitude: float = Field(
        ..., ge=0.0, le=1.0, description="Expected price change magnitude"
    )
    expected_price: float = Field(
        ..., ge=0.0, le=1.0, description="Expected new price after impact"
    )

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    model: str = Field(default="sequential_thinking_mcp", description="Model used for assessment")

    @property
    def is_significant(self) -> bool:
        """Whether impact is significant (relevance > 0.1 for MVP)."""
        return self.relevance > 0.1

    @property
    def is_high_confidence(self) -> bool:
        """Whether assessment is high confidence (>= 0.7)."""
        return self.confidence >= 0.7

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        use_enum_values = True
