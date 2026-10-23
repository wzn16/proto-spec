# F5 清新活力·彩

> 家族 id：F5 · 版本：v0.1（草案建档） · 上级：[美学家族库](../family-library.md)

```json family-manifest
{
  "id": "F5",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#FFFBF5",
    "--s-bg-card": "#FFFFFF",
    "--s-color-primary": "#C2410C",
    "--g-radius-8": "16px",
    "--g-radius-12": "20px"
  }
}
```

## ① 调性

明亮、轻快、有笑意。大面积留白配一处大胆的深橙，圆角大而软，图标圆端点——像一本配色明快的产品手册，不像后台系统。打开任何一页：留白让人放松，橙只在主动作和关键数据上出现。

## ② tokens 覆盖值表（diff vs F0）

| 槽位 | F0 | F5 | 备注 |
| --- | --- | --- | --- |
| `--g-bg-page` / `--s-bg-page` | #F5F7FA | **#FFFBF5** | 暖白米 |
| `--s-bg-card` | #FFFFFF | #FFFFFF | 白卡（同 F0） |
| `--g-radius-6/8/12` | 6/8/12px | **10/16/20px** | 大圆角 |
| `--s-color-primary` | blue-600 | **#C2410C** | 深橙（白字 4.9:1 ✓）；hover #9A3412、active #7C2D12 |
| `--s-color-primary-soft/softer` | blue-50/100 | **#FFEDD5 / #FED7AA** | 橙浅底 |
| `--s-color-success(-strong)` | 绿 | #16A34A / #15803D | 不变 |
| `--s-color-warning(-strong)` | 琥珀 | #B45309 / **#92400E** | strong 加深以过暖底门槛 |
| `--s-text-primary` | #111827 | #111827 | 不变 |
| `--s-text-secondary` | gray-600 | #4B5563 | 同 F0 v0.2 |
| `--s-border/strong` | #E5E7EB / #D1D5DB | **#F0E6DA / #E3D4C4** | 暖调细线 |
| `--s-bg-hover` | gray-100 | **#FDF2E9** | 暖橙 hover |
| `--s-shadow-card` | e1 | **0 2px 8px rgba(194, 65, 12, 0.06)** | 略带暖色的软阴影 |

## ③ 组件风格规则

- 按钮：主=深橙实底白字、圆角大（12px 或胶囊）；次=白底暖描边；hover 轻微上浮 1px。
- 卡片：白底 + 大圆角 + 暖软阴影；卡片内边距比 F0 宽一档（20px）。
- 表格：行 hover 暖橙浅底；表头 12px 次级灰；数字等宽。
- 侧栏/顶栏：白底；选中 = 橙 soft 底 + 深橙文字。
- 图标：线性 1.5px 圆端点（stroke-linecap: round）。
- 动效：200–300ms 柔和 ease-out。

## ④ 场景边界

- 适用：C 端消费产品、教育/社区、活动运营后台、面向非技术用户的工具。
- 不适用：金融风控（活力削弱严肃）、数据大屏、强合规汇报、开发者工具。

## ⑤ 身份特征与禁忌

- 身份特征：暖白页底 + 大圆角（10/16/20）+ 深橙主色 + 暖软阴影。
- 禁忌：①冷蓝角色出场（主色系必须暖）；②直角感圆角（<8px）；③满屏彩色贴纸/插画（装饰只许空状态一处）；④灰黑生硬阴影。
- 校验记录：白字/#C2410C ≈ 4.9:1；#111827/#FFFBF5 ≈ 16.9:1；#4B5563/#FFFBF5 ≈ 7.0:1；#4B5563/#FFFFFF ≈ 7.2:1。
