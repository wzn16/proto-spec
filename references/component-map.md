# 组件映射（Component Map）

> 由 `scripts/` 从 `components.css` 解析生成，人工补充用途与对应框架组件。改动组件时请同步本表。

共 56 个基础类。变体用 `--x` 表示，状态用 `is-*` 表示，子元素用 `__x` 表示。

| 基础类 | 用途 | 变体 | 运行时状态 | 关键子元素 | 对应 Element Plus / AntD |
| --- | --- | --- | --- | --- | --- |
| `c-alert` | 提示条 | error/info/success/warning | — | — | ElAlert / Alert |
| `c-breadcrumb` | 面包屑 | — | — | — | ElBreadcrumb / Breadcrumb |
| `c-btn` | 按钮 | danger/disabled/lg/secondary/sm/text | — | — | ElButton / Button |
| `c-bulkbar` | 批量操作条 | — | — | — | 自定义 |
| `c-card` | 卡片 | flush | — | — | ElCard / Card |
| `c-check` | 内部结构类 | — | — | — | — |
| `c-chip` | 内部结构类 | — | — | — | — |
| `c-chips` | 条件 chips | — | — | — | ElTag closable / Tag |
| `c-col-ck` | 内部结构类 | — | — | — | — |
| `c-col-code` | 内部结构类 | long | — | — | — |
| `c-col-idx` | 内部结构类 | — | — | — | — |
| `c-col-name` | 内部结构类 | — | — | — | — |
| `c-col-num` | 内部结构类 | — | — | — | — |
| `c-col-ops` | 内部结构类 | — | — | — | — |
| `c-data-table` | 台账数据表（冻结/密度/分组） | comfort/dense/pin-first/zebra | — | — | ElTable / Table |
| `c-desc` | 描述列表 | — | — | — | ElDescriptions / Descriptions |
| `c-detail` | 详情面板 | — | — | — | ElDescriptions 组合 / Descriptions |
| `c-drawer` | 抽屉（默认浮动） | float/md/sm | — | — | ElDrawer / Drawer |
| `c-dropdown` | 下拉菜单 | — | — | — | ElDropdown / Dropdown |
| `c-empty` | 空状态 | compact/inline | — | — | ElEmpty / Empty |
| `c-field` | 表单字段容器（label+控件+hint） | error/full/readonly/required | is-error | — | ElFormItem / Form.Item |
| `c-filter-drawer` | 筛选抽屉 | — | — | — | Drawer 内表单 |
| `c-filterbar` | 内部结构类 | — | — | — | — |
| `c-form-footer` | 表单粘底操作条 | — | — | — | 自定义 |
| `c-form-grid` | 表单栅格 | 1/3/label-left | — | — | ElRow+ElCol / Row+Col |
| `c-form-section` | 表单分组 | — | — | — | ElCard 分组 / Divider+Form |
| `c-input` | 单行输入 | — | is-error | — | ElInput / Input |
| `c-kpi` | 指标卡 | — | — | — | ElStatistic / Statistic |
| `c-kpi-row` | 指标卡行 | 2/3/6 | — | — | ElRow+Statistic / Row+Statistic |
| `c-kv` | 键值列表 | — | — | — | ElDescriptions 简化 / Descriptions |
| `c-list-grid` | 内部结构类 | — | — | — | — |
| `c-list-row` | 内部结构类 | — | — | — | — |
| `c-list-rows` | 列表行流（看板卡片） | — | — | — | 自定义 |
| `c-modal` | 弹窗 | — | — | — | ElDialog / Modal |
| `c-nav` | 侧栏导航 | — | — | — | ElMenu / Menu |
| `c-pager` | 简化分页条 | — | — | — | 自定义 |
| `c-pagination` | 分页 | — | — | — | ElPagination / Pagination |
| `c-qbar` | 查询条（下划线式） | — | — | — | ElForm inline / Form |
| `c-radio` | 单选 | — | — | — | ElRadio / Radio |
| `c-segmented` | 分段器 | — | is-on | — | ElSegmented / Segmented |
| `c-select` | 下拉选择 | — | is-error | — | ElSelect / Select |
| `c-side-menu` | 工作台侧栏菜单 | — | is-active | — | Menu / Menu |
| `c-skeleton` | 骨架屏 | — | — | — | ElSkeleton / Skeleton |
| `c-split` | 主从两栏布局 | full/tree | — | — | Layout Sider / Layout |
| `c-stat` | 内部结构类 | down/up | — | — | — |
| `c-switch` | 开关 | — | — | — | ElSwitch / Switch |
| `c-tabbar` | 工作台页签条 | — | is-on | — | 自定义 |
| `c-table` | 只读快照表 | dense/loose/sticky | is-error/is-selected | — | ElTable / Table |
| `c-tabs` | 页签 | — | — | — | ElTabs / Tabs |
| `c-tag` | 标签/徽标 | dot/error/info/success/warning | — | — | ElTag / Tag |
| `c-textarea` | 多行文本 | — | is-error | — | ElInput type=textarea / Input.TextArea |
| `c-timeline` | 时间线 | — | — | — | ElTimeline / Timeline |
| `c-toast` | 轻提示 | — | — | — | ElMessage / message |
| `c-toolbar` | 工具栏 | — | — | — | 自定义 |
| `c-tree` | 层级树 | — | is-active | — | ElTree / Tree |
| `c-workbench` | 工作台外壳（侧栏+主区） | — | — | — | Layout / Layout |

## 使用纪律

1. 变体只通过 `--x` 修饰，运行时状态只通过 `is-*`；不要用行内 style 覆盖。
2. 子元素结构（`__x`）由组件决定，页面不得自造同义子元素。
3. 本表未收录的类视为内部结构类，页面不得直接使用。
