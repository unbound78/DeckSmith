# Changelog

本项目的所有重要变更都记录在此文件。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，版本遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [0.1.0] - Unreleased

首个版本。实战派中文场景演示生成工具，HTML + PPT 双输出。

### 新增

- **HTML 渲染引擎**（`deck_smith/html_renderer.py`）：14 种布局（cover / dashboard / milestone-line / progress-cards / image-text / icon-duo / timeline / compare-table / split-layout / tier / dual-path / product-gallery / chart-duo / thanks），scroll-snap 单页放映。
- **PPT 工具积木**（`deck_smith/pptx_toolkit.py`）：渐变 / 阴影 / 文字渐变 / 中文字体三套 / 基础形状 / 文本溢出预检，全部输出 PPT 原生可编辑形状。
- **8 套配色预设**（`presets/`）：暖金暗黑 / 蓝橙亮色 / 漆黑幽紫 / 莫兰迪灰 / 教育亲子等，四维度轴（tone/hue/saturation/contrast）。
- **Claude Code Skill**（`skill/SKILL.md`）：7-step 设计逻辑（形态→语境→内容→图片策略→信息架构→布局→配色→渲染→自检），给判断准则而非固定模板。
- **设计科学 references**（`skill/references/`）：配色推导（color-guide）/ 设计方法论（design-logic）/ 中文场景避坑（chinese-pitfalls）/ 布局字段（plan-schema）。
- **可运行示例**（`examples/`）：一份材料的 HTML + PPT 双版本产出。
- **CLI 脚本**：`render_html.py`（HTML 渲染）/ `verify_pptx.py`（字体字号合规校验）。

### 说明

- 智能配图能力（生图工具集成）为预留接口设计（见 `skill/references/image-gen-bridge.md`），当前版本**不含**生图工具本身。

[0.1.0]: #
