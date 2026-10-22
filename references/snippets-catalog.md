# 组件片段目录（snippets 白名单）

> 上级入口：SKILL.md 步骤 4。片段位于项目 `assets/snippets/`，HTML 结构与 CSS 分离：结构在片段文件，样式集中在 `assets/components.css`。
> 使用方式见 tokens-reference.md 的「片段复制纪律」。

## 目录

| 片段文件 | 根类名 | 变体 / 关键子元素 | 可改范围 |
| --- | --- | --- | --- |
| snippet-button.html | `c-btn` | `--secondary` 描边 · `--text` 文字 · `--danger` 危险 · `--sm`/`--lg` 尺寸 · `--disabled` | 只改文案与 `disabled` 态 |
| snippet-form-controls.html | `c-field` | `c-input` / `c-select` / `c-textarea` / `c-check` / `c-radio` / `c-switch`；`c-field__hint`、`--error` 态 | 只改 label、placeholder、hint 文案；增删整个 `c-field` |
| snippet-data-table.html | `c-table` | `c-table__th` 可排序标记 · 行内 `c-tag` 状态 · 行操作 `c-btn--text` | 只改列头、单元格内容；增删 `tbody` 行 |
| snippet-card.html | `c-card` | `c-card__header/__body/__footer` | 改标题与内容；增删卡片 |
| snippet-stat.html | `c-stat` | `c-stat__label/__value/__delta`；`--up`/`--down` | 改数值文案；增删指标卡 |
| snippet-desc-list.html | `c-desc` | `c-desc__item`（label + value） | 改字段名与值；增删条目 |
| snippet-page-nav.html | `c-breadcrumb` + `c-pagination` | 面包屑项、页码/上下页 | 改文案与链接；页码数量 |
| snippet-sidebar-nav.html | `c-nav` | `c-nav__group` 分组 · `c-nav__item` · `--active` | 改菜单文案与链接；增删菜单项 |
| snippet-filter-bar.html | `c-filterbar` | 搜索 `c-input` + 下拉 `c-select` + 重置/查询按钮 | 改筛选项；增删控件 |
| snippet-feedback.html | `c-alert` + `c-tag` | alert `--success/--warning/--error/--info`；tag 同色系 | 改文案；增删 |
| snippet-modal.html | `c-modal` | `c-modal__dialog/__header/__body/__footer`；`data-action="open-modal"` 触发 | 改标题、正文、按钮文案 |
| snippet-tabs.html | `c-tabs` | `c-tabs__tab` + `c-tabs__panel`；`data-action="switch-tab"` | 改页签名与面板内容 |
| snippet-empty.html | `c-empty` | 图形区 + `c-empty__title/__desc` + 动作按钮 | 改文案与动作 |

## 拼装规则

1. 片段文件头部有 HTML 注释：用途、变体清单、必选/可选子元素、可改范围——复制前先读注释。
2. 复制后**只改**：文字内容、真实链接 `href`、增删重复单元；**禁改** class 结构与命名、禁加内联样式。
3. 页面需要片段库没有的组件：先组合现有片段；确实没有 → 新建 `snippet-<名>.html` 入库并在本目录登记，样式写进 components.css 对应分节，然后才能在页面使用。
4. components.css 按注释分节（按钮/表单/表格/卡片/导航/反馈/浮层），新组件样式写进对应分节，只用 tokens 变量。
