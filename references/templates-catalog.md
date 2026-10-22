# 模板、目录与链接约定

> 上级入口：SKILL.md 步骤 4。模板位于项目 `templates/`，是填了示例数据的可运行页面；生成正式页 = 复制模板到 `pages/` 改名 → 替换插槽内容。

## 模板清单

| 模板 | 结构 | 用途 |
| --- | --- | --- |
| index.html | 站点地图首页（无壳）：项目说明卡 → 按任务流分组的页面卡组 → 变更记录 | 原型导览与演示入口 |
| tpl-list.html | 壳（侧栏+顶栏）+ 页头 + `c-filterbar` + 工具栏 + `c-table` + `c-pagination` | 业务对象列表 |
| tpl-detail.html | 壳 + 页头（标题+动作区）+ `c-desc` 描述列表 + 关联 `c-card`/`c-tabs` | 对象详情 |
| tpl-form.html | 壳 + 页头 + 分组表单（`c-field` × n）+ 底部操作栏 | 新建/编辑 |

路线图（后续版本）：tpl-modal-form（弹窗表单变体）、tpl-dashboard（指标卡行+图表卡）、tpl-login、tpl-steps（向导）、tpl-result、m-shell/m-list/m-detail/m-form（移动端）。

## 插槽约定

每个模板头部 HTML 注释写三件事：

1. 区域 ASCII 图，标出 `SLOT-1/SLOT-2/…` 位置；
2. 插槽清单：每个插槽填什么数据、可用片段类名；
3. 假数据要求：真实感中文（姓名/单号/金额用真实格式），禁 lorem。

插槽本身用注释对标记：`<!-- SLOT-2: 表格列定义（片段 snippet-data-table） -->`，替换内容时整对删除。

## 项目目录结构（复制 starter 后）

```
项目/
├── SPEC.md                  # 冻结规范
├── pages-manifest.json      # 页面清单（G3 对账基准，与 SPEC §8 同步）
├── index.html               # 站点地图
├── assets/                  # tokens.css / shell.css / base.css / components.css / app.js / snippets/
├── templates/               # 模板（保留，供新页复制）
├── pages/                   # 全部正式页面，扁平目录
└── qa/                      # screenshots/ 与 reports/（脚本生成）
```

> 壳样式独立在 `assets/shell.css`（l-* 布局壳 + proto-bar）：小样式表对各类渲染环境更稳，
> 页面引入顺序固定为 tokens.css → base.css → shell.css → components.css。

## 命名与链接约定

1. **扁平优先**：`pages/` 下平铺；页面引用资源统一 `../assets/…`。页面超 15 个才升级二级目录 `pages/<模块>/`，此时统一 `../../assets/…`。只有这两种写法。
2. **状态页**：`<页面id>.<state>.html`（`empty` / `loading` / `error`），与主页面并列放 `pages/`，并登记进 manifest 与站点地图。不用查询参数区分状态。
3. **死链 = 0**：页面内 `href` 指向的文件必须存在；锚点指向的 `id` 必须存在；禁止裸 `#` 占位；禁止外部 http(s) 链接与外链资源（原型可能断网演示）。
4. **title 格式**：`<title>页面名 - 模块名 | 项目名</title>` 全站统一。
5. **原型工具条**：每页右下角 `proto-bar`（返回站点地图 + 当前页路径），`proto-` 前缀类，不属于业务 UI；样式已在 components.css。
6. **页头只放标题**：列表页的「＋ 新增」按钮置于表格上方左侧（l-toolbar），页头右侧不放重复入口。
7. **表单页是隐藏页 + 抽屉优先**：新增/编辑默认右侧抽屉表单（drawer + c-field 组合，与详情同形态），「＋ 新增」按钮置于表格上方左侧；独立表单页（tpl-form）仅用于复杂多步流程。manifest 标 `nav=false`，不进侧边栏菜单——G3 会做菜单一致性检查。
8. **站点地图分组**：index.html 按用户任务流分组（如「订单管理」组：列表 → 详情 → 编辑弹窗说明），不是文件目录镜像；每张页面卡含页面名、一句话说明、状态页子链接。
