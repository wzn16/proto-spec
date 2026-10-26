# F8 政务蓝灰·庄重

> 家族 id：F8 · 版本：v0.1 · 上级：[美学家族库](../family-library.md)

```json family-manifest
{
  "id": "F8",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#F4F6F8",
    "--s-bg-card": "#FFFFFF",
    "--s-color-primary": "#1B4B8F",
    "--g-radius-12": "8px"
  },
  "structure": [
    ".c-card { box-shadow: none; border-radius: var(--s-radius-small); }",
    ".c-workbench__head h1 { border-left: var(--s-space-1) solid var(--s-color-primary); padding-left: var(--s-space-2); }"
  ]
}```

## ① 调性

端庄、克制、可归档。冷灰纸面 + 公文深蓝，方正小圆角，细线分栏——像一份装订规范的政务报告，不像互联网产品。打开任何一页：信息密集但秩序明确，蓝只出现在标题栏与主操作。

## ② tokens 覆盖值表（diff vs F0）

| 槽位 | F0 | F8 | 备注 |
| --- | --- | --- | --- |
| `--g-bg-page` | #F5F7FA | **#F4F6F8** | 冷灰 |
| `--s-color-primary` | blue-600 | **#1B4B8F** | 公文蓝（白字 7.4:1 ✓）；hover #163D75、active #12325F |
| `--s-color-primary-soft/softer` | blue-50/100 | **#E8EEF6 / #D6E2F0** | 蓝浅底 |
| `--s-text-primary` | #111827 | **#1F2937** | 墨蓝灰 |
| `--s-text-secondary` | gray-600 | **#4B5563** | 同 v0.2 基准 |
| `--s-border/strong` | #E5E7EB / #D1D5DB | **#DCE3EA / #C6D0DA** | 冷灰线 |
| `--g-radius-6/8/12` | 6/8/12px | **2/4/6px** | 方正 |
| `--s-shadow-card` | e1 | **none** | 用线分层 |

## ③ 组件规则

- 表格：横线分隔 + 表头浅灰底；数字等宽右对齐；无斑马纹。
- 按钮：主=公文蓝实底；次=白底灰蓝描边；圆角 4。
- 卡片：白底 + 1px 冷灰线，不投影；标题左侧加 2px 深蓝竖条作为**唯一**装饰。
- 顶栏/侧栏：深蓝 #12325F 底 + 白字。
- 图标：直角端点线框，1.5px。

## ④ 场景边界

- 适用：政务/国企/事业单位后台、监管报送、审计归档、面向甲方的正式系统。
- 不适用：C 端产品、创意工具、需要活泼感的运营后台。

## ⑤ 身份特征与禁忌

- 特征：冷灰底 + 方正小圆角（2/4/6）+ 公文深蓝 + 细线分层 + 无投影。
- 禁忌：①大圆角（>8px）；②彩色渐变；③高饱合强调色；④投影堆叠；⑤圆润图标。
- 校验：白字/#1B4B8F 7.4:1；#1F2937/#F4F6F8 14.2:1；#4B5563/#F4F6F8 6.8:1。
