"""
Polymarket Gamma API client for market data.

This module provides an async client for querying market data from Polymarket's Gamma API.
"""

import asyncio
from datetime import datetime
from typing import Any, Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from src.models.market import Market, MarketData
from src.utils.config import settings
from src.utils.logging_config import logger


class PolymarketClientError(Exception):
    """Base exception for Polymarket client errors."""

    pass


class PolymarketGammaClient:
    """
    Client for Polymarket Gamma API with rate limiting and retry logic.

    This client provides async methods to:
    - Fetch active markets
    - Get current prices for tokens
    - Fetch order books
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        requests_per_second: Optional[int] = None
    ):
        """
        Initialize the Polymarket Gamma client.

        Args:
            base_url: Base URL for Gamma API (defaults to settings)
            timeout: Request timeout in seconds (defaults to settings)
            requests_per_second: Rate limit (defaults to settings)
        """
        self.base_url = f"https://{base_url or settings.polymarket_gamma_host}"
        self.timeout = timeout or settings.polymarket_timeout
        self.rate_limit = requests_per_second or settings.polymarket_rate_limit

        # Rate limiting
        self.semaphore = asyncio.Semaphore(self.rate_limit)
        self.request_times: list[float] = []

        # HTTP client
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "User-Agent": "PolymarketArbitrageAgent/0.1.0",
                "Accept": "application/json"
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Make rate-limited HTTP request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            **kwargs: Additional arguments for httpx

        Returns:
            Response JSON as dict

        Raises:
            PolymarketClientError: If request fails after retries
        """
        async with self.semaphore:
            # Enforce rate limit
            now = asyncio.get_event_loop().time()
            self.request_times = [t for t in self.request_times if now - t < 1.0]

            if len(self.request_times) >= self.rate_limit:
                sleep_time = 1.0 - (now - self.request_times[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                self.request_times = []

            self.request_times.append(now)

            # Make request with retry
            try:
                url = f"{endpoint.lstrip('/')}"
                logger.debug("api_request", method=method, endpoint=url, params=params)

                response = await self.client.request(
                    method,
                    url,
                    params=params,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(
                    "http_error",
                    endpoint=endpoint,
                    status=e.response.status_code,
                    response=e.response.text[:200]
                )
                raise PolymarketClientError(f"HTTP {e.response.status_code}: {e.response.text}")

            except httpx.NetworkError as e:
                logger.error("network_error", endpoint=endpoint, error=str(e))
                raise PolymarketClientError(f"Network error: {e}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(PolymarketClientError)
    )
    async def get_markets(
        self,
        active: bool = True,
        limit: int = 100,
        offset: int = 0,
        tag: Optional[str] = None
    ) -> list[Market]:
        """
        Fetch list of markets from Gamma API.

        Args:
            active: Filter for active/inactive markets
            limit: Maximum number of markets to return
            offset: Pagination offset
            tag: Filter by tag

        Returns:
            List of Market objects

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            params = {
                "active": str(active).lower(),
                "limit": min(limit, 100),
                "offset": offset
            }

            if tag:
                params["tag"] = tag

            data = await self._request("GET", "/markets", params=params)

            markets = []
            # Handle both list and dict response formats
            market_list = data if isinstance(data, list) else data.get("data", [])

            for market_data in market_list:
                try:
                    # Extract token IDs from clobTokenIds (JSON array string)
                    clob_tokens_str = market_data.get("clobTokenIds", "[]")
                    try:
                        import json
                        clob_tokens = json.loads(clob_tokens_str)
                        yes_token = clob_tokens[0] if len(clob_tokens) > 0 else ""
                        no_token = clob_tokens[1] if len(clob_tokens) > 1 else ""
                    except (json.JSONDecodeError, IndexError, TypeError):
                        # Fallback to other field names if clobTokenIds fails
                        yes_token = (
                            market_data.get("outcome_token_id_yes") or
                            market_data.get("token_id_yes") or
                            market_data.get("yes_token") or
                            ""
                        )
                        no_token = (
                            market_data.get("outcome_token_id_no") or
                            market_data.get("token_id_no") or
                            market_data.get("no_token") or
                            ""
                        )

                    # Extract prices from outcomePrices if available
                    yes_price_val = None
                    no_price_val = None
                    outcome_prices_str = market_data.get("outcomePrices", "[]")
                    try:
                        outcome_prices = json.loads(outcome_prices_str)
                        yes_price_val = float(outcome_prices[0]) if len(outcome_prices) > 0 and outcome_prices[0] else None
                        no_price_val = float(outcome_prices[1]) if len(outcome_prices) > 1 and outcome_prices[1] else None
                    except (json.JSONDecodeError, IndexError, TypeError, ValueError):
                        pass

                    market = Market(
                        market_id=str(market_data.get("condition_id", market_data.get("id", ""))),
                        question=market_data.get("question", ""),
                        description=market_data.get("description", ""),
                        end_date=self._parse_end_date(market_data),
                        active=market_data.get("active", True),
                        yes_token_id=str(yes_token),
                        no_token_id=str(no_token),
                        yes_price=yes_price_val,
                        no_price=no_price_val,
                        tags=market_data.get("tags", [])
                    )

                    # Only add markets with valid token IDs
                    if market.yes_token_id and market.no_token_id:
                        markets.append(market)
                    else:
                        logger.debug(
                            "skipping_market_no_tokens",
                            market_id=market.market_id,
                            question=market.question[:50]
                        )
                except Exception as e:
                    logger.warning("failed_to_parse_market", market_id=market_data.get("condition_id"), error=str(e))

            logger.info(
                "markets_fetched",
                count=len(markets),
                active=active
            )

            return markets

        except Exception as e:
            logger.error("fetch_markets_error", error=str(e))
            raise

    async def get_market(self, market_id: str) -> Optional[Market]:
        """
        Fetch details for a specific market.

        Args:
            market_id: The market identifier

        Returns:
            Market object or None if not found

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            data = await self._request("GET", f"/markets/{market_id}")

            market_data = data.get("data", {})
            market = Market(
                market_id=str(market_data.get("condition_id", market_id)),
                question=market_data.get("question", ""),
                description=market_data.get("description", ""),
                end_date=self._parse_end_date(market_data),
                active=market_data.get("active", True),
                yes_token_id=str(market_data.get("outcome_token_id_yes", "")),
                no_token_id=str(market_data.get("outcome_token_id_no", "")),
                tags=market_data.get("tags", [])
            )

            return market

        except PolymarketClientError as e:
            if "404" in str(e):
                return None
            raise

    async def get_price(self, token_id: str, side: str = "buy") -> float:
        """
        Fetch current price for a token.

        Args:
            token_id: The token identifier
            side: "buy" or "sell" side

        Returns:
            Current price (0.0-1.0)

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            data = await self._request("GET", f"/price/{token_id}", params={"side": side})
            price = float(data.get("price", 0.0))

            logger.debug(
                "price_fetched",
                token_id=token_id,
                side=side,
                price=price
            )

            return price

        except Exception as e:
            logger.error(
                "fetch_price_error",
                token_id=token_id,
                side=side,
                error=str(e)
            )
            raise

    async def get_market_data(self, market: Market) -> MarketData:
        """
        Fetch current price data for a market.

        Uses prices from market object if available, otherwise fetches from API.

        Args:
            market: Market object

        Returns:
            MarketData with YES and NO prices

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            # Use prices from market object if available
            if market.yes_price is not None and market.no_price is not None:
                yes_price = market.yes_price
                no_price = market.no_price

                logger.debug(
                    "market_data_from_cache",
                    market_id=market.market_id,
                    yes_price=yes_price,
                    no_price=no_price
                )
            else:
                # Fallback to fetching prices via API
                yes_price = await self.get_price(market.yes_token_id, "buy")
                no_price = await self.get_price(market.no_token_id, "buy")

                logger.debug(
                    "market_data_fetched_api",
                    market_id=market.market_id,
                    yes_price=yes_price,
                    no_price=no_price
                )

            # Normalize prices (YES + NO should equal ~1.0)
            total = yes_price + no_price
            if total > 0:
                yes_price = yes_price / total
                no_price = no_price / total

            market_data = MarketData(
                market_id=market.market_id,
                yes_price=yes_price,
                no_price=no_price,
                timestamp=datetime.utcnow()
            )

            return market_data

        except Exception as e:
            logger.error(
                "fetch_market_data_error",
                market_id=market.market_id,
                error=str(e)
            )
            raise

    async def get_order_book(self, token_id: str) -> dict[str, list]:
        """
        Fetch order book for a token.

        Args:
            token_id: The token identifier

        Returns:
            Dictionary with 'bids' and 'asks' lists

        Raises:
            PolymarketClientError: If API request fails
        """
        try:
            data = await self._request("GET", f"/book/{token_id}")

            return {
                "bids": data.get("bids", []),
                "asks": data.get("asks", [])
            }

        except Exception as e:
            logger.error(
                "fetch_order_book_error",
                token_id=token_id,
                error=str(e)
            )
            raise

    def _parse_end_date(self, market_data: dict[str, Any]) -> Optional[datetime]:
        """Parse end date from market data."""
        end_timestamp = market_data.get("end_date")
        if end_timestamp:
            try:
                # Convert milliseconds to seconds if needed
                if end_timestamp > 1000000000000:  # Milliseconds
                    end_timestamp = end_timestamp / 1000
                return datetime.fromtimestamp(end_timestamp)
            except (ValueError, OSError):
                return None
        return None
