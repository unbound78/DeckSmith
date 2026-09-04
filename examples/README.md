# 示例

## case_app_review · 「省心记账 2025 年度产品复盘」

一份**纯虚构**材料，展示 DeckSmith 的核心：**同一份材料 → HTML + PPT 双输出**，以及**按设计逻辑为材料设计框架**（不是套模板）。

| 文件 | 说明 |
|---|---|
| `source.md` | 原始材料（模拟输入——一段散乱的工作记录） |
| `design-notes.md` | **7-step 设计决策记录**（展示"材料 → 框架"怎么一步步推导出来） |
| `plan.json` | HTML 端 plan（设计产物） |
| `review.html` | HTML 演示产物（浏览器打开，滚动放映 7 页） |
| `build_pptx.py` | PPT 端脚本（用 `pptx_toolkit` 积木逐页现搭，示范 PPT 端做法） |
| `review.pptx` | PPT 产物（4 页，可编辑） |

跑一遍：

```bash
# HTML
python skill/scripts/render_html.py \
    presets/blue-orange-light.json \
    examples/case_app_review/plan.json \
    examples/case_app_review/review.html

# PPT
python examples/case_app_review/build_pptx.py
python skill/scripts/verify_pptx.py examples/case_app_review/review.pptx
```

> 换一份不同的材料（如议题型的预算申请），同一套设计逻辑会推导出**完全不同**的框架——这就是"给逻辑不给样子"。

## demo_plan.json

最小 HTML demo（3 页 dogfooding——用 DeckSmith 介绍 DeckSmith 自己），用于快速验证渲染器：

```bash
python skill/scripts/render_html.py presets/blue-orange-light.json examples/demo_plan.json demo.html
```
