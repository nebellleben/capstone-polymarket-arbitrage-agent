"""Workflow state model."""

from datetime import datetime
from typing import Annotated, TypedDict

import operator

from src.models.news import NewsArticle
from src.models.market import Market, MarketData
from src.models.impact import MarketImpact
from src.models.opportunity import Opportunity
from src.models.alert import Alert


class ArbitrageState(TypedDict):
    """State for the arbitrage detection workflow."""

    # Configuration (input)
    search_query: str
    confidence_threshold: float
    min_profit_margin: float

    # Data collected
    news_articles: list[NewsArticle]
    markets: list[Market]
    market_data: dict[str, MarketData]  # market_id -> MarketData
    market_impacts: list[MarketImpact]

    # Results
    opportunities: list[Opportunity]
    alerts: list[Alert]

    # Metadata
    cycle_start_time: datetime
    cycle_end_time: datetime | None
    errors: list[str]
    messages: Annotated[list[dict], operator.add]  # Accumulated messages
