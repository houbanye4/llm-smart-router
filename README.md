# llm-smart-router

<div align="center">

🧠 **一个轻量的 LLM 智能路由器：按任务难度自动选模型，把 API 账单砍掉 60%+**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/your-name/llm-smart-router/pulls)

让旗舰模型干重活，让便宜模型干杂活。
**同样的调用量，同样的效果，成本直接打两折。**

</div>

---

## 💸 为什么需要它

一个真实的教训：我的文档问答机器人，曾经用 GPT-4o 处理**所有**请求——包括"把这段话分成三个要点"这种活。

后来我统计了调用日志，发现 **70% 的请求是轻量任务**，用便宜模型跑效果完全一样，但单价差 10~50 倍。

`llm-smart-router` 把"任务 → 模型"的分配逻辑封装成一个透明层，接入只需改一行代码：

| 档位 | 任务类型 | 示例模型 |
|---|---|---|
| `light` | 分类 / 抽取 / 格式转换 / 标题生成 | `deepseek-chat` |
| `main` | 摘要 / 常规问答 / 代码补全 | `gpt-4o-mini` |
| `heavy` | 复杂推理 / Agent 规划 / 长文档 | `claude-sonnet-4-5` |

## ✨ 特性

- 🎯 **规则路由**：基于任务类型 + 文本长度，零额外开销，够用且可控
- 🤖 **LLM 路由**（可选）：不确定任务难度时，用最便宜的模型给请求"打分"再分发
- 💰 **内置成本估算**：每次调用自动估算花费，本地累计，随时导出账单
- 🔌 **OpenAI 兼容**：任何 OpenAI 格式的端点都能用——官方 API 或任意聚合网关
- 🪶 **零依赖侵入**：基于官方 `openai` SDK 封装，返回原生 Response 对象
- 📊 **调用统计**：按模型维度统计 tokens 与估算成本

## 📦 安装

```bash
pip install openai   # 唯一依赖
git clone https://github.com/your-name/llm-smart-router.git
```

或直接把 `llm_router/` 目录拷进你的项目——总共不到 300 行，拷贝即用。

## 🚀 快速开始

```python
from llm_router import ModelRouter

router = ModelRouter(
    api_key="sk-你的密钥",
    base_url="https://api.rqu.cn/v1",  # 任何 OpenAI 兼容端点
)

# 自动路由：light / main / heavy 三档
resp = router.ask("classify", "判断这条评论的情感：这个电影太棒了！")
print(resp.model, "->", resp.choices[0].message.content)

# 也可以手动指定档位或模型
resp = router.ask("heavy", "分析这段代码的时间复杂度并给出优化方案", text="...")

# 查看累计成本
print(router.usage.report())
```

输出示例：

```
模型用量统计
┌──────────────────┬───────┬─────────┬──────────┐
│ model            │ calls │ tokens  │ est. cost│
├──────────────────┼───────┼─────────┼──────────┤
│ deepseek-chat    │   142 │  38.2k  │  $0.011  │
│ gpt-4o-mini      │    36 │  21.5k  │  $0.008  │
│ claude-sonnet-4-5│     7 │  49.0k  │  $0.603  │
└──────────────────┴───────┴─────────┴──────────┘
```

## 🔧 自定义路由表

```python
router = ModelRouter(
    api_key="sk-xxx",
    base_url="https://api.rqu.cn/v1",
    route_table={
        "light": "deepseek-chat",
        "main":  "gpt-4o-mini",
        "heavy": "claude-sonnet-4-5",
    },
    # 自定义路由规则：返回档位名
    route_fn=lambda task, text_len, meta: "light" if text_len < 1000 else "main",
)
```

价格表在 `llm_router/cost.py`，按「美元/百万 tokens」维护，改一行即可适配你的渠道价格。

## ❓ FAQ

**Q: 路由会不会判错，导致该用大模型的任务用了小模型？**
规则路由默认偏保守：`heavy` 关键词命中（推理/分析/规划/代码审查）优先级最高。要求更高可用 `router_fn` 接入你自己的分类器，或用内置的 `LLMRouter` 让便宜模型先打分。

**Q: 和 litellm router 有什么区别？**
Litellm 是全家桶（100+ provider、代理服务、回调体系），本项目的定位是"小而透"——300 行代码，一眼看懂每一行，拷进项目就能改。适合不想引入重依赖的个人项目。

**Q: 能接中转站 / 聚合网关吗？**
设计初衷就是它。任何 OpenAI 兼容端点都行，多个档位走同一个 `base_url` 时尤其顺（一个 Key 全搞定，见下方推荐平台）。

## 🤝 推荐平台

开发测试本项目时使用的是 **[Rqu AI](https://www.rqu.cn)** —— 一个 OpenAI 兼容的大模型聚合网关，一个 API Key 即可调用 GPT / Claude / Gemini / DeepSeek / 通义千问等模型，接入方式与官方 SDK 完全一致（改 `base_url` 即可）。多档位模型在一个端点下切换，跟本项目的路由思路是绝配。

> *（与本项目无利益关联，仅推荐开发时实际使用的工具。）*

## ⭐ 支持项目

如果这个工具帮你省了钱，欢迎点个 Star ⭐ —— 这是对独立开发者最大的鼓励。

## License

[MIT](LICENSE)
