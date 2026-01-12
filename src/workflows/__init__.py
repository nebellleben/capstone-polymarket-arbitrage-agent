"""Workflows package for LangGraph workflow orchestration."""

# Main MVP workflow
from src.workflows.mvp_workflow import ArbitrageDetectionGraph, main

__all__ = ["ArbitrageDetectionGraph", "main"]
