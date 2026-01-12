"""
SQLAlchemy ORM models for arbitrage detection system.

This module defines the database schema for storing alerts and
cycle metrics with proper indexing for performance.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""


class Alert(Base):
    """
    Database model for arbitrage alerts.

    Represents a detected arbitrage opportunity with full details
    about the news, market, and pricing information.
    """

    __tablename__ = "alerts"

    # Primary key
    id: Mapped[str] = mapped_column(String(100), primary_key=True)

    # Opportunity reference
    opportunity_id: Mapped[str] = mapped_column(String(100), index=True)

    # Severity and classification
    severity: Mapped[str] = mapped_column(String(20), index=True)
    title: Mapped[str] = mapped_column(String(500))
    message: Mapped[str] = mapped_column(Text)

    # News information
    news_url: Mapped[str] = mapped_column(String(1000), index=True)
    news_title: Mapped[str] = mapped_column(String(500))

    # Market information
    market_id: Mapped[str] = mapped_column(String(100), index=True)
    market_question: Mapped[str] = mapped_column(Text)

    # AI reasoning
    reasoning: Mapped[str] = mapped_column(Text)

    # Pricing details
    confidence: Mapped[float] = mapped_column(Float, index=True)
    current_price: Mapped[float] = mapped_column(Float)
    expected_price: Mapped[float] = mapped_column(Float)
    discrepancy: Mapped[float] = mapped_column(Float)

    # Recommended action
    recommended_action: Mapped[str] = mapped_column(String(50))

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, index=True)

    # Indexes for common queries
    __table_args__ = (
        Index("idx_alerts_timestamp_desc", Alert.timestamp.desc()),
        Index("idx_alerts_severity_timestamp", Alert.severity, Alert.timestamp.desc()),
        Index("idx_alerts_confidence_timestamp", Alert.confidence, Alert.timestamp.desc()),
    )

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, severity={self.severity}, timestamp={self.timestamp})>"


class CycleMetric(Base):
    """
    Database model for detection cycle metrics.

    Stores performance data for each detection cycle including
    API calls, opportunities found, and timing information.
    """

    __tablename__ = "cycle_metrics"

    # Primary key
    cycle_id: Mapped[str] = mapped_column(String(100), primary_key=True)

    # Timing
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    duration_seconds: Mapped[float] = mapped_column(Float)

    # News data
    news_articles_fetched: Mapped[int] = mapped_column(Integer)
    news_articles_new: Mapped[int] = mapped_column(Integer)

    # Market data
    markets_fetched: Mapped[int] = mapped_column(Integer)
    markets_with_prices: Mapped[int] = mapped_column(Integer)

    # Analysis results
    impacts_analyzed: Mapped[int] = mapped_column(Integer)
    impacts_significant: Mapped[int] = mapped_column(Integer)

    reasoning_time_total: Mapped[float] = mapped_column(Float)

    # Opportunities and alerts
    opportunities_detected: Mapped[int] = mapped_column(Integer, index=True)
    opportunities_high_confidence: Mapped[int] = mapped_column(Integer)

    alerts_generated: Mapped[int] = mapped_column(Integer)

    # API calls (stored as JSON string)
    api_calls_json: Mapped[str] = mapped_column(Text)

    # Errors
    error_count: Mapped[int] = mapped_column(Integer)

    # Rates
    news_to_alert_rate: Mapped[float] = mapped_column(Float)
    opportunity_detection_rate: Mapped[float] = mapped_column(Float)

    # Indexes for common queries
    __table_args__ = (
        Index("idx_cycles_start_time_desc", CycleMetric.start_time.desc()),
        Index("idx_cycles_opportunities", CycleMetric.opportunities_detected),
    )

    def __repr__(self) -> str:
        return f"<CycleMetric(cycle_id={self.cycle_id}, start_time={self.start_time}, opportunities={self.opportunities_detected})>"
