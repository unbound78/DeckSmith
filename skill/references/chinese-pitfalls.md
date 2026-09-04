# 中文场景避坑指南（chinese-pitfalls）

> **这篇干嘛**：国外开源的演示生成工具（无论 PPT 还是 HTML）几乎都不解决中文特有的工程问题——中文字体在 OOXML 里的回退机制、中文按字宽估算的溢出、GBK 终端、国内 CDN 不可达……这些坑不解决，生成的中文演示会字体错乱、文字溢出卡片、图表空白、大屏看不清。本文把 DeckSmith 在实战中踩过并解决的中文场景坑，整理成 **Claude / 开发者能照着避坑的可操作清单**，每坑一个「症状 → 根因 → 解法」。这是 DeckSmith 相对国外工具的核心差异化。
>
> **何时读**：
> - 呼应 `SKILL.md` **Step 5**（大屏放映字号分级）和 **Step 7 自检**（文本溢出检测、字体三套）——写到那两步时对照本文。
> - 用 `pptx_toolkit` 生成 PPT **之前**：必看坑 1（字体三套）、坑 2（渐变质感）、坑 4（溢出预检）。
> - 用 `html_renderer` 生成 HTML 演示并要 **playwright 截图/验证** 时：必看坑 5、坑 6、坑 7、坑 8。
> - 演示要 **投屏/大屏放映** 或 **发给别的电脑打开**：必看坑 3（字号）、坑 9（CDN 本地化）。
> - 写任何 **`.bat`** 启动脚本前：看坑 10。
>
> 全文数值（`0.18in/字`、字号 pt、`30px` 阈值、`60-100px` buffer 等）都是实测校准值，改前先理解为什么是这个数。

---

## 坑 1 · 🔴 中文字体三套：`set_run_font` 必须同时写 ea / latin / cs 三个 typeface

**症状**：python-pptx 里用 `run.font.name = '微软雅黑'` 设了字体，PowerPoint 打开后中文却显示成默认宋体/等线，或者中文正常但**英文和标点（，。：；""）回退成另一种字体**，一段话里中英文字体不一致、参差不齐。

**根因**：OOXML（.pptx 底层 XML）对一个 run 的字体不是一个字段，而是**三套 typeface**，各管一类字符：
- `<a:ea>` = **East Asian**（东亚字符：中文、日文、韩文）
- `<a:latin>` = **Latin**（拉丁字符：英文字母、数字）
- `<a:cs>` = **Complex Script**（复杂文种，很多标点/符号按这套解析）

python-pptx 的 `run.font.name` **只写了 `<a:latin>`**（有时连 latin 都不完整），`<a:ea>` 缺失 → PowerPoint 渲染中文时找不到指定字体 → **回退到主题默认东亚字体**。这就是"设了字体中文还是错"的根本原因。

**解法**：三套 typeface 全写。DeckSmith 的 `pptx_toolkit.set_run_font()` 已封装好，直接用：

```python
from deck_smith.pptx_toolkit import set_run_font
# 默认微软雅黑 + ≥12pt(min_pt 兜底) + 自动写 ea/latin/cs 三套
set_run_font(run, size_pt=14, color=RGBColor(0xFF,0xFF,0xFF), bold=True)
```

它内部的关键动作（要点，理解原理用）：

```python
run.font.name = font          # python-pptx 只写 latin
run.font.size = Pt(size_pt)
rPr = run._r.get_or_add_rPr()
# 先清掉旧的三套(防叠加)
for tag in ('a:ea', 'a:latin', 'a:cs'):
    for el in rPr.findall(qn(tag)):
        rPr.remove(el)
# 🔴 三套 typeface 全部显式写同一个字体名
for tag in ('a:ea', 'a:latin', 'a:cs'):
    el = etree.SubElement(rPr, qn(tag))
    el.set('typeface', font)   # 如 '微软雅黑'
```

**铁律**：
1. **任何写文字的地方都走 `set_run_font`**，不要图省事只写 `run.font.name`——那是 latin-only，中文必回退。
2. 演讲者备注（notes）里的中文同样要写三套，否则备注区中文也回退。
3. **COM 路径**（win32com 驱动 PowerPoint）等价写法是 `run.Font.Name = '微软雅黑'` **加** `run.Font.NameFarEast = '微软雅黑'`——`NameFarEast` 就是 COM 侧的 `<a:ea>`，漏了中文照样回退。
4. 交付前跑 `scripts/verify_pptx.py` 遍历所有 run 校验 `font.name == 微软雅黑` 且 `size.pt >= 12`。

---

## 坑 2 · PPT 渐变 / 阴影 / 文字渐变：python-pptx 原生不支持，靠 XML；哪些地方必须加

**症状**：python-pptx 生成的 PPT 全是纯色块，和同内容的 HTML 演示一比"很素、很廉价"，没有高端质感。

**根因**：python-pptx 原生 API **没有渐变填充、外阴影、发光、文字渐变**这些接口。这些效果在 OOXML 里是 `<a:gradFill>` / `<a:effectLst>/<a:outerShdw>` / `<a:glow>` 等 DrawingML 标签，必须**直接操作底层 XML（lxml）**写入。纯色 PPT 与 HTML 的视觉差距，**主要来源就是渐变缺失**——补上 5 处必做渐变能拉近 70%+ 的视觉差距。

**解法**：用 `pptx_toolkit` 的三个封装（已处理好 OOXML schema 顺序，写错顺序 PowerPoint 会打不开文件）：

```python
from deck_smith.pptx_toolkit import apply_grad_shape, apply_grad_run, apply_shadow

# 形状渐变: stops=[(pos_0_100, RGBColor或(r,g,b), alpha_0_1)]
apply_grad_shape(bg, [(0,(0x02,0x06,0x17),1.0),(100,(0x12,0x1c,0x35),1.0)], angle_deg=135)
# 文字渐变(标题): 对一个 run 生效
apply_grad_run(title_run, [(0,(0x60,0xa5,0xfa),1.0),(50,(0xa7,0x8b,0xfa),1.0),(100,(0xf4,0x72,0xb6),1.0)], angle_deg=0)
# 外阴影: blur/dist 单位 pt
apply_shadow(card, blur_pt=8, dist_pt=2, dir_deg=45, alpha=0.3)
# 径向光晕(封面装饰): 用 OVAL 形状 + path_circle=True, 中心 alpha 0.2 → 边缘 alpha 0
apply_grad_shape(glow, [(0,(0x60,0xa5,0xfa),0.20),(100,(0x60,0xa5,0xfa),0.0)], path_circle=True)
```

**5 处必做渐变清单**（PPT 想对齐 HTML 质感时逐项加，缺一处就"素"一分）：

| # | 位置 | 渐变方案 |
|---|---|---|
| 1 | **整页背景** | 主色 → 副色（如 `#020617 → #121c35`，angle 135°）|
| 2 | **大标题文字** | 多色文字渐变（如 蓝→紫→粉，angle 0° 横向）|
| 3 | **卡片背景** | 细微 亮 → 暗（如 `#1a253c → #101a2e`，angle 135°）|
| 4 | **accent 横条** | 颜色 → 透明（angle 0°，pos 0→100 对应 alpha 1→0）|
| 5 | **底部 banner** | 多色（如 暗金→暗粉→暗紫，angle 135°）|

**写 XML 的关键约束**（用封装就不用操心，但理解原理防踩坑）：
1. **`<a:gradFill>` 的位置**：在形状 `spPr` 里必须排在 `<a:ln>` **之前**；在文字 `rPr` 里必须排在 `<a:ln>` **之后**。顺序错 → PowerPoint 报文件损坏打不开。
2. `pos` 单位 = 1000 × 百分比（100% = `100000`）。
3. `alpha` 单位同样 = 100000（100% = `100000`）。
4. `ang`（角度）单位 = 60000 × 度数（90° = `5400000`）。
5. 移除已有 fill 时要**扫全 5 个标签**：`solidFill / gradFill / noFill / blipFill / pattFill`，只删一个会残留。
6. **单个 `<a:gradFill>` 的线性角度只支持 0/90/180/270**——要"横向多色渐变条"得用**多段矩形拼接**，每段独立渐变。

**暗色背景上的图表适配**（python-pptx 原生图表默认黑色轴/网格，在暗底看不见）：轴标签字体改白色 `axis.tick_labels.font.color.rgb`、网格线改深灰或隐藏、图例/数据标签改白色或强调色。

> **铁律**：不要交付纯色块 PPT。渐变/阴影/文字渐变是 DeckSmith PPT 的质感来源，是"够用审美"的底线。

---

## 坑 3 · 大屏放映字号分级：PC 上合适的字号，大屏缩水约 25%

**症状**：在自己电脑（22-27 寸显示器、0.5 米距离）上调得刚好的字号，投到会议室大屏 / 80 寸屏 / 投影（5-10 米距离观看）后，反馈"字太小看不清"。

**根因**：观看距离和屏幕尺寸变了，**同样的字号在大屏的视觉占比缩水约 25%**。正文受影响最大（本来就小），大字影响小（本来就大）。

**解法 A · HTML 端（`clamp()` rem 分档放大）**：写第一版时就按观看场景分三档放大 `clamp(min, vw, max)`：

| 字号档 | 判据（max 值） | 放大比例 | 典型元素 |
|---|---|---|---|
| **大字** | max > 5rem | **+10%**（本来已很大，过头会撑破）| 封面大标题、章节大数字、致谢页 |
| **中字** | max 2–5rem | **+15%** | 章节标题、页面主标题 |
| **正文/标签** | max < 2rem | **+25%**（受益最大）| 正文、卡片描述、图注、标签 |

做法：写完 HTML 第一版 → 正则批量放大三档 → playwright 复测溢出 → 局部微调。**副作用**：padding/margin/gap 不动的话，字号放大后内容更挤；若再往上放大（+30% 以上）要同步加 padding/gap 防拥挤。

**解法 B · PPTX 端（pt 字号梯度表）**：`12pt` 是**底线不是默认终点**——关键元素要往 13-18pt 甚至更高走，否则大屏上所有字看起来一个量级、没有视觉层级。

| 角色 | 字号 pt | 用法 |
|---|---|---|
| 大数字 / KPI 主值 | **22–32** | 卡片中心大数字 |
| 章节大主标 | **18–22** | 大块 banner 主句 |
| 页面命题 summary（一句话总结）| **16** | 页面顶部叙事核心，必 ≥16 |
| 序号符号（壹/贰/叁 等）| **18** | 落点条章节符号 |
| 支柱名 / 板块名 | **14** | 落点条名称 |
| 卡片标题 | **14** | 行动卡 / KPI 卡标题 |
| 强调性小标签 | **14**（不是 12）| 如"本页目标"框里的指标名 |
| 关键注释 | **14** | 强调性补充说明 |
| 一般 hint / 长描述正文 / 普通备注 | **12**（绝对底线）| 辅助性文字 |

**判别口诀**：写到 12pt 时自问"这个元素要不要被读者注意到？"——要 → 至少 13pt；只是辅助说明 → 12pt 可以。**任何带强调意图的元素都不许 12pt。**

---

## 坑 4 · 🔴 中文文本溢出预检：`autofit=NONE` 不报错，只是默默溢出

**症状**：PPT 生成脚本跑通、无任何报错，但 PowerPoint 打开后**文字超出卡片底部**、盖住下方元素（如长描述穿透到下面的大数字上）。HTML 端 1080p 检测全过的内容，PPTX 里仍可能溢出。

**根因**：
1. python-pptx 文本框默认 `autofit=MSO_AUTO_SIZE.NONE`——**文字装不下时不缩字、不扩框、不报错，直接溢出画面**。它不像 HTML 会撑高父容器。
2. python-pptx 按"字号 × 行距 × 字符数 / 宽度"估算的高度，和 PowerPoint 实际渲染有**微差异**（字宽/字距/字体回退），实际渲染行数常常更多。
3. 中文没有空格断词，一个卡片能塞多少字，取决于**每字物理宽度**——这需要专门的中文估算法。

**解法：中文按字宽估算 + 交付前批量审计**。核心经验值：**中文 12pt ≈ 0.18 in / 字**（含字间距 + 标点占位），字号线性缩放。`pptx_toolkit` 已内置三函数：

```python
from deck_smith.pptx_toolkit import estimate_text_height, verify_text_fit, audit_text_boxes

# 估算一段中文在给定宽度文本框里需要的最小高度(英寸)
need_in = estimate_text_height(text, w_in=5.1, size_pt=12, line_spacing=1.35)
```

`estimate_text_height` 的算法（要点）：
```python
char_w = (size_pt / 12.0) * 0.18          # 🔴 中文 12pt 基准 0.18 in/字, 线性缩放
avail_w = max(w_in - 0.10, 0.1)           # 扣左右内边距
chars_per_line = max(int(avail_w / char_w), 1)
n_lines = (len(text) + chars_per_line - 1) // chars_per_line  # 向上取整
return n_lines * (size_pt / 72.0) * line_spacing + 0.06       # +0.06 上下 padding
```

**交付前必跑审计**（把所有长 desc 注册进清单，一次性查全）：
```python
cases = [
    # (label, text, w_in, h_in, size_pt, line_spacing)
    ("P4 行动 01", action_text, 5.1, 0.80, 12, 1.35),
    # ... 所有长描述文本框全部注册
]
fails = audit_text_boxes(cases)   # 打印逐项 [OK]/[BAD] + 每个溢出项要加大到多少
if fails:
    print(f">>> {fails} 项溢出, 请修复后再交付")
```

**三种修复策略**（按"会不会挤到别的元素"选）：

| 多出字数 | 策略 |
|---|---|
| 1–2 字 | A. 略微拉长本框 |
| 半行–1 行 | B. 拉长本框 + 同步下移底邻框（保持卡片不撞底）|
| ≥ 2 行 | C. 缩文字 + 略拉框（避免连带失衡）|

**版式层预防铁律**：
1. **任何文字描述框 height 留 30-50% buffer**（预计 2.0 in 就给 2.6 in），不要"刚好卡进去"。
2. **长文本永远放卡片最底部**（垂直方向最后一个元素）——不和任何元素相邻，溢出最多撞卡片底、PowerPoint 自动裁切，不会穿透压别的元素。反模式是"长描述 + 大数字相邻"，描述一溢出就盖住数字。
3. 保证 `desc_top + desc_height < 下一元素_top`（含 buffer）。
4. **Windows GBK 终端**：审计打印标记必须用 ASCII `[OK]` / `[BAD]`，**不要用 ✓/✗**（U+2713 等在 GBK 下 `UnicodeEncodeError`）。

> ⚠️ **审计 0 溢出是"必要不充分"**：`audit_text_boxes` 只查"单框内文字装不装得下"，**管不了框与框之间的遮挡/越界**（浮标压表格行、图片压图注、圆角越界等）。高保真交付时仍要导 PNG 逐页 Read 复核。

---

## 坑 5 · 🔴 playwright 截图 + scroll-snap reveal class 陷阱

**症状**：给 scroll-snap 风格的 HTML 演示（每页 `.reveal` 元素 + IntersectionObserver 入场动画）做 playwright 截图，截出来的图**核心内容元素全部缺失**（只有背景和标题，正文/卡片不见了）；而且 overflow 检测报"0 溢出"，看起来"测试通过"，实际内容根本没渲染。

**根因**：`.reveal` 元素初始 `opacity: 0`，只有父 `.slide` 拿到 `.active` class（由 IntersectionObserver 滑入视口触发）才 `opacity: 1` 显示：
```css
.reveal { opacity: 0; transform: translateY(24px); transition: opacity 1s; }
.slide.active .reveal { opacity: 1; transform: translateY(0); }
```
playwright 用 `scrollIntoView` 滚到目标页，**在 headless 截图环境里不会可靠触发 IntersectionObserver 切换 `.active`**。后果：截图里 reveal 内容全是 `opacity:0` 不可见；而**隐藏元素不计入 overflow**，所以溢出检测假阳性报 0。

**解法：截图前用 `evaluate` 强制切换 active，再等动画跑完**：
```python
await page.evaluate(f"""
    (() => {{
        const slides = document.querySelectorAll('.slide');
        slides.forEach((s, j) => s.classList.toggle('active', j === {i}));
        slides[{i}].scrollIntoView({{behavior:'instant'}});
    }})()
""")
await asyncio.sleep(2.0)   # 让 reveal transition(1s) + stagger delay(最多 0.7s) 跑完
```
单页长卷（非 scroll-snap）同理：`document.querySelectorAll('.rv').forEach(e => ...)` 或直接注入 `beforeprint` 钩子把动画元素强制显示。

**通用判读铁律**：**playwright「0 overflow + 0 error」≠ 视觉验证通过**。任何 `.reveal` / `.fade-in` / `.slide-up` 类动画演示，截图后**必须逐张 Read 确认内容真的渲染出来了**，不能只看 playwright 维度的"绿"。

---

## 坑 6 · HTML 三层溢出检测：单一 bbox 检测有盲区

**症状**：只用 `getBoundingClientRect()` 比较子元素 bottom 与页面 bottom 的检测报"0 溢出"，但浏览器里明显看到**内容被切掉 / 显示不全 / 底部内容贴着页脚重叠**。

**根因**：单靠 bbox 有两个抓不到的盲区：
- **盲区一**：被 `overflow:hidden` 切掉的子元素，其 `bbox.bottom` 仍在父边界内（因为已经被切了），bbox 检测看不出，实际内容已丢。
- **盲区二**：`position:absolute` 的页脚（`bottom:固定`）脱离文档流，内容溢出向下延伸和它视觉重叠时，bbox（footer 在边界内）和 scrollHeight（footer 不在 flow、不增高）**两个都抓不到**。

**解法：三层检测缺一不可**：

```js
// 层 1 · bbox 边界溢出(子元素 bottom 超出父 slide)
// 层 2 · scrollHeight 真溢出(抓 overflow:hidden 切掉的内容)
const scrollOver = slide.scrollHeight - slide.clientHeight;   // >阈值 = 真溢出
slide.querySelectorAll('*').forEach(el => {
  const over = el.scrollHeight - el.clientHeight;
  if (over > 0 && el.clientHeight > 0) culprits.push({cls: el.className, over});
});
// 层 3 · absolute 页脚重叠(内容最低 bottom vs footer top)
const ft = slide.querySelector('.page-footer');
if (ft) {
  const ftTop = ft.getBoundingClientRect().top;
  let maxB = 0;
  slide.querySelectorAll('*').forEach(el => {
    if (el.closest('.page-footer')) return;
    const tg = el.tagName.toLowerCase();
    if (tg==='script'||tg==='style') return;
    const eb = el.getBoundingClientRect().bottom;
    if (eb > maxB) maxB = eb;
  });
  footerOverlap = Math.round(maxB - ftTop);   // >2px = 内容侵入页脚
}
```

**阈值经验**：`scrollHeight-clientHeight` **≤ 30px 视为盒模型 quirk**（box-shadow/margin 累加，视觉无影响，忽略）；**> 30px 视为真溢出必修**。footer 重叠 **> 2px 就算侵入**。

**修复手法**：
- grid 内容撑大 → `grid-template-rows` 用 `minmax(0,1fr)`（默认 `minmax(auto,1fr)` 会被内容撑高）+ 子元素 `min-height:0; overflow:hidden`。
- 页脚重叠 → 给该页内容容器加 `padding-bottom`（比缩字号有效——缩字号会被 flex 兄弟元素吸收、总高不变）。

**跨浏览器铁律**：headless chromium 渲染 ≠ 用户真实浏览器（`clamp()` 取值、DPI 缩放、字体回退、line-height 都有差异）。**playwright 通过是必要非充分条件**。CSS 收紧时**主动留 60-100px buffer**，把内容高度控制在视口的 **90%**（1080px 视口内 content 目标 ≤ 970px），给跨设备渲染差异留容错。**宁可"装舒服"，不要"刚好挤满"。**

---

## 坑 7 · CSS 类名冲突：长演示多页共用前缀，后定义覆盖先定义

**症状**：多页（10+ 页）演示里，新加的某页做完后，**之前某页的元素"位置乱了 / 尺寸变了"**——明明没动那页。

**根因**：多页复用同名 class 前缀（如 `.node` / `.card-` / `.action-`），**后定义的 CSS 规则覆盖先定义的**。例如第 1 页封面的 `.node` 是紧凑小节点，第 3 页新加的 `.node` 定义了更大尺寸 → 第 1 页的节点被连带变大、位置错乱。CSS 是全局的，同名类不隔离。

**解法（二选一）**：
1. **独立前缀**：每页用 `.p1-` / `.p2-` / `.p3-` 前缀彻底命名隔离（推荐，最干净）。
2. **容器作用域限定**：`.diagram-a .node {}` vs `.diagram-b .node {}`，用父容器隔离。

**排查方法**（用户反馈"位置乱了"时第一步）：
```bash
grep -nE "^\.node(-center)? \{" your.html   # 看同名 CSS 是否多次定义
grep -nE 'class="node(-center)?' your.html   # 看 HTML 哪几处在用
```

**预防铁律**：新增页要复用现有视觉模板（飞轮/卡片/时间线）前，**先 grep 已有 class 名**，确认是新建 namespace 还是有意复用。

**连带坑（同源）**：做过"容器作用域批量配色"（如 `.track .tr .dn-tags b {}`，特异性 0,3,1）后，**后写的所有状态类**（`.hot`/`.active`/`.warn`）都要带**同级或更高的作用域前缀**，否则特异性不足被压掉 background，高亮标签变成白字压浅底不可读。这类 bug **不报错、playwright 检测不出，只能靠 Read 截图发现**。

---

## 坑 8 · 装饰伪元素溢出伪报判别：≤30px 恒定量是盒模型 quirk

**症状**：scrollHeight 溢出检测报了 N 处 `clipped`，类名全是带 `overflow:hidden` 的卡片（`.tr-head` / `.val` 之类），但看截图**文字并没有缺失**。

**根因**：这些卡片故意用 `::before` / `::after` 放**超出边界的装饰**（圆形色块、大号水印数字、装饰圆环），被 `overflow:hidden` 裁掉是**设计意图**，但 `scrollHeight - clientHeight` 把它算成了溢出。

**判别法**（真溢出 vs 伪报）：
- **溢出量恒定**——同类卡片全是同一个数字（如三张卡都报 42）→ **装饰伪元素，伪报**，不用管。
- **溢出量各不相同、且与文字长度相关** → **真内容被切**，必修。
- 阈值上：**≤ 30px** 基本是盒模型计算 quirk（box-shadow/margin 累加或装饰伪元素），视觉无影响；**> 30px** 才当真溢出排查。

**解法**：不要为消警告去掉装饰；看截图确认无文字缺失即可放行。playwright 元素截图还有个相关伪影——会把 `position:fixed` 元素（如顶部进度条）一起拍进某段图里，判别法是"伪影横贯全宽、位置随滚动变化"→ 截图伪影而非缺陷，要干净图就截图前临时 `display:none` 掉 fixed 元素。

---

## 坑 9 · 第三方 CDN 本地化：echarts / 字体 CDN 国内易失败

**症状**：playwright 测试或用户打开演示时，图表**完全空白**（chart count = 0）；控制台报 `ERR_CONNECTION_CLOSED`。字体则回退成系统默认、排版走样。

**根因**：`jsdelivr` / `fonts.googleapis.com` 等国外 CDN 在国内**经常不可达**（连接被重置/超时）。依赖 CDN 的 echarts 拉不到 → 图表不渲染；Google Fonts 拉不到 → 中文字体回退乱套。会议室大屏 / 内网 / 公网不稳定环境尤其常见。

**解法（分场景）**：

1. **开发/一般放映**：把第三方 JS/CSS **下载到本地**引用。国内可达 CDN 优先 `bootcdn.net`，备用 `staticfile.org` / `lib.baomitu.com` / `cdnjs.cloudflare.com`。改成 `<script src="./echarts.min.js"></script>`。
   - **副作用**：HTML 文件移动时必须带上同目录的本地 js——在项目说明里记明。

2. **要发给别人打开（微信/邮件/U 盘，离线交付）**：做**完全离线单文件**——
   - **JS 内联**：把 echarts.min.js 内容嵌进 HTML 的 `<script>` 标签内。**前置检查** `grep -c '</script>' echarts.min.js` 必须为 0，否则字符串会破坏 HTML 结构（压缩版 echarts 安全，自定义 js 不一定）。
   - **字体去 CDN**：移除 Google Fonts `<link>`，CSS 变量改纯系统字体 fallback（国内 Windows/Mac 都有，0 依赖，视觉略变但可靠）：
     ```css
     --f-display: Georgia, 'Times New Roman', Cambria, STSong, '宋体', serif;
     --f-body:    -apple-system, 'Segoe UI', 'Microsoft YaHei', '微软雅黑', sans-serif;
     --f-serif-cn:STSong, SimSun, '宋体', 'Source Han Serif SC', serif;
     ```

**元规则**：**任何要在内网 / 会议室大屏 / 公网不稳定环境放映的 HTML 演示，第一版就把所有第三方依赖（echarts、字体、Chart.js 等）本地化**——不要等现场才发现 CDN 不通。用 PowerShell `Invoke-WebRequest -Uri '...' -Method Head` 可预先验证某 CDN 是否可达。

---

## 坑 10 · Windows `.bat` 中文编码（简要）

**症状**：双击写好的 `.bat` 启动脚本，中文显示乱码，或直接报 `'某某' 不是内部或外部命令`——整行逻辑失效。

**根因**：cmd.exe 用 **GBK** 解码 .bat 文件。若文件存成 UTF-8，或 `rem` 注释/`echo` 里有中文，cmd.exe 会误解码，把中文字节当成命令，整行报错。

**解法**：**.bat 文件强制 ASCII-only**——所有中文逻辑（提示语、注释、含中文的处理）放到 `.ps1`（PowerShell）或 `.py`（Python）里，让 .bat 只做一件事：调那个脚本。
```bat
@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0run.ps1"
```
不要试图在 .bat 里转码/加 `chcp 65001` 硬撑——那些方法不稳定、经常失败。**"bat 只当启动器、中文全外放"是唯一可靠方案。**

---

## 交付前速查清单（中文场景专项）

```
PPT 端：
□ 所有文字都走 set_run_font(写 ea/latin/cs 三套)，没有裸 run.font.name
□ 5 处必做渐变到位(背景/标题/卡片/accent/banner)，不是纯色块
□ audit_text_boxes() 全 [OK]，无 [BAD] 溢出
□ 关键元素字号按梯度表(命题≥16/序号 18/强调标签 14)，12pt 只给辅助文字
□ 审计打印用 ASCII [OK]/[BAD]，无 ✓✗ emoji(防 GBK 报错)
□ scripts/verify_pptx.py 通过(微软雅黑 + ≥12pt)

HTML 端：
□ playwright 截图前强制切 .active/.rv，逐张 Read 确认内容真渲染出来
□ 三层溢出检测(bbox + scrollHeight-clientHeight + footer 重叠)全过
□ 溢出量 ≤30px 且恒定 = 装饰伪报，忽略；>30px 且随文字变 = 真溢出，修
□ 多页 class 用独立前缀(.p1-/.p2-)或容器作用域，grep 过无同名冲突
□ 内容高度控制在视口 90%，留 60-100px 跨浏览器 buffer

放映/交付：
□ 大屏放映 → 字号分档放大(正文+25%/中字+15%/大字+10%)
□ 投屏/内网/离线 → echarts + 字体 CDN 本地化(或内联成单文件)
□ .bat 启动脚本 ASCII-only，中文逻辑放 .ps1/.py
```
