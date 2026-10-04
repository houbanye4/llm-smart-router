"""核心路由器：按任务难度把请求分发到不同档位的模型."""

from __future__ import annotations

from typing import Callable, Optional

from openai import OpenAI

from .cost import UsageTracker, estimate_cost

# 默认档位关键词：命中即路由到 heavy（保守策略，宁可贵不可降智）
_HEAVY_KEYWORDS = (
    "推理", "分析", "规划", "证明", "审查", "重构", "架构",
    "reason", "analyze", "plan", "review", "refactor", "architecture",
    "为什么", "why", "debug", "优化", "optimize",
)

_LIGHT_KEYWORDS = (
    "分类", "判断", "抽取", "格式化", "转换", "标题", "翻译",
    "classify", "extract", "format", "convert", "title", "translate",
)

LONG_TEXT_THRESHOLD = 50_000  # 超过该长度直接走 heavy（长上下文旗舰）


class ModelRouter:
    """OpenAI 兼容端点的三档模型路由器.

    Args:
        api_key: API 密钥.
        base_url: OpenAI 兼容端点（官方或任意聚合网关）.
        route_table: 档位 -> 模型名 的映射.
        route_fn: 自定义路由函数 (task, text_len, kwargs) -> 档位名.
                  提供后优先于内置规则.
        tracker: 外部传入的 UsageTracker（多 router 共享统计时用）.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        route_table: Optional[dict] = None,
        route_fn: Optional[Callable[[str, int, dict], str]] = None,
        tracker: Optional[UsageTracker] = None,
        default_tier: str = "main",
        **client_kwargs,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url, **client_kwargs)
        self.route_table = route_table or {
            "light": "deepseek-chat",
            "main": "gpt-4o-mini",
            "heavy": "claude-sonnet-4-5",
        }
        self.route_fn = route_fn
        self.default_tier = default_tier
        self.usage = tracker or UsageTracker()

    def pick(self, task: str, text: str = "", **kwargs) -> str:
        """根据任务描述与文本选择模型."""
        if self.route_fn is not None:
            tier = self.route_fn(task, len(text), kwargs)
            return self.route_table.get(tier, tier)

        if len(text) > LONG_TEXT_THRESHOLD:
            return self.route_table["heavy"]
        # 关键词匹配：heavy 优先（保守）
        if any(k in task.lower() for k in _HEAVY_KEYWORDS):
            return self.route_table["heavy"]
        if any(k in task.lower() for k in _LIGHT_KEYWORDS):
            return self.route_table["light"]
        return self.route_table.get(self.default_tier, self.route_table["main"])

    def ask(self, task: str, prompt: str, *, model: Optional[str] = None,
            text: str = "", **kwargs):
        """发起一次自动路由的对话.

        Args:
            task: 任务类型描述（用于路由决策，如 classify / summarize / reason）.
            prompt: 实际发给模型的用户消息.
            model: 显式指定模型（跳过路由）.
            text: 参与长度判断的原文（如 RAG 召回的文档），不进入消息体.
        """
        model = model or self.pick(task, text=text, **kwargs)
        messages = kwargs.pop("messages", None) or [{"role": "user", "content": prompt}]
        resp = self.client.chat.completions.create(
            model=model, messages=messages, **kwargs
        )
        u = resp.usage
        if u is not None:
            cost = estimate_cost(model, u.prompt_tokens, u.completion_tokens)
            self.usage.record(model, u.prompt_tokens, u.completion_tokens, cost)
        return resp

    # ---- 便捷方法：直接指定档位 ----
    def light(self, prompt: str, **kwargs):
        return self.ask("light task", prompt, model=self.route_table["light"], **kwargs)

    def main(self, prompt: str, **kwargs):
        return self.ask("main task", prompt, model=self.route_table["main"], **kwargs)

    def heavy(self, prompt: str, **kwargs):
        return self.ask("heavy task", prompt, model=self.route_table["heavy"], **kwargs)
