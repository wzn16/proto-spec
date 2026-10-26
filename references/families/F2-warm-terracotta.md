# F2 暖陶人文·赤
```json family-manifest
{
  "id": "F2",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#F7F5F0",
    "--s-bg-card": "#FFFDF9",
    "--s-color-primary": "#B05330",
    "--s-text-primary": "#2D2A26",
    "--g-radius-8": "10px",
    "--g-radius-12": "14px",
    "--c-sidebar-w": "240px",
    "--c-content-max": "1120px"
  },
  "structure": [
    ".c-workbench__head h1, .l-page-head h1 { font-family: \"Songti SC\", \"Noto Serif SC\", serif; letter-spacing: 0; }",
    ".c-card { border-radius: var(--s-radius-card); }",
    ".c-workbench__head { background: var(--s-color-primary-soft); border-radius: var(--s-radius-card); padding: var(--s-space-4); }",
    ".c-data-table th { background: var(--s-color-primary-soft); }",
    ".c-kpi { border-radius: var(--s-radius-card); }",
    ".c-workbench__content { max-width: var(--c-content-max); margin-inline: auto; width: 100%; }"
  ]
}```


> 家族 id：F2 · 版本：v0.1（草案建档） · 上级：[美学家族库](../family-library.md)

## ① 调性

温暖亲和、人文气。暖米色的纸面、赤陶色的点缀、圆一点的角落——像精装人文书而非仪表盘。打开任何一页：光线是暖的，边角是圆的，错误提示都像在商量而不是训斥。

## ② tokens 覆盖值表（diff vs F0）

| 槽位 | F0 | F2 | 备注 |
| --- | --- | --- | --- |
| `--g-bg-page` / `--s-bg-page` | #F5F7FA | **#F7F5F0** | 暖米白 |
| `--s-bg-card` | #FFFFFF | **#FFFDF9** | 暖白卡底（比页底亮一档，靠色温差分层） |
| `--s-color-primary` | blue-600 | **#B05330** | 赤陶（白字 5.09:1 ✓）；hover #9C4628、active #873C22 |
| `--s-color-primary-soft` / `softer` | blue-50/100 | **#F6E8E1 / #EFD9CE** | |
| `--s-color-success` / `strong` | #16A34A / #15803D | **#3F7E44 / #35693A** | 暖调绿（strong 校验 ≥4.5 于 soft 底待入库脚本全量验） |
| `--s-color-warning` / `strong` | #D97706 / **#92400E** | strong 实测修订（v0.1 原值 #B45309 于暖灰底仅 4.19:1） |
| `--s-color-error` / `strong` | #DC2626 / #B91C1C | **#B3372B / #962D23** | 暖调红，攻击性降低 |
| `--s-text-primary` | #111827 | **#2D2A26** | 暖黑 |
| `--s-text-secondary` | #6B7280 | **#6F6963** | 暖灰（校验 4.97:1 ✓；原拟 #78716C 仅 4.40 已否决） |
| `--s-text-disabled` | #9CA3AF | #A8A29E | stone 系 |
| `--s-border` / `strong` | #E5E7EB / #D1D5DB | **#E7E2DA / #D6CFC4** | 暖调线 |
| `--g-radius-6/8/12` | 6/8/12px | **8/10/14px** | 更圆 |
| `--g-shadow-e1/e2` | 冷黑阴影 | **rgba(45,42,38,0.06) / rgba(45,42,38,0.10)** | 暖色调阴影 |
| `--s-bg-hover` | gray-100 | **#EFEAE2** | 暖灰 hover |

## ③ 组件风格规则（family.css 承载项加 ◆）

- 按钮：主=赤陶实底白字；次=暖白底暖描边；◆主按钮与胶囊形（`--s-radius-full`）在本家族默认启用（Q4-1 联动值：12px 或胶囊）。
- 卡片：暖白卡底 + 暖阴影；◆允许 `c-empty` 图形区使用有机形状装饰（圆角不规则 blob，单一暖色 8% 透明度）——本家族唯一合法的装饰位。
- 表格：行 hover 暖灰 #EFEAE2；表头字重 500、无字距处理；分隔线用 --s-border 暖线。
- 侧栏导航：暖白底；选中 = 赤陶 soft 底 + #873C22 文字。
- 标题排版：标题字重可用 600 + 行高 1.25；展示场景标题可选系统衬线（同 F1 衬线栈），本家族衬线出场率高于 F1。
- 图标：线性 1.5px，端点圆帽（stroke-linecap:round——family.css 可达）。
- 动效：200–300ms，柔和 ease-out，「被邀请」的手感。

## ④ 适用 / 不适用场景

- 适用：内部协作/文档/知识工具、HR·行政·后勤系统、教育社区产品、面向非技术用户的后台。
- 不适用：金融交易/风控（暖调削弱严肃与精确感）、数据大屏、开发者工具、强合规汇报。

## ⑤ 身份特征与禁忌

- 身份特征：暖米页底 + 色温差分层（暖白卡，不靠阴影硬拉）+ 赤陶主色 + 暖调语义色。
- 禁忌：①冷灰/冷蓝任何角色出场（#111827、gray 系全部禁用——暖黑 #2D2A26 顶替）；②玻璃拟态与彩色大阴影；③满屏插画贴纸（装饰只许空状态有机形状一处）；④纯黑 #000 文字。
- 校验记录：白字/#B05330 = 5.09:1；#92400E/#EFEAE2 ≈ 5.1:1（warning-strong 实测修订后）；#2D2A26/#F7F5F0 = 13.1:1；#6F6963/#F7F5F0 = 4.97:1；#2D2A26/#FFFDF9 = 14.05:1。
