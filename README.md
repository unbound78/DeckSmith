<div align="center">

# DeckSmith

**实战派中文场景演示生成工具 · HTML + PPT 双输出**

*Battle-tested deck generator for Chinese-context work presentations — driven by design logic, not templates.*

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange.svg)

</div>

---

## 这是什么

DeckSmith **不是**又一个"AI 一键生成 PPT"的黑盒。它是一套 **设计科学 + 渲染引擎 + Claude Code Skill**：给你一份材料（工作汇报 / 述职 / 复盘 / 方案），它按沉淀的设计逻辑**为这份材料设计适配的框架**——而不是把内容硬塞进固定模板。

- **给的是逻辑，不是样子**：14 种布局是经实战验证的起点积木，覆盖不了需求时不受限、可自定义。
- **审美够用、专为工作呈现**：经真实工作场景打磨，不花哨，适合汇报与演示。
- **面向**：用 [Claude Code](https://claude.com/claude-code) / Claude 的开发者与内容创作者。

## 核心特性

| 特性 | 说明 |
|---|---|
| 🖥️ **HTML + PPT 双输出** | 同一份材料 → scroll-snap 网页长卷（浏览器直接放映）或 python-pptx 原生**可编辑** PPT |
| 🧠 **设计逻辑而非模板** | 教 Claude「材料 → 语境识别 → 信息架构 → 按内容选布局 → 配色 → 自检」的判断流程 |
| 🎨 **配色科学** | 8 套开箱预设 + 从一两个品牌色**推导整套协调色板**的 10 步方法论 |
| 🇨🇳 **中文场景专治** | 字体三套防回退 / 中文文本溢出预检 / 大屏字号分级 / 渐变发光——国外工具不解决的坑 |
| 📦 **即装即用的 Skill** | 作为 Claude Code Skill，对话一句即可生成 |

## 能力边界（诚实说明）

| 能力 | 状态 |
|---|---|
| HTML 演示生成 | ✅ 成熟（14 布局 × 8 预设，已验证） |
| PPT 生成 | ✅ 可用（工具积木 + 示例，Claude 按逻辑现搭） |
| 设计逻辑 / 配色科学 / 中文避坑 | ✅ 见 `skill/references/` |
| 智能配图 | 🔬 预留接口设计，当前版本**不含**生图工具 |

## 安装

```bash
git clone <this-repo>
cd DeckSmith
pip install -r requirements.txt   # python-pptx + lxml
```

## 快速开始

### 生成 HTML 演示

```bash
python skill/scripts/render_html.py \
    presets/blue-orange-light.json \
    examples/case_app_review/plan.json \
    review.html
```
浏览器打开 `review.html`，滚动即放映（右下角全屏按钮 / F 键）。

### 生成 PPT

参考 `examples/case_app_review/build_pptx.py`——用 `deck_smith.pptx_toolkit` 积木为你的材料逐页搭建（渐变 / 阴影 / 文字渐变 / 字体三套 / 溢出预检全内置）。

```bash
python examples/case_app_review/build_pptx.py   # → review.pptx
python skill/scripts/verify_pptx.py review.pptx  # 交付前字体字号校验
```

## 作为 Claude Code Skill 使用（推荐）

把 `skill/` 目录装进 `~/.claude/skills/decksmith/`，然后在 Claude Code 里直接说：

> 「用 DeckSmith 把这份材料做成 PPT，给领导汇报」

Claude 会读取 `SKILL.md` 的设计逻辑，为你的材料设计框架并渲染。

## 项目结构

```
DeckSmith/
├── deck_smith/          # 渲染引擎
│   ├── html_renderer.py #   HTML 渲染器（14 布局）
│   └── pptx_toolkit.py  #   PPT 视觉工具积木
├── presets/             # 8 套配色预设
├── schemas/             # preset JSON Schema
├── skill/               # Claude Code Skill
│   ├── SKILL.md         #   设计逻辑（7-step 工作流）
│   ├── references/      #   设计科学（配色 / 方法论 / 中文避坑 / 字段参考）
│   └── scripts/         #   render_html / verify_pptx
└── examples/            # 可运行示例（HTML + PPT 双版本）
```

## 设计科学（DeckSmith 的灵魂）

`skill/references/` 不是补充文档，是承载完整设计判断力的地方：

- **`color-guide.md`** — 配色推导：色相环 / 等明度等饱和 / OKLCH / 从 RGB 推导整套色板 10 步
- **`design-logic.md`** — 设计方法论：语境识别 / 内容性格化版式 / 视觉精修 / anti-AI-slop
- **`chinese-pitfalls.md`** — 中文场景避坑：字体三套 / 溢出预检 / 大屏字号 / 截图陷阱
- **`plan-schema.md`** — 14 布局字段参考
- **`image-gen-bridge.md`** — 可选生图工具的调用编排

## License

MIT © [unbound78](https://github.com/unbound78)
