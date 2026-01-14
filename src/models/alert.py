"""Alert model."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl

from src.models.news import NewsArticle
from src.models.opportunity import Opportunity
from src.models.market import Market


class AlertSeverity(str, Enum):
    """Alert severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class Alert(BaseModel):
    """Alert generated for an opportunity."""

    # Identification
    id: str = Field(..., description="Unique alert identifier")
    opportunity_id: str = Field(..., description="Related opportunity")

    # Severity
    severity: AlertSeverity = Field(..., description="Alert severity")

    # Content
    title: str = Field(..., min_length=1, max_length=200, description="Alert title")
    message: str = Field(..., min_length=1, max_length=2000, description="Alert message")

    # Detailed information
    news_url: HttpUrl = Field(..., description="Related news article")
    news_title: str = Field(..., description="News article title")

    market_id: str = Field(..., description="Affected market")
    market_question: str = Field(..., description="Market question")

    # Reasoning
    reasoning: str = Field(..., description="AI reasoning for impact")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level")

    # Price details
    current_price: float = Field(..., ge=0.0, le=1.0, description="Current price")
    expected_price: float = Field(..., ge=0.0, le=1.0, description="Expected price")
    discrepancy: float = Field(..., ge=0.0, le=1.0, description="Price discrepancy")

    # Action
    recommended_action: str = Field(..., description="Recommended action")

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_opportunity(
        cls,
        opportunity: Opportunity,
        news: NewsArticle,
        market: Market,
        reasoning: str
    ) -> "Alert":
        """Create alert from opportunity."""
        # Determine severity based on profit margin (MVP thresholds)
        # For MVP with fallback reasoning (confidence ~0.4), prioritize profit over confidence
        if opportunity.potential_profit >= 0.15:  # 15%+ profit = CRITICAL
            severity = AlertSeverity.CRITICAL
        elif opportunity.potential_profit >= 0.05:  # 5%+ profit = WARNING
            severity = AlertSeverity.WARNING
        else:  # Below 5% profit = INFO
            severity = AlertSeverity.INFO

        direction_str = "up" if opportunity.expected_price > opportunity.current_price else "down"

        return cls(
            id=f"alert-{datetime.utcnow().timestamp()}",
            opportunity_id=opportunity.id,
            severity=severity,
            title=f"Arbitrage opportunity: {market.question[:80]}...",
            message=f"News '{news.title}' suggests price should move {direction_str} from {opportunity.current_price:.2f} to {opportunity.expected_price:.2f} (discrepancy: {opportunity.discrepancy:.2%})",
            news_url=news.url,
            news_title=news.title,
            market_id=market.market_id,
            market_question=market.question,
            reasoning=reasoning,
            confidence=opportunity.confidence,
            current_price=opportunity.current_price,
            expected_price=opportunity.expected_price,
            discrepancy=opportunity.discrepancy,
            recommended_action=opportunity.action
        )

    class Config:
        """Pydantic config."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        use_enum_values = True
