"""
Main arbitrage detection workflow using LangGraph.

This module implements the core workflow for detecting arbitrage opportunities
by orchestrating news monitoring, AI reasoning, market analysis, and alert generation.
"""

import asyncio
import logging
import operator
from datetime import datetime
from typing import Annotated, Literal

import structlog
from langgraph.graph import StateGraph, END

from src.agents.alert_generator import AlertGenerator
from src.agents.arbitrage_detector import ArbitrageDetector
from src.models.alert import Alert
from src.models.impact import MarketImpact
from src.models.market import Market, MarketData
from src.models.news import NewsArticle
from src.models.opportunity import Opportunity
from src.models.workflow import ArbitrageState
from src.tools.brave_search_client import BraveSearchClient
from src.tools.polymarket_client import PolymarketGammaClient
from src.tools.reasoning_client import ReasoningClient
from src.utils.config import settings
from src.utils.logging_config import configure_logging, logger


class ArbitrageDetectionGraph:
    """Main arbitrage detection workflow orchestration."""

    def __init__(self):
        """Initialize the arbitrage detection graph."""
        # Initialize components
        self.news_client = BraveSearchClient()
        self.reasoning_client = ReasoningClient()
        self.polymarket_client = PolymarketGammaClient()
        self.detector = ArbitrageDetector(
            confidence_threshold=settings.confidence_threshold,
            min_profit_margin=settings.min_profit_margin
        )
        self.alert_generator = AlertGenerator()

        # Build the workflow graph
        self.graph = self._build_graph()

        # In-memory state - clear on startup to prevent stale data
        self.news_cache: dict[str, NewsArticle] = {}
        self.market_cache: dict[str, Market] = {}
        self.market_data_cache: dict[str, MarketData] = {}

        logger.info(
            "workflow_initialized",
            caches_cleared=True,
            news_cache_size=0,
            market_cache_size=0,
            market_data_cache_size=0
        )

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(ArbitrageState)

        # Add nodes
        workflow.add_node("search_news", self.search_news)
        workflow.add_node("fetch_markets", self.fetch_markets)
        workflow.add_node("analyze_impacts", self.analyze_impacts)
        workflow.add_node("detect_opportunities", self.detect_opportunities)
        workflow.add_node("generate_alerts", self.generate_alerts)

        # Define edges
        workflow.set_entry_point("search_news")
        workflow.add_edge("search_news", "fetch_markets")
        workflow.add_edge("fetch_markets", "analyze_impacts")
        workflow.add_edge("analyze_impacts", "detect_opportunities")
        workflow.add_edge("detect_opportunities", "generate_alerts")
        workflow.add_edge("generate_alerts", END)

        return workflow.compile()

    async def search_news(self, state: ArbitrageState) -> ArbitrageState:
        """
        Search for breaking news using Brave Search.

        This node fetches recent news articles relevant to the search query.
        Performs secondary validation to ensure articles are fresh enough.
        """
        logger.info("search_news_start", query=state["search_query"])

        try:
            articles = await self.news_client.search(
                query=state["search_query"],
                count=settings.news_max_results,
                freshness=settings.news_freshness
            )

            # SECONDARY VALIDATION: Double-check article ages
            from datetime import datetime, timezone, timedelta
            now = datetime.now(timezone.utc)
            max_age = timedelta(days=settings.news_max_age_days)

            validated_articles = []
            filtered_count = 0

            for article in articles:
                if article.published_date and (now - article.published_date.replace(tzinfo=timezone.utc)) <= max_age:
                    validated_articles.append(article)
                else:
                    filtered_count += 1
                    logger.warning(
                        "article_filtered_secondary",
                        title=article.title[:50],
                        published_date=str(article.published_date),
                        age_days=(now - article.published_date.replace(tzinfo=timezone.utc)).days if article.published_date else "unknown"
                    )

            # Deduplicate validated articles against cache
            new_articles = []
            for article in validated_articles:
                article_url = str(article.url)
                if article_url not in self.news_cache:
                    self.news_cache[article_url] = article
                    new_articles.append(article)

            state["news_articles"] = new_articles
            state["messages"].append({
                "role": "system",
                "content": f"Found {len(articles)} articles, {len(validated_articles)} passed validation, {len(new_articles)} new"
            })

            logger.info(
                "search_news_complete",
                total_fetched=len(articles),
                passed_validation=len(validated_articles),
                filtered_out=filtered_count,
                new_articles=len(new_articles)
            )

        except Exception as e:
            logger.error("search_news_error", error=str(e))
            state["errors"].append(f"News search failed: {e}")
            state["news_articles"] = []

        return state

    async def fetch_markets(self, state: ArbitrageState) -> ArbitrageState:
        """
        Fetch market data from Polymarket Gamma API.

        This node retrieves active markets and their current prices.
        """
        logger.info("fetch_markets_start")

        try:
            async with self.polymarket_client as client:
                # Fetch active markets (API will filter by freshness)
                markets = await client.get_markets(active=True, limit=100)

                # Additional validation: log market details for debugging
                logger.info(
                    "markets_before_validation",
                    count=len(markets),
                    sample_questions=[m.question[:50] for m in markets[:3]]
                )

                # Update cache with validated markets
                for market in markets:
                    self.market_cache[market.market_id] = market

                # Fetch current prices for markets
                market_data_map = {}
                for market in markets[:50]:  # Limit for MVP
                    try:
                        market_data = await client.get_market_data(market)
                        # Filter out markets with no liquidity (price = 0)
                        if market_data.yes_price > 0:
                            self.market_data_cache[market.market_id] = market_data
                            market_data_map[market.market_id] = market_data
                    except Exception as e:
                        logger.warning(
                            "fetch_market_data_failed",
                            market_id=market.market_id,
                            error=str(e)
                        )

                state["markets"] = markets
                state["market_data"] = market_data_map

                logger.info(
                    "fetch_markets_complete",
                    markets=len(markets),
                    with_prices=len(market_data_map),
                    sample_questions=[m.question[:50] for m in markets[:3]]
                )

        except Exception as e:
            logger.error("fetch_markets_error", error=str(e))
            state["errors"].append(f"Market fetch failed: {e}")
            state["markets"] = []
            state["market_data"] = {}

        return state

    async def analyze_impacts(self, state: ArbitrageState) -> ArbitrageState:
        """
        Analyze news impact on markets using AI reasoning.

        This node evaluates how breaking news should affect market prices.
        """
        logger.info(
            "analyze_impacts_start",
            news_count=len(state["news_articles"]),
            market_count=len(state["markets"])
        )

        impacts = []

        # Limit combinations for MVP
        max_news = min(len(state["news_articles"]), 5)
        max_markets = min(len(state["markets"]), 10)

        for i, news in enumerate(state["news_articles"][:max_news]):
            for j, market in enumerate(state["markets"][:max_markets]):
                try:
                    logger.debug(
                        "analyzing_impact",
                        news_index=i,
                        market_index=j,
                        news_url=str(news.url),
                        market_id=market.market_id
                    )

                    impact = await self.reasoning_client.analyze_impact(news, market)

                    # Only keep significant impacts
                    if impact.is_significant:
                        impacts.append(impact)

                except Exception as e:
                    logger.warning(
                        "impact_analysis_failed",
                        news_url=str(news.url),
                        market_id=market.market_id,
                        error=str(e)
                    )

        state["market_impacts"] = impacts

        logger.info(
            "analyze_impacts_complete",
            total_analyzed=max_news * max_markets,
            significant_impacts=len(impacts)
        )

        return state

    def detect_opportunities(self, state: ArbitrageState) -> ArbitrageState:
        """
        Detect arbitrage opportunities.

        This node compares expected vs actual prices to find discrepancies.
        """
        logger.info("detect_opportunities_start", impacts=len(state["market_impacts"]))

        try:
            opportunities = self.detector.detect_opportunities(
                impacts=state["market_impacts"],
                market_data_map=state["market_data"]
            )

            state["opportunities"] = opportunities

            logger.info(
                "detect_opportunities_complete",
                opportunities_found=len(opportunities)
            )

        except Exception as e:
            logger.error("detect_opportunities_error", error=str(e))
            state["errors"].append(f"Opportunity detection failed: {e}")
            state["opportunities"] = []

        return state

    def generate_alerts(self, state: ArbitrageState) -> ArbitrageState:
        """
        Generate alerts for detected opportunities.

        This node creates human-readable alerts and outputs them.
        """
        logger.info("generate_alerts_start", opportunities=len(state["opportunities"]))

        alerts = []

        for opportunity in state["opportunities"]:
            try:
                # Find related news and market
                impact = next(
                    (i for i in state["market_impacts"] if i.id == opportunity.impact_id),
                    None
                )
                if not impact:
                    continue

                news = next(
                    (n for n in state["news_articles"] if str(n.url) == str(impact.news_url)),
                    None
                )
                if not news:
                    continue

                market = next(
                    (m for m in state["markets"] if m.market_id == opportunity.market_id),
                    None
                )
                if not market:
                    continue

                # Create alert
                alert = self.alert_generator.create_alert(
                    opportunity=opportunity,
                    news=news,
                    market=market,
                    reasoning=impact.reasoning
                )

                alerts.append(alert)

                # Output to console
                print(self.alert_generator.format_console(alert))

            except Exception as e:
                logger.error(
                    "alert_generation_failed",
                    opportunity_id=opportunity.id,
                    error=str(e)
                )

        state["alerts"] = alerts
        state["cycle_end_time"] = datetime.utcnow()

        # Export alerts to JSON
        if alerts:
            self.alert_generator.export_json(alerts)

        logger.info(
            "generate_alerts_complete",
            alerts_created=len(alerts),
            cycle_duration=(state["cycle_end_time"] - state["cycle_start_time"]).total_seconds()
        )

        return state

    async def run_cycle(
        self,
        search_query: str | None = None
    ) -> ArbitrageState:
        """
        Run a single detection cycle.

        Args:
            search_query: Search query for news (defaults to settings)

        Returns:
            Final state after workflow completion
        """
        query = search_query or settings.search_queries.split(",")[0]

        logger.info("cycle_start", query=query)

        initial_state: ArbitrageState = {
            "search_query": query,
            "confidence_threshold": settings.confidence_threshold,
            "min_profit_margin": settings.min_profit_margin,
            "news_articles": [],
            "markets": [],
            "market_data": {},
            "market_impacts": [],
            "opportunities": [],
            "alerts": [],
            "cycle_start_time": datetime.utcnow(),
            "cycle_end_time": None,
            "errors": [],
            "messages": []
        }

        try:
            final_state = await self.graph.ainvoke(initial_state)
            return final_state

        except Exception as e:
            logger.error("cycle_failed", error=str(e))
            initial_state["errors"].append(f"Cycle failed: {e}")
            return initial_state

    async def run_continuous(
        self,
        interval: int | None = None,
        max_cycles: int | None = None
    ):
        """
        Run continuous detection cycles.

        Args:
            interval: Seconds between cycles (defaults to news_search_interval)
            max_cycles: Maximum number of cycles (None = infinite)
        """
        cycle_interval = interval or settings.news_search_interval
        cycle_count = 0

        logger.info(
            "continuous_start",
            interval=cycle_interval,
            max_cycles=max_cycles or "infinite"
        )

        try:
            while True:
                cycle_count += 1

                logger.info("cycle_begin", number=cycle_count)

                try:
                    await self.run_cycle()
                except Exception as cycle_error:
                    # Log cycle error but continue running
                    logger.error(
                        "cycle_failed",
                        cycle_number=cycle_count,
                        error=str(cycle_error),
                        error_type=type(cycle_error).__name__
                    )
                    # Continue to next cycle despite failure

                if max_cycles and cycle_count >= max_cycles:
                    logger.info("max_cycles_reached", count=cycle_count)
                    break

                logger.info("cycle_sleep", interval=cycle_interval)
                await asyncio.sleep(cycle_interval)

        except KeyboardInterrupt:
            logger.info("continuous_stop", cycles_completed=cycle_count)

        except Exception as e:
            logger.error("continuous_error", error=str(e), error_type=type(e).__name__)
            raise


async def main():
    """Main entry point for the arbitrage detection system."""
    logger.info("system_start")

    graph = ArbitrageDetectionGraph()

    # Run continuous cycles for deployment
    # For local testing (single cycle): run SINGLE_CYCLE=true python -m src.workflows.mvp_workflow
    import os
    if os.getenv("SINGLE_CYCLE", "false").lower() == "true":
        result = await graph.run_cycle(search_query="breaking news politics")
        logger.info("single_cycle_complete", result_summary={
            "news_articles": len(result['news_articles']),
            "markets": len(result['markets']),
            "impacts": len(result['market_impacts']),
            "opportunities": len(result['opportunities']),
            "alerts": len(result['alerts'])
        })
    else:
        await graph.run_continuous(
            interval=settings.news_search_interval,
            max_cycles=None  # Run forever
        )

    # Note: Summaries are printed at the end of each cycle in run_cycle()


if __name__ == "__main__":
    asyncio.run(main())
