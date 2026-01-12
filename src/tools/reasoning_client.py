"""Sequential Thinking MCP client for AI reasoning."""

import asyncio
from datetime import datetime
from typing import Optional

import anthropic

from src.models.impact import MarketImpact, PriceDirection
from src.models.market import Market
from src.models.news import NewsArticle
from src.utils.config import settings

from src.utils.logging_config import logger


class ReasoningClient:
    """Client for Sequential Thinking MCP integration."""

    def __init__(self):
        """Initialize the Reasoning client."""
        self.timeout = settings.sequential_thinking_timeout
        # Note: Using Anthropic API as fallback if MCP not configured
        self.client: Optional[anthic.Anthropic] = None

    async def analyze_impact(
        self,
        news_article: NewsArticle,
        market: Market
    ) -> MarketImpact:
        """
        Analyze news impact on a market using AI reasoning.

        Args:
            news_article: News article to analyze
            market: Market to assess impact on

        Returns:
            MarketImpact assessment
        """
        try:
            context = self._prepare_context(news_article, market)
            response = await self._perform_reasoning(context, news_article, market)

            impact = MarketImpact(
                id=self._generate_impact_id(news_article, market),
                news_url=news_article.url,
                market_id=market.market_id,
                relevance=response["relevance"],
                direction=PriceDirection(response["direction"]),
                confidence=response["confidence"],
                reasoning=response["reasoning"],
                expected_magnitude=response["expected_magnitude"],
                expected_price=response["expected_price"]
            )

            logger.info(
                "reasoning_success",
                market_id=market.market_id,
                news_url=str(news_article.url),
                relevance=impact.relevance,
                confidence=impact.confidence,
                direction=impact.direction
            )

            return impact

        except Exception as e:
            logger.error(
                "reasoning_error",
                market_id=market.market_id,
                news_url=str(news_article.url),
                error=str(e)
            )
            # Return neutral impact on error
            return self._create_neutral_impact(news_article, market, str(e))

    def _prepare_context(self, news: NewsArticle, market: Market) -> str:
        """Prepare context for reasoning."""
        return f"""
You are an expert at analyzing news impact on prediction markets.

NEWS ARTICLE:
Title: {news.title}
Summary: {news.summary}
Published: {news.published_date or 'Unknown'}
Source: {news.source or 'Unknown'}

PREDICTION MARKET:
Question: {market.question}
Description: {market.description}
End Date: {market.end_date or 'Open-ended'}

TASK:
Analyze how this news article should impact this prediction market. Consider:
1. RELEVANCE: How directly relevant is this news to the market resolution? (0.0-1.0)
2. DIRECTION: Which way should the price move? (up/down/neutral)
3. CONFIDENCE: How confident are you in this assessment? (0.0-1.0)
4. MAGNITUDE: Expected price change magnitude (0.0-1.0)

Provide your response as a concise analysis.
"""

    async def _perform_reasoning(
        self,
        context: str,
        news: NewsArticle,
        market: Market
    ) -> dict[str, any]:
        """Perform AI reasoning using Claude API."""
        # For MVP, using Anthropic API directly
        # In production, this would integrate with Sequential Thinking MCP

        try:
            # Import anthropic if available
            import anthropic

            if not self.client:
                api_key = getattr(settings, 'anthropic_api_key', None)
                if not api_key:
                    logger.warning("anthropic_api_key not set, using fallback reasoning")
                    return self._fallback_reasoning(news, market)

                self.client = anthropic.Anthropic(api_key=api_key)

            prompt = f"""{context}

Please respond in the following JSON format:
{{
    "relevance": <float 0-1>,
    "direction": <"up", "down", or "neutral">,
    "confidence": <float 0-1>,
    "expected_magnitude": <float 0-1>,
    "expected_price": <float 0-1>,
    "reasoning": "<brief explanation>"
}}"""

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text

            # Parse JSON response
            import json
            result = json.loads(content)

            return {
                "relevance": float(result.get("relevance", 0.5)),
                "direction": str(result.get("direction", "neutral")),
                "confidence": float(result.get("confidence", 0.5)),
                "expected_magnitude": float(result.get("expected_magnitude", 0.1)),
                "expected_price": float(result.get("expected_price", 0.5)),
                "reasoning": str(result.get("reasoning", "No reasoning provided"))
            }

        except ImportError:
            logger.warning("anthropic package not installed, using fallback")
            return self._fallback_reasoning(news, market)

        except Exception as e:
            logger.error("anthropic_api_error", error=str(e))
            return self._fallback_reasoning(news, market)

    def _fallback_reasoning(self, news: NewsArticle, market: Market) -> dict[str, any]:
        """Fallback reasoning using keyword matching."""
        logger.info("using_fallback_reasoning", news_url=str(news.url), market_id=market.market_id)

        # Simple keyword matching
        title_lower = news.title.lower()
        summary_lower = news.summary.lower()
        question_lower = market.question.lower()

        # Check for relevance
        question_words = set(question_lower.split())
        news_words = set(title_lower.split()) | set(summary_lower.split())

        overlap = len(question_words & news_words)
        relevance = min(overlap / max(len(question_words), 1), 1.0)

        # Determine direction based on sentiment keywords
        positive_words = {"win", "gain", "success", "approve", "pass", "yes", "up"}
        negative_words = {"lose", "fail", "reject", "down", "no", "fall", "drop"}

        all_text = title_lower + " " + summary_lower
        pos_count = sum(1 for word in positive_words if word in all_text)
        neg_count = sum(1 for word in negative_words if word in all_text)

        if pos_count > neg_count:
            direction = "up"
        elif neg_count > pos_count:
            direction = "down"
        else:
            direction = "neutral"

        # Low confidence for fallback
        confidence = 0.4
        magnitude = 0.1

        # Calculate expected price (simplified)
        expected_price = 0.5
        if direction == "up":
            expected_price = 0.6
        elif direction == "down":
            expected_price = 0.4

        return {
            "relevance": relevance,
            "direction": direction,
            "confidence": confidence,
            "expected_magnitude": magnitude,
            "expected_price": expected_price,
            "reasoning": f"Keyword-based analysis: {direction} direction based on article content. Relevance: {relevance:.2f} based on word overlap."
        }

    def _create_neutral_impact(
        self,
        news: NewsArticle,
        market: Market,
        error: str
    ) -> MarketImpact:
        """Create neutral impact when reasoning fails."""
        return MarketImpact(
            id=self._generate_impact_id(news, market),
            news_url=news.url,
            market_id=market.market_id,
            relevance=0.0,
            direction=PriceDirection.NEUTRAL,
            confidence=0.0,
            reasoning=f"Failed to analyze: {error}",
            expected_magnitude=0.0,
            expected_price=0.5
        )

    def _generate_impact_id(self, news: NewsArticle, market: Market) -> str:
        """Generate unique impact ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"impact-{int(timestamp)}-{hash(str(news.url)) % 10000}-{market.market_id[:8]}"
