# F9 医疗青绿·清冷

> 家族 id：F9 · 版本：v0.1 · 上级：[美学家族库](../family-library.md)

```json family-manifest
{
  "id": "F9",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#F2F7F6",
    "--s-bg-card": "#FFFFFF",
    "--s-color-primary": "#0F766E",
    "--g-radius-12": "12px"
  },
  "structure": [
    ".c-data-table td, .c-data-table th { padding-top: var(--s-space-3); padding-bottom: var(--s-space-3); }",
    ".c-kpi { border-radius: var(--s-radius-card); }",
    ".c-card { border-radius: var(--s-radius-card); }"
  ]
}```

## ① 调性

洁净、低饱和、可信。带一点青的浅底 + 青绿主色，圆角适中，留白略大于常规后台——像诊所里的电子病历系统：安静、准确、不刺激。

## ② tokens 覆盖值表（diff vs F0）

| 槽位 | F0 | F9 | 备注 |
| --- | --- | --- | --- |
| `--g-bg-page` | #F5F7FA | **#F2F7F6** | 青灰底 |
| `--s-color-primary` | blue-600 | **#0F766E** | 青绿（白字 5.0:1 ✓）；hover #115E59、active #134E4A |
| `--s-color-primary-soft/softer` | blue-50/100 | **#E6F4F1 / #CCE9E4** | 青浅底 |
| `--s-text-primary` | #111827 | **#0F172A** | 冷墨 |
| `--s-text-secondary` | gray-600 | **#475569** | 冷灰 |
| `--s-color-success(-strong)` | 绿 | #15803D / #166534 | 与青绿区分 |
| `--s-color-warning(-strong)` | 琥珀 | #B45309 / **#92400E** | 暖底门槛 |
| `--s-border/strong` | #E5E7EB / #D1D5DB | **#D8E6E3 / #BFD5D1** | 青灰线 |
| `--g-radius-6/8/12` | 6/8/12px | **8/10/12px** | 柔和 |
| `--c-row-h` | 44 | **48** | 略松，降低视觉疲劳 |

## ③ 组件规则

- 表格：行高 48，行线极淡；数字等宽；状态用圆点+文字（青绿=正常、琥珀=关注、红=异常）。
- 按钮：主=青绿实底；次=白底青灰描边；焦点环 3px 青浅底。
- 卡片：白底 + 1px 青灰线 + 极轻阴影；卡片内边距 20。
- 图表：单色青绿序列 + 中性灰对照，不出现高饱和平行色。
- 图标：圆端点线框 1.5px；医疗相关图标可用实心但只用于状态。

## ④ 场景边界

- 适用：医疗/健康管理、检验检查、康养、教育健康档案、需要长时间注视的后台。
- 不适用：营销活动、游戏化、需要强对比提醒的告警大屏（青绿不够刺眼）。

## ⑤ 身份特征与禁忌

- 特征：青灰底 + 中等圆角（8/10/12）+ 青绿主色 + 行高 48。
- 禁忌：①高饱和红蓝对冲；②纯黑文字；③密集压缩行高；④装饰性渐变；⑤状态只用颜色不配文字。
- 校验：白字/#0F766E 5.0:1；#0F172A/#F2F7F6 15.1:1；#475569/#F2F7F6 7.2:1。
