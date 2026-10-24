---
name: proto-spec
description: >-
  规范驱动的多页 HTML 原型生成：先通过人机访谈确立设计规范并冻结为 SPEC 与 design tokens，再按规范批量生成风格一致、可点击跳转的静态 HTML 原型，脚本自动检查规范符合性、死链、对比度、细节与像素级指标，替代 Axure 类原型工具；产出以「能直接交付甲方演示与评审」的商务交付水平为质量标准。当用户要做网页原型、后台或移动端演示原型、从手绘草图转原型、多页面高保真 demo，或要求先定设计规范再生成页面时使用；不要用于真实业务系统开发、需要后端与真实数据的工程、单页官网视觉稿（无多页一致性诉求），也不替代已有设计系统的工程化还原。
  Spec-driven multi-page HTML prototyping: freeze a design spec and tokens via interview, then batch-generate consistent clickable prototypes with eight quality gates — an Axure alternative.
license: MIT
metadata:
  author: wzn16
  version: 1.2.0
  tags: prototype html spec-driven axure frontend design-system
---

# proto-spec — 规范驱动的多页 HTML 原型

把「设计规范」做成可冻结、机器可读的一层：页面只准引用，不准发明。产出纯静态项目（`index.html` 站点地图 + `pages/` + `assets/`），双击即演示、零构建、零依赖。改规范一处，全站生效。

## 模式

| 模式 | 触发 | 路径 |
| --- | --- | --- |
| A 全流程 | 后台/多页系统（默认） | 步骤 1→6 全跑 |
| B 补页 | 已有规范，续加页面 | 步骤 3 读旧 SPEC → 4→6 |
| C 改版 | 已有原型要重做 | 步骤 1.5 诊断 → 2→6 |
| D 体检 | 只检查已有项目 | 步骤 6（含像素与双评） |
| E 单页轻量 | ≤3 页或单屏演示 | 步骤 2 走捷径 → tpl-single → 5.5→6 |

## 步骤 1 — 目标与约束

一句话目标 + 成功标准；记下角色、数据量级、使用场合、是否打印/投影、是否触屏。缺的信息列入待确认，不静默假设。

## 步骤 1.5 — 只有草图或文字时先做设计推理

**只有草图** → 按功能重建信息架构，不照搬原布局：读 `references/design-from-brief.md` 六步（功能族 → 信息架构 → 骨架 → 容器 → 旋钮 → 自检），骨架从 `references/layout-patterns.md` 里选一个主骨架。
**混合功能族必须拆页**，不允许塞进一屏。草图的屏幕数不是页面数。

## 步骤 2 — 访谈

读 `references/interview-bank.md`：G0 语境 4 题必答 → 气质词映射家族（`references/family-library.md`，10 个家族 F0–F9）→ G1–G8 分组批量确认（一次一组，给「当前值 + 备选 + 理由」）。细节类问题必须问到答案。

## 步骤 2.5 — 定旋钮

读 `references/design-knobs.md`：对比强度 / 信息密度 / 圆角柔软度 / 色温与强调面积 / 动效幅度，各给一句取值与理由，写进 SPEC §2。禁止跳过直接套家族——家族定方向，旋钮定强度。

## 步骤 2.6 — 出方向（用户未指定时）

读 `references/design-direction.md` 出 2–3 个方向：认品类拆标杆 → 五刻度调性 → 把模糊词翻译成可观察决定 → 每方向选一个生成引擎 → 各定色相家族 → 选工作区骨架 → 写方向卡。
用 `references/direction-explorer.md` 做成对比页给用户选。同一轮方向之间骨架/色相/控件语法必须不同；只换颜色不算方向。

## 步骤 3 — 冻结 SPEC

按 `references/spec-template.md` 写 SPEC：调性、色板（含对比度）、字阶、间距、圆角、动效、家族与旋钮、页面清单、组件清单、生成契约。状态置 frozen 后页面不得偏离。

## 步骤 4 — 生成

选模板 `references/templates-catalog.md`，拼装用 `references/snippets-catalog.md` 白名单组件，变量查 `references/tokens-reference.md`（三层：`--g-*` / `--s-*` / `--c-*`；类名前缀 `c-/l-/u-/p-`）。

**4.2 细节默认值**：读 `references/detail-rules.md`（27 条，含防溢出、列宽档位、动作不重复、KPI 语义、数字口径、抽屉浮动、三态）。
**4.3 设计→实现映射**：读 `references/implementation-map.md`，逐区块写「组件 / token / 是否新增原语 / 成本（低中高）」；高成本手段默认不做。
**4.4 台账与表单基线**：`references/patterns-ledger.md` 给台账形态菜单与可调维度，`references/patterns-form.md` 给容器判据与字段规格；可偏离，需写理由。
**4.5 工具页例外**：交互密集单页允许 `p-` 级脚本（≤120 行、零依赖、只读 DOM）；超出则下沉为组件行为。

## 步骤 5 — 自检

`references/taste-checklist.md` 反模板感 17 条 + `references/visual-refinement.md` 精修清单，逐条过。

## 步骤 5.5 — 双评（强制）

1. 有截图后跑 `scripts/check_pixels.py`（G8，判据见 `references/pixel-rules.md`：锚线 / 贴边 / 右缘留白 / 强调面积 / 字号层级 / 行距）。
2. 按 `references/visual-scorecard.md` 写自评 `qa/visual-review.md`：三秒测试两句、锚线条数、六维打分（<4 必须改）、改进项、保留项。
3. 按 `references/visual-review-protocol.md` 派发独立评审 → `qa/visual-review-peer.md`；同一维度差 ≥2 分必须在自评单写「分歧」并说明改不改。
4. 迭代方法见 `references/tuning-loop.md`；有上一版截图时用 `scripts/diff_shots.py` 看变化区块与指标走向。

## 步骤 6 — 验收

读 `references/qa-gates.md`，脚本在 `scripts/`（Python ≥3.10，纯标准库 + Pillow）：

```bash
# 单项门
python3 scripts/check_tokens.py   --project <目录>   # G1
python3 scripts/check_links.py    --project <目录>   # G3
python3 scripts/check_contrast.py --project <目录>   # G4
python3 scripts/check_details.py  --project <目录>   # G6
python3 scripts/check_visual_review.py --project <目录>  # G7
python3 scripts/check_pixels.py   --project <目录>   # G8
python3 scripts/check_screens.py  --project <目录>   # G2
```

```bash
# 总验收与交付
python3 scripts/final_gate.py --project <目录>              # G5 重跑全部子门
python3 scripts/check_tokens.py --project <目录> --family F3  # 家族保真
python3 scripts/gen_delivery_readme.py --project <目录>      # 交付 README
```

G5 全绿才算完成；不合格项按脚本 hint 逐条改，不讨价还价。

## 交付与边界

交付：项目目录（页面 + assets + SPEC + qa 报告）+ 交付 README（页面地图、门禁摘要、已知限制）。首轮概览页注明演示版本与占位说明。
不承诺：真实接口/权限/并发/后端校验；截图、评审执行者等外部能力只写调用协议，不写死实现。已知限制必须写进 README。

## 参考资料

**探索**：`references/design-from-brief.md` · `references/layout-patterns.md` · `references/design-direction.md` · `references/direction-explorer.md` · `references/design-knobs.md`

**规范**：`references/interview-bank.md` · `references/family-library.md`（F0–F9）· `references/spec-template.md` · `references/tokens-reference.md`

**生成**：`references/templates-catalog.md` · `references/snippets-catalog.md` · `references/patterns-ledger.md` · `references/patterns-form.md` · `references/detail-rules.md` · `references/implementation-map.md`

**评审**：`references/taste-checklist.md` · `references/visual-refinement.md` · `references/visual-scorecard.md` · `references/visual-review-protocol.md` · `references/tuning-loop.md` · `references/design-knowledge.md` · `references/pixel-rules.md` · `references/qa-gates.md`

## 自检

```bash
python3 scripts/selftest.py    # 本 skill 的合规/违规样例双向验证
```
