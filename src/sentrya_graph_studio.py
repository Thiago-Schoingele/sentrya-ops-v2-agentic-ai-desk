"""LangGraph Studio adapter for local Sentrya Ops V2 graph debugging.

This module is development/debug-only. Production and Telegram runtime paths
must continue to call ``run_sentrya_agent()`` from ``src.sentrya_agent`` so the
Security Gate, Lockdown Guard, Language Router, public-safe response shaping,
security state controls, and optional rate limiting remain active.
"""

from __future__ import annotations

import os
from importlib import import_module
from typing import Any

os.environ.setdefault("SENTRYA_STUDIO_MODE", "true")

_sentrya_agent = import_module("src.sentrya_agent")

agent = _sentrya_agent.SENTRYA_GRAPH
graph = agent


def make_graph(config: dict[str, Any] | None = None) -> Any:
    """Create a fresh compiled graph for local Studio debugging."""
    return _sentrya_agent.create_sentrya_graph()
