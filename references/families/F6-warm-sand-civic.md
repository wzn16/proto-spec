# F6 暖砂政务·青绿

> 家族 id：F6 · 版本：v0.1（草案建档） · 上级：[美学家族库](../family-library.md)

```json family-manifest
{
  "id": "F6",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#F7F6F2",
    "--s-bg-card": "#FFFFFF",
    "--s-color-primary": "#0F766E"
  },
  "structure": [
    ".c-workbench__head h1, .l-page-head h1 { font-family: \"Songti SC\", \"Noto Serif SC\", serif; }",
    ".c-card { border-radius: var(--s-radius-card); }",
    ".c-workbench__head { background: var(--s-color-primary-soft); border-radius: var(--s-radius-card); padding: var(--s-space-4); }",
    ".c-data-table th { background: var(--s-bg-hover); }"
  ]
}```

## ① 调性

稳重、可信、有温度。暖砂色纸面 + 青绿主色，圆角适中，线条克制——像一份装帧规范的政务白皮书，专业但不冷漠。打开任何一页：信息密集但呼吸均匀，青绿只用于动作与选中。

## ② tokens 覆盖值表（diff vs F0）

| 槽位 | F0 | F6 | 备注 |
| --- | --- | --- | --- |
| `--g-bg-page` / `--s-bg-page` | #F5F7FA | **#F7F6F2** | 暖砂 |
| `--s-bg-card` | #FFFFFF | #FFFFFF | 白卡 |
| `--g-radius-6/8/12` | 6/8/12px | **6/8/12px** | 不变（克制） |
| `--s-color-primary` | blue-600 | **#0F766E** | 青绿（白字 5.0:1 ✓）；hover #115E59、active #134E4A |
| `--s-color-primary-soft/softer` | blue-50/100 | **#E6F4F1 / #CCE9E4** | 青绿浅底 |
| `--s-color-success(-strong)` | 绿 | #15803D / #166534 | 略深以与青绿区分 |
| `--s-color-warning(-strong)` | 琥珀 | #B45309 / **#92400E** | strong 加深过暖底 |
| `--s-color-error(-strong)` | 红 | #B91C1C / #991B1B | 略深 |
| `--s-text-primary` | #111827 | **#1F2937** | 沉稳深灰蓝 |
| `--s-text-secondary` | gray-600 | #4B5563 | 同 F0 v0.2 |
| `--s-border/strong` | #E5E7EB / #D1D5DB | **#E7E4DC / #D4D0C6** | 暖砂线 |
| `--s-bg-hover` | gray-100 | **#F1EFE9** | 暖砂 hover |
| `--s-shadow-card` | e1 | 不变（e1 轻阴影） | 克制 |

## ③ 组件风格规则

- 按钮：主=青绿实底白字；次=白底砂描边；无额外位移。
- 卡片：白卡 + 1px 砂线 + 轻阴影（边框与阴影并用，政务系统辨识度）。
- 表格：横线分隔 + hover 砂底；表头 12px 次级灰 + 常规字重；数字等宽。
- 侧栏/顶栏：白底；选中 = 青绿 soft 底 + 青绿文字。
- 图标：线性 1.5px 直角端点（稳重）。
- 动效：150–200ms 干脆。

## ④ 场景边界

- 适用：政务/国企后台、医疗行政、教育管理、面向监管方的汇报系统。
- 不适用：C 端消费、创意作品集、开发者工具、数据大屏（青绿不足以承载多系列分类色）。

## ⑤ 身份特征与禁忌

- 身份特征：暖砂页底 + 白卡砂线 + 青绿主色。
- 禁忌：①高饱和跳色（政务场景克制）；②直角或超圆角（6/8/12 之外）；③可点击元素无 hover 反馈；④纯黑 #000 文字。
- 校验记录：白字/#0F766E ≈ 5.0:1；#1F2937/#F7F6F2 ≈ 14.5:1；#4B5563/#F7F6F2 ≈ 7.0:1。
