# SPEC — <项目名>

> 状态机：draft → confirmed → frozen。本骨架预填「企业后台·蓝」风格包默认值，访谈后逐项覆盖。
> 铁律：本文档出现的每个值都要对应 `assets/tokens.css` 的变量；冲突以 tokens.css 为准回改本文档。

## §0 元信息

| 项 | 值 |
| --- | --- |
| 版本 | 0.1.0 |
| 状态 | draft |
| 冻结日期 | — |
| 来源 | 访谈记录 / 草图文件路径 |
| 继承基线 | 企业后台·蓝 v0.1 |

## §1 产品语境（Q0）

| 项 | 值 |
| --- | --- |
| 产品类型 | 后台管理系统 |
| 目标用户 | <填写> |
| 设备优先 | 桌面优先 |
| 气质关键词 | 简洁专业 |

## §2.0 美学家族

| 项 | 值 |
| --- | --- |
| 家族 id | F0（冷静企业·蓝，基准家族） |
| 家族版本 | v0.1 |
| 覆盖项清单 | 无（沿用家族默认值；自由变量覆盖在此逐项登记并重过 AA 校验，身份特征不得覆盖） |

## §2 色彩系统（G1/G2）

| 用途 | token |
| --- | --- |
| 主色（含 hover/active） | `--s-color-primary` / `-hover` / `-active` |
| 主色浅底 | `--s-color-primary-soft` / `-softer` |
| 语义色 | `--s-color-success` / `--s-color-warning` / `--s-color-error` / `--s-color-info` |
| 语义色 strong（浅底文字专用，对比度达标） | `--s-color-success-strong` / `--s-color-warning-strong` / `--s-color-error-strong` / `--s-color-info-strong` |
| 表面 | 页面 `--s-bg-page` · 卡片 `--s-bg-card` · hover `--s-bg-hover` · 遮罩 `--s-bg-overlay` |
| 文字 | 主 `--s-text-primary` · 次 `--s-text-secondary` · 禁用 `--s-text-disabled` · 反白 `--s-text-inverse` |
| 边框 | 常规 `--s-border` · 强调 `--s-border-strong` |

对比度实测：正文对页面底 ≥4.5:1（已验证：#111827 on #F5F7FA）；自定义色须补测并在此记录。

## §3 字体排版（G3）

字体栈 `--s-font-ui`；字重 400/500/600；行高正文 `--s-lh-body`、标题 `--s-lh-heading`。
字号档位：caption 12 / small 13 / body 14（正文本项目取值） / lead 16 / title 20 / headline 24 / display 30。

## §4 空间质感（G5）

间距刻度 `--s-space-1..8` = 4/8/12/16/20/24/32/48px；场景：页面间距 `--s-gap-page`、卡片间距 `--s-gap-card`、行内 `--s-gap-inline`。
圆角：小件 `--s-radius-small`(6) / 控件 `--s-radius-control`(8) / 卡片 `--s-radius-card`(12) / 胶囊 `--s-radius-full`。
阴影：卡片 `--s-shadow-card`(e1) / 浮层 `--s-shadow-overlay`(e2)；卡片「描边+轻阴影」。

## §5 组件规范（G4）

| 组件 | 约定 | 片段 |
| --- | --- | --- |
| 按钮 | 实底主钮 / 描边次钮 / 文字钮 / 危险钮；高 36（sm 28 / lg 44）；8px 圆角 | snippet-button |
| 输入 | 描边式，高 36，聚焦主色描边；错误态红描边 + hint | snippet-form-controls |
| 导航 | 白底侧栏 240px 可折叠 + 顶栏 56px；选中主色浅底 + 主色文字 | snippet-sidebar-nav |
| 反馈 | alert 四色系 / tag 状态色 / modal 遮罩 e2 | snippet-feedback / snippet-modal |
| 数据 | 表格行高 44 / 卡片 12 圆角 / KPI 指标卡 | snippet-data-table / snippet-card / snippet-stat |

## §6 布局骨架（G6）

侧边栏 `--c-sidebar-w`(240px) + 顶栏 `--c-header-h`(56px) + 内容区（padding `--s-gap-page`）。
栅格 12 列 gutter 16；断点 640/768/1024/1280。

## §7 交互保真度（G8）

等级：中高保真。做：页面跳转、hover 态、弹窗/抽屉/页签演示（app.js 声明式交互）。
不做：真实校验、业务逻辑、变量传值。假数据：真实感中文，禁 lorem。动效：150–300ms 过渡。

## §8 页面清单与流程（G7）

> 本表是 pages-manifest.json 的人读投影，两处同步；G3 以 json 为对账基准。
> **IA 规则**：台账进菜单（nav=true）；表单/详情为隐藏页（nav=false），由台账按钮触发。

| id | 路径 | 标题 | 类型 | 状态页 |
| --- | --- | --- | --- | --- |
| order-list | pages/order-list.html | 订单列表 - 订单管理 \| <项目名> | list | empty |
| order-detail | pages/order-detail.html | 订单详情 - 订单管理 \| <项目名> | detail | — |
| order-form | pages/order-form.html | 新建订单 - 订单管理 \| <项目名> | form | — |

站点地图树：订单管理（列表 → 详情 / 新建）。核心流程：新建订单 → 列表可见 → 查看详情。

## §9 生成契约

技术约定：纯静态单页 HTML；引用 `../assets/`（扁平 pages/ 目录）；语义化标签；c-/l-/u-/p- 类名；页面局部 style 仅 p- 类且 ≤30 行。
引用规则：颜色/字号/间距/圆角/阴影全部 `var(--s-*)` / `var(--c-*)`。
生成后自查：色值一致 / 字号未越阶 / 间距圆角在档 / 主钮每屏至多一个 / 链接无死链 / taste-checklist 判据逐条过一遍（含家族禁忌自查）。

## 附录 A — token 清单

权威源：`assets/tokens.css`（三层 --g-/--s-/--c- 全表见该文件注释）。

## 附录 C — 元素对账单（有参照截图时必填，用户逐项确认后冻结）

| 区域 | 参照物元素 | 形态描述 | 决策（沿用/简化/舍弃） | 理由 |
| --- | --- | --- | --- | --- |
| 顶栏 | 模块名+下拉 | 白字加粗 ∨ | （示例行） | |

## 附录 B — 访谈决策记录

| 题号 | 默认值 | 最终选择 | 来源 | 理由 |
| --- | --- | --- | --- | --- |
| Q0-1 | 后台管理系统 | （示例）后台管理系统 | preset | 示例行，访谈后逐题追加 |
| 家族登记 | F0 v0.1（冷静企业·蓝） | （示例）F0 v0.1，覆盖项清单：无 | preset | 所选美学家族；换家族或覆盖自由变量时更新此行，记录「家族 id + 版本 + 覆盖项清单」 |
