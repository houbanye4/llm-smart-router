"""用量统计与成本估算：价格表按「美元 / 百万 tokens」维护."""

from __future__ import annotations

from collections import defaultdict

# 近似牌价（美元 / 百万 tokens）：(输入, 输出)
# 仅为估算用途，请按你的实际渠道价格修改。
PRICING: dict[str, tuple[float, float]] = {
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "gemini-2.5-pro": (1.25, 10.00),
    "deepseek-chat": (0.27, 1.10),
    "deepseek-reasoner": (0.55, 2.19),
    "qwen-plus": (0.40, 1.20),
}

DEFAULT_PRICE = (1.00, 4.00)  # 未知模型的兜底估价


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    """按价格表估算单次调用成本（美元）."""
    pin, pout = PRICING.get(model, DEFAULT_PRICE)
    return prompt_tokens / 1e6 * pin + completion_tokens / 1e6 * pout


class UsageTracker:
    """按模型维度累计 tokens 与估算成本."""

    def __init__(self):
        self._data: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0.0, 0])
        # model -> [prompt_tokens, completion_tokens, cost_usd, calls]

    def record(self, model: str, prompt_tokens: int,
               completion_tokens: int, cost_usd: float) -> None:
        row = self._data[model]
        row[0] += prompt_tokens
        row[1] += completion_tokens
        row[2] += cost_usd
        row[3] += 1

    def report(self) -> str:
        """输出对齐的文本报表."""
        rows = sorted(self._data.items(), key=lambda x: -x[1][2])
        header = f"{'model':<24}{'calls':>7}{'prompt':>10}{'completion':>12}{'est. cost':>12}"
        lines = [header, "-" * len(header)]
        total = 0.0
        for model, (pt, ct, cost, calls) in rows:
            total += cost
            lines.append(f"{model:<24}{calls:>7}{pt:>10,}{ct:>12,}{cost:>11.4f}$")
        lines.append("-" * len(header))
        lines.append(f"{'TOTAL':<24}{'':>7}{'':>10}{'':>12}{total:>11.4f}$")
        return "\n".join(lines)

    @property
    def total_cost(self) -> float:
        return sum(v[2] for v in self._data.values())
