"""Pytest configuration and shared fixtures."""

import asyncio
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from typing import Any

from src.models.alert import AlertSeverity
from src.models.impact import MarketImpact, PriceDirection
from src.models.market import Market, MarketData
from src.models.news import NewsArticle
from src.models.opportunity import Opportunity


@pytest.fixture
def sample_news():
    """Sample news article for testing."""
    return NewsArticle(
        url="https://example.com/news/breaking-1",
        title="Breaking News: Major Event Occurred",
        summary="This is a major event that could impact prediction markets.",
        published_date=datetime.utcnow(),
        source="example.com"
    )


@pytest.fixture
def sample_market():
    """Sample market for testing."""
    return Market(
        market_id="market-test-123",
        question="Will the event occur by end of year?",
        description="This market resolves based on whether a specific event occurs.",
        yes_token_id="yes-test-123",
        no_token_id="no-test-123",
        active=True
    )


@pytest.fixture
def sample_market_data(sample_market):
    """Sample market data for testing."""
    return MarketData(
        market_id=sample_market.market_id,
        yes_price=0.55,
        no_price=0.45,
        timestamp=datetime.utcnow()
    )


@pytest.fixture
def sample_impact(sample_news, sample_market):
    """Sample market impact assessment for testing."""
    return MarketImpact(
        id="impact-test-123",
        news_url=sample_news.url,
        market_id=sample_market.market_id,
        relevance=0.8,
        direction=PriceDirection.UP,
        confidence=0.75,
        reasoning="The news suggests a positive outcome for this market",
        expected_magnitude=0.15,
        expected_price=0.70
    )


@pytest.fixture
def sample_opportunity(sample_impact, sample_market):
    """Sample opportunity for testing."""
    return Opportunity(
        id="opp-test-123",
        impact_id=sample_impact.id,
        market_id=sample_market.market_id,
        market_question=sample_market.question,
        current_price=0.55,
        expected_price=0.70,
        discrepancy=0.15,
        potential_profit=0.1125,  # 0.15 * 0.75
        confidence=0.75,
        action="investigate"
    )


@pytest.fixture
def mock_brave_client():
    """Mock Brave Search client."""
    client = MagicMock()
    client.search = AsyncMock(return_value=[
        NewsArticle(
            url="https://example.com/news1",
            title="News Article 1",
            summary="Summary 1"
        ),
        NewsArticle(
            url="https://example.com/news2",
            title="News Article 2",
            summary="Summary 2"
        )
    ])
    return client


@pytest.fixture
def mock_polymarket_client():
    """Mock Polymarket client."""
    client = AsyncMock()

    # Mock get_markets
    client.get_markets = AsyncMock(return_value=[
        Market(
            market_id="market-1",
            question="Test Market 1",
            description="Description 1",
            yes_token_id="yes-1",
            no_token_id="no-1"
        ),
        Market(
            market_id="market-2",
            question="Test Market 2",
            description="Description 2",
            yes_token_id="yes-2",
            no_token_id="no-2"
        )
    ])

    # Mock get_market_data
    client.get_market_data = AsyncMock(return_value=MarketData(
        market_id="market-1",
        yes_price=0.60,
        no_price=0.40
    ))

    return client


@pytest.fixture
def mock_reasoning_client():
    """Mock Reasoning client."""
    client = MagicMock()

    # Mock analyze_impact
    client.analyze_impact = AsyncMock(return_value=MarketImpact(
        id="impact-mock-123",
        news_url="https://example.com/news1",
        market_id="market-1",
        relevance=0.8,
        direction=PriceDirection.UP,
        confidence=0.75,
        reasoning="Mock reasoning",
        expected_magnitude=0.1,
        expected_price=0.7
    ))

    return client


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("LOG_LEVEL", "INFO")
    monkeypatch.setenv("CONFIDENCE_THRESHOLD", "0.7")
    monkeypatch.setenv("MIN_PROFIT_MARGIN", "0.05")
    monkeypatch.setenv("SEARCH_QUERIES", "test query")
