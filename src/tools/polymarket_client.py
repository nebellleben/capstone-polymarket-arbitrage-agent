"""
Polymarket API client for interacting with Gamma and CLOB APIs.

This module provides a unified interface for querying market data and executing trades.
"""

import os
from typing import Any
import logging

import httpx
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class PolymarketClientError(Exception):
    """Base exception for Polymarket client errors."""

    pass


class MarketData(BaseModel):
    """Market data model."""

    market_id: str
    question: str
    description: str
    end_date: str | None
    active: bool


class PriceData(BaseModel):
    """Price data model."""

    token_id: str
    price: float
    side: str  # "buy" or "sell"


class OrderBook(BaseModel):
    """Order book data model."""

    token_id: str
    bids: list[dict]
    asks: list[dict]


class PolymarketClient:
    """
    Client for interacting with Polymarket APIs.

    This client provides methods to:
    - Query market data from Gamma API
    - Fetch current prices and order books
    - Execute trades via CLOB API
    """

    def __init__(self):
        """Initialize the Polymarket client."""
        self.gamma_host = os.getenv(
            "POLYMARKET_GAMMA_HOST", "gamma-api.polymarket.com"
        )
        self.clob_host = os.getenv("POLYMARKET_CLOB_HOST", "api.polymarket.com")
        self.api_key = os.getenv("POLYMARKET_API_KEY", "")
        self.secret_key = os.getenv("POLYMARKET_SECRET_KEY", "")

        self.http_client = httpx.AsyncClient(
            base_url=f"https://{self.gamma_host}",
            headers={
                "User-Agent": "PolymarketArbitrageAgent/0.1.0",
            },
        )

    async def get_markets(
        self,
        active: bool = True,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MarketData]:
        """
        Fetch list of markets from Gamma API.

        Args:
            active: Filter for active/inactive markets
            limit: Maximum number of markets to return
            offset: Pagination offset

        Returns:
            List of market data objects

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            params = {
                "active": active,
                "limit": limit,
                "offset": offset,
            }

            response = await self.http_client.get("/markets", params=params)
            response.raise_for_status()

            data = response.json()
            return [MarketData(**market) for market in data.get("data", [])]

        except httpx.HTTPError as e:
            logger.error(f"Error fetching markets: {e}")
            raise PolymarketClientError(f"Failed to fetch markets: {e}")

    async def get_market(self, market_id: str) -> MarketData:
        """
        Fetch details for a specific market.

        Args:
            market_id: The market identifier

        Returns:
            Market data object

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            response = await self.http_client.get(f"/markets/{market_id}")
            response.raise_for_status()

            data = response.json()
            return MarketData(**data["data"])

        except httpx.HTTPError as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            raise PolymarketClientError(f"Failed to fetch market: {e}")

    async def get_price(self, token_id: str, side: str = "buy") -> PriceData:
        """
        Fetch current price for a token.

        Args:
            token_id: The token identifier
            side: "buy" or "sell" side

        Returns:
            Price data object

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            params = {"side": side}
            response = await self.http_client.get(f"/price/{token_id}", params=params)
            response.raise_for_status()

            data = response.json()
            return PriceData(
                token_id=token_id,
                price=data["price"],
                side=side,
            )

        except httpx.HTTPError as e:
            logger.error(f"Error fetching price for {token_id}: {e}")
            raise PolymarketClientError(f"Failed to fetch price: {e}")

    async def get_order_book(self, token_id: str) -> OrderBook:
        """
        Fetch order book for a token.

        Args:
            token_id: The token identifier

        Returns:
            Order book data object

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            response = await self.http_client.get(f"/book/{token_id}")
            response.raise_for_status()

            data = response.json()
            return OrderBook(
                token_id=token_id,
                bids=data.get("bids", []),
                asks=data.get("asks", []),
            )

        except httpx.HTTPError as e:
            logger.error(f"Error fetching order book for {token_id}: {e}")
            raise PolymarketClientError(f"Failed to fetch order book: {e}")

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
