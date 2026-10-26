# 字体、构图与动效编排（吸收自 Anthropic frontend-design，按 B 端适配）

> 读时机：步骤 2（定家族/字体）与步骤 4（写页面）。这里治的是「千人一面」。

## 一、反滥用字体清单

以下字体是**默认值，不是选择**。用它们必须在 SPEC 写理由（例如"客户品牌就是系统字体"）：

- Inter / Roboto / Arial / Helvetica / 系统栈（-apple-system, PingFang, Microsoft YaHei）/ Space Grotesk。

**替代方向**（按气质）：
| 气质 | 展示层（标题/数字） | 正文层 |
| --- | --- | --- |
| 编辑/刊物 | Noto Serif SC / Source Han Serif / Newsreader | Noto Sans SC / IBM Plex Sans |
| 精密工业 | IBM Plex Sans / Roboto Condensed（仅标题） | IBM Plex Sans / Noto Sans SC |
| 亲和消费 | 圆体（ZCOOL KuaiLe 类，仅标题）/ Nunito | Nunito Sans / Noto Sans SC |
| 政务庄重 | Source Han Serif（标题）/ 思源黑体 Medium | 思源黑体 Regular |
| 终端机能 | JetBrains Mono / IBM Plex Mono（标题与数字） | Inter→改 IBM Plex Sans |

规则：**展示层与正文层必须分开选**，且至少有一项差异（字重差 ≥2 档 / 字族不同 / 字距不同）。

## 二、B 端也能有辨识度：三条硬做法

1. **字重差 ≥2 档**：标题 600–700，正文 400，辅助 400 但降色阶；不要全站 500。
2. **字距分级**：display/大标题 `letter-spacing: -0.01em`；表头与全大写标签 `+0.02em`；正文 0。
3. **数字排版独立成规则**：大数字用 `tabular-nums` 或等宽；单位小一号且次级色；金额右对齐；千分位全站统一（1,786 不是 1786）；百分比保留 1 位小数。

## 三、构图：三种非常规但 B 端可用的做法

| 做法 | 怎么用 | 反例 |
| --- | --- | --- |
| 主指标跨栏 | 4 栏 KPI 里，主指标占 2 栏（其余各 1 栏） | 四张等宽卡，重要性与版面无关 |
| 主从不对称 | 侧树 280/300 + 内容 `minmax(0,1fr)`；不要 50/50 | 左右各半，主内容被挤 |
| 内容跨边界 | 表格区横向顶到卡片内边距之外；分组标题骑在分隔线上 | 所有内容都缩在卡片 padding 里，层层内缩 |

禁忌：左侧彩色粗边条、渐变文字、Emoji 当图标、四张等宽卡 + 满屏彩色胶囊。

## 四、动效：编排优于零散

- **一次编排好的入场**：页面加载时 2–3 段，staggered 60–80ms，总时长 ≤600ms；列表项按行错峰（每行 20–30ms）。
- **状态切换只动变化的那一块**：抽屉从触发按钮方向展开；行删除向下收拢；不要整页淡入。
- **微交互**：按钮 hover 改底色不改位移；focus 环 2px 主色 + 2px 偏移。
- `prefers-reduced-motion: reduce` 时全部降到 0.01ms，不做例外。
