"""
HTML 渲染器 (Stage B)
输入：
- preset JSON（色板 + 字体 + 效果）
- plan JSON（页面列表：每页的布局类型 + 内容）
输出：
- 一份完整的 HTML 文件

布局类型支持（与 color_theory_design.md 验证过的 8 种对应）：
- cover: 封面
- icon-duo: 双卡图标对比
- timeline: 三阶段时间线
- compare-table: 对照表
- split-layout: 左右双栏
- tier-diagram: 阶梯分档
- dual-path: 双路径卡片
- thanks: 谢谢页
"""
import json
from pathlib import Path
from typing import Any


def render_css_vars(palette: dict) -> str:
    """Convert palette dict to CSS custom properties."""
    lines = [":root {"]
    mapping = {
        "bg": "--bg", "bg_soft": "--bg-soft",
        "card_top": "--card-top", "card_bottom": "--card-bottom",
        "border": "--border-color",
        "text": "--text", "text_dim": "--text-dim",
        "text_mute": "--text-mute", "text_faint": "--text-faint",
        "primary": "--primary", "primary_mid": "--primary-mid",
        "primary_bright": "--primary-bright", "primary_soft": "--primary-soft",
        "primary_pale": "--primary-pale", "primary_wash": "--primary-wash",
        "accent": "--accent", "accent_soft": "--accent-soft",
        "accent_pale": "--accent-pale", "accent_wash": "--accent-wash",
    }
    for k, v in mapping.items():
        if k in palette:
            lines.append(f"  {v}: {palette[k]};")
    lines.append("}")
    return "\n".join(lines)


def render_base_css(preset: dict) -> str:
    """Core CSS (layout-agnostic)."""
    typo = preset.get("typography", {})
    f_display = typo.get("display", "Cormorant, serif")
    f_body = typo.get("body", "sans-serif")
    f_mono = typo.get("mono", "monospace")
    f_serif_cn = typo.get("serif_cn", "serif")
    tone = preset["axes"]["tone"]

    # Tone-specific background texture
    if tone == "dark":
        texture = """
.slide::before {
  content: ''; position: absolute; inset: 0; z-index: 0;
  background:
    radial-gradient(ellipse 60% 45% at 18% 12%, rgba(255,240,213,0.06), transparent 55%),
    radial-gradient(ellipse 70% 60% at 88% 90%, rgba(62,56,49,0.35), transparent 60%),
    radial-gradient(ellipse 90% 80% at 50% 50%, rgba(10,9,7,0.35) 50%, transparent 85%);
  pointer-events: none;
}"""
    else:  # light / medium
        texture = """
.slide::before {
  content: ''; position: absolute; inset: 0; z-index: 0;
  background-image:
    radial-gradient(circle at 1px 1px, var(--border-color) 1px, transparent 0);
  background-size: 28px 28px;
  pointer-events: none;
  opacity: 0.4;
}
.slide::after {
  content: ''; position: absolute; inset: 0; z-index: 1;
  background:
    radial-gradient(ellipse 50% 40% at 0% 0%, var(--primary-wash) 0%, transparent 60%),
    radial-gradient(ellipse 45% 35% at 100% 100%, var(--accent-wash) 0%, transparent 55%);
  opacity: 0.5;
  pointer-events: none;
}"""

    return f"""
*, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{
  background: var(--bg);
  color: var(--text);
  font-family: {f_body};
  font-weight: 300;
  font-size: 16px;
  line-height: 1.6;
  height: 100vh; height: 100dvh;
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
}}

.deck {{
  height: 100vh; height: 100dvh;
  width: 100vw;
  overflow-y: scroll; overflow-x: hidden;
  scroll-snap-type: y mandatory;
  scroll-behavior: smooth;
  scrollbar-width: none;
}}
.deck::-webkit-scrollbar {{ display: none; }}

.slide {{
  position: relative;
  height: 100vh; height: 100dvh;
  width: 100%;
  scroll-snap-align: start;
  scroll-snap-stop: always;
  padding: clamp(2.8rem, 5vh, 4.5rem) clamp(4.5rem, 9vw, 10rem);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}}
.slide > * {{ position: relative; z-index: 2; }}
{texture}

/* Typography helpers */
.accent {{ color: var(--accent); font-weight: 500; }}
.primary-text {{ color: var(--primary); font-weight: 500; }}

.eyebrow {{
  font-weight: 500;
  font-size: clamp(0.7rem, 0.82vw, 0.88rem);
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: var(--primary-mid);
}}

/* Reveal animations */
.reveal {{
  opacity: 0; transform: translateY(24px);
  transition: opacity 1s cubic-bezier(0.2,0.8,0.2,1), transform 1s cubic-bezier(0.2,0.8,0.2,1);
}}
.slide.active .reveal {{ opacity: 1; transform: translateY(0); }}
{"".join(f'.slide.active .reveal[data-d="{i}"] {{ transition-delay: {0.10 + i*0.12:.2f}s; }} ' for i in range(1, 9))}
.reveal.blur-in {{ filter: blur(8px); }}
.slide.active .reveal.blur-in {{ filter: blur(0); }}
.reveal.scale-in {{ transform: translateY(24px) scale(0.96); }}
.slide.active .reveal.scale-in {{ transform: translateY(0) scale(1); }}

/* Page header */
.page-header {{
  display: flex; align-items: center;
  gap: clamp(1rem, 1.6vw, 1.5rem);
  margin-bottom: clamp(1.6rem, 3vh, 2.8rem);
  position: relative;
}}
.page-header::after {{
  content: ''; position: absolute; bottom: -0.6rem; left: 0; right: 30%;
  height: 1px;
  background: linear-gradient(90deg, var(--border-color), transparent);
}}
.page-header .num-badge {{
  font-family: {f_display}; font-style: italic; font-weight: 600;
  font-size: clamp(2.4rem, 3.4vw, 3.6rem);
  color: var(--accent);
}}
.page-header .tick {{
  width: 3px; height: clamp(32px, 3.2vw, 44px);
  background: linear-gradient(180deg, var(--primary), var(--primary-soft));
  border-radius: 2px;
}}
.page-header .h-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1.3rem, 1.8vw, 1.9rem);
  color: var(--primary);
}}
.page-header .h-en {{
  font-weight: 300;
  font-size: clamp(0.6rem, 0.72vw, 0.78rem);
  letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--text-mute); margin-top: 4px;
}}
.page-header .h-spacer {{ flex: 1; }}
.page-header .h-meta {{
  font-family: {f_mono};
  font-size: clamp(0.72rem, 0.85vw, 0.92rem);
  color: var(--text-faint);
}}
.page-footer {{
  position: absolute; left: 0; right: 0;
  bottom: clamp(1rem, 1.6vh, 1.4rem);
  text-align: center;
  font-size: clamp(0.6rem, 0.7vw, 0.74rem);
  letter-spacing: 0.3em;
  color: var(--text-faint);
}}

/* Card */
.card {{
  background: linear-gradient(180deg, var(--card-top) 0%, var(--card-bottom) 100%);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  position: relative; overflow: hidden;
}}
.card .card-accent {{
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--primary-bright), var(--accent));
}}

/* ========== Cover ========== */
.cover {{ justify-content: center; align-items: center; }}
.cover-inner {{
  display: grid; grid-template-columns: 1.3fr 1fr;
  gap: clamp(3rem, 6vw, 6rem); align-items: center;
  max-width: 1200px; width: 100%;
}}
.cover-watermark {{
  position: absolute; top: 48%; left: 2%; transform: translateY(-50%);
  font-family: {f_display}; font-weight: 700;
  font-size: clamp(16rem, 24vw, 26rem);
  color: var(--border-color);
  opacity: 0.15;
  line-height: 0.75; z-index: 0; pointer-events: none;
}}
.cover-title {{
  font-family: {f_serif_cn}; font-weight: 700;
  font-size: clamp(2.8rem, 5.8vw, 5.2rem); line-height: 1.08;
  color: var(--primary);
}}
.cover-title .yr {{
  background: linear-gradient(100deg, var(--accent) 0%, var(--accent-soft) 100%);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
}}
.cover-title-en {{
  font-family: {f_display}; font-style: italic;
  font-size: clamp(1.05rem, 1.5vw, 1.6rem);
  color: var(--text-mute);
  margin-top: clamp(0.3rem, 0.6vh, 0.5rem);
}}
.cover-line {{
  width: clamp(60px, 8vw, 100px); height: 2px;
  background: linear-gradient(90deg, var(--accent), var(--primary-soft));
  margin: clamp(1.4rem, 2.5vh, 2rem) 0; border: 0;
}}
.cover-sub {{
  font-size: clamp(0.9rem, 1.1vw, 1.08rem);
  color: var(--text-dim);
}}
.cover-meta {{
  display: grid; gap: clamp(1.2rem, 2vh, 1.8rem);
  padding: clamp(2rem, 3.2vh, 3rem);
  background: linear-gradient(180deg, var(--card-top), var(--card-bottom));
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  position: relative; overflow: hidden;
}}
.cover-meta::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
}}
.cover-meta .m-label {{
  font-family: {f_mono}; font-size: clamp(0.6rem, 0.72vw, 0.78rem);
  letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--accent-soft);
}}
.cover-meta .m-value {{
  font-family: {f_display}; font-weight: 600;
  font-size: clamp(1.4rem, 1.8vw, 2rem);
  color: var(--primary); margin-top: 0.15rem;
}}
.cover-meta .m-value-cn {{
  font-family: {f_serif_cn};
  font-size: clamp(1.2rem, 1.6vw, 1.7rem);
  color: var(--text);
}}

/* ========== Icon Duo ========== */
.icon-duo {{
  flex: 1; display: flex; flex-direction: column;
  justify-content: center;
  max-width: 1180px; margin: 0 auto; width: 100%;
  gap: clamp(1.8rem, 3.5vh, 2.8rem);
}}
.icon-duo-row {{
  display: grid; grid-template-columns: 1fr 1fr;
  gap: clamp(1.8rem, 3vw, 2.6rem);
}}
.icon-card {{
  padding: clamp(2rem, 3vw, 2.8rem);
  display: flex; flex-direction: column;
  gap: clamp(0.9rem, 1.6vh, 1.2rem);
}}
.icon-card .ik-icon-wrap {{
  width: clamp(68px, 5.5vw, 82px); height: clamp(68px, 5.5vw, 82px);
  border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.8rem, 2.4vw, 2.2rem);
  background: linear-gradient(135deg, var(--primary-wash), var(--primary-pale));
  color: var(--primary);
}}
.icon-card:nth-child(2) .ik-icon-wrap {{
  background: linear-gradient(135deg, var(--accent-wash), var(--accent-pale));
  color: var(--accent);
}}
.icon-card .ik-num {{
  font-family: {f_display}; font-style: italic;
  font-size: clamp(0.88rem, 1.05vw, 1.1rem);
  color: var(--accent);
}}
.icon-card .ik-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1.35rem, 1.75vw, 1.8rem);
  color: var(--text); line-height: 1.25;
}}
.icon-card .ik-divider {{
  height: 1px;
  background: linear-gradient(90deg, var(--border-color), transparent 70%);
}}
.icon-card .ik-points {{ display: flex; flex-wrap: wrap; gap: 0.5rem; }}
.ik-tag {{
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 1rem; border-radius: 8px;
  font-size: clamp(0.8rem, 0.92vw, 0.96rem);
}}
.ik-tag.primary {{
  background: var(--primary-wash);
  color: var(--primary-mid);
  border: 1px solid var(--border-color);
}}
.ik-tag.warm {{
  background: var(--accent-wash);
  color: var(--accent-soft);
  border: 1px solid var(--border-color);
}}
.ik-tag::before {{
  content: ''; width: 6px; height: 6px;
  border-radius: 50%; flex-shrink: 0;
}}
.ik-tag.primary::before {{ background: var(--primary-bright); }}
.ik-tag.warm::before {{ background: var(--accent-soft); }}
.icon-duo-bottom {{
  text-align: center;
  padding: clamp(1rem, 1.8vh, 1.4rem) clamp(2rem, 3vw, 2.4rem);
  border-radius: 10px;
  background: linear-gradient(90deg, var(--primary-wash), var(--card-top) 50%, var(--accent-wash));
  border: 1px solid var(--border-color);
}}
.icon-duo-bottom span {{
  font-family: {f_serif_cn};
  font-size: clamp(0.95rem, 1.1vw, 1.14rem);
  color: var(--primary-mid); font-weight: 500;
}}

/* ========== Timeline ========== */
.timeline-page {{
  flex: 1; display: flex; flex-direction: column;
  justify-content: center;
  max-width: 1100px; margin: 0 auto; width: 100%;
  gap: clamp(2.5rem, 5vh, 4rem);
}}
.timeline-summary {{
  text-align: center; font-family: {f_serif_cn};
  font-size: clamp(1.05rem, 1.25vw, 1.28rem); color: var(--text-dim);
  line-height: 1.9; max-width: 50ch; margin: 0 auto;
}}
.timeline-track {{
  display: grid; grid-template-columns: 1fr auto 1fr auto 1fr;
  align-items: start;
}}
.tl-stage {{ text-align: center; padding: 0 clamp(0.5rem, 1vw, 1rem); }}
.tl-stage .tl-node {{
  width: clamp(76px, 6.5vw, 92px); height: clamp(76px, 6.5vw, 92px);
  border-radius: 50%; margin: 0 auto clamp(1.2rem, 2.2vh, 1.8rem);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.6rem, 2.2vw, 2rem);
}}
.tl-stage.tl-current .tl-node {{
  background: var(--bg); border: 2px dashed var(--text-faint); color: var(--text-mute);
}}
.tl-stage.tl-mid .tl-node {{
  background: var(--primary-wash); border: 2px solid var(--primary-soft); color: var(--primary-mid);
}}
.tl-stage.tl-future .tl-node {{
  background: linear-gradient(135deg, var(--primary), var(--primary-mid));
  border: none; color: white; box-shadow: 0 6px 28px rgba(0,0,0,0.15);
}}
.tl-stage .tl-sub {{
  font-family: {f_mono}; font-size: clamp(0.62rem, 0.74vw, 0.78rem);
  letter-spacing: 0.2em; color: var(--accent);
  margin-bottom: clamp(0.4rem, 0.8vh, 0.6rem);
}}
.tl-stage .tl-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1.15rem, 1.4vw, 1.45rem);
  color: var(--text); margin-bottom: clamp(0.5rem, 1vh, 0.8rem);
}}
.tl-stage .tl-desc {{
  font-size: clamp(0.8rem, 0.92vw, 0.96rem);
  color: var(--text-mute); line-height: 1.6;
}}
.tl-stage .tl-desc strong {{ color: var(--primary-mid); font-weight: 500; }}
.tl-arrow {{ display: flex; align-items: center; padding-top: clamp(34px, 3.2vw, 42px); }}
.tl-arrow .tl-line {{
  width: clamp(36px, 3.5vw, 52px); height: 2px;
  background: linear-gradient(90deg, var(--primary-soft), var(--primary-mid));
  position: relative; border-radius: 1px;
}}
.tl-arrow .tl-line::after {{
  content: ''; position: absolute; right: -5px; top: -4px;
  width: 10px; height: 10px;
  border-top: 2px solid var(--primary-mid); border-right: 2px solid var(--primary-mid);
  transform: rotate(45deg);
}}

/* ========== Compare Table ========== */
.compare-page {{
  flex: 1; display: flex; flex-direction: column; justify-content: center;
  max-width: 1180px; margin: 0 auto; width: 100%;
  gap: clamp(1.4rem, 2.6vh, 2rem);
}}
.compare-summary {{
  font-family: {f_serif_cn};
  font-size: clamp(0.92rem, 1.08vw, 1.12rem);
  color: var(--text-dim); line-height: 1.8;
  padding-left: clamp(1rem, 1.6vw, 1.4rem);
  border-left: 3px solid var(--accent);
}}
.compare-table {{
  display: grid; grid-template-columns: 1fr 1fr;
  border: 1px solid var(--border-color); border-radius: 10px;
  overflow: hidden;
  background: var(--card-top);
}}
.ct-header {{
  padding: clamp(0.9rem, 1.5vh, 1.2rem) clamp(1.2rem, 2vw, 1.8rem);
  font-size: clamp(0.65rem, 0.78vw, 0.82rem);
  letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--primary-mid);
  background: var(--primary-wash);
  border-bottom: 1px solid var(--border-color);
}}
.ct-header:first-child {{ border-right: 1px solid var(--border-color); }}
.ct-cell {{
  padding: clamp(1.2rem, 2vw, 1.8rem);
  border-top: 1px solid var(--border-color);
  background: var(--card-top);
}}
.ct-cell.ct-pain {{ border-right: 1px solid var(--border-color); }}
.ct-num {{
  font-family: {f_display}; font-style: italic;
  font-size: clamp(0.85rem, 1vw, 1.05rem);
  color: var(--accent); margin-bottom: 0.4rem;
}}
.ct-title-text {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1rem, 1.2vw, 1.25rem);
  color: var(--text); margin-bottom: clamp(0.4rem, 0.8vh, 0.6rem);
}}
.ct-text {{
  font-size: clamp(0.88rem, 1.02vw, 1.06rem);
  color: var(--text-dim); line-height: 1.75;
}}

/* ========== Split Layout ========== */
.split-layout {{
  flex: 1; display: grid; grid-template-columns: 1.1fr 0.9fr;
  gap: clamp(2rem, 3.5vw, 3rem);
  align-items: center;
  max-width: 1280px; margin: 0 auto; width: 100%;
}}
.split-left {{
  padding: clamp(1.8rem, 2.8vw, 2.6rem);
}}
.split-left .sl-label {{
  font-size: clamp(0.62rem, 0.75vw, 0.78rem);
  letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--primary-mid); margin-bottom: 0.45rem;
}}
.split-left .sl-bg-text {{
  font-family: {f_serif_cn};
  font-size: clamp(0.88rem, 1vw, 1.05rem);
  color: var(--text-mute); line-height: 1.75;
  margin-bottom: clamp(1.4rem, 2.6vh, 2rem);
}}
.split-left .sl-divider {{
  height: 1px; background: var(--border-color);
  margin-bottom: clamp(1rem, 1.8vh, 1.4rem);
}}
.split-left .sl-ask-text {{
  font-family: {f_serif_cn};
  font-size: clamp(0.92rem, 1.06vw, 1.1rem);
  color: var(--text-dim); line-height: 1.8;
}}
.split-right {{ display: flex; flex-direction: column; gap: clamp(1rem, 1.8vh, 1.4rem); }}
.split-right .sr-label {{
  font-size: clamp(0.62rem, 0.75vw, 0.78rem);
  letter-spacing: 0.28em; text-transform: uppercase;
  color: var(--primary-mid); margin-bottom: 0.2rem;
}}
.value-item {{
  padding: clamp(1.2rem, 2vw, 1.8rem);
  display: flex; gap: clamp(0.8rem, 1.4vw, 1.2rem);
  align-items: flex-start;
}}
.value-item .vi-icon {{
  width: clamp(40px, 3.2vw, 48px); height: clamp(40px, 3.2vw, 48px);
  border-radius: 10px;
  background: linear-gradient(135deg, var(--accent-wash), var(--accent-pale));
  color: var(--accent-soft);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.05rem, 1.3vw, 1.3rem);
  flex-shrink: 0;
}}
.value-item .vi-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(0.95rem, 1.12vw, 1.15rem);
  color: var(--text); margin-bottom: 0.3rem;
}}
.value-item .vi-desc {{
  font-size: clamp(0.82rem, 0.94vw, 0.98rem);
  color: var(--text-dim); line-height: 1.65;
}}

/* ========== Tier Diagram ========== */
.tier-page {{
  flex: 1; display: flex; flex-direction: column; justify-content: center;
  max-width: 1280px; margin: 0 auto; width: 100%;
  gap: clamp(1.4rem, 2.6vh, 2rem);
}}
.tier-summary {{
  font-family: {f_serif_cn};
  font-size: clamp(0.92rem, 1.08vw, 1.12rem);
  color: var(--text-dim); line-height: 1.8;
  padding-left: clamp(1rem, 1.6vw, 1.4rem);
  border-left: 3px solid var(--accent);
}}
.tier-diagram {{
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: clamp(1.2rem, 2.2vw, 2rem);
  align-items: end;
}}
.tier-step {{ display: flex; flex-direction: column; }}
.tier-step .ts-bar {{
  border-radius: 6px 6px 0 0;
  border: 1px solid var(--border-color);
  border-bottom: none;
  display: flex; align-items: center; justify-content: center;
  font-family: {f_display}; font-style: italic; font-weight: 500;
  font-size: clamp(2.2rem, 3.2vw, 3.5rem);
  color: var(--primary);
}}
.tier-step.tier-current .ts-bar {{
  background: var(--card-bottom);
}}
.tier-step.tier-mid .ts-bar {{
  background: linear-gradient(180deg, var(--primary-pale), var(--primary-wash));
}}
.tier-step.tier-future .ts-bar {{
  background: linear-gradient(180deg, var(--primary-soft), var(--primary-pale));
  box-shadow: 0 0 20px rgba(0,0,0,0.08);
}}
.tier-step .ts-base {{
  padding: clamp(0.9rem, 1.5vh, 1.2rem) clamp(0.9rem, 1.3vw, 1.3rem);
  background: var(--card-top);
  border: 1px solid var(--border-color);
  border-radius: 0 0 6px 6px;
}}
.tier-step .ts-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(0.92rem, 1.1vw, 1.15rem);
  color: var(--text); margin-bottom: 0.3rem;
}}
.tier-step .ts-desc {{
  font-size: clamp(0.78rem, 0.9vw, 0.94rem);
  color: var(--text-dim); line-height: 1.6;
}}
.tier-result {{
  text-align: center;
  padding: clamp(0.9rem, 1.6vh, 1.2rem) clamp(1.6rem, 3vw, 2.4rem);
  border: 1px solid var(--border-color); border-radius: 8px;
  background: linear-gradient(90deg, var(--primary-wash), var(--accent-wash));
}}
.tier-result span {{
  font-family: {f_serif_cn};
  font-size: clamp(0.88rem, 1.02vw, 1.06rem);
  color: var(--primary-mid); font-weight: 500;
}}

/* ========== Dual Path ========== */
.dual-path {{
  flex: 1; display: flex; flex-direction: column; justify-content: center;
  max-width: 1280px; margin: 0 auto; width: 100%;
  gap: clamp(1.4rem, 2.6vh, 2rem);
}}
.dp-summary {{
  font-family: {f_serif_cn};
  font-size: clamp(0.92rem, 1.08vw, 1.12rem);
  color: var(--text-dim); line-height: 1.8;
  padding-left: clamp(1rem, 1.6vw, 1.4rem);
  border-left: 3px solid var(--accent);
}}
.dual-path-row {{
  display: grid; grid-template-columns: 1fr 1fr;
  gap: clamp(1.6rem, 3vw, 2.8rem);
}}
.path-card {{
  padding: clamp(1.8rem, 2.8vw, 2.6rem);
  display: flex; flex-direction: column;
  gap: clamp(0.6rem, 1vh, 0.9rem);
}}
.path-card .pc-icon {{
  width: clamp(52px, 4.2vw, 64px); height: clamp(52px, 4.2vw, 64px);
  border-radius: 14px;
  background: linear-gradient(135deg, var(--accent-wash), var(--accent-pale));
  color: var(--accent-soft);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.4rem, 1.8vw, 1.7rem);
}}
.path-card .pc-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1.2rem, 1.5vw, 1.55rem);
  color: var(--text); line-height: 1.3;
}}
.path-card .pc-sub {{
  font-family: {f_mono};
  font-size: clamp(0.65rem, 0.78vw, 0.82rem);
  color: var(--accent-soft); letter-spacing: 0.12em;
}}
.path-card .pc-divider {{ height: 1px; background: var(--border-color); }}
.path-card .pc-desc {{
  font-family: {f_serif_cn};
  font-size: clamp(0.88rem, 1.02vw, 1.06rem);
  color: var(--text-dim); line-height: 1.75;
}}
.dp-bottom {{
  text-align: center;
  padding: clamp(0.9rem, 1.6vh, 1.2rem) clamp(1.6rem, 3vw, 2.4rem);
  border: 1px solid var(--border-color); border-radius: 8px;
  background: linear-gradient(90deg, var(--primary-wash), var(--accent-wash));
}}
.dp-bottom span {{
  font-family: {f_serif_cn};
  font-size: clamp(0.88rem, 1.02vw, 1.06rem);
  color: var(--primary-mid); font-weight: 500;
}}

/* ========== Thanks ========== */
.thanks-slide {{
  justify-content: center; align-items: center; text-align: center;
}}
.thanks-rings {{
  position: absolute; inset: 0; z-index: 0; pointer-events: none; overflow: hidden;
}}
.thanks-rings .ring {{
  position: absolute; border-radius: 50%; border: 1px solid var(--border-color);
  top: 50%; left: 50%; transform: translate(-50%, -50%);
}}
.ring-1 {{ width: 500px; height: 500px; opacity: 0.5; }}
.ring-2 {{ width: 700px; height: 700px; opacity: 0.3; }}
.thanks-eyebrow {{
  font-size: clamp(0.7rem, 0.9vw, 0.95rem);
  letter-spacing: 0.4em; text-transform: uppercase;
  color: var(--primary-mid); margin-bottom: clamp(1.5rem, 3vh, 2.5rem);
}}
.thanks-display {{
  font-family: {f_display}; font-weight: 500; font-style: italic;
  font-size: clamp(5rem, 10vw, 10rem); line-height: 1;
  background: linear-gradient(120deg, var(--primary) 0%, var(--primary-mid) 40%, var(--accent) 100%);
  -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent;
  margin-bottom: clamp(1rem, 2vh, 1.6rem);
  filter: drop-shadow(0 0 40px rgba(0,0,0,0.1));
}}
.thanks-cn {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1.6rem, 2.3vw, 2.5rem);
  color: var(--text); letter-spacing: 0.4em;
  margin-bottom: clamp(2rem, 4vh, 3rem);
}}
.thanks-line {{
  width: clamp(80px, 10vw, 140px); height: 1px;
  background: linear-gradient(90deg, transparent, var(--accent), transparent);
  margin: 0 auto clamp(1.5rem, 3vh, 2rem);
}}
.thanks-sub {{
  font-family: {f_serif_cn};
  font-size: clamp(1rem, 1.2vw, 1.25rem);
  color: var(--text-dim); letter-spacing: 0.18em;
}}

/* ========== Chart Duo ========== */
.chart-summary {{
  text-align: center; font-family: {f_serif_cn};
  font-size: clamp(0.95rem, 1.1vw, 1.15rem);
  color: var(--text-dim); line-height: 1.8;
  max-width: 60ch; margin: 0 auto clamp(1.4rem, 2.5vh, 2rem);
}}
.chart-duo {{
  flex: 1; display: grid; grid-template-columns: 1fr 1fr;
  gap: clamp(1.6rem, 2.8vw, 2.4rem);
  min-height: 0;
}}
.chart-kpis {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: clamp(0.8rem, 1.4vw, 1.2rem);
  padding: clamp(0.9rem, 1.6vh, 1.2rem) clamp(1.2rem, 2vw, 1.8rem);
  margin-bottom: clamp(1rem, 1.8vh, 1.4rem);
  background: linear-gradient(90deg, var(--primary-wash), var(--accent-wash));
  border: 1px solid var(--border-color); border-radius: 10px;
}}
.chart-kpis .ck-item {{
  display: flex; flex-direction: column; align-items: flex-start; gap: 0.2rem;
}}
.chart-kpis .ck-value {{
  font-family: {f_display}; font-weight: 600;
  font-size: clamp(1.3rem, 1.8vw, 1.9rem);
  color: var(--primary); line-height: 1;
}}
.chart-kpis .ck-unit {{
  font-size: clamp(0.7rem, 0.85vw, 0.92rem);
  color: var(--accent); margin-left: 0.3em; font-weight: 500;
}}
.chart-kpis .ck-label {{
  font-size: clamp(0.7rem, 0.82vw, 0.88rem);
  color: var(--text-mute); margin-top: 0.15rem;
}}

/* Product Gallery: 4-col grid of product cards with images */
.pg-summary {{
  text-align: center; max-width: 60ch; margin: 0 auto clamp(1rem, 2vh, 1.6rem);
  font-size: clamp(0.92rem, 1.06vw, 1.1rem); color: var(--text-dim); line-height: 1.7;
}}
.product-gallery {{
  flex: 1; display: grid; gap: clamp(1rem, 1.6vw, 1.4rem);
  align-content: stretch;
}}
.product-gallery.cols-4 {{ grid-template-columns: repeat(4, 1fr); }}
.product-gallery.cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.pg-card {{
  background: var(--card-top); border: 1px solid var(--border-color);
  border-radius: 10px; overflow: hidden;
  display: flex; flex-direction: column;
  box-shadow: 0 2px 12px rgba(0,0,0,0.05);
  transition: transform 0.4s, box-shadow 0.4s;
}}
.pg-card .pg-image {{
  width: 100%; aspect-ratio: 16/9;
  background: linear-gradient(135deg, var(--primary-wash), var(--primary-pale));
  overflow: hidden;
}}
.pg-card .pg-image img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.pg-card .pg-body {{
  padding: clamp(0.7rem, 1.2vw, 1rem);
  display: flex; flex-direction: column; gap: 0.4rem;
  flex: 1;
}}
.pg-card .pg-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(0.92rem, 1.05vw, 1.1rem);
  color: var(--text); line-height: 1.3;
}}
.pg-card .pg-desc {{
  font-size: clamp(0.74rem, 0.85vw, 0.9rem);
  color: var(--text-mute); line-height: 1.55; flex: 1;
}}
.pg-card .pg-revenue {{
  display: flex; align-items: baseline; gap: 0.3rem;
  margin-top: auto; padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
}}
.pg-card .pg-rev-value {{
  font-family: {f_display}; font-weight: 600; font-style: italic;
  font-size: clamp(1.1rem, 1.4vw, 1.5rem);
  color: var(--accent);
}}
.pg-card .pg-rev-label {{
  font-size: clamp(0.7rem, 0.78vw, 0.82rem);
  color: var(--text-mute);
}}
.pg-card .pg-no-data {{
  font-size: clamp(0.74rem, 0.82vw, 0.88rem);
  color: var(--text-faint); font-style: italic;
}}
.pg-summary-card {{
  background: linear-gradient(135deg, var(--primary-wash), var(--accent-wash));
  border: 1px solid var(--border-color); border-radius: 10px;
  padding: clamp(1rem, 1.6vw, 1.4rem);
  display: flex; flex-direction: column; gap: clamp(0.6rem, 1vh, 0.9rem);
  justify-content: center;
}}
.pg-summary-card .pg-sum-eyebrow {{
  font-family: {f_mono}; font-size: clamp(0.62rem, 0.74vw, 0.78rem);
  letter-spacing: 0.28em; color: var(--accent); text-transform: uppercase;
}}
.pg-summary-card .pg-sum-text {{
  font-family: {f_serif_cn};
  font-size: clamp(0.84rem, 0.96vw, 1rem);
  color: var(--text-dim); line-height: 1.7;
}}
.pg-summary-card .pg-sum-text strong {{ color: var(--primary); font-weight: 600; }}
.pg-bottom {{
  text-align: center;
  padding: clamp(0.8rem, 1.4vh, 1.1rem) clamp(1.6rem, 3vw, 2.4rem);
  margin-top: clamp(0.8rem, 1.4vh, 1.2rem);
  background: linear-gradient(90deg, var(--primary-wash), var(--accent-wash));
  border: 1px solid var(--border-color); border-radius: 8px;
}}
.pg-bottom span {{
  font-family: {f_serif_cn}; font-size: clamp(0.92rem, 1.06vw, 1.1rem);
  color: var(--primary-mid); font-weight: 500;
}}
.chart-card {{
  padding: clamp(1.4rem, 2.2vw, 2rem);
  background: var(--card-top);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  display: flex; flex-direction: column;
  position: relative; overflow: hidden;
}}
.chart-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
}}
.chart-card .cc-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1rem, 1.2vw, 1.25rem);
  color: var(--text);
  margin-bottom: 0.3rem;
}}
.chart-card .cc-en {{
  font-family: {f_display}; font-style: italic;
  font-size: clamp(0.72rem, 0.85vw, 0.92rem);
  color: var(--text-mute);
  margin-bottom: clamp(0.6rem, 1vh, 0.9rem);
  letter-spacing: 0.05em;
}}
.chart-card .chart-canvas {{
  flex: 1; width: 100%; min-height: 220px;
}}
.chart-card .chart-insight {{
  margin-top: clamp(0.6rem, 1vh, 0.9rem);
  padding-top: clamp(0.6rem, 1vh, 0.9rem);
  padding-left: clamp(0.8rem, 1.4vw, 1.2rem);
  border-top: 1px solid var(--border-color);
  border-left: 3px solid var(--accent);
  font-family: {f_serif_cn};
  font-size: clamp(0.82rem, 0.94vw, 0.98rem);
  color: var(--text-dim); line-height: 1.65;
}}
.chart-card .chart-insight strong {{ color: var(--accent-soft); font-weight: 500; }}

/* ========== Dashboard (KPI Grid) ========== */
.dashboard {{
  flex: 1; display: flex; flex-direction: column; justify-content: center;
  max-width: 1280px; margin: 0 auto; width: 100%;
  gap: clamp(2rem, 4vh, 3rem);
}}
.dashboard-summary {{
  text-align: center; font-family: {f_serif_cn};
  font-size: clamp(1rem, 1.18vw, 1.22rem);
  color: var(--text-dim); line-height: 1.8;
  max-width: 60ch; margin: 0 auto;
}}
.kpi-grid {{
  display: grid;
  gap: clamp(1.4rem, 2.5vw, 2.2rem);
}}
.kpi-cols-2 {{ grid-template-columns: 1fr 1fr; }}
.kpi-cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.kpi-cols-4 {{ grid-template-columns: repeat(4, 1fr); }}
.kpi-card {{
  padding: clamp(1.6rem, 2.5vw, 2.2rem) clamp(1.4rem, 2vw, 1.8rem);
  background: var(--card-top);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  position: relative; overflow: hidden;
  display: flex; flex-direction: column; gap: 0.5rem;
}}
.kpi-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--primary), var(--accent));
}}
.kpi-card .kpi-icon {{
  width: clamp(40px, 3.2vw, 50px); height: clamp(40px, 3.2vw, 50px);
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary-wash), var(--primary-pale));
  color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(1.2rem, 1.5vw, 1.5rem);
  margin-bottom: 0.4rem;
}}
.kpi-card .kpi-value {{
  font-family: {f_display}; font-weight: 600;
  font-size: clamp(2.4rem, 3.4vw, 3.4rem);
  line-height: 1;
  color: var(--primary);
  display: flex; align-items: baseline; gap: 0.3rem;
}}
.kpi-card .kpi-unit {{
  font-size: clamp(0.95rem, 1.1vw, 1.15rem);
  color: var(--text-mute); font-weight: 400;
  font-family: {f_body};
}}
.kpi-card .kpi-label {{
  font-family: {f_serif_cn};
  font-size: clamp(0.92rem, 1.05vw, 1.1rem);
  color: var(--text-dim);
  font-weight: 500;
}}
.kpi-card .kpi-trend {{
  font-family: {f_mono};
  font-size: clamp(0.7rem, 0.82vw, 0.86rem);
  color: var(--accent);
  letter-spacing: 0.05em;
  margin-top: 0.2rem;
}}

/* ========== Milestone Line ========== */
.milestone-page {{
  flex: 1; display: flex; flex-direction: column; justify-content: center;
  max-width: 1300px; margin: 0 auto; width: 100%;
  gap: clamp(2.5rem, 5vh, 4rem);
}}
.ml-summary {{
  text-align: center; font-family: {f_serif_cn};
  font-size: clamp(1rem, 1.18vw, 1.22rem);
  color: var(--text-dim); line-height: 1.8;
  max-width: 56ch; margin: 0 auto;
}}
.ml-track {{
  display: grid; position: relative;
  gap: clamp(0.8rem, 1.5vw, 1.4rem);
  padding: clamp(1.5rem, 2.5vh, 2rem) 0;
}}
.ml-track .ml-line {{
  position: absolute; top: 70px; left: 4%; right: 4%; height: 2px;
  background: linear-gradient(90deg, var(--primary-soft), var(--primary), var(--accent));
  z-index: 0;
}}
.ml-node {{
  position: relative; z-index: 1;
  display: flex; flex-direction: column; align-items: center;
  text-align: center;
  padding: 0 clamp(0.3rem, 0.6vw, 0.6rem);
}}
.ml-node .ml-month {{
  font-family: {f_mono};
  font-size: clamp(0.7rem, 0.82vw, 0.86rem);
  color: var(--accent);
  letter-spacing: 0.18em;
  margin-bottom: 0.6rem;
}}
.ml-node .ml-dot {{
  width: 16px; height: 16px;
  border-radius: 50%;
  background: var(--bg);
  border: 3px solid var(--primary);
  box-shadow: 0 0 0 4px var(--primary-wash), 0 4px 12px rgba(0,0,0,0.1);
  margin-bottom: 1rem;
}}
.ml-node .ml-event {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(0.92rem, 1.05vw, 1.1rem);
  color: var(--text);
  margin-bottom: 0.3rem;
  line-height: 1.3;
}}
.ml-node .ml-desc {{
  font-size: clamp(0.74rem, 0.85vw, 0.9rem);
  color: var(--text-mute);
  line-height: 1.55;
}}

/* ========== Progress Cards ========== */
.progress-cards-grid {{
  flex: 1; display: grid;
  gap: clamp(1.4rem, 2.4vw, 2rem);
  align-items: stretch;
  min-height: 0;
}}
.progress-cards-grid.grid-cols-2 {{ grid-template-columns: 1fr 1fr; }}
.progress-cards-grid.grid-cols-3 {{ grid-template-columns: repeat(3, 1fr); }}
.progress-cards-grid.grid-cols-4 {{ grid-template-columns: repeat(4, 1fr); }}
.progress-card {{
  background: var(--card-top);
  border: 1px solid var(--border-color);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  display: flex; flex-direction: column;
}}
.progress-card .pc-image {{
  width: 100%; aspect-ratio: 16/9;
  background: linear-gradient(135deg, var(--primary-wash), var(--primary-pale));
  position: relative; overflow: hidden;
  flex-shrink: 0;
}}
.progress-card-textonly {{
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(165deg, var(--card-top) 0%, var(--primary-wash) 135%);
}}
.progress-card-textonly .pc-watermark {{
  position: absolute; top: 0.8rem; right: 1.2rem;
  font-size: clamp(5rem, 9vw, 10rem); font-weight: 800;
  color: var(--primary); opacity: 0.09; line-height: 1;
  pointer-events: none; user-select: none;
}}
.progress-card-textonly::before {{
  content: '';
  display: block; width: 100%; height: 4px;
  background: linear-gradient(90deg, var(--primary), var(--primary-bright), var(--accent));
  flex-shrink: 0;
}}
.progress-card-textonly .pc-body {{
  padding: clamp(1.4rem, 2.6vh, 2rem) clamp(1.4rem, 2.4vw, 2rem);
  flex: 1; display: flex; flex-direction: column;
  gap: clamp(0.7rem, 1.4vh, 1rem);
}}
.progress-card-textonly .pc-status {{
  align-self: flex-start;
}}
.progress-card-textonly .pc-title {{
  font-size: clamp(1.2rem, 1.45vw, 1.5rem);
  margin-top: clamp(0.4rem, 0.8vh, 0.7rem);
}}
.progress-card-textonly .pc-desc {{
  flex: 1;
  font-size: clamp(0.88rem, 1.02vw, 1.06rem);
  line-height: 1.7;
}}
.progress-card-textonly .pc-progress {{
  margin-top: auto;
}}
.progress-card-textonly .pc-metric {{
  margin-top: clamp(0.5rem, 1vh, 0.8rem);
  padding-top: clamp(0.5rem, 1vh, 0.8rem);
  border-top: 1px solid var(--border-color);
}}
/* 全文字卡片：卡片撑满成高卡填满内容区，靠大序号水印/渐变填充视觉，内容垂直居中，不为图片留白 */
.progress-cards-grid.all-textonly .progress-card-textonly {{ justify-content: center; }}
.progress-cards-grid.all-textonly .progress-card-textonly .pc-body {{ justify-content: center; flex: 1; }}
.progress-cards-grid.all-textonly .progress-card-textonly .pc-desc {{ flex: none; }}
.progress-card .pc-image img {{
  width: 100%; height: 100%; object-fit: cover; display: block;
}}
.progress-card .pc-placeholder {{
  width: 100%; height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  color: var(--primary-soft);
  font-size: clamp(2rem, 3vw, 3rem);
  gap: 0.5rem;
}}
.progress-card .pc-ph-text {{
  font-family: {f_mono};
  font-size: clamp(0.7rem, 0.85vw, 0.88rem);
  letter-spacing: 0.15em;
  color: var(--primary-mid);
}}
.progress-card .pc-body {{
  padding: clamp(1.2rem, 2vw, 1.6rem);
  display: flex; flex-direction: column;
  gap: clamp(0.5rem, 0.9vh, 0.8rem);
  flex: 1;
}}
.progress-card .pc-status {{
  display: inline-block; align-self: flex-start;
  padding: 0.25rem 0.7rem; border-radius: 4px;
  font-family: {f_mono};
  font-size: clamp(0.65rem, 0.75vw, 0.78rem);
  letter-spacing: 0.12em; text-transform: uppercase;
}}
.pc-status-done {{ background: var(--primary-wash); color: var(--primary-mid); border: 1px solid var(--border-color); }}
.pc-status-doing {{ background: var(--accent-wash); color: var(--accent-soft); border: 1px solid var(--border-color); }}
.pc-status-plan {{ background: var(--card-bottom); color: var(--text-mute); border: 1px solid var(--border-color); }}
.progress-card .pc-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1.05rem, 1.25vw, 1.3rem);
  color: var(--text); line-height: 1.3;
}}
.progress-card .pc-desc {{
  font-size: clamp(0.84rem, 0.96vw, 1rem);
  color: var(--text-dim); line-height: 1.65;
  flex: 1;
}}
.progress-card .pc-progress {{
  display: flex; align-items: center; gap: 0.7rem;
}}
.progress-card .pc-progress-bar {{
  flex: 1; height: 6px;
  background: var(--card-bottom);
  border-radius: 3px; overflow: hidden;
}}
.progress-card .pc-progress-fill {{
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  border-radius: 3px;
}}
.progress-card .pc-progress-text {{
  font-family: {f_mono}; font-weight: 500;
  font-size: clamp(0.78rem, 0.9vw, 0.94rem);
  color: var(--primary);
  min-width: 2.5rem; text-align: right;
}}
.progress-card .pc-metric {{
  display: flex; align-items: baseline; gap: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--border-color);
}}
.progress-card .pc-metric-value {{
  font-family: {f_display}; font-weight: 600;
  font-size: clamp(1.3rem, 1.6vw, 1.65rem);
  color: var(--accent);
}}
.progress-card .pc-metric-label {{
  font-size: clamp(0.74rem, 0.85vw, 0.9rem);
  color: var(--text-mute);
}}

/* ========== Image-Text Layout ========== */
.image-text-layout {{
  flex: 1; display: grid;
  gap: clamp(2rem, 3.5vw, 3rem);
  align-items: center;
  max-width: 1300px; margin: 0 auto; width: 100%;
}}
.image-text-layout.image-left {{ grid-template-columns: 1fr 1.05fr; }}
.image-text-layout.image-right {{ grid-template-columns: 1.05fr 1fr; }}
.image-text-layout.image-right .it-image {{ order: 2; }}
.image-text-layout.text-only {{ grid-template-columns: 1fr; max-width: 980px; align-items: start; padding-top: clamp(1rem, 2vh, 1.6rem); }}
.image-text-layout.text-only .it-list {{ gap: clamp(1.6rem, 3vh, 2.4rem); }}
.image-text-layout.text-only .it-item {{ padding: clamp(1.2rem, 2vh, 1.8rem) 0; border-bottom: 1px solid var(--border-color); }}
.image-text-layout.text-only .it-item:last-child {{ border-bottom: none; }}
.it-image {{
  aspect-ratio: 4/3;
  border-radius: 14px; overflow: hidden;
  background: linear-gradient(135deg, var(--primary-wash), var(--primary-pale));
  border: 1px solid var(--border-color);
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  position: relative;
}}
.it-image img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.it-placeholder {{
  width: 100%; height: 100%;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 0.7rem;
  color: var(--primary);
}}
.it-placeholder .it-ph-icon {{
  font-size: clamp(2.5rem, 4vw, 4rem);
}}
.it-placeholder .it-ph-text {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1rem, 1.2vw, 1.2rem);
  color: var(--primary-mid);
}}
.it-placeholder .it-ph-hint {{
  font-family: {f_mono};
  font-size: clamp(0.7rem, 0.82vw, 0.86rem);
  color: var(--text-mute);
  letter-spacing: 0.12em;
}}
.it-list {{
  display: flex; flex-direction: column;
  gap: clamp(1rem, 1.8vh, 1.5rem);
}}
.it-item {{
  display: grid; grid-template-columns: auto 1fr;
  gap: clamp(0.9rem, 1.5vw, 1.4rem);
  padding: clamp(1rem, 1.6vh, 1.4rem) 0;
  border-bottom: 1px solid var(--border-color);
}}
.it-item:last-child {{ border-bottom: none; }}
.it-num {{
  font-family: {f_display}; font-style: italic; font-weight: 600;
  font-size: clamp(1.6rem, 2vw, 2.2rem);
  line-height: 1;
  color: var(--accent);
  min-width: 2.4rem;
}}
.it-title {{
  font-family: {f_serif_cn}; font-weight: 600;
  font-size: clamp(1.1rem, 1.3vw, 1.35rem);
  color: var(--text);
  margin-bottom: 0.3rem;
}}
.it-desc {{
  font-size: clamp(0.86rem, 0.98vw, 1.04rem);
  color: var(--text-dim); line-height: 1.7;
}}
.it-desc strong {{ color: var(--primary-mid); font-weight: 500; }}
.it-metric {{
  display: inline-block; margin-top: 0.5rem;
  padding: 0.3rem 0.8rem; border-radius: 4px;
  background: var(--accent-wash);
  color: var(--accent-soft);
  font-family: {f_mono};
  font-size: clamp(0.78rem, 0.9vw, 0.94rem);
}}

/* ========== Nav ========== */
.progress-bar {{
  position: fixed; top: 0; left: 0; right: 0; height: 3px;
  background: var(--border-color); z-index: 100;
}}
.progress-fill {{
  height: 100%; width: 0;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  transition: width 0.7s cubic-bezier(0.2,0.8,0.2,1);
}}
.page-indicator {{
  position: fixed; left: clamp(1.8rem, 3vw, 3rem); bottom: clamp(1.2rem, 2vh, 1.8rem);
  font-family: {f_mono}; font-size: clamp(0.72rem, 0.85vw, 0.92rem);
  color: var(--text-faint); z-index: 100;
}}
.page-indicator .cur {{ color: var(--primary); font-weight: 500; }}

/* Fullscreen button */
.fs-btn {{
  position: fixed; right: clamp(1.8rem, 3vw, 3rem); bottom: clamp(1.2rem, 2vh, 1.8rem);
  width: clamp(36px, 3vw, 44px); height: clamp(36px, 3vw, 44px);
  border-radius: 8px; border: 1px solid var(--border-color);
  background: var(--card-top);
  color: var(--text-mute);
  cursor: pointer; z-index: 100;
  display: flex; align-items: center; justify-content: center;
  font-size: clamp(0.95rem, 1.15vw, 1.2rem);
  transition: all 0.3s; padding: 0;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}}
.fs-btn:hover {{
  background: var(--primary-wash); color: var(--primary);
  border-color: var(--primary-soft);
  transform: translateY(-2px);
}}
.fs-btn .fs-icon-exit {{ display: none; }}
.fs-btn.is-fullscreen .fs-icon-enter {{ display: none; }}
.fs-btn.is-fullscreen .fs-icon-exit {{ display: inline; }}
"""


def render_slide_cover(s: dict, page_num: int, total: int) -> str:
    meta = s.get("meta", [])
    meta_html = "\n".join(
        f'<div><div class="m-label">{m["label"]}</div>'
        f'<div class="m-value {"m-value-cn" if m.get("is_cn") else ""}">{m["value"]}</div></div>'
        for m in meta
    )
    return f"""
<section class="slide cover" data-slide="{page_num}">
  <div class="cover-watermark">{s.get("watermark", str(page_num))}</div>
  <div class="cover-inner">
    <div>
      <div class="eyebrow reveal" data-d="1">{s.get("eyebrow", "")}</div>
      <h1 class="cover-title reveal blur-in" data-d="2">
        <span class="yr">{s.get("title_accent", "")}</span><br>{s.get("title", "")}
      </h1>
      <div class="cover-title-en reveal" data-d="3">{s.get("title_en", "")}</div>
      <hr class="cover-line reveal" data-d="4">
      <div class="cover-sub reveal" data-d="5">{s.get("subtitle", "")}</div>
    </div>
    <div class="cover-meta reveal scale-in" data-d="6">{meta_html}</div>
  </div>
</section>"""


def render_slide_icon_duo(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    cards = s.get("cards", [])
    cards_html = "\n".join(
        f'''<div class="card icon-card reveal scale-in" data-d="{2+i}">
  <div class="card-accent"></div>
  <div class="ik-icon-wrap">{c.get("icon", "◈")}</div>
  <div class="ik-num">{c.get("num", "")}</div>
  <div class="ik-title">{c.get("title", "")}</div>
  <div class="ik-divider"></div>
  <div class="ik-points">
    {"".join(f"<span class='ik-tag {t.get('style','primary')}'>{t.get('text','')}</span>" for t in c.get("tags", []))}
  </div>
</div>'''
        for i, c in enumerate(cards)
    )
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div>
      <div class="h-title">{header.get("title", "")}</div>
      <div class="h-en">{header.get("en", "")}</div>
    </div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="icon-duo">
    <div class="icon-duo-row">{cards_html}</div>
    <div class="icon-duo-bottom reveal" data-d="{2+len(cards)+1}"><span>{s.get("bottom_message", "")}</span></div>
  </div>
</section>"""


def render_slide_timeline(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    stages = s.get("stages", [])
    stage_classes = ["tl-current", "tl-mid", "tl-future"]
    parts = []
    for i, st in enumerate(stages):
        klass = stage_classes[min(i, 2)]
        parts.append(f'''
<div class="tl-stage {klass} reveal scale-in" data-d="{3 + i*2}">
  <div class="tl-node">{st.get("icon", "◆")}</div>
  <div class="tl-sub">{st.get("sub", "")}</div>
  <div class="tl-title">{st.get("title", "")}</div>
  <div class="tl-desc">{st.get("desc", "")}</div>
</div>''')
        if i < len(stages) - 1:
            parts.append(f'<div class="tl-arrow reveal" data-d="{4 + i*2}"><div class="tl-line"></div></div>')

    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div>
      <div class="h-title">{header.get("title", "")}</div>
      <div class="h-en">{header.get("en", "")}</div>
    </div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="timeline-page">
    <div class="timeline-summary reveal" data-d="2">{s.get("summary", "")}</div>
    <div class="timeline-track">{"".join(parts)}</div>
  </div>
</section>"""


def render_slide_compare_table(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    rows = s.get("rows", [])
    row_html = ""
    for i, r in enumerate(rows):
        row_html += f'''
<div class="ct-cell ct-pain reveal" data-d="{3+i*2}">
  <div class="ct-num">{r.get("num", "")}</div>
  <div class="ct-title-text">{r.get("pain_title", "")}</div>
  <div class="ct-text">{r.get("pain_text", "")}</div>
</div>
<div class="ct-cell ct-ask reveal" data-d="{4+i*2}">
  <div class="ct-title-text">{r.get("ask_title", "")}</div>
  <div class="ct-text">{r.get("ask_text", "")}</div>
</div>'''
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="compare-page">
    <div class="compare-summary reveal" data-d="2">{s.get("summary", "")}</div>
    <div class="compare-table">
      <div class="ct-header">痛点 · PAIN POINT</div>
      <div class="ct-header">协同诉求 · THE ASK</div>
      {row_html}
    </div>
  </div>
</section>"""


def render_slide_split_layout(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    values = s.get("values", [])
    values_html = "\n".join(
        f'''<div class="card value-item reveal scale-in" data-d="{4+i}">
  <div class="vi-icon">{v.get("icon", "◆")}</div>
  <div><div class="vi-title">{v.get("title", "")}</div><div class="vi-desc">{v.get("desc", "")}</div></div>
</div>'''
        for i, v in enumerate(values)
    )
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="split-layout">
    <div class="card split-left reveal scale-in" data-d="2">
      <div class="sl-label">背景 · BACKGROUND</div>
      <div class="sl-bg-text">{s.get("background", "")}</div>
      <div class="sl-divider"></div>
      <div class="sl-label">协同诉求 · THE ASK</div>
      <div class="sl-ask-text">{s.get("ask", "")}</div>
    </div>
    <div class="split-right">
      <div class="sr-label reveal" data-d="3">业务价值 · VALUE</div>
      {values_html}
    </div>
  </div>
</section>"""


def render_slide_tier(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    tiers = s.get("tiers", [])
    tiers_html = ""
    heights = [100, 155, 210]
    for i, t in enumerate(tiers):
        h = heights[min(i, 2)]
        klass = ["tier-current", "tier-mid", "tier-future"][min(i, 2)]
        tiers_html += f'''
<div class="tier-step {klass} reveal scale-in" data-d="{3+i}">
  <div class="ts-bar" style="height: {h}px;">{t.get("num", "")}</div>
  <div class="ts-base">
    <div class="ts-title">{t.get("title", "")}</div>
    <div class="ts-desc">{t.get("desc", "")}</div>
  </div>
</div>'''
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="tier-page">
    <div class="tier-summary reveal" data-d="2">{s.get("summary", "")}</div>
    <div class="tier-diagram">{tiers_html}</div>
    <div class="tier-result reveal" data-d="{3+len(tiers)}"><span>{s.get("result", "")}</span></div>
  </div>
</section>"""


def render_slide_dual_path(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    paths = s.get("paths", [])
    paths_html = "\n".join(
        f'''<div class="card path-card reveal scale-in" data-d="{3+i}">
  <div class="card-accent"></div>
  <div class="pc-icon">{p.get("icon", "◆")}</div>
  <div class="pc-title">{p.get("title", "")}</div>
  <div class="pc-sub">{p.get("sub", "")}</div>
  <div class="pc-divider"></div>
  <div class="pc-desc">{p.get("desc", "")}</div>
</div>'''
        for i, p in enumerate(paths)
    )
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="dual-path">
    <div class="dp-summary reveal" data-d="2">{s.get("summary", "")}</div>
    <div class="dual-path-row">{paths_html}</div>
    <div class="dp-bottom reveal" data-d="{3+len(paths)}"><span>{s.get("bottom_principle", "")}</span></div>
  </div>
</section>"""


def render_slide_thanks(s: dict, page_num: int, total: int) -> str:
    return f"""
<section class="slide thanks-slide" data-slide="{page_num}">
  <div class="thanks-rings">
    <div class="ring ring-1"></div>
    <div class="ring ring-2"></div>
  </div>
  <div class="thanks-eyebrow reveal" data-d="1">{s.get("eyebrow", "END OF REPORT")}</div>
  <div class="thanks-display reveal blur-in" data-d="2">{s.get("display", "Thank You")}</div>
  <div class="thanks-cn reveal" data-d="3">{s.get("cn", "")}</div>
  <div class="thanks-line reveal" data-d="4"></div>
  <div class="thanks-sub reveal" data-d="5">{s.get("sub", "")}</div>
</section>"""


def render_slide_chart_duo(s: dict, page_num: int, total: int) -> str:
    """Two ECharts side by side, each with a title + insight."""
    header = s.get("header", {})
    charts = s.get("charts", [])
    chart_html = ""
    for i, c in enumerate(charts):
        chart_html += f'''
<div class="chart-card reveal scale-in" data-d="{2+i}">
  <div class="cc-title">{c.get("title", "")}</div>
  <div class="cc-en">{c.get("en", "")}</div>
  <div class="chart-canvas" id="chart_{page_num}_{i}"></div>
  <div class="chart-insight">{c.get("insight", "")}</div>
</div>'''
    # Chart init scripts (deferred to bottom, will be added by render_html main)
    return f"""
<section class="slide chart-slide" data-slide="{page_num}" data-charts='{json.dumps(charts, ensure_ascii=False)}'>
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="chart-summary reveal" data-d="2">{s.get("summary", "")}</div>
  {f'''<div class="chart-kpis reveal" data-d="3">
    {"".join(f'<div class="ck-item"><span class="ck-value">{k.get("value","")}</span><span class="ck-unit">{k.get("unit","")}</span><span class="ck-label">{k.get("label","")}</span></div>' for k in s.get("kpis", []))}
  </div>''' if s.get("kpis") else ""}
  <div class="chart-duo">
    {chart_html}
  </div>
</section>"""


def render_slide_dashboard(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    kpis = s.get("kpis", [])
    cols = min(len(kpis), 4)
    kpis_html = "\n".join(
        f'''<div class="kpi-card reveal scale-in" data-d="{2+i}">
  <div class="kpi-icon">{k.get("icon", "◆")}</div>
  <div class="kpi-value">{k.get("value", "")}<span class="kpi-unit">{k.get("unit", "")}</span></div>
  <div class="kpi-label">{k.get("label", "")}</div>
  {f'<div class="kpi-trend">{k.get("trend", "")}</div>' if k.get("trend") else ""}
</div>'''
        for i, k in enumerate(kpis)
    )
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="dashboard">
    <div class="dashboard-summary reveal" data-d="2">{s.get("summary", "")}</div>
    <div class="kpi-grid kpi-cols-{cols}">{kpis_html}</div>
  </div>
</section>"""


def render_slide_milestone_line(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    nodes = s.get("nodes", [])
    nodes_html = "\n".join(
        f'''<div class="ml-node reveal" data-d="{3+i}" style="grid-column: {i+1}">
  <div class="ml-month">{n.get("month", "")}</div>
  <div class="ml-dot"></div>
  <div class="ml-event">{n.get("event", "")}</div>
  {f'<div class="ml-desc">{n.get("desc", "")}</div>' if n.get("desc") else ""}
</div>'''
        for i, n in enumerate(nodes)
    )
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="milestone-page">
    <div class="ml-summary reveal" data-d="2">{s.get("summary", "")}</div>
    <div class="ml-track" style="grid-template-columns: repeat({len(nodes)}, 1fr);">
      <div class="ml-line"></div>
      {nodes_html}
    </div>
  </div>
</section>"""


def render_slide_progress_cards(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    cards = s.get("cards", [])
    cards_html = "\n".join(
        f'''<div class="progress-card{' progress-card-textonly' if not c.get("image") else ''} reveal scale-in" data-d="{2+i}">
  {f'<div class="pc-watermark">{i+1:02d}</div>' if not c.get("image") else ''}
  {f'<div class="pc-image"><img src="{c.get("image")}" alt="{c.get("title","")}"></div>' if c.get("image") else ''}
  <div class="pc-body">
    <div class="pc-status pc-status-{c.get("status", "doing")}">{c.get("status_label", "")}</div>
    <div class="pc-title">{c.get("title", "")}</div>
    <div class="pc-desc">{c.get("desc", "")}</div>
    {f'''<div class="pc-progress">
      <div class="pc-progress-bar"><div class="pc-progress-fill" style="width: {c.get("progress")}%"></div></div>
      <div class="pc-progress-text">{c.get("progress")}%</div>
    </div>''' if c.get("progress") is not None else ""}
    {f'<div class="pc-metric"><span class="pc-metric-value">{c.get("metric_value")}</span><span class="pc-metric-label">{c.get("metric_label", "")}</span></div>' if c.get("metric_value") else ""}
  </div>
</div>'''
        for i, c in enumerate(cards)
    )
    all_textonly = all(not c.get("image") for c in cards)
    grid_cls = f"progress-cards-grid grid-cols-{len(cards)}" + (" all-textonly" if all_textonly else "")
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="{grid_cls}">
    {cards_html}
  </div>
</section>"""


def render_slide_image_text(s: dict, page_num: int, total: int) -> str:
    header = s.get("header", {})
    image_side = s.get("image_side", "left")  # left or right
    items = s.get("items", [])
    items_html = "\n".join(
        f'''<div class="it-item reveal" data-d="{3+i}">
  <div class="it-num">{it.get("num", str(i+1).zfill(2))}</div>
  <div class="it-content">
    <div class="it-title">{it.get("title", "")}</div>
    <div class="it-desc">{it.get("desc", "")}</div>
    {f'<div class="it-metric">{it.get("metric")}</div>' if it.get("metric") else ""}
  </div>
</div>'''
        for i, it in enumerate(items)
    )
    has_image = bool(s.get("image"))
    image_html = f'<img src="{s.get("image")}" alt="">' if has_image else ""
    layout_class = f"image-text-layout image-{image_side}" if has_image else "image-text-layout text-only"
    image_block = f'<div class="it-image reveal scale-in" data-d="2">{image_html}</div>' if has_image else ""
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  <div class="{layout_class}">
    {image_block}
    <div class="it-list">{items_html}</div>
  </div>
</section>"""


def render_slide_product_gallery(s: dict, page_num: int, total: int) -> str:
    """Product gallery: grid of product cards.
    If summary_inline=True, summary becomes the first cell of the grid (replaces empty slot)."""
    header = s.get("header", {})
    products = s.get("products", [])
    cols = s.get("cols", 4)
    summary = s.get("summary", "")
    summary_inline = s.get("summary_inline", False)

    cells_html = ""
    if summary_inline and summary:
        cells_html += f'''
<div class="pg-summary-card reveal" data-d="2">
  <div class="pg-sum-eyebrow">OVERVIEW</div>
  <div class="pg-sum-text">{summary}</div>
</div>'''
    for i, p in enumerate(products):
        img = p.get("image", "")
        img_html = f'<img src="{img}" alt="{p.get("title","")}">' if img else ''
        revenue = p.get("revenue", "")
        rev_html = f'<div class="pg-revenue"><span class="pg-rev-value">{revenue}</span><span class="pg-rev-label">{p.get("revenue_label", "万元")}</span></div>' if revenue else f'<div class="pg-revenue pg-no-data">{p.get("revenue_label", "持续运营")}</div>'
        cells_html += f'''
<div class="pg-card reveal scale-in" data-d="{3+i if summary_inline else 2+i}">
  <div class="pg-image">{img_html}</div>
  <div class="pg-body">
    <div class="pg-title">{p.get("title", "")}</div>
    <div class="pg-desc">{p.get("desc", "")}</div>
    {rev_html}
  </div>
</div>'''
    return f"""
<section class="slide" data-slide="{page_num}">
  <header class="page-header reveal" data-d="1">
    <div class="num-badge">{header.get("num", "")}</div>
    <div class="tick"></div>
    <div><div class="h-title">{header.get("title", "")}</div><div class="h-en">{header.get("en", "")}</div></div>
    <div class="h-spacer"></div>
    <div class="h-meta">{page_num:02d} / {total:02d}</div>
  </header>
  {f'<div class="pg-summary reveal" data-d="2">{summary}</div>' if summary and not summary_inline else ""}
  <div class="product-gallery cols-{cols}">{cells_html}</div>
</section>"""


SLIDE_RENDERERS = {
    "cover": render_slide_cover,
    "icon-duo": render_slide_icon_duo,
    "timeline": render_slide_timeline,
    "compare-table": render_slide_compare_table,
    "split-layout": render_slide_split_layout,
    "tier": render_slide_tier,
    "dual-path": render_slide_dual_path,
    "thanks": render_slide_thanks,
    "dashboard": render_slide_dashboard,
    "milestone-line": render_slide_milestone_line,
    "progress-cards": render_slide_progress_cards,
    "image-text": render_slide_image_text,
    "product-gallery": render_slide_product_gallery,
    "chart-duo": render_slide_chart_duo,
}


def render_html(preset: dict, plan: dict) -> str:
    slides = plan.get("slides", [])
    total = len(slides)

    slides_html = []
    has_chart = False
    for i, s in enumerate(slides, 1):
        layout = s.get("layout", "cover")
        if layout == "chart-duo":
            has_chart = True
        renderer = SLIDE_RENDERERS.get(layout)
        if renderer is None:
            slides_html.append(f'<section class="slide"><p>Unknown layout: {layout}</p></section>')
        else:
            slides_html.append(renderer(s, i, total))

    pal = preset["palette"]
    chart_js = f"""
const CHART_COLORS = {{
  primary: '{pal["primary"]}',
  primaryMid: '{pal.get("primary_mid", pal["primary"])}',
  primaryBright: '{pal.get("primary_bright", pal["primary"])}',
  primaryPale: '{pal.get("primary_pale", "#cccccc")}',
  accent: '{pal["accent"]}',
  accentSoft: '{pal.get("accent_soft", pal["accent"])}',
  text: '{pal["text"]}',
  textDim: '{pal.get("text_dim", "#666")}',
  textMute: '{pal.get("text_mute", "#999")}',
  border: '{pal.get("border", "rgba(0,0,0,0.1)")}',
  cardBottom: '{pal.get("card_bottom", "#f5f5f5")}'
}};

const CHART_INSTANCES = new Map();

function buildChartOption(spec) {{
  const FONT = "IBM Plex Sans, 'Noto Sans SC', sans-serif";
  const opt = {{
    backgroundColor: 'transparent',
    grid: {{ top: 30, right: 30, bottom: 50, left: 50, containLabel: true }},
    legend: spec.legend !== false ? {{
      bottom: 4, icon: 'roundRect', itemWidth: 12, itemHeight: 6, itemGap: 24,
      textStyle: {{ color: CHART_COLORS.textDim, fontSize: 11, fontFamily: FONT }}
    }} : undefined,
    tooltip: {{
      trigger: spec.type === 'pie' ? 'item' : 'axis',
      backgroundColor: 'rgba(255,255,255,0.96)',
      borderColor: CHART_COLORS.primaryPale, borderWidth: 1,
      textStyle: {{ color: CHART_COLORS.text, fontFamily: FONT, fontSize: 12 }}
    }},
    animationEasing: 'cubicOut', animationDuration: 1100
  }};

  if (spec.type === 'bar') {{
    opt.xAxis = {{
      type: 'category', data: spec.categories,
      axisLine: {{ lineStyle: {{ color: CHART_COLORS.cardBottom }} }},
      axisTick: {{ show: false }},
      axisLabel: {{ color: CHART_COLORS.text, fontSize: 13, fontFamily: "'Noto Sans SC', sans-serif", margin: 12 }}
    }};
    opt.yAxis = {{
      type: 'value',
      axisLine: {{ show: false }}, axisTick: {{ show: false }},
      axisLabel: {{ color: CHART_COLORS.textMute, fontSize: 11, fontFamily: 'IBM Plex Mono, monospace', formatter: spec.yFormat || '{{value}}' }},
      splitLine: {{ lineStyle: {{ color: CHART_COLORS.cardBottom, type: 'dashed' }} }}
    }};
    opt.series = (spec.series || []).map((s, idx) => {{
      const colors = [CHART_COLORS.primary, CHART_COLORS.accent, CHART_COLORS.primaryBright];
      return {{
        name: s.name, type: 'bar', data: s.data,
        barWidth: spec.series.length > 1 ? '32%' : '50%',
        itemStyle: {{ color: colors[idx % 3], borderRadius: [4, 4, 0, 0] }},
        label: spec.showLabel !== false ? {{
          show: true, position: 'top',
          color: idx === 0 ? CHART_COLORS.primary : CHART_COLORS.accent,
          fontSize: 12, fontFamily: 'IBM Plex Mono, monospace', fontWeight: 500,
          formatter: spec.labelFormat || '{{c}}'
        }} : undefined
      }};
    }});
  }} else if (spec.type === 'pie') {{
    const colors = [CHART_COLORS.primary, CHART_COLORS.accent, CHART_COLORS.primaryBright,
                    CHART_COLORS.accentSoft, CHART_COLORS.primaryMid];
    opt.series = [{{
      type: 'pie', radius: ['45%', '70%'], center: ['50%', '50%'],
      avoidLabelOverlap: true,
      label: {{
        show: true, position: 'outside',
        color: CHART_COLORS.text, fontSize: 12, fontFamily: FONT,
        formatter: '{{b}}\\n{{d}}%'
      }},
      labelLine: {{ length: 12, length2: 8, lineStyle: {{ color: CHART_COLORS.textMute }} }},
      itemStyle: {{ borderColor: '#fff', borderWidth: 2 }},
      data: (spec.data || []).map((d, idx) => ({{
        ...d, itemStyle: {{ color: colors[idx % colors.length] }}
      }})),
      animationType: 'scale', animationEasing: 'elasticOut'
    }}];
  }} else if (spec.type === 'horizontal-bar') {{
    opt.grid = {{ top: 16, right: 100, bottom: 16, left: 80, containLabel: true }};
    opt.xAxis = {{
      type: 'value',
      axisLine: {{ show: false }}, axisTick: {{ show: false }},
      axisLabel: {{ show: false }}, splitLine: {{ show: false }}
    }};
    opt.yAxis = {{
      type: 'category', data: spec.categories,
      axisLine: {{ show: false }}, axisTick: {{ show: false }},
      axisLabel: {{ color: CHART_COLORS.text, fontSize: 13, fontFamily: "'Noto Sans SC', sans-serif" }},
      inverse: true
    }};
    opt.series = [{{
      type: 'bar', data: spec.data, barWidth: '52%',
      itemStyle: {{
        color: {{ type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [{{ offset: 0, color: CHART_COLORS.primary }}, {{ offset: 1, color: CHART_COLORS.accent }}] }},
        borderRadius: [4, 4, 4, 4]
      }},
      label: {{ show: true, position: 'right', color: CHART_COLORS.primary,
        fontSize: 13, fontFamily: 'IBM Plex Mono, monospace', fontWeight: 500,
        formatter: spec.labelFormat || '{{c}}' }}
    }}];
  }}
  return opt;
}}

function initChartsForSlide(slide) {{
  const charts = slide.dataset.charts;
  if (!charts || !window.echarts) return;
  const specs = JSON.parse(charts);
  const slideIdx = slide.dataset.slide;
  specs.forEach((spec, i) => {{
    const id = `chart_${{slideIdx}}_${{i}}`;
    const el = document.getElementById(id);
    if (!el) return;
    if (CHART_INSTANCES.has(id)) {{
      try {{ CHART_INSTANCES.get(id).dispose(); }} catch(e) {{}}
      CHART_INSTANCES.delete(id);
    }}
    setTimeout(() => {{
      const chart = echarts.init(el, null, {{ renderer: 'canvas' }});
      chart.setOption(buildChartOption(spec));
      CHART_INSTANCES.set(id, chart);
    }}, 460);
  }});
}}
"""

    nav_js = """
class SP {
  constructor(d) {
    this.deck=d; this.slides=[...d.querySelectorAll('.slide')]; this.total=this.slides.length;
    this.current=0; this.lock=false;
    this.initObserver(); this.initKB(); this.initWheel();
    this.slides[0].classList.add('active'); this.update();
  }
  initObserver() { const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting&&e.intersectionRatio>=0.55){const i=this.slides.indexOf(e.target);if(i!==this.current){this.slides.forEach((s,j)=>s.classList.toggle('active',j===i));this.current=i;this.update();const cur=this.slides[i];if(cur.classList.contains('chart-slide')&&typeof initChartsForSlide==='function')initChartsForSlide(cur);}}});},{root:this.deck,threshold:[0.55]});this.slides.forEach(s=>io.observe(s)); }
  goto(i){i=Math.max(0,Math.min(this.total-1,i));this.slides[i].scrollIntoView({behavior:'smooth',block:'start'});}
  initKB(){window.addEventListener('keydown',e=>{if(['ArrowDown','ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();this.goto(this.current+1);}else if(['ArrowUp','ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();this.goto(this.current-1);}});}
  initWheel(){this.deck.addEventListener('wheel',e=>{e.preventDefault();if(this.lock||Math.abs(e.deltaY)<10)return;this.lock=true;this.goto(this.current+(e.deltaY>0?1:-1));setTimeout(()=>{this.lock=false;},800);},{passive:false});}
  update(){const p=this.total>1?(this.current/(this.total-1))*100:0;document.getElementById('pf').style.width=p+'%';document.getElementById('cur').textContent=String(this.current+1).padStart(2,'0');document.getElementById('tot').textContent=String(this.total).padStart(2,'0');}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',()=>new SP(document.getElementById('deck')));
else new SP(document.getElementById('deck'));
"""

    echarts_cdn = '<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>' if has_chart else ''
    chart_init_js = chart_js if has_chart else ''
    chart_init_first = """
// init chart on first slide if it's a chart slide
const firstSlide = document.getElementById('deck').querySelector('.slide.active');
if (firstSlide && firstSlide.classList.contains('chart-slide') && typeof initChartsForSlide === 'function') {
  setTimeout(() => initChartsForSlide(firstSlide), 800);
}
""" if has_chart else ''

    return f"""<!doctype html>
<html lang="zh-CN"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{plan.get("title", "Smart PPT")} · {preset["name_cn"]}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=IBM+Plex+Sans:wght@200;300;400;500;600&family=IBM+Plex+Mono:wght@300;400&family=Noto+Serif+SC:wght@400;500;600;700&family=Noto+Sans+SC:wght@200;300;400;500;600&display=swap" rel="stylesheet">
{echarts_cdn}
<style>
{render_css_vars(preset["palette"])}
{render_base_css(preset)}
</style>
</head><body>
<div class="progress-bar"><div class="progress-fill" id="pf"></div></div>
<div class="page-indicator"><span class="cur" id="cur">01</span> / <span id="tot">{total:02d}</span></div>
<button class="fs-btn" id="fsBtn" type="button" aria-label="全屏切换" title="全屏 (F)">
  <span class="fs-icon-enter">⛶</span>
  <span class="fs-icon-exit">⤢</span>
</button>
<div class="deck" id="deck" tabindex="0">
{"".join(slides_html)}
</div>
<script>
(function(){{
  const btn = document.getElementById('fsBtn');
  const isFs = () => !!(document.fullscreenElement || document.webkitFullscreenElement);
  const enter = () => {{
    const el = document.documentElement;
    (el.requestFullscreen || el.webkitRequestFullscreen).call(el).catch(()=>{{}});
  }};
  const exit = () => {{
    (document.exitFullscreen || document.webkitExitFullscreen).call(document).catch(()=>{{}});
  }};
  btn.addEventListener('click', () => {{ isFs() ? exit() : enter(); }});
  document.addEventListener('keydown', e => {{
    if (e.key === 'f' || e.key === 'F') {{
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      e.preventDefault();
      isFs() ? exit() : enter();
    }}
  }});
  document.addEventListener('fullscreenchange', () => btn.classList.toggle('is-fullscreen', isFs()));
  document.addEventListener('webkitfullscreenchange', () => btn.classList.toggle('is-fullscreen', isFs()));
}})();
</script>
<script>
{chart_init_js}
{nav_js}
{chart_init_first}
</script>
</body></html>"""


def render_from_files(preset_path: str, plan_path: str, output_path: str):
    with open(preset_path, 'r', encoding='utf-8') as f:
        preset = json.load(f)
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)
    html = render_html(preset, plan)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return output_path
