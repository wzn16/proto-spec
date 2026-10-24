---
name: proto-spec
description: >-
  规范驱动的多页 HTML 原型生成：先通过人机访谈确立设计规范并冻结为 SPEC 与 design tokens，再按规范批量生成风格一致、可点击跳转的静态 HTML 原型，脚本自动检查规范符合性与死链，替代 Axure 类原型工具；产出以「能直接交付甲方演示与评审」的商务交付水平为质量标准。当用户要做网页原型、后台或移动端演示原型、从手绘草图转原型、多页面高保真 demo，或要求先定设计规范再生成页面时使用；不要用于真实业务系统开发、需要后端与真实数据的工程、单页官网视觉稿（无多页一致性诉求），也不替代已有设计系统的工程化还原。
  Spec-driven multi-page HTML prototyping: freeze a design spec and tokens via interview, then batch-generate consistent clickable prototypes with quality gates — an Axure alternative.
license: MIT
metadata:
  author: wzn16
  version: 0.3.1
  tags: prototype html spec-driven axure frontend
---

# proto-spec — 规范驱动的多页 HTML 原型

把「设计规范」做成独立、可冻结、机器可读的一层，页面只准引用、不准发明。
产出物：一个纯静态原型项目目录（`index.html` 站点地图 + `pages/` 页面 + `assets/` 共享样式），
双击即可演示，无构建、零依赖。核心价值：多页视觉一致由机制保证；改规范一处生效全站。

## 模式选择

| 模式 | 进入条件 | 执行路径 |
| --- | --- | --- |
| A 全流程 | 目标目录没有冻结的 SPEC.md | 步骤 1→2→3→4→5→6 |
| B 迭代 | 目录已有 `SPEC.md`（frozen）+ 质量门通过记录 | 步骤 5（意见三分法）→ 4（受影响页）→ 6 |
| C 仅规范 | 用户只要规范文档与 tokens，不要页面 | 步骤 1→2→3 后停止 |
| D 体检 | 用户只要求检查已有原型项目 | 步骤 6 后输出验收单 |
| E 单页轻量 | ≤3 页或单屏演示/路演 | 步骤 1→2（风格包默认 + ≤3 问）→3→4（用 tpl-single 单页模板）→5.5→6 |

## 硬红线（任何模式都生效）

1. 页面只准引用 tokens 变量与片段库组件；裸色值、档外间距/字号、脱库组件即违规。
2. CSS 变量只许在项目内的 tokens.css 定义；页面自定义颜色变量即违规。
3. SPEC 冻结后，复现于 ≥2 页的意见必须写回规范（版本 +1）并批量重生成受影响页，禁止逐页打补丁。
4. 一切「通过」必须引用质量门报告的计数字段；脚本 exit ≠ 0 时逐条修复重跑，禁止口头豁免。
5. tokens.css 与 SPEC.md 冲突时，以 tokens.css 为准回改文档。

## 步骤 1 — 输入接收

- 用户给了草图/截图：用模型自身的视觉能力读图，提取布局骨架、主色（取色聚类）、密度、控件形状、页面类型线索，形成带置信度的推断值集，供步骤 2 使用。
- 纯对话：直接进步骤 2。
- 需求超出静态原型范畴（要真实业务逻辑、数据库、登录鉴权）：停止并说明本 skill 只做演示原型。

## 步骤 1.5 — 无参考物的设计推理（文字需求 → 界面）

用户只给功能描述、没有参考产品/设计稿时，走 `references/design-from-brief.md` 六步：
① 识别功能族（记录/单据/流程/分析/配置/工具）→ ② 定信息架构（导航形态）→ ③ 选骨架
（`references/layout-patterns.md` 八个骨架，一个页面只用一个主骨架）→ ④ 定容器与字段顺序
→ ⑤ 定旋钮 → ⑥ 自检三问（删掉一半 / 三秒测试 / 名字测试）。
每一步的决策与理由写进 SPEC；交付时附「本版已知弱点 3 条」。
混合功能族必须拆页，不允许塞进一屏。

## 步骤 2 — 访谈定规范

读 `references/interview-bank.md` 并严格按其执行：G0 语境 4 题必答（唯一不许全默认的组）→
气质关键词映射候选美学家族（见 `references/family-library.md`），按所选家族整包推荐 → G1–G8 分组批量确认（一次一组，组内「当前值 + 备选 + 理由」表格呈现）→
钉子题必须用户显式表态。用户说风格没想好时，先生成 2–3 个候选家族的迷你示例页供其挑选，再继续访谈。
产出：填写完成的 `SPEC.md`（从 `starter/SPEC.md` 复制）。
停止条件：钉子题（G0 全组、主色、页面底色、页面清单、保真度）未获用户表态，不得进入步骤 3。
有参照截图时，还须产出**元素对账单**（按顶栏/侧栏/筛选区/表格/分页/表单区逐区域枚举参照物可见元素，
每个元素标注沿用/简化/舍弃并给理由）。停止条件：**对账单未经用户逐项确认，不得进入步骤 3 生成**——
细节类决策（形态/位置/文案/组件）用户未给明确的，一律先问，禁止靠假设下手。

## 步骤 3 — 冻结规范

1. 把 `starter/` 整体复制到目标项目目录（保持内部结构不变）。
2. 用访谈结果同步更新项目内 SPEC.md 与 tokens.css；含家族整包替换时，tokens.css 与 family.css 一起换，并在 SPEC §2.0 冻结所选家族的 id + 版本（附录 B 记家族登记行）。
3. 落定页面清单：SPEC §8（人读表格）+ 项目根 `pages-manifest.json`（机器可读，G3 对账基准），
   含每页 id、路径、标题、类型、状态页，两处同步。
4. 状态机 `draft → confirmed → frozen`：分组确认完为 confirmed，用户明确同意后才标 frozen。
停止条件：SPEC 未到 frozen，禁止进入步骤 4。

## 步骤 4 — 批量生成

读 `references/templates-catalog.md` 与 `references/snippets-catalog.md`，再动工：

1. 先生成 `index.html` 站点地图（按用户任务流分组，不是文件目录镜像），页面树先行，杜绝孤页。
2. 逐页生成：复制对应模板 → 替换插槽内容（真实感中文假数据，禁 lorem）→ 挂跳转链接 → 加原型工具条。
3. 每页完成立即跑 G1 单页检（见步骤 6），exit 0 才允许开始下一页。
4. 全部页面完成后跑 G1 全量复检 + G3。
5. **状态页由 manifest 驱动生成**：manifest 里 `states` 声明的每个状态（empty/loading/error/failed/denied），
   复制主页面骨架 + 换成对应状态内容（空态用 `c-empty`、错误态用 `c-alert--error`），文件名 `<id>.<state>.html`，
   并登记进站点地图；不得只声明不生成（G3 三方对账会拦）。

## 步骤 4 — 后台工作台页

后台工作台（侧栏模块 + 页签 + KPI + 查询栏 + 树/表）一律使用组件库「工作台层」：
`c-workbench` / `c-side-menu__*` / `c-tabbar` / `c-kpi-row` / `c-qbar` / `c-split` / `c-tree__*` / `c-data-table__*` / `c-pager`。
禁止在页面里重造侧栏、页签、KPI、查询栏、树、表格的骨架与配色——页面只写业务专属的 `p-` 局部样式。
这层保证跨项目一致的层级节奏（卡片 16px 间距、页面 24px 内边距、三级文字色、浅蓝强调底、代码列等宽）。

## 步骤 4.2 — 细节默认值（写页面前必读）

`references/detail-rules.md` 给的是**默认值而非建议**：容器防溢出、列宽档位、动作不重复、KPI 语义、
数字口径、抽屉浮动、三态齐全等 27 条。违反要在 SPEC 写理由。三条可机检项由 `scripts/check_details.py` 把关。

## 步骤 4.3 — 设计→实现映射（写页面前必做）

逐区块写映射（组件 / token / 是否新增原语 / 成本：低中高），依据 `references/implementation-map.md`：
能用现有组件的不许自定义；需要新原语的先升级组件库再用；成本「高」（伪元素拟物、transform、嵌套滚动、绝对定位）默认不做，
除非有说服力理由并写进 SPEC。原型不承诺接口级能力，须在交付说明列明边界。

## 步骤 4.4 — 台账与表单：选基线，然后调

`references/patterns-ledger.md` 与 `references/patterns-form.md` 给的是**参考基线**（形态菜单、可调维度、默认值、常见病）。
它们是起点不是终点：按业务语境选形态与参数，写进 SPEC；交付前用 `references/tuning-loop.md` 跑 ≥1 轮调优
（生成 → 三档截图 → 六维打分 → 只改最低分 → 再截图对比 → 记录结论）。

- 形态：标准 / 主从 / 卡片 / 高密度（也可自创，写清理由）
- 参数：密度、斑马纹、行选中、操作列、分页、KPI、筛选形态、抽屉尺寸、栅格、标签位置、校验时机、保存策略
- 装配方式：优先用修饰类（`c-data-table--dense|--comfort|--zebra|--pin-first`、`c-drawer--sm|--md|--lg`、`c-form-grid--1|--2|--3|--label-left`、`c-kpi-row--2|--3|--6`、`c-list-rows`）与 tokens 档位（`--c-row-h*`、`--c-cell-px*`、`--c-drawer-*`）
- 允许偏离基线：**只要在 SPEC 的设计决策里写清「为什么这样更好」**；不要因为基线这么写就把项目扭成基线

## 步骤 4.5 — 工具型页面例外

交互密集的单页工具（树形选择、多级联动筛选、可折叠面板等）允许**页面级 `p-` 前缀脚本**：
≤120 行、零外部依赖、只读 DOM 操作（渲染/过滤/切换显隐），不引入框架、不发请求。
其余页面仍遵守「零自定义 JS」；脚本必须写进 SPEC §9 的技术约定并在交付说明中声明。
超过 120 行说明该交互应下沉为项目内 app.js 的新 data-action 行为（走组件库修订）。

## 步骤 5 — 评审与迭代

交付 = 项目目录（可 zip）。演示入口为 `index.html`。用户意见按三分法分诊：

- 页面级（只这页）：定向重生成该页，只准引用现有 tokens 与片段，改完重跑 G1/G3。
- 规范级（所有页都该这样）：解冻 SPEC → 改 SPEC + tokens.css → 版本 +1 并记录原因与影响面 → 批量重生成受影响页 → 全量 G1/G3。
- 新页面：先补 SPEC §8 manifest 与站点地图，再按步骤 4 生成。
同类页面级例外 ≥3 处时，提示用户该走规范级通道（例外变多说明规范该改）。

## 步骤 5.5 — 视觉精修与评审（G7 强制门）

每轮页面完成后**立刻**写 `qa/visual-review.md`（模板与判据见 `references/visual-scorecard.md`）：
三秒测试两句 → 锚线条数 → 六维打分（<4 必须改）→ 改进项 ≤5 条 → 保留 1–2 条。
`scripts/check_visual_review.py` 会拦：缺文件、缺小节、缺分数、低分未处理（除非写「不采纳 + 理由」）。
配合 `references/tuning-loop.md`（迭代方法）与 `references/design-knowledge.md`（判断标准）使用。
有截图后跑 `scripts/check_pixels.py`（G8 像素判据见 `references/pixel-rules.md`：锚线/贴边/强调面积/字号层级）。
自评完成后按 `references/visual-review-protocol.md` 派发独立评审，产出 `qa/visual-review-peer.md`；
两份评分单同一维度差 ≥2 分时，必须在自评单写「分歧」小节说明处理方式（改 或 不采纳+理由）。

先跑 `references/design-knowledge.md` 第四节的三秒测试与模型默认做法清单，再按 `tuning-loop.md` 六维打分迭代。
评审结论写成「位置 → 现象 → 改完要达到的可验收结果」，不写「再精致一点」。

## 步骤 5.6 — 视觉精修执行（原步骤 5.5）（推荐）

质量门通过后，从**组件库层**做一轮视觉精修：只加过渡、状态反馈（hover/active/focus-visible）、
层次节奏（表头字距、卡片表头分隔、选中指示条、细滚动条），**不改规范值**——改的是组件实现质量，
不是设计决策。精修可借助环境内界面设计类 skill；精修后必须重跑质量门。样式精细度类用户反馈，
优先回写组件库而非逐页打补丁。
精修方法与逐维评审清单见 `references/visual-refinement.md`。

## 步骤 6 — 质量门

读 `references/qa-gates.md`；脚本在 `scripts/`，用 `python3` 运行（≥3.10，纯标准库）：

```
python3 scripts/check_tokens.py --project <项目目录>            # G1 规范符合性（可加 --page 单页检）
python3 scripts/check_links.py  --project <项目目录>            # G3 死链与三方对账
python3 scripts/check_screens.py --project <项目目录>           # G2 截图矩阵（可选，见下）
python3 scripts/check_contrast.py --project <项目目录>          # G4 可访问性对比度
python3 scripts/check_tokens.py --project <项目目录> --family F3  # 家族保真（身份特征 diff=0）
python3 scripts/final_gate.py   --project <项目目录>            # G5 总验收（重跑全部子门）
python3 scripts/gen_delivery_readme.py --project <项目目录>      # 生成交付 README（页面地图/门摘要/已知占位）
```

- G2 能力接口：当前环境具备截图/浏览器能力时，对每页 × 断点（1440/768/375）截图存入
  `<项目>/qa/screenshots/`（文件名 `<页面id>-<宽>.png`）再跑 G2；不具备时跳过 G2，
  并在交付说明中声明「视觉门未执行」。G1/G3/G5 任何环境都必须执行。
- G5 通过后输出人读验收单：引用各报告 JSON 的计数字段原文（如 `"violations": 0`）。
- 报告统一写入 `<项目>/qa/reports/`。

## 兼容性

- 产物：纯静态 HTML + CSS + 少量原生 JS（app.js 声明式交互），无构建、无外部请求，file:// 直开。
- 脚本：Python 3.10+ 标准库，无第三方包。
- 分发：整个 skill 目录复制到目标宿主的 skills 目录即可；项目产物对查看者零要求（浏览器即可）。
- 已验证：macOS + Python 3.12；其他平台未逐一验证，脚本仅用标准库以降低差异风险。

## 参考资料索引

**探索与规范**（步骤 1.5–3）

| 文件 | 何时读 |
| --- | --- |
| `references/design-from-brief.md` | 文字需求 → 六步推理 |
| `references/layout-patterns.md` | 八个骨架与错法 |
| `references/design-direction.md` | 品类、调性、引擎、方向卡 |
| `references/direction-explorer.md` | 方向对比页做法 |
| `references/design-knobs.md` | 五旋钮与组合矩阵 |
| `references/interview-bank.md` | 访谈协议与题库 |
| `references/family-library.md` | 家族索引与治理 |
| `references/spec-template.md` | SPEC 章节结构 |

**生成**（步骤 4）

| 文件 | 何时读 |
| --- | --- |
| `references/tokens-reference.md` | 三层变量与命名空间 |
| `references/snippets-catalog.md` | 组件片段白名单 |
| `references/templates-catalog.md` | 模板清单与插槽 |
| `references/patterns-ledger.md` | 台账基线 |
| `references/patterns-form.md` | 表单基线 |

**评审与验收**（步骤 5–6）

| 文件 | 何时读 |
| --- | --- |
| `references/design-knowledge.md` | 三秒测试与判断标准 |
| `references/tuning-loop.md` | 六维评分与迭代 |
| `references/visual-refinement.md` | 精修清单 |
| `references/taste-checklist.md` | 反模板感自查 |
| `references/qa-gates.md` | 各门判据与降级 |
