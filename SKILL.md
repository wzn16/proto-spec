---
name: proto-spec
description: >-
  规范驱动的多页 HTML 原型生成：先通过人机访谈确立设计规范并冻结为 SPEC 与 design tokens，再按规范批量生成风格一致、可点击跳转的静态 HTML 原型，脚本自动检查规范符合性与死链，替代 Axure 类原型工具。当用户要做网页原型、后台或移动端演示原型、从手绘草图转原型、多页面高保真 demo，或要求先定设计规范再生成页面时使用；不要用于真实业务系统开发、需要后端与真实数据的工程、单页官网视觉稿（无多页一致性诉求），也不替代已有设计系统的工程化还原。
  Spec-driven multi-page HTML prototyping: freeze a design spec and tokens via interview, then batch-generate consistent clickable prototypes with quality gates — an Axure alternative.
license: MIT
metadata:
  author: wzn16
  version: 0.1.2
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

## 步骤 2 — 访谈定规范

读 `references/interview-bank.md` 并严格按其执行：G0 语境 4 题必答（唯一不许全默认的组）→
按 G0 套风格包整包推荐 → G1–G8 分组批量确认（一次一组，组内「当前值 + 备选 + 理由」表格呈现）→
钉子题必须用户显式表态。用户说风格没想好时，先生成 2–3 套候选配色的迷你示例页供其挑选，再继续访谈。
产出：填写完成的 `SPEC.md`（从 `starter/SPEC.md` 复制）。
停止条件：钉子题（G0 全组、主色、页面底色、页面清单、保真度）未获用户表态，不得进入步骤 3。
有参照截图时，还须产出**元素对账单**（按顶栏/侧栏/筛选区/表格/分页/表单区逐区域枚举参照物可见元素，
每个元素标注沿用/简化/舍弃并给理由）。停止条件：**对账单未经用户逐项确认，不得进入步骤 3 生成**——
细节类决策（形态/位置/文案/组件）用户未给明确的，一律先问，禁止靠假设下手。

## 步骤 3 — 冻结规范

1. 把 `starter/` 整体复制到目标项目目录（保持内部结构不变）。
2. 用访谈结果同步更新项目内 SPEC.md 与 tokens.css（含风格包整体替换时，两处一起换）。
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

## 步骤 5 — 评审与迭代

交付 = 项目目录（可 zip）。演示入口为 `index.html`。用户意见按三分法分诊：

- 页面级（只这页）：定向重生成该页，只准引用现有 tokens 与片段，改完重跑 G1/G3。
- 规范级（所有页都该这样）：解冻 SPEC → 改 SPEC + tokens.css → 版本 +1 并记录原因与影响面 → 批量重生成受影响页 → 全量 G1/G3。
- 新页面：先补 SPEC §8 manifest 与站点地图，再按步骤 4 生成。
同类页面级例外 ≥3 处时，提示用户该走规范级通道（例外变多说明规范该改）。

## 步骤 6 — 质量门

读 `references/qa-gates.md`；脚本在 `scripts/`，用 `python3` 运行（≥3.10，纯标准库）：

```
python3 scripts/check_tokens.py --project <项目目录>            # G1 规范符合性（可加 --page 单页检）
python3 scripts/check_links.py  --project <项目目录>            # G3 死链与三方对账
python3 scripts/check_screens.py --project <项目目录>           # G2 截图矩阵（可选，见下）
python3 scripts/final_gate.py   --project <项目目录>            # G5 总验收（重跑全部子门）
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

| 文件 | 何时读 |
| --- | --- |
| `references/interview-bank.md` | 步骤 2 开始前（题库、风格包、访谈协议） |
| `references/spec-template.md` | 填写 SPEC.md 时（章节结构与填写说明） |
| `references/tokens-reference.md` | 改 tokens 或生成页面前（三层变量、类名命名空间） |
| `references/snippets-catalog.md` | 步骤 4 拼装页面前（组件片段白名单） |
| `references/templates-catalog.md` | 步骤 4 选模板时（模板清单、插槽、目录与链接约定） |
| `references/taste-checklist.md` | 每页生成后自查与 G5 前（反模板感判据） |
| `references/qa-gates.md` | 步骤 6（各门判据、执行时点、降级规则） |
