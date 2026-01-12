"""Unit tests for data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.news import NewsArticle
from src.models.market import Market, MarketData
from src.models.impact import MarketImpact, PriceDirection
from src.models.opportunity import Opportunity
from src.models.alert import Alert, AlertSeverity


class TestNewsArticle:
    """Tests for NewsArticle model."""

    def test_create_news_article(self):
        """Test creating a valid news article."""
        article = NewsArticle(
            url="https://example.com/news1",
            title="Breaking News",
            summary="This is a summary"
        )

        assert article.title == "Breaking News"
        assert article.summary == "This is a summary"
        assert article.url == "https://example.com/news1"
        assert article.processed is False
        assert isinstance(article.fetched_at, datetime)

    def test_news_article_deduplication(self):
        """Test news article deduplication by URL."""
        article1 = NewsArticle(
            url="https://example.com/news1",
            title="Title 1",
            summary="Summary 1"
        )
        article2 = NewsArticle(
            url="https://example.com/news1",
            title="Title 2",
            summary="Summary 2"
        )

        # Same URL means same article
        assert article1 == article2
        assert hash(article1) == hash(article2)

    def test_news_article_validation(self):
        """Test validation of news article fields."""
        with pytest.raises(ValidationError):
            NewsArticle(
                url="not-a-url",
                title="",
                summary="Summary"
            )


class TestMarket:
    """Tests for Market model."""

    def test_create_market(self):
        """Test creating a valid market."""
        market = Market(
            market_id="market-123",
            question="Will it rain tomorrow?",
            description="Weather prediction market",
            yes_token_id="yes-123",
            no_token_id="no-123"
        )

        assert market.market_id == "market-123"
        assert market.question == "Will it rain tomorrow?"
        assert market.active is True
        assert market.tags == []

    def test_market_data(self):
        """Test market data model."""
        data = MarketData(
            market_id="market-123",
            yes_price=0.65,
            no_price=0.35
        )

        assert data.yes_price == 0.65
        assert data.no_price == 0.35
        assert data.implied_probability == 0.65
        assert data.spread == 0.0


class TestMarketImpact:
    """Tests for MarketImpact model."""

    def test_create_impact(self):
        """Test creating a market impact assessment."""
        impact = MarketImpact(
            id="impact-123",
            news_url="https://example.com/news1",
            market_id="market-123",
            relevance=0.8,
            direction=PriceDirection.UP,
            confidence=0.75,
            reasoning="News suggests positive outcome",
            expected_magnitude=0.1,
            expected_price=0.7
        )

        assert impact.relevance == 0.8
        assert impact.direction == PriceDirection.UP
        assert impact.confidence == 0.75
        assert impact.is_significant is True
        assert impact.is_high_confidence is True

    def test_insufficient_relevance(self):
        """Test impact with low relevance."""
        impact = MarketImpact(
            id="impact-123",
            news_url="https://example.com/news1",
            market_id="market-123",
            relevance=0.3,
            direction=PriceDirection.NEUTRAL,
            confidence=0.8,
            reasoning="Low relevance",
            expected_magnitude=0.0,
            expected_price=0.5
        )

        assert impact.is_significant is False


class TestOpportunity:
    """Tests for Opportunity model."""

    def test_create_opportunity(self):
        """Test creating an arbitrage opportunity."""
        opp = Opportunity(
            id="opp-123",
            impact_id="impact-123",
            market_id="market-123",
            market_question="Test question",
            current_price=0.5,
            expected_price=0.65,
            discrepancy=0.15,
            potential_profit=0.10,
            confidence=0.75,
            action="investigate"
        )

        assert opp.discrepancy == 0.15
        assert opp.potential_profit == 0.10
        assert opp.is_profitable(min_profit_margin=0.05) is True
        assert opp.is_high_confidence is True

    def test_opportunity_not_profitable(self):
        """Test opportunity below profit threshold."""
        opp = Opportunity(
            id="opp-123",
            impact_id="impact-123",
            market_id="market-123",
            market_question="Test question",
            current_price=0.5,
            expected_price=0.52,
            discrepancy=0.02,
            potential_profit=0.01,
            confidence=0.7,
            action="watch"
        )

        assert opp.is_profitable(min_profit_margin=0.05) is False


class TestAlert:
    """Tests for Alert model."""

    def test_create_alert(self):
        """Test creating an alert."""
        alert = Alert(
            id="alert-123",
            opportunity_id="opp-123",
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            message="Test message",
            news_url="https://example.com/news1",
            news_title="Test News",
            market_id="market-123",
            market_question="Test question",
            reasoning="Test reasoning",
            confidence=0.75,
            current_price=0.5,
            expected_price=0.65,
            discrepancy=0.15,
            recommended_action="investigate"
        )

        assert alert.severity == AlertSeverity.WARNING
        assert alert.confidence == 0.75
        assert alert.discrepancy == 0.15
