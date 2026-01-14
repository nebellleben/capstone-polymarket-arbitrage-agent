"""Arbitrage opportunity model."""

from datetime import datetime

from pydantic import BaseModel, Field


class Opportunity(BaseModel):
    """Arbitrage opportunity detected."""

    # Identification
    id: str = Field(..., description="Unique opportunity identifier")
    impact_id: str = Field(..., description="Related impact assessment")

    # Market information
    market_id: str = Field(..., description="Affected market")
    market_question: str = Field(..., description="Market question")

    # Price information
    current_price: float = Field(..., ge=0.0, le=1.0, description="Current market price")
    expected_price: float = Field(..., ge=0.0, le=1.0, description="Expected price after impact")
    discrepancy: float = Field(..., ge=0.0, le=1.0, description="Price difference")

    # Profitability
    potential_profit: float = Field(..., ge=0.0, description="Expected profit %")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Assessment confidence")

    # Action recommendation
    action: str = Field(
        ...,
        description="Recommended action: 'watch', 'monitor', 'investigate'",
    )

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime | None = Field(None, description="When opportunity expires")

    def is_profitable(self, min_profit_margin: float = 0.05) -> bool:
        """Whether opportunity meets minimum profit threshold."""
        return self.potential_profit >= min_profit_margin

    @property
    def is_high_confidence(self) -> bool:
        """Whether opportunity is high confidence."""
        return self.confidence >= 0.7

    @property
    def age_seconds(self) -> float:
        """Age of opportunity in seconds."""
        return (datetime.utcnow() - self.timestamp).total_seconds()

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
