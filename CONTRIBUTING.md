# 贡献指南 · Contributing to DeckSmith

欢迎贡献！DeckSmith 的目标是**用设计逻辑（而非固定模板）生成有实战架构、审美够用的中文场景演示**。无论是修 bug、加布局、补预设，还是完善设计方法论文档，都欢迎。

## 开发环境

```bash
git clone <this-repo>
cd DeckSmith
pip install -r requirements.txt   # python-pptx + lxml
# 可选：HTML 截图验证需要 playwright
pip install playwright && playwright install chromium
```

Python 3.8+。无需构建，纯脚本运行。

## 项目结构（快速定位）

| 目录 | 改这里当你想… |
|---|---|
| `deck_smith/html_renderer.py` | 加/改 HTML 布局 |
| `deck_smith/pptx_toolkit.py` | 加/改 PPT 视觉工具（渐变/形状/字体） |
| `presets/` | 加/改配色预设 |
| `skill/SKILL.md` | 改设计逻辑（材料→框架的判断流程） |
| `skill/references/` | 完善设计科学（配色/方法论/中文坑） |

## 如何扩展

### 加一个 HTML 布局

1. 在 `html_renderer.py` 加 `render_slide_xxx(s, page_num, total) -> str` 函数。
2. 注册到 `SLIDE_RENDERERS` 字典：`"xxx": render_slide_xxx`。
3. 在 `skill/references/plan-schema.md` 补字段说明。

> 记住：**布局是积木不是枷锁**。加布局是为了覆盖现有布局表达不了的信息结构，不是堆数量。

### 加一套配色预设

1. 复制 `presets/blue-orange-light.json` 改值，遵循 `schemas/preset.schema.json`。
2. 配色请按 `skill/references/color-guide.md` 的方法推导（等明度等饱和、图底关系等），不要随手拍脑袋选色。
3. 在 `presets/index.json` 登记。

## 代码规范

- Python：遵循 PEP 8，函数职责单一，工具层**不硬编码业务内容/主题色/文案**（全部调用方传入）。
- 中文场景铁律：PPT 文字走 `set_run_font`（默认微软雅黑 + ≥12pt），交付前跑 `verify_pptx.py`；细节见 `skill/references/chinese-pitfalls.md`。
- 提交演示改动前，用 `skill/references/design-logic.md` 的 Anti-AI-Slop 清单自查。

## 提交 PR

1. Fork → 新建分支 → 改动 → 自测（跑一遍 examples 确认没崩）。
2. PR 描述说清：改了什么、为什么、如何验证。
3. 涉及视觉的改动，附前后截图。

## 报 Issue

请附：DeckSmith 版本、Python 版本、复现步骤、期望 vs 实际（视觉问题附截图）。

## License

贡献即视为同意以 [MIT License](LICENSE) 授权你的贡献。
