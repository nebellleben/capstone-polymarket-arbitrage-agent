"""Brave Search MCP client for news monitoring."""

import asyncio
from datetime import datetime
from typing import Any, Optional

import httpx

from src.models.news import NewsArticle
from src.utils.config import settings
from src.utils.logging_config import logger


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
                "result_filter": "news",  # Only news results have reliable timestamps
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
        """
        Parse Brave Search API response into NewsArticle objects.

        Filters out articles that are older than news_max_age_days.
        """
        articles = []
        rejected_count = 0

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

                # Validate article age (web results don't have dates, so we reject them all)
                # Only news results have reliable timestamps
                logger.debug("web_result_no_date", url=result.get("url", ""))

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

                # VALIDATE: Check if article is fresh enough
                if self._is_article_fresh(article.published_date):
                    articles.append(article)
                else:
                    rejected_count += 1

            except Exception as e:
                logger.warning("failed_to_parse_news_result", error=str(e))

        logger.info(
            "articles_parsed",
            total_fetched=len(articles) + rejected_count,
            accepted=len(articles),
            rejected=rejected_count,
            rejection_rate=f"{rejected_count / (len(articles) + rejected_count) * 100:.1f}%" if (len(articles) + rejected_count) > 0 else "0%"
        )

        return articles

    def _extract_source(self, url: str) -> str:
        """Extract source hostname from URL."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc or "unknown"
        except Exception:
            return "unknown"

    def _is_article_fresh(self, published_date: Optional[datetime]) -> bool:
        """
        Check if article is within acceptable age range.

        Args:
            published_date: Article publication date

        Returns:
            True if article is fresh enough, False otherwise
        """
        if published_date is None:
            # If no date, reject it (safety first)
            logger.warning("article_no_date", message="Article has no published date, rejecting")
            return False

        # Calculate age in days
        from datetime import timezone, timedelta
        now = datetime.now(timezone.utc)
        article_age = (now - published_date.replace(tzinfo=timezone.utc)).days

        # Check against threshold
        max_age_days = settings.news_max_age_days

        if article_age > max_age_days:
            logger.info(
                "article_rejected_old",
                article_age_days=article_age,
                max_age_days=max_age_days,
                published_date=published_date.isoformat()
            )
            return False

        return True

    def _parse_news_age(self, age_str: Optional[str]) -> Optional[datetime]:
        """Parse Brave Search age string to datetime."""
        if not age_str:
            return None

        # Parse strings like "2h ago", "1d ago", "1w ago"
        try:
            from datetime import timedelta
            age_str = age_str.lower().replace(" ", "")

            now = datetime.utcnow()

            if age_str.endswith("h") or age_str.endswith("hours"):
                hours = int(age_str.replace("h", "").replace("hours", ""))
                return now - timedelta(hours=hours)

            if age_str.endswith("d") or age_str.endswith("days"):
                days = int(age_str.replace("d", "").replace("days", ""))
                return now - timedelta(days=days)

            if age_str.endswith("w") or age_str.endswith("weeks"):
                weeks = int(age_str.replace("w", "").replace("weeks", ""))
                return now - timedelta(weeks=weeks)

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
