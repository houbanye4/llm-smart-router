"""llm-smart-router: 按任务难度自动路由到合适档位的 LLM."""

from .router import ModelRouter
from .cost import UsageTracker, PRICING

__all__ = ["ModelRouter", "UsageTracker", "PRICING"]
__version__ = "0.1.0"
