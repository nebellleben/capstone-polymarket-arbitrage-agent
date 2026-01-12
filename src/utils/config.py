"""Configuration management using pydantic-settings."""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment (development/production)")

    # News Monitoring
    search_queries: str = Field(
        default="breaking news politics",
        description="Comma-separated search queries"
    )
    news_search_interval: int = Field(
        default=60,
        description="News search interval in seconds"
    )
    news_max_results: int = Field(
        default=10,
        description="Maximum news articles per search"
    )
    news_freshness: str = Field(
        default="pd",
        description="News freshness filter (pd=pw=pm)"
    )

    # Market Data
    polymarket_gamma_host: str = Field(
        default="gamma-api.polymarket.com",
        description="Polymarket Gamma API host"
    )
    market_refresh_interval: int = Field(
        default=300,
        description="Market data refresh interval in seconds"
    )
    polymarket_timeout: int = Field(
        default=30,
        description="API request timeout in seconds"
    )
    polymarket_rate_limit: int = Field(
        default=10,
        description="API rate limit (requests per second)"
    )

    # Arbitrage Detection
    confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Minimum confidence for alerts"
    )
    min_profit_margin: float = Field(
        default=0.05,
        ge=0.0,
        description="Minimum price discrepancy (5%)"
    )
    relevance_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum news-market relevance"
    )

    # MCP Configuration
    brave_api_key: Optional[str] = Field(
        default=None,
        description="Brave Search API key"
    )
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key for AI reasoning"
    )
    brave_search_timeout: int = Field(
        default=30,
        description="Brave Search MCP timeout"
    )

    sequential_thinking_timeout: int = Field(
        default=30,
        description="Sequential Thinking MCP timeout"
    )

    # Alerting
    alert_retention: int = Field(
        default=100,
        description="Number of alerts to retain in memory"
    )
    alert_cooldown: int = Field(
        default=300,
        description="Alert cooldown period in seconds"
    )

    # Cache TTL
    market_cache_ttl: int = Field(
        default=300,
        description="Market cache TTL in seconds"
    )
    news_cache_ttl: int = Field(
        default=86400,
        description="News cache TTL in seconds (24 hours)"
    )


# Global settings instance
settings = Settings()
