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

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(message)s"
)
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()


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

        # In-memory state
        self.news_cache: dict[str, NewsArticle] = {}
        self.market_cache: dict[str, Market] = {}
        self.market_data_cache: dict[str, MarketData] = {}

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
        """
        logger.info("search_news_start", query=state["search_query"])

        try:
            articles = await self.news_client.search(
                query=state["search_query"],
                count=settings.news_max_results,
                freshness=settings.news_freshness
            )

            # Deduplicate against cache
            new_articles = []
            for article in articles:
                article_url = str(article.url)
                if article_url not in self.news_cache:
                    self.news_cache[article_url] = article
                    new_articles.append(article)

            state["news_articles"] = new_articles
            state["messages"].append({
                "role": "system",
                "content": f"Found {len(articles)} articles, {len(new_articles)} new"
            })

            logger.info(
                "search_news_complete",
                total=len(articles),
                new=len(new_articles)
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
                # Fetch active markets
                markets = await client.get_markets(active=True, limit=100)

                # Update cache
                for market in markets:
                    self.market_cache[market.market_id] = market

                # Fetch current prices for markets
                market_data_map = {}
                for market in markets[:50]:  # Limit for MVP
                    try:
                        market_data = await client.get_market_data(market)
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
                    with_prices=len(market_data_map)
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

                await self.run_cycle()

                if max_cycles and cycle_count >= max_cycles:
                    logger.info("max_cycles_reached", count=cycle_count)
                    break

                logger.info("cycle_sleep", interval=cycle_interval)
                await asyncio.sleep(cycle_interval)

        except KeyboardInterrupt:
            logger.info("continuous_stop", cycles_completed=cycle_count)

        except Exception as e:
            logger.error("continuous_error", error=str(e))
            raise


async def main():
    """Main entry point for the arbitrage detection system."""
    logger.info("system_start")

    graph = ArbitrageDetectionGraph()

    # Run a single cycle for MVP testing
    result = await graph.run_cycle(search_query="breaking news politics")

    # Print summary
    print("\n" + "=" * 80)
    print("CYCLE SUMMARY")
    print("=" * 80)
    print(f"News Articles: {len(result['news_articles'])}")
    print(f"Markets Analyzed: {len(result['markets'])}")
    print(f"Impacts Found: {len(result['market_impacts'])}")
    print(f"Opportunities Detected: {len(result['opportunities'])}")
    print(f"Alerts Generated: {len(result['alerts'])}")

    if result['errors']:
        print(f"\nErrors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")

    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
