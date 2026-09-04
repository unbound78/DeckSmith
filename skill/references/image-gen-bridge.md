# DeckSmith · 生图工具桥接指南

> ⚠️ **预留接口设计文档**:DeckSmith 当前版本**不含生图工具本身**。本文描述的是"若未来接入兼容的生图工具,应如何编排 提炼→生图→回填"。当前无图场景一律走 Step 2.5「图片策略 C」(纯文字 + 设计填充)。
>
> 何时读:未来接入了兼容的生图工具、需要配图时(SKILL.md「配图增强」+ Step 2.5 图片策略 B)。
> **DeckSmith 本体不含生图。** 这篇说明如何在用户额外安装生图工具后，由执行 skill 的 Claude 编排"提炼 prompt → 生图 → 回填"。这是 **agent 编排，不是硬编码闭环**。

## 生图工具是什么

一个**独立可选**的配套工具（`deck-image-gen`，浏览器自动化生图引擎）：
- 基于 Playwright 驱动 **Google Chrome**，调 **Gemini / ChatGPT 网页版**生图。
- **不用 API key**——用网页版登录额度（省钱，但需人工登录一次）。
- 提供本地 HTTP 接口，接收 prompt → 落盘图片。

## 🔴 运行条件（如实告知用户，缺一不可）

1. 安装 **Node.js**（14+）。
2. 安装 **Google Chrome**（Playwright 驱动它，首次会下载 Chromium）。
3. 启动服务后，**在弹出的浏览器里手动登录** Google 账号（用 Gemini）或 OpenAI 账号（用 ChatGPT）——登录态会被 Playwright 持久化。
4. 如需代理，配 `HTTPS_PROXY` 环境变量。

> 未满足条件（没装工具 / 没登录）→ **不报错，直接走图片策略 C**（纯文字 + 设计填充），见 SKILL.md Step 2.5。

## 调用接口

服务默认监听本地端口（以工具 README 为准，通常 `http://localhost:<PORT>`）。

**生成图片**：`POST /api/generate`
```json
{
  "prompts": ["一句具象的画面描述", "第二张图的描述"],
  "mode": "image",
  "provider": "gemini",
  "prefix": "deck_scene",
  "referenceImages": ["可选：参考图绝对路径"],
  "timeout": 300000
}
```
- `prompts`（数组，内部串行）或 `prompt`（单条）。
- `provider`: `gemini`（默认）或 `chatgpt`。
- `mode`: `image` / `text` / `canvas`。

**返回**：
```json
{ "ok": true, "results": [
  { "index": 1, "prompt": "...", "filename": "deck_scene_001.png",
    "path": "<工具目录>/downloads/deck_scene_001.png", "ok": true, "provider": "gemini" }
] }
```
图片落盘在工具的 `downloads/` 目录，用返回的 `path` 引用。

## Claude 的编排逻辑（三步）

当图片策略判定为 B（需要且能生成图），执行 skill 的 Claude 这样做：

**1. 提炼 prompt**（每张图一句）
- 从演示内容提炼**具象**画面描述，风格与演示调性一致（如商务/科技/温暖）。
- 一句一画面，写清主体 + 场景 + 氛围；避免抽象词。
- ⚠️ 不要生成含真实人物肖像 / 品牌 logo / 版权角色的图。

**2. 调用生图**
- POST `/api/generate`，把提炼好的 prompt 传进去。
- 拿回 `results[].path`。

**3. 回填 + 重渲染**
- **HTML**：把图片 `path` 填进 plan JSON 对应布局的 `image` 字段（progress-cards / image-text / product-gallery）→ 重新 `render_from_files`。
- **PPT**：用 `pptx_toolkit.add_image(slide, path, left, top, w, h)` 放进对应位置。

## 与图片策略的关系

| 图片策略（SKILL Step 2.5） | 生图工具的角色 |
|---|---|
| A. 有业务图 | 不用生图，直接用用户的图 |
| **B. 需要且能生成** | **用本工具**：提炼 prompt → 生成 → 回填 |
| C. 只有文字 | 不用生图，纯设计填充 |

**核心：先按图片策略规划要哪些图，再生成，再按生成的图设计版面——绝不先留白位等图。**
