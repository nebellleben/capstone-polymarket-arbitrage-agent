"""Brave Search MCP client for news monitoring."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Optional

import httpx

from src.models.news import NewsArticle
from src.utils.config import settings

logger = logging.getLogger(__name__)


class BraveSearchClient:
    """Client for Brave Search MCP integration."""

    def __init__(self):
        """Initialize the Brave Search client."""
        self.api_key = settings.brave_api_key
        self.timeout = settings.brave_search_timeout
        self.base_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(
        self,
        query: str,
        count: int = 10,
        freshness: str = "pd",
        offset: int = 0
    ) -> list[NewsArticle]:
        """
        Search for news using Brave Search API.

        Args:
            query: Search query string
            count: Number of results (1-50)
            freshness: Time filter - "pd" (day), "pw" (week), "pm" (month)
            offset: Pagination offset

        Returns:
            List of NewsArticle objects

        Raises:
            httpx.HTTPError: If API call fails
        """
        if not self.api_key:
            logger.warning("brave_api_key not set, returning mock data")
            return self._mock_news(query, count)

        try:
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }

            params = {
                "q": query,
                "count": min(count, 50),
                "text_decorations": False,
                "search_lang": "en",
                "result_filter": "news,web",
                "freshness": freshness,
                "offset": offset
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info("brave_search_request", query=query, count=count)
                response = await client.get(self.base_url, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()
                articles = self._parse_response(data)

                logger.info(
                    "brave_search_success",
                    query=query,
                    results=len(articles)
                )

                return articles

        except httpx.HTTPStatusError as e:
            logger.error(
                "brave_search_http_error",
                query=query,
                status=e.response.status_code,
                response=e.response.text
            )
            raise

        except Exception as e:
            logger.error(
                "brave_search_error",
                query=query,
                error=str(e),
                error_type=type(e).__name__
            )
            raise

    def _parse_response(self, data: dict[str, Any]) -> list[NewsArticle]:
        """Parse Brave Search API response into NewsArticle objects."""
        articles = []

        # Parse web results
        web_results = data.get("web", {}).get("results", [])
        for result in web_results:
            try:
                article = NewsArticle(
                    url=result.get("url", ""),
                    title=result.get("title", ""),
                    summary=result.get("description", ""),
                    source=self._extract_source(result.get("url", "")),
                )
                articles.append(article)
            except Exception as e:
                logger.warning("failed_to_parse_web_result", error=str(e))

        # Parse news results if available
        news_results = data.get("news", {}).get("results", [])
        for result in news_results:
            try:
                article = NewsArticle(
                    url=result.get("url", ""),
                    title=result.get("title", ""),
                    summary=result.get("description", ""),
                    published_date=self._parse_news_age(result.get("age")),
                    source=self._extract_source(result.get("url", "")),
                )
                articles.append(article)
            except Exception as e:
                logger.warning("failed_to_parse_news_result", error=str(e))

        return articles

    def _extract_source(self, url: str) -> str:
        """Extract source hostname from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or "unknown"
        except Exception:
            return "unknown"

    def _parse_news_age(self, age_str: Optional[str]) -> Optional[datetime]:
        """Parse Brave Search age string to datetime."""
        if not age_str:
            return None

        # Parse strings like "2h ago", "1d ago", "1w ago"
        try:
            age_str = age_str.lower().replace(" ", "")

            now = datetime.utcnow()

            if age_str.endswith("h") or age_str.endswith("hours"):
                hours = int(age_str.replace("h", "").replace("hours", ""))
                return now.replace(hour=now.hour - hours)

            if age_str.endswith("d") or age_str.endswith("days"):
                days = int(age_str.replace("d", "").replace("days", ""))
                return now.replace(day=now.day - days)

            if age_str.endswith("w") or age_str.endswith("weeks"):
                weeks = int(age_str.replace("w", "").replace("weeks", ""))
                return now.replace(week=now.week - weeks)

            return None

        except (ValueError, TypeError):
            return None

    def _mock_news(self, query: str, count: int) -> list[NewsArticle]:
        """Generate mock news articles for testing."""
        logger.info("using_mock_news", query=query, count=count)

        mock_articles = []
        for i in range(count):
            article = NewsArticle(
                url=f"https://example.com/news-{i}",
                title=f"Breaking News {i + 1}: {query}",
                summary=f"This is a mock news article about {query}. " * 5,
                published_date=datetime.utcnow(),
                source="example.com"
            )
            mock_articles.append(article)

        return mock_articles
