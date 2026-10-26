# F7 玻璃暗夜·霜

> 家族 id：F7 · 版本：v0.1（草案建档） · 上级：[美学家族库](../family-library.md)

```json family-manifest
{
  "id": "F7",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#0B0D12",
    "--s-bg-card": "#11131A",
    "--s-color-primary": "#A5B4FC",
    "--s-color-accent": "#38BDF8",
    "--g-radius-12": "20px",
    "--s-text-primary": "#E6E8F0",
    "--s-text-secondary": "#A3A9C2",
    "--s-border": "#232838",
    "--s-bg-sidebar": "#08090D",
    "--s-on-dark-text": "#E6E8F0",
    "--s-text-inverse": "#0B0D12",
    "--s-color-error-strong": "#FCA5A5",
    "--s-color-success-strong": "#86EFAC",
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
    "--s-glass-bg": "rgba(255, 255, 255, .06)",
    "--s-glass-line": "rgba(255, 255, 255, .12)",
    "--s-brand-text": "#E5E7EB",
    "--s-segmented-text": "#C7CBD3",
    "--s-bg-hover": "#1A1F2B",
    "--s-segmented-bg": "#1A1F2B",
    "--c-sidebar-w": "256px",
    "--c-content-max": "1140px"
  },
  "structure": [
    ".c-card { background: var(--s-glass-bg); backdrop-filter: blur(14px); border-color: var(--s-glass-line); }",
    ".c-workbench__side { backdrop-filter: blur(18px); }",
    ".c-workbench__head h1 { letter-spacing: .02em; }",
    ".c-data-table th { background: var(--s-glass-bg); }",
    ".c-workbench__content { max-width: var(--c-content-max); margin-inline: auto; width: 100%; }"
  ]
}```

## ① 调性

深夜磨砂，半透明层叠，柔光描边——像隔着一层霜玻璃看数据。底色是深石板，浮层是磨砂玻璃，光只在边缘和主动作上出现。打开任何一页：安静、有厚度、带一点未来的雾气。

## ② tokens 覆盖值表（diff vs F0）

| 槽位 | F0 | F7 | 备注 |
| --- | --- | --- | --- |
| `--g-bg-page` / `--s-bg-page` | #F5F7FA | **#0B0D12** | 深石板 |
| `--s-bg-card` | #FFFFFF | **#11131A** | 实底表面（保证对比度可计算） |
| `--s-bg-hover` | gray-100 | **#171A24** | |
| `--g-radius-6/8/12` | 6/8/12px | **12/16/20px** | 柔和圆角 |
| `--s-color-primary` | blue-600 | **#A5B4FC** | 淡靛（深底字 11.6:1 ✓）；hover #C7D2FE、active #818CF8 |
| `--s-color-primary-soft/softer` | blue-50/100 | **#1A1F33 / #232A45** | 深底靛 |
| `--s-color-accent` **（新增槽位）** | 无 | **#38BDF8** | 霜蓝：链接/选中/焦点环 |
| `--s-color-success(-strong)` | 绿 | #34D399 / #6EE7B7 | 暗底提亮 |
| `--s-color-warning(-strong)` | 琥珀 | #FBBF24 / #FDE68A | |
| `--s-color-error(-strong)` | 红 | #F87171 / #FCA5A5 | |
| `--s-text-primary` | #111827 | **#E4E7EE** | 14.9:1 ✓ |
| `--s-text-secondary` | gray-600 | **#98A2B8** | 6.8:1 ✓ |
| `--s-text-disabled` | gray-400 | #5A6478 | |
| `--s-text-inverse` | #FFF | **#0B0D12** | |
| `--s-border/strong` | #E5E7EB / #D1D5DB | **rgba(255,255,255,0.10) / rgba(255,255,255,0.18)** | 柔光描边 |
| `--s-shadow-card` | e1 | **none** | 表面靠提亮与描边分层 |
| `--s-shadow-overlay` | e2 | **0 12px 40px rgba(0,0,0,0.5)** | |
| `--s-surface-frost` **（新增槽位）** | 无 | **rgba(17, 19, 26, 0.72)** | 磨砂浮层底（family.css 消费） |

## ③ 组件风格规则

- 顶栏 / 侧栏 / 抽屉 / 弹窗：`backdrop-filter: blur(16px)` + `--s-surface-frost` 底色（family.css 承载）。
- 按钮：主=淡靛实底深字；次=透明底柔光描边；hover 变亮不位移。
- 卡片：实底 #11131A + 柔光描边，无阴影。
- 表格：行 hover #171A24；表头 12px 次级灰；数字等宽。
- 链接与选中：霜蓝 `--s-color-accent`；focus 环 2px 霜蓝。
- 动效：200–280ms，柔缓 ease-out。


- 状态标签：深底上用「低透明同色底 + 亮同色字」（如 success：底 `rgba(74,222,128,.14)`、字 `#86EFAC`），不要用亮底白字。
- 导航激活项：用 `--s-on-dark-active` 底 + 主色字，或主色 8% 透明底；不要用亮色实底配浅字。

## ④ 场景边界

- 适用：数据产品、AI/云服务控制台、科技品牌演示、需要「未来感但不刺眼」的评审场景。
- 不适用：**打印交付**（磨砂与深底打印全黑，硬伤，访谈时须明示代价）；政务/医疗正式汇报；长表单录入后台（暗底疲劳）。
- 已知风险：`backdrop-filter` 在部分截图引擎与旧版浏览器降级为纯色（不破版、仅失去磨砂感）——家族可作为渐进增强使用。

## ⑤ 身份特征与禁忌

- 身份特征：深石板底 + 实底卡片 + 磨砂浮层 + 淡靛主色 + 霜蓝强调 + 大圆角（12/16/20）。
- 禁忌：①大面积纯白/浅灰表面（破坏暗色阶层）；②hover 加深（暗底必须变亮）；③高饱和彩虹色装饰；④把磨砂用在正文卡片上（只许浮层：顶栏/侧栏/抽屉/弹窗）。
- 校验记录：白字/#A5B4FC 反白（深字 #0B0D12 on #A5B4FC ≈ 11.6:1 ✓）；#E4E7EE/#11131A ≈ 14.9:1；#98A2B8/#11131A ≈ 6.8:1；#38BDF8 on #11131A ≈ 8.2:1。
