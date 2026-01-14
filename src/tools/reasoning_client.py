"""Gemini AI client for market impact reasoning."""

import asyncio
import json
import re
from datetime import datetime
from typing import Optional

import google.generativeai as genai

from src.models.impact import MarketImpact, PriceDirection
from src.models.market import Market
from src.models.news import NewsArticle
from src.utils.config import settings

from src.utils.logging_config import logger


def repair_json(json_str: str) -> dict:
    """
    Attempt to repair malformed JSON by applying common fixes.

    Args:
        json_str: Potentially malformed JSON string

    Returns:
        Parsed dictionary, or empty dict if all repairs fail
    """
    # Try 1: Parse as-is
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    repairs = [
        # Repair 1: Fix truncated strings (common issue)
        lambda s: re.sub(r'"([^"]*?)$', r'"\1"', s),

        # Repair 2: Fix missing commas between fields
        lambda s: re.sub(r'"\s*\n\s*"', '", "', s),

        # Repair 3: Fix trailing commas
        lambda s: re.sub(r',\s*}', '}', s).replace(',]', ']'),

        # Repair 4: Fix unquoted property names
        lambda s: re.sub(r'(\w+)\s*:', r'"\1":', s),

        # Repair 5: Fix single quotes to double quotes
        lambda s: s.replace("'", '"'),

        # Repair 6: Fix missing closing braces
        lambda s: s + '}' if s.count('{') > s.count('}') else s,

        # Repair 7: Fix missing closing brackets
        lambda s: s + ']' if s.count('[') > s.count(']') else s,

        # Repair 8: Remove control characters
        lambda s: re.sub(r'[\x00-\x1f\x7f-\x9f]', '', s),

        # Repair 9: Fix escaped quotes
        lambda s: s.replace('\\"', '"').replace('\\n', ' '),

        # Repair 10: Extract partial JSON and complete it
        lambda s: re.sub(r'^.*?(\{[^{}]*\{[^{}]*\}[^{}]*\}).*$', r'\1', s, flags=re.DOTALL)
    ]

    # Try each repair strategy
    for i, repair in enumerate(repairs, 1):
        try:
            repaired = repair(json_str)
            result = json.loads(repaired)
            logger.info(f"json_repair_success", repair_method=i, original_length=len(json_str))
            return result
        except (json.JSONDecodeError, ValueError) as e:
            continue

    # All repairs failed
    logger.warning("json_repair_failed", original_length=len(json_str), repairs_attempted=len(repairs))
    return None


class ReasoningClient:
    """Client for Gemini AI reasoning integration."""

    def __init__(self):
        """Initialize the Reasoning client."""
        self.timeout = settings.sequential_thinking_timeout
        self.client: Optional[genai.GenerativeModel] = None
        self._initialized = False
        # Rate limiting: max 10 requests per minute for free tier
        self._request_times = []
        self._rate_limit = 10  # requests per minute
        self._rate_window = 60  # seconds

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

    async def _acquire_rate_limit(self):
        """Acquire rate limit permit, waiting if necessary."""
        now = datetime.utcnow().timestamp()

        # Remove old timestamps outside the rate window
        self._request_times = [t for t in self._request_times if now - t < self._rate_window]

        # If at limit, wait for slot
        if len(self._request_times) >= self._rate_limit:
            wait_time = self._rate_window - (now - self._request_times[0])
            if wait_time > 0:
                logger.info(f"rate_limit_wait", wait_seconds=wait_time)
                await asyncio.sleep(wait_time)

        # Add current request time
        self._request_times.append(datetime.utcnow().timestamp())

    async def _perform_reasoning(
        self,
        context: str,
        news: NewsArticle,
        market: Market
    ) -> dict[str, any]:
        """Perform AI reasoning using Gemini API."""

        try:
            # Initialize Gemini client if not already done
            if not self._initialized:
                api_key = getattr(settings, 'gemini_api_key', None)
                if not api_key:
                    logger.warning("gemini_api_key not set, using fallback reasoning")
                    return self._fallback_reasoning(news, market)

                genai.configure(api_key=api_key)
                model_name = getattr(settings, 'gemini_model', 'gemini-2.5-flash')
                self.client = genai.GenerativeModel(model_name)
                self._initialized = True

            # Acquire rate limit permit
            await self._acquire_rate_limit()

            prompt = f"""{context}

IMPORTANT: You must respond with ONLY a valid JSON object. No other text, no markdown formatting, no explanations outside the JSON.

Response format (copy this exact structure):
{{
    "relevance": 0.75,
    "direction": "up",
    "confidence": 0.8,
    "expected_magnitude": 0.15,
    "expected_price": 0.65,
    "reasoning": "Brief explanation here"
}}

Replace the example values with your actual analysis."""

            response = await asyncio.to_thread(
                self.client.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=500,
                    temperature=0.7,
                )
            )

            content = response.text

            # Extract and repair JSON from response
            content = content.strip()

            # Try to find JSON object in the response
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            # Extract from markdown code blocks if present
            elif "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            # Clean up the JSON string
            content = content.replace('\n', ' ').replace('\r', '').strip()

            # Use repair_json function to handle malformed JSON
            result = repair_json(content)
            if result is None:
                raise ValueError("Failed to parse JSON after repair attempts")

            return {
                "relevance": float(result.get("relevance", 0.5)),
                "direction": str(result.get("direction", "neutral")),
                "confidence": float(result.get("confidence", 0.5)),
                "expected_magnitude": float(result.get("expected_magnitude", 0.1)),
                "expected_price": float(result.get("expected_price", 0.5)),
                "reasoning": str(result.get("reasoning", "No reasoning provided"))
            }

        except ImportError:
            logger.warning("google.generativeai package not installed, using fallback")
            return self._fallback_reasoning(news, market)

        except Exception as e:
            logger.error("gemini_api_error", error=str(e), exc_info=True)
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
