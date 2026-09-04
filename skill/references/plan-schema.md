# DeckSmith · plan JSON 字段参考

> 何时读:写 HTML plan JSON 时(SKILL.md Step 6 渲染)。
> plan 描述每一页的布局类型 + 内容;preset 描述配色。渲染:`render_from_files(preset.json, plan.json, out.html)`。

## 顶层结构

```json
{
  "title": "演示标题",
  "slides": [
    { "layout": "cover", ... },
    { "layout": "dashboard", ... }
  ]
}
```

每个 slide 必有 `layout` 字段,取值见下表。**布局是起点积木——不够用时可在 `html_renderer.py` 加 `render_slide_xxx` 函数自定义,不受这 14 种限制。**

## 14 种布局字段

### cover（封面）
```json
{ "layout": "cover", "watermark": "25", "eyebrow": "ANNUAL REVIEW",
  "title_accent": "标题强调词", "title": "主标题", "title_en": "English Subtitle",
  "subtitle": "副标题一句话",
  "meta": [ {"label": "Date", "value": "2025", "is_cn": false} ] }
```

### dashboard（KPI 大数字网格，工作汇报型）
```json
{ "layout": "dashboard", "header": {"num": "01", "title": "年度数据", "en": "KEY METRICS"},
  "summary": "一句话概括",
  "kpis": [ {"icon": "◆", "value": "420", "unit": "万", "label": "注册用户", "trend": "▲ +133%"} ] }
```
kpis 建议 4 个（自动 4 列）；trend 可省略。

### milestone-line（横向时间线）
```json
{ "layout": "milestone-line", "header": {...}, "summary": "...",
  "nodes": [ {"month": "Q1", "event": "事件", "desc": "补充说明"} ] }
```
nodes 4-6 个最佳（横向均分）。

### progress-cards（进度卡 / 成果卡 / 方向卡）
```json
{ "layout": "progress-cards", "header": {...},
  "cards": [ {"status": "done", "status_label": "已完成", "title": "标题",
              "desc": "描述", "metric_value": "-70%", "metric_label": "指标名"} ] }
```
- `status`: `done` / `doing` / `plan`（决定状态标签颜色）。
- 有真实图片时加 `"image": "path.png"`；**无图片时不要加 image 字段**——渲染器自动切纯文字模式（高卡 + 大序号水印，不留白）。
- `metric_value`/`metric_label` 可省略；`progress`（数字百分比）仅"进行中"事项用，未启动事项不给。

### image-text（图文混排 / 编号清单）
```json
{ "layout": "image-text", "header": {...}, "image_side": "left",
  "image": "path.png",
  "items": [ {"num": "01", "title": "标题", "desc": "描述", "metric": "指标"} ] }
```
无 `image` 字段 → 自动纯文字编号清单（不留图位）。

### icon-duo（双卡图标对比，议题型）
```json
{ "layout": "icon-duo", "header": {"num": "i.", "title": "...", "en": "..."},
  "cards": [ {"icon": "⟳", "num": "1.1", "title": "标题",
              "tags": [ {"text": "标签", "style": "primary"} ]} ],
  "bottom_message": "底部一句话" }
```
tag `style`: `primary` / `warm`。

### timeline（三阶段时间线）
```json
{ "layout": "timeline", "header": {...}, "summary": "...",
  "stages": [ {"icon": "◇", "sub": "CURRENT", "title": "标题", "desc": "<strong>加粗</strong><br>换行"} ] }
```
desc 支持内联 HTML（`<strong>` / `<br>`）。

### compare-table（痛点↔诉求对照，议题型）
```json
{ "layout": "compare-table", "header": {...}, "summary": "...",
  "rows": [ {"num": "01", "pain_title": "痛点标题", "pain_text": "...",
             "ask_title": "诉求标题", "ask_text": "..."} ] }
```
> 注：表头文字（"痛点 / 协同诉求"）目前在渲染器内写死，其它语境需改 `render_slide_compare_table` 或换布局。

### split-layout（左背景+诉求 / 右价值，议题型）
```json
{ "layout": "split-layout", "header": {...},
  "background": "背景说明", "ask": "诉求说明",
  "values": [ {"icon": "◆", "title": "价值点", "desc": "..."} ] }
```
> 同上，左栏标签（背景/诉求/业务价值）内置。

### tier（阶梯分档，递进/分层）
```json
{ "layout": "tier", "header": {...}, "summary": "...",
  "tiers": [ {"num": "01", "title": "阶段", "desc": "..."} ],
  "result": "收尾结论" }
```
tiers 3 个（高度递增）。

### dual-path（双路径卡片）
```json
{ "layout": "dual-path", "header": {...}, "summary": "...",
  "paths": [ {"icon": "◆", "title": "路径", "sub": "副标", "desc": "..."} ],
  "bottom_principle": "底部原则" }
```

### chart-duo（双 ECharts 图表 + KPI 条）
```json
{ "layout": "chart-duo", "header": {...}, "summary": "...",
  "kpis": [ {"value": "...", "unit": "...", "label": "..."} ],
  "charts": [ {"title": "图表标题", "en": "EN", "insight": "洞察一句",
               "type": "bar", "data": {...}} ] }
```
> chart-duo 依赖 ECharts。演示前把 ECharts 下载到本地引用（国内 CDN 易失败，见 `chinese-pitfalls.md`）。纯文字/无图场景优先用 dashboard。

### product-gallery（产品图网格）
```json
{ "layout": "product-gallery", "header": {...}, "summary": "...",
  "summary_inline": true, "cols": 4,
  "products": [ {"image": "p.png", "title": "...", "desc": "...",
                 "revenue": "825", "revenue_label": "万元"} ] }
```
> 图片驱动布局——**无真实图片时不要用**（会留白），改用 dashboard / progress-cards 纯文字模式。

### thanks（致谢页）
```json
{ "layout": "thanks", "eyebrow": "END OF REPORT", "display": "Thank You",
  "cn": "中文收尾句", "sub": "署名 / 团队" }
```

## preset（配色）结构

```json
{
  "id": "blue-orange-light", "name": "Blue Orange Light", "name_cn": "蓝橙亮色",
  "description": "...",
  "axes": { "tone": "light", "hue_family": "mixed", "saturation": "medium", "contrast": "high" },
  "palette": { "bg": "#...", "card_top": "#...", "text": "#...", "primary": "#...",
               "accent": "#...", "...": "见 schemas/preset.schema.json" },
  "typography": { "display": "...", "body": "...", "mono": "...", "serif_cn": "..." },
  "effects": { "noise_overlay": true, "mesh_gradient": true, "card_shadow": "heavy" }
}
```
- `axes` 四轴：`tone`(dark/medium/light) / `hue_family`(warm/cool/neutral/mixed) / `saturation`(very_low/low/medium/high) / `contrast`(low/medium/high)。按场景调性选最贴的预设。
- 自定义配色 → 见 `color-guide.md` 的 RGB→色板工作流。
