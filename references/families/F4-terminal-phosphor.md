# F4 终端机能·磷光
```json family-manifest
{
  "id": "F4",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#0A0C10",
    "--s-color-primary": "#D8DEE9",
    "--s-color-accent": "#2DD4BF",
    "--s-font-mono": "ui-monospace, \"SF Mono\", \"Cascadia Code\", Consolas, monospace",
    "--g-radius-6": "4px",
    "--g-radius-8": "4px",
    "--s-text-primary": "#E8EAED",
    "--s-text-secondary": "#9AA3AF",
    "--s-text-inverse": "#0A0C10",
    "--s-border": "#23262E",
    "--s-bg-sidebar": "#06070A",
    "--s-color-success-strong": "#4ADE80",
    "--s-color-error-strong": "#F87171",
    "--s-bg-card": "#11141A",
    "--s-bg-hover": "#1A1E26",
    "--s-nav-active-bg": "rgba(255, 255, 255, .12)",
    "--s-nav-active-text": "#E5E7EB",
    "--s-tag-success-bg": "rgba(74, 222, 128, .14)",
    "--s-tag-success-text": "#86EFAC",
    "--s-tag-success-line": "rgba(74, 222, 128, .24)",
    "--s-tag-warning-bg": "rgba(251, 191, 36, .14)",
    "--s-tag-warning-text": "#FCD34D",
    "--s-tag-warning-line": "rgba(251, 191, 36, .24)",
    "--s-tag-error-bg": "rgba(248, 113, 113, .14)",
    "--s-tag-error-text": "#FCA5A5",
    "--s-tag-error-line": "rgba(248, 113, 113, .24)",
    "--s-radius-square": "2px",
    "--s-brand-text": "#E5E7EB",
    "--s-segmented-text": "#C7CBD3",
    "--c-sidebar-w": "240px",
    "--c-content-max": "1100px"
  },
  "structure": [
    ".c-data-table td, .c-data-table th { font-family: var(--s-font-mono); font-size: var(--s-fs-small); }",
    ".c-kpi__num { font-family: var(--s-font-mono); letter-spacing: -0.02em; }",
    ".c-card { box-shadow: none; border-color: var(--s-border); }",
    ".c-workbench__head h1 { font-family: var(--s-font-mono); text-transform: uppercase; letter-spacing: .04em; }",
    ".c-data-table th { text-transform: uppercase; letter-spacing: .08em; }",
    ".c-card { border-radius: var(--s-radius-square); }",
    ".c-workbench__content { max-width: var(--c-content-max); margin-inline: auto; width: 100%; }"
  ]
}```


> 家族 id：F4 · 版本：v0.1（草案建档） · 上级：[美学家族库](../family-library.md)

> 实测记录（2026-10-23，样本页 tpl-list）：家族氛围完全成立；首轮派生漏抄 `--s-text-inverse` 重映射，
> 主钮对比度 1.35:1 被实测拦截——印证「家族保真机检」的必要性，该检查进入实现排期。

## ① 调性

近黑底、等宽字、一根磷光青。克制到近乎刻薄的界面 + 一处荧光点缀，像一台设计良好的终端。打开任何一页：每次点击都像按下回车。

## ② tokens 覆盖值表（diff vs F0）

| 槽位 | F0 | F4 | 备注 |
| --- | --- | --- | --- |
| `--g-bg-page` / `--s-bg-page` | #F5F7FA | **#0A0C10** | 近黑 |
| `--s-bg-card` | #FFFFFF | **#11141A** | |
| `--s-bg-hover` | gray-100 | **#171B22** | |
| `--s-color-primary` | blue-600 | **#D8DEE9** | **主操作=亮灰实底黑字**（终端回车键隐喻；14.5:1 ✓）；hover #FFFFFF、active #B9C2CF |
| `--s-color-primary-soft` / `softer` | blue-50/100 | **#1A1F27 / #232A34** | |
| `--s-color-accent` **（新增槽位）** | 无（=主色） | **#2DD4BF** | 磷光青：链接/选中/焦点环/数据高亮专用（on 页底 10.5:1 ✓）——**与主操作色分离是本家族反「teal everywhere」指纹的关键设计** |
| `--s-color-success(-strong)` | 绿 | **#4ADE80 / #86EFAC** | ANSI 绿，11.2:1 ✓ |
| `--s-color-warning(-strong)` | 琥珀 | **#FACC15 / #FDE047** | 12.8:1 ✓ |
| `--s-color-error(-strong)` | 红 | **#F87171 / #FCA5A5** | 7.1:1 ✓ |
| `--s-text-primary` | #111827 | **#D8DEE9** | |
| `--s-text-secondary` | #6B7280 | **#7C8698** | 5.3:1 ✓ |
| `--s-border` / `strong` | #E5E7EB/#D1D5DB | **#1E242E / #2A323F** | |
| `--g-radius-6/8/12` | 6/8/12px | **4/4/8px** | 硬边 |
| `--s-shadow-card` | e1 | **none** | 纯描边 |
| `--s-shadow-overlay` | e2 | **0 12px 40px rgba(0,0,0,0.7)** | |
| `--s-font-mono` **（新增槽位）** | 无 | **ui-monospace,"SF Mono","Cascadia Code",Consolas,monospace** | 系统栈，离线安全 |

## ③ 组件风格规则（family.css 承载项加 ◆）

- 按钮：主=亮灰实底黑字；次=透明底 1px 描边；◆hover 无位移只变色；硬边直角。
- 数据字体：◆表格数字列、单号、路径、代号、`c-stat__value` 一律 --s-font-mono（family.css 字体声明）；界面正文仍无衬线（可读性优先，mono 只进数据位）。
- 表格：1px 细横线、无斑马；表头 12px 次级灰。
- 侧栏导航：深底；◆选中 = 左侧 2px 磷光青指示条 + 青字（family.css ::before）。
- 链接与选中态：一律磷光青；focus 环 2px 磷光青。
- 状态徽标：tag 用描边式（彩字彩边透明底），不用实底——终端的克制。
- 动效：150ms、ease 直切感（禁 ease-in-out 的「软」）；光标闪烁只允许出现在演示性空状态，业务控件禁用。
- 图标：线性 1.5px 直角端点。

## ④ 适用 / 不适用场景

- 适用：开发者工具、DevOps/CLI/网关类产品、技术品牌演示、极客向内部工具。
- 不适用：面向非技术决策者的汇报（黑客风显得不正式）、政务/医疗/C 端消费、长文阅读密集型后台。

## ⑤ 身份特征与禁忌

- 身份特征：近黑底 + mono 数据字体 + 主操作与强调色分离（亮灰主钮 / 磷光青强调）+ 硬边三档（4/4/8）。
- 禁忌：①磷光青大面积使用（青只准出现在链接/选中/焦点/数据四处，出现第五处即指纹复发）；②圆角软化回 8px+；③彩色渐变任何形式；④闪烁/呼吸类动画进业务控件。
- 校验记录：#D8DEE9/#0A0C10 = 14.5:1；#0A0C10/#D8DEE9（主钮）= 14.5:1；#7C8698 = 5.3:1；#2DD4BF = 10.5:1；语义三色 7.1–12.8:1。
