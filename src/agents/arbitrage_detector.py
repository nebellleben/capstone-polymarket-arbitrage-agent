"""Arbitrage detection engine."""

from datetime import datetime

from src.models.impact import MarketImpact
from src.models.market import MarketData
from src.models.opportunity import Opportunity

from src.utils.logging_config import logger


class ArbitrageDetector:
    """
    Detect arbitrage opportunities by comparing expected vs actual prices.

    This engine:
    1. Receives market impact assessments from reasoning
    2. Fetches current market prices
    3. Calculates discrepancies
    4. Identifies profitable opportunities
    """

    def __init__(
        self,
        confidence_threshold: float = 0.7,
        min_profit_margin: float = 0.05
    ):
        """
        Initialize the arbitrage detector.

        Args:
            confidence_threshold: Minimum confidence for opportunities
            min_profit_margin: Minimum price discrepancy (0.05 = 5%)
        """
        self.confidence_threshold = confidence_threshold
        self.min_profit_margin = min_profit_margin

    def detect_opportunities(
        self,
        impacts: list[MarketImpact],
        market_data_map: dict[str, MarketData]
    ) -> list[Opportunity]:
        """
        Detect arbitrage opportunities from impact assessments.

        Args:
            impacts: List of market impact assessments
            market_data_map: Map of market_id -> MarketData

        Returns:
            List of detected opportunities
        """
        opportunities = []

        for impact in impacts:
            # Filter by relevance and confidence
            if not impact.is_significant:
                logger.debug(
                    "skipping_low_relevance",
                    impact_id=impact.id,
                    relevance=impact.relevance
                )
                continue

            if impact.confidence < self.confidence_threshold:
                logger.debug(
                    "skipping_low_confidence",
                    impact_id=impact.id,
                    confidence=impact.confidence
                )
                continue

            # Get current market data
            market_data = market_data_map.get(impact.market_id)
            if not market_data:
                logger.debug(
                    "no_market_data",
                    impact_id=impact.id,
                    market_id=impact.market_id
                )
                continue

            # Calculate opportunity
            opportunity = self._calculate_opportunity(impact, market_data)
            if opportunity and opportunity.is_profitable(self.min_profit_margin):
                opportunities.append(opportunity)
                logger.info(
                    "opportunity_detected",
                    opportunity_id=opportunity.id,
                    market_id=opportunity.market_id,
                    current_price=opportunity.current_price,
                    expected_price=opportunity.expected_price,
                    discrepancy=opportunity.discrepancy,
                    confidence=opportunity.confidence
                )

        logger.info(
            "opportunities_detected",
            total_impacts=len(impacts),
            opportunities_found=len(opportunities)
        )

        return opportunities

    def _calculate_opportunity(
        self,
        impact: MarketImpact,
        market_data: MarketData
    ) -> Opportunity | None:
        """
        Calculate opportunity from impact and market data.

        Args:
            impact: Market impact assessment
            market_data: Current market data

        Returns:
            Opportunity object or None
        """
        # Get current price (YES price for prediction markets)
        current_price = market_data.yes_price
        expected_price = impact.expected_price

        # Calculate discrepancy
        discrepancy = abs(expected_price - current_price)

        # Calculate potential profit
        # Profit = discrepancy * confidence
        potential_profit = discrepancy * impact.confidence

        # Determine action
        if potential_profit >= self.min_profit_margin and impact.confidence >= 0.8:
            action = "investigate"
        elif potential_profit >= self.min_profit_margin * 0.5:
            action = "monitor"
        else:
            action = "watch"

        opportunity = Opportunity(
            id=self._generate_opportunity_id(impact, market_data),
            impact_id=impact.id,
            market_id=impact.market_id,
            market_question="",  # Will be filled by workflow
            current_price=current_price,
            expected_price=expected_price,
            discrepancy=discrepancy,
            potential_profit=potential_profit,
            confidence=impact.confidence,
            action=action
        )

        return opportunity

    def _generate_opportunity_id(
        self,
        impact: MarketImpact,
        market_data: MarketData
    ) -> str:
        """Generate unique opportunity ID."""
        timestamp = datetime.utcnow().timestamp()
        return f"opp-{int(timestamp)}-{impact.market_id[:8]}"

    def update_thresholds(
        self,
        confidence_threshold: float | None = None,
        min_profit_margin: float | None = None
    ):
        """
        Update detection thresholds.

        Args:
            confidence_threshold: New confidence threshold
            min_profit_margin: New minimum profit margin
        """
        if confidence_threshold is not None:
            self.confidence_threshold = confidence_threshold
            logger.info("confidence_threshold_updated", value=confidence_threshold)

        if min_profit_margin is not None:
            self.min_profit_margin = min_profit_margin
            logger.info("min_profit_margin_updated", value=min_profit_margin)
