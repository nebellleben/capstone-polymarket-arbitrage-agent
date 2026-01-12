"""Integration tests for the main workflow."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from src.workflows.mvp_workflow import ArbitrageDetectionGraph


@pytest.mark.asyncio
async def test_workflow_full_cycle(mock_env_vars):
    """Test a complete detection cycle with mocked components."""
    # Create workflow
    graph = ArbitrageDetectionGraph()

    # Mock the components
    with patch.object(graph.news_client, 'search', new_callable=AsyncMock) as mock_search, \
         patch.object(graph.polymarket_client, 'get_markets', new_callable=AsyncMock) as mock_get_markets, \
         patch.object(graph.polymarket_client, 'get_market_data', new_callable=AsyncMock) as mock_get_data, \
         patch.object(graph.reasoning_client, 'analyze_impact', new_callable=AsyncMock) as mock_analyze:

        # Set up mock returns
        from src.models.news import NewsArticle
        from src.models.market import Market, MarketData
        from src.models.impact import MarketImpact, PriceDirection

        mock_search.return_value = [
            NewsArticle(
                url="https://example.com/news1",
                title="Breaking News",
                summary="Important event occurred"
            )
        ]

        market = Market(
            market_id="market-1",
            question="Test Question",
            description="Test Description",
            yes_token_id="yes-1",
            no_token_id="no-1"
        )

        mock_get_markets.return_value = [market]
        mock_get_data.return_value = MarketData(
            market_id="market-1",
            yes_price=0.5,
            no_price=0.5
        )

        mock_analyze.return_value = MarketImpact(
            id="impact-1",
            news_url="https://example.com/news1",
            market_id="market-1",
            relevance=0.8,
            direction=PriceDirection.UP,
            confidence=0.75,
            reasoning="Test reasoning",
            expected_magnitude=0.2,
            expected_price=0.7
        )

        # Run cycle
        result = await graph.run_cycle(search_query="test query")

        # Verify results
        assert len(result["news_articles"]) == 1
        assert len(result["markets"]) == 1
        assert len(result["market_impacts"]) == 1
        assert result["cycle_end_time"] is not None

        # Verify opportunities were detected
        assert len(result["opportunities"]) > 0

        # Verify alerts were generated
        assert len(result["alerts"]) > 0


@pytest.mark.asyncio
async def test_workflow_with_no_opportunities(mock_env_vars):
    """Test workflow when no opportunities are detected."""
    graph = ArbitrageDetectionGraph()

    with patch.object(graph.news_client, 'search', new_callable=AsyncMock) as mock_search, \
         patch.object(graph.polymarket_client, 'get_markets', new_callable=AsyncMock) as mock_get_markets, \
         patch.object(graph.polymarket_client, 'get_market_data', new_callable=AsyncMock) as mock_get_data, \
         patch.object(graph.reasoning_client, 'analyze_impact', new_callable=AsyncMock) as mock_analyze:

        from src.models.news import NewsArticle
        from src.models.market import Market, MarketData
        from src.models.impact import MarketImpact, PriceDirection

        mock_search.return_value = [
            NewsArticle(
                url="https://example.com/news1",
                title="Irrelevant News",
                summary="Not relevant to markets"
            )
        ]

        market = Market(
            market_id="market-1",
            question="Test Question",
            description="Test Description",
            yes_token_id="yes-1",
            no_token_id="no-1"
        )

        mock_get_markets.return_value = [market]
        mock_get_data.return_value = MarketData(
            market_id="market-1",
            yes_price=0.5,
            no_price=0.5
        )

        # Low relevance, low confidence - should not generate opportunities
        mock_analyze.return_value = MarketImpact(
            id="impact-1",
            news_url="https://example.com/news1",
            market_id="market-1",
            relevance=0.3,  # Below threshold
            direction=PriceDirection.NEUTRAL,
            confidence=0.4,  # Below threshold
            reasoning="Not significant",
            expected_magnitude=0.0,
            expected_price=0.5
        )

        result = await graph.run_cycle(search_query="test")

        # Should have impacts but no opportunities
        assert len(result["market_impacts"]) == 1
        assert len(result["opportunities"]) == 0
        assert len(result["alerts"]) == 0


@pytest.mark.asyncio
async def test_workflow_error_handling(mock_env_vars):
    """Test workflow handles API errors gracefully."""
    graph = ArbitrageDetectionGraph()

    with patch.object(graph.news_client, 'search', new_callable=AsyncMock) as mock_search, \
         patch.object(graph.polymarket_client, 'get_markets', new_callable=AsyncMock) as mock_get_markets:

        # Simulate API failure
        mock_search.side_effect = Exception("API Error")
        mock_get_markets.side_effect = Exception("Market API Error")

        result = await graph.run_cycle(search_query="test")

        # Should have errors but not crash
        assert len(result["errors"]) > 0
        assert "API Error" in result["errors"][0] or "Market API Error" in result["errors"][1]


@pytest.mark.asyncio
async def test_detect_opportunities_logic(sample_impact, sample_market_data):
    """Test the opportunity detection logic."""
    from src.agents.arbitrage_detector import ArbitrageDetector

    detector = ArbitrageDetector(
        confidence_threshold=0.7,
        min_profit_margin=0.05
    )

    opportunities = detector.detect_opportunities(
        impacts=[sample_impact],
        market_data_map={sample_impact.market_id: sample_market_data}
    )

    assert len(opportunities) > 0
    opp = opportunities[0]
    assert opp.market_id == sample_impact.market_id
    assert opp.current_price == sample_market_data.yes_price
    assert opp.expected_price == sample_impact.expected_price
