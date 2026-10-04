"""最小示例：三档路由 + 成本统计.

运行前设置环境变量：
    export LLM_API_KEY=sk-xxx
    export LLM_BASE_URL=https://api.rqu.cn/v1   # 任何 OpenAI 兼容端点
"""

import os

from llm_router import ModelRouter

router = ModelRouter(
    api_key=os.environ["LLM_API_KEY"],
    base_url=os.environ.get("LLM_BASE_URL", "https://api.rqu.cn/v1"),
)

# 1) 自动路由：命中 light 关键词 -> 便宜模型
r1 = router.ask("classify", "判断情感：这个电影太棒了！")
print("[auto]", r1.model, "->", r1.choices[0].message.content)

# 2) 命中 heavy 关键词 -> 旗舰模型
r2 = router.ask("reason", "为什么天空是蓝色的？请从瑞利散射角度分析")
print("[auto]", r2.model, "->", r2.choices[0].message.content[:80], "...")

# 3) 手动指定档位
r3 = router.light("给这篇文章起个标题：今天发布了新版本")
print("[light]", r3.model, "->", r3.choices[0].message.content)

# 4) 成本报表
print()
print(router.usage.report())
