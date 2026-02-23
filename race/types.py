"""Shared lightweight types for race execution data."""

from typing import NotRequired, TypedDict


class AgentResult(TypedDict, total=False):
    agent: str
    agent_type: str
    final_balance: float
    total_profit: float
    total_items_sold: int
    duration: float
    bankrupt: bool
    error: str
    composite_score: NotRequired[float]


class RaceRecord(TypedDict, total=False):
    timestamp: str
    simulation: str
    seed: int
    agents: list[str]
    agent_types: list[str]
    results: list[AgentResult]
