# -*- coding: utf-8 -*-
"""
DeckSmith · PPT 端示例：用 pptx_toolkit 积木为「省心记账 2025 复盘」搭 PPT。

演示 PPT 端"用积木现搭"的方式（不是套固定模板）——对照 plan.json（HTML 端），
同一份材料两种输出。运行：
    python build_pptx.py   →  review.pptx
"""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)

from pptx import Presentation
from pptx.util import Inches
from pptx.dml.color import RGBColor
from deck_smith import pptx_toolkit as T

# ---- 配色（与 blue-orange-light 呼应）----
BLUE      = RGBColor(0x1B, 0x3A, 0x6B)
BLUE_MID  = RGBColor(0x2E, 0x5C, 0x9E)
ORANGE    = RGBColor(0xE8, 0x76, 0x3A)
ORANGE_LT = RGBColor(0xF5, 0xA6, 0x6B)
BG        = RGBColor(0xF7, 0xF9, 0xFC)
CARD      = RGBColor(0xFF, 0xFF, 0xFF)
BORDER    = RGBColor(0xE2, 0xE7, 0xEF)
TEXT_DARK = RGBColor(0x1A, 0x2A, 0x40)
TEXT_DIM  = RGBColor(0x5A, 0x66, 0x7A)
TEXT_MUTE = RGBColor(0x94, 0x9E, 0xAE)


def page_bg(slide):
    T.add_rect(slide, 0, 0, 13.333, 7.5, fill=BG, no_line=True)
    bar1 = T.add_rect(slide, 0, 0, 13.333, 0.06, no_line=True)
    T.apply_grad_shape(bar1, [(0, BLUE, 1.0), (100, BLUE_MID, 1.0)], angle_deg=0)
    bar2 = T.add_rect(slide, 0, 0.06, 13.333, 0.04, no_line=True)
    T.apply_grad_shape(bar2, [(0, ORANGE, 1.0), (100, ORANGE_LT, 1.0)], angle_deg=0)


def header(slide, num, title, en, page, total):
    T.add_text(slide, 0.55, 0.42, 1.0, 0.7, num, size=30, color=ORANGE, bold=True,
               italic=True, anchor='middle')
    T.add_rect(slide, 1.5, 0.5, 0.03, 0.55, fill=BORDER, no_line=True)
    T.add_text(slide, 1.7, 0.42, 9.0, 0.5, title, size=22, color=BLUE, bold=True)
    T.add_text(slide, 1.7, 0.86, 9.0, 0.3, en, size=12, color=TEXT_MUTE)
    T.add_text(slide, 11.6, 0.5, 1.4, 0.4, f"{page:02d} / {total:02d}", size=12,
               color=TEXT_MUTE, align='right')


def build():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]
    TOTAL = 4

    # ---- P1 封面 ----
    s = prs.slides.add_slide(blank)
    page_bg(s)
    T.add_text(s, 0.5, 1.2, 4.0, 3.0, "25", size=200, color=RGBColor(0xEC, 0xF0, 0xF6),
               bold=True, italic=True, anchor='middle')
    T.add_text(s, 1.4, 2.0, 10.0, 0.4, "ANNUAL PRODUCT REVIEW · 2025", size=13, color=ORANGE, bold=True)
    box = T.add_text(s, 1.4, 2.5, 11.0, 1.2, "2025 年度产品复盘", size=52, color=BLUE, bold=True)
    run = box.text_frame.paragraphs[0].runs[0]
    T.apply_grad_run(run, [(0, BLUE, 1.0), (100, ORANGE, 1.0)], angle_deg=0)
    T.add_text(s, 1.42, 3.8, 10.0, 0.5, "省心记账 · 一年的增长、动作与未尽之事", size=16, color=TEXT_DIM)
    line = T.add_rect(s, 1.45, 4.5, 3.0, 0.03, no_line=True)
    T.apply_grad_shape(line, [(0, ORANGE, 1.0), (100, ORANGE_LT, 0.0)], angle_deg=0)

    # ---- P2 KPI ----
    s = prs.slides.add_slide(blank)
    page_bg(s)
    header(s, "01", "年度核心数据", "KEY METRICS", 2, TOTAL)
    T.add_text(s, 0.55, 1.5, 12.0, 0.4, "用户规模翻倍，留存与付费同步抬升", size=15, color=TEXT_DIM)
    kpis = [("420", "万", "注册用户", "▲ +133%"), ("120", "万", "月活 MAU", "▲ +85%"),
            ("58", "%", "次日留存", "▲ +13pt"), ("430", "万", "年付费收入", "▲ +210%")]
    x, w, gap = 0.55, 2.95, 0.14
    for i, (val, unit, label, trend) in enumerate(kpis):
        cx = x + i * (w + gap)
        card = T.add_grad_round_rect(s, cx, 2.4, w, 3.4,
                                     [(0, CARD, 1.0), (100, RGBColor(0xEE, 0xF3, 0xFA), 1.0)],
                                     angle=90, corner=0.06)
        T.apply_shadow(card, blur_pt=10, dist_pt=3, dir_deg=90, alpha=0.08)
        top = T.add_rect(s, cx, 2.4, w, 0.06, no_line=True)
        T.apply_grad_shape(top, [(0, BLUE, 1.0), (100, ORANGE, 1.0)], angle_deg=0)
        T.add_text(s, cx, 3.2, w, 1.0, [(val, {"size": 44, "color": BLUE, "bold": True}),
                                        (" " + unit, {"size": 18, "color": TEXT_MUTE})],
                   align='center', anchor='middle')
        T.add_text(s, cx, 4.35, w, 0.4, label, size=15, color=TEXT_DARK, align='center')
        T.add_text(s, cx, 4.85, w, 0.4, trend, size=13, color=ORANGE, align='center', bold=True)

    # ---- P3 重点成果 ----
    s = prs.slides.add_slide(blank)
    page_bg(s)
    header(s, "02", "重点动作与成果", "WHAT WE SHIPPED", 3, TOTAL)
    items = [("自动记账引擎", "短信+账单智能识别，把手动记账变自动归集", "记账耗时 -70%"),
             ("家庭账本", "多人共享账本，覆盖家庭协作记账场景", "家庭用户 38 万"),
             ("会员体系 2.0", "权益分层重构，付费路径更清晰", "付费会员 8.6 万"),
             ("年度账单 H5", "社交化年度报告，带来一波自传播拉新", "传播 PV 2400 万")]
    x, w, gap = 0.55, 2.95, 0.14
    for i, (title, desc, metric) in enumerate(items):
        cx = x + i * (w + gap)
        card = T.add_round_rect(s, cx, 2.0, w, 3.9, fill=CARD, line=BORDER, corner=0.05, no_line=False)
        T.apply_shadow(card, blur_pt=8, dist_pt=2, dir_deg=90, alpha=0.06)
        top = T.add_rect(s, cx, 2.0, w, 0.05, no_line=True)
        T.apply_grad_shape(top, [(0, BLUE, 1.0), (100, ORANGE, 1.0)], angle_deg=0)
        T.add_text(s, cx + 0.25, 2.3, w - 0.5, 0.4, f"0{i+1}", size=30, color=RGBColor(0xD6, 0xDE, 0xEA), bold=True, italic=True)
        T.add_text(s, cx + 0.25, 2.95, w - 0.5, 0.6, title, size=17, color=BLUE, bold=True)
        T.add_text(s, cx + 0.25, 3.7, w - 0.5, 1.4, desc, size=12.5, color=TEXT_DIM, line_spacing=1.4)
        T.add_rect(s, cx + 0.25, 5.25, w - 0.5, 0.02, fill=BORDER, no_line=True)
        T.add_text(s, cx + 0.25, 5.35, w - 0.5, 0.4, metric, size=14, color=ORANGE, bold=True)

    # ---- P4 致谢 ----
    s = prs.slides.add_slide(blank)
    page_bg(s)
    T.add_text(s, 0, 2.4, 13.333, 0.4, "END OF REVIEW", size=13, color=TEXT_MUTE, align='center')
    box = T.add_text(s, 0, 2.9, 13.333, 1.3, "Thank You", size=64, color=BLUE, bold=True, align='center')
    run = box.text_frame.paragraphs[0].runs[0]
    T.apply_grad_run(run, [(0, BLUE, 1.0), (100, ORANGE, 1.0)], angle_deg=0)
    T.add_text(s, 0, 4.4, 13.333, 0.5, "2025 已成，2026 再战", size=20, color=TEXT_DARK, align='center')
    T.add_text(s, 0, 5.2, 13.333, 0.4, "省心记账 · 产品与增长团队", size=13, color=TEXT_MUTE, align='center')

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review.pptx")
    prs.save(out)
    print(f"[OK] PPT 已生成: {out} ({TOTAL} 页)")

    # 交付前字体字号审计（DeckSmith 铁律）
    T.audit_text_boxes([
        ("P3 desc 01", items[0][1], 2.45, 1.4, 12, 1.4),
        ("P3 desc 02", items[1][1], 2.45, 1.4, 12, 1.4),
    ])


if __name__ == "__main__":
    build()
