# -*- coding: utf-8 -*-
"""DeckSmith HTML 渲染 CLI。

用法:
    python render_html.py <preset.json> <plan.json> <output.html>
"""
import argparse
import os
import sys

# 让脚本能找到 deck_smith 包(repo 根目录)
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from deck_smith.html_renderer import render_from_files


def main():
    ap = argparse.ArgumentParser(description="DeckSmith HTML 渲染器")
    ap.add_argument("preset", help="预设 JSON 路径(presets/ 下任选)")
    ap.add_argument("plan", help="plan JSON 路径(页面内容)")
    ap.add_argument("output", help="输出 HTML 路径")
    args = ap.parse_args()
    render_from_files(args.preset, args.plan, args.output)
    print(f"[OK] HTML 已生成: {args.output}")


if __name__ == "__main__":
    main()
