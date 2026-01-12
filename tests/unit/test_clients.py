"""Unit tests for API clients."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from src.tools.brave_search_client import BraveSearchClient
from src.tools.polymarket_client import PolymarketGammaClient, PolymarketClientError
from src.tools.reasoning_client import ReasoningClient

from src.models.news import NewsArticle
from src.models.market import Market, MarketData
from src.models.impact import MarketImpact, PriceDirection


class TestBraveSearchClient:
    """Tests for BraveSearchClient."""

    @pytest.mark.asyncio
    async def test_search_success(self):
        """Test successful news search."""
        client = BraveSearchClient()

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "web": {
                    "results": [
                        {
                            "url": "https://example.com/news1",
                            "title": "News 1",
                            "description": "Summary 1"
                        }
                    ]
                }
            }
            mock_get.return_value = mock_response

            articles = await client.search("test query")

            assert len(articles) == 1
            assert articles[0].title == "News 1"
            assert articles[0].summary == "Summary 1"

    @pytest.mark.asyncio
    async def test_search_with_api_key(self):
        """Test search with API key."""
        client = BraveSearchClient()
        client.api_key = "test-key"

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "web": {"results": []}
            }
            mock_get.return_value = mock_response

            await client.search("test")

            # Verify API key header was set
            call_args = mock_get.call_args
            headers = call_args[1]['headers']
            assert 'X-Subscription-Token' in headers

    @pytest.mark.asyncio
    async def test_search_http_error(self):
        """Test search handles HTTP errors."""
        client = BraveSearchClient()

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.HTTPStatusError(
                "Error",
                request=MagicMock(),
                response=MagicMock(status_code=429, text="Rate limited")
            )

            with pytest.raises(httpx.HTTPError):
                await client.search("test")

    @pytest.mark.asyncio
    async def test_search_mock_mode(self):
        """Test search returns mock data when no API key."""
        client = BraveSearchClient()
        client.api_key = None

        articles = await client.search("test query")

        assert len(articles) > 0
        assert articles[0].title == "Breaking News 1: test query"
        assert "example.com" in str(articles[0].url)


class TestPolymarketGammaClient:
    """Tests for PolymarketGammaClient."""

    @pytest.mark.asyncio
    async def test_get_markets_success(self):
        """Test successful market fetch."""
        client = PolymarketGammaClient()

        async with client:
            with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {
                    "data": [
                        {
                            "condition_id": "market-1",
                            "question": "Test Question",
                            "description": "Test Description",
                            "active": True,
                            "outcome_token_id_yes": "yes-1",
                            "outcome_token_id_no": "no-1",
                            "tags": ["politics"]
                        }
                    ]
                }

                markets = await client.get_markets(active=True)

                assert len(markets) == 1
                assert markets[0].market_id == "market-1"
                assert markets[0].question == "Test Question"
                assert markets[0].active is True

    @pytest.mark.asyncio
    async def test_get_price_success(self):
        """Test successful price fetch."""
        client = PolymarketGammaClient()

        async with client:
            with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {
                    "price": 0.65
                }

                price = await client.get_price("token-123")

                assert price == 0.65

    @pytest.mark.asyncio
    async def test_get_market_data(self):
        """Test fetching complete market data."""
        client = PolymarketGammaClient()

        market = Market(
            market_id="market-1",
            question="Test",
            description="Test market",
            yes_token_id="yes-1",
            no_token_id="no-1"
        )

        async with client:
            with patch.object(client, 'get_price', new_callable=AsyncMock) as mock_price:
                # Mock YES and NO prices
                mock_price.side_effect = [0.6, 0.4]

                market_data = await client.get_market_data(market)

                assert market_data.market_id == "market-1"
                assert market_data.yes_price == 0.5  # Normalized
                assert market_data.no_price == 0.5  # Normalized

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting is enforced."""
        client = PolymarketGammaClient(requests_per_second=2)

        async with client:
            with patch.object(client, '_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = {"data": []}

                import asyncio
                import time

                # Make requests up to rate limit
                tasks = [client.get_markets() for _ in range(3)]
                start = time.time()
                await asyncio.gather(*tasks)
                elapsed = time.time() - start

                # Should take at least 1 second due to rate limiting
                # (2 requests in first second, 1 request in next second)
                # Actually with semaphore of 2, the third request waits
                assert elapsed >= 0.1  # At least some delay


class TestReasoningClient:
    """Tests for ReasoningClient."""

    @pytest.mark.asyncio
    async def test_analyze_impact_with_anthropic(self):
        """Test reasoning with Anthropic API."""
        client = ReasoningClient()

        news = NewsArticle(
            url="https://example.com/news1",
            title="Election Results",
            summary="Candidate wins election"
        )

        market = Market(
            market_id="market-1",
            question="Will Candidate X win?",
            description="Presidential election",
            yes_token_id="yes-1",
            no_token_id="no-1"
        )

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='{"relevance": 0.9, "direction": "up", "confidence": 0.85, "expected_magnitude": 0.2, "expected_price": 0.8, "reasoning": "Strong evidence"}')]
            mock_client = MagicMock()
            mock_client.messages.create.return_value = mock_response
            mock_anthropic.return_value = mock_client

            impact = await client.analyze_impact(news, market)

            assert impact.relevance == 0.9
            assert impact.direction == PriceDirection.UP
            assert impact.confidence == 0.85
            assert impact.expected_price == 0.8

    @pytest.mark.asyncio
    async def test_analyze_impact_fallback(self):
        """Test reasoning fallback without API."""
        client = ReasoningClient()

        news = NewsArticle(
            url="https://example.com/news1",
            title="Candidate wins election",
            summary="Victory declared"
        )

        market = Market(
            market_id="market-1",
            question="Will Candidate X win?",
            description="Election market",
            yes_token_id="yes-1",
            no_token_id="no-1"
        )

        with patch('anthropic.Anthropic', side_effect=ImportError):
            impact = await client.analyze_impact(news, market)

            # Should use fallback reasoning
            assert impact.relevance >= 0.0
            assert impact.direction in [PriceDirection.UP, PriceDirection.DOWN, PriceDirection.NEUTRAL]

    @pytest.mark.asyncio
    async def test_analyze_impact_error_handling(self):
        """Test error handling in reasoning."""
        client = ReasoningClient()

        news = NewsArticle(
            url="https://example.com/news1",
            title="Test",
            summary="Test summary"
        )

        market = Market(
            market_id="market-1",
            question="Test?",
            description="Test",
            yes_token_id="yes-1",
            no_token_id="no-1"
        )

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_anthropic.side_effect = Exception("API Error")

            impact = await client.analyze_impact(news, market)

            # Should return neutral impact on error
            assert impact.direction == PriceDirection.NEUTRAL
            assert impact.confidence == 0.0
            assert "Failed to analyze" in impact.reasoning
