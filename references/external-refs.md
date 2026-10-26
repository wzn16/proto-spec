# 外部标杆索引（只参考，不引入代码）

> 读时机：需要找"这个产品/这个风格怎么做"时；或需要给用户解释"标杆长什么样"时。
> 原则：**只借判断，不搬代码**。任何外部仓库的代码/规则全文都不进本 skill，避免体积、许可与漂移问题。

| 标杆 | 是什么 | 可借鉴点 | 在我们哪一步用 |
| --- | --- | --- | --- |
| Anthropic frontend-design | 官方前端设计 skill | 反滥用字体、主导色 + 尖锐强调、一次编排的入场、非对称构图 | 步骤 2 字体与构图 |
| UI/UX Pro Max | 设计数据库（风格/配色/字对/UX 规则/图表） | "风格 → 字对/图表/反模式"的检索形态；主系统 + 页面级覆盖 | 步骤 2.5、SPEC §7.5 |
| impeccable | 界面质量检测规则集（数十条） | 规则可被脚本消费；每条规则配反面教材 | 我们的 G6 / detail-rules |
| awesome-design-md | 顶级产品设计系统合集 | 参考"大厂怎么定 toカン与密度"；只做参考不抄 | 步骤 2.6 拆标杆 |
| shadcn / Radix | 无样式组件 + 可访问性原语 | 组件语义与 a11y 默认值 | 组件库对照（component-map） |
| emil-design-eng | 交互细节与动效打磨 | 按钮反馈、展开自然、常用操作跟手 | typography-and-composition §动效 |
| Taste Skill | 自查空间节奏/字体层级/配色留白 | 三查快速清单 | visual-scorecard 的三秒测试前 |
| frontend-design-direction | 先定受众与重点再布局 | 与我们 design-from-brief 同源 | 步骤 1.5 |
| reference-design-contract | 参考图 → 设计规范 | 取色/量距/字阶的契约化 | reference-to-spec.md |

## 使用纪律

1. 引用时给仓库名与用途，不复制其规则清单全文；
2. 若某条规则明显更优，用**自己的话**写进 detail-rules / taste-checklist，并在文末注明灵感来源；
3. 不引入其依赖（npm 包、字体文件、图标库）到原型交付物，保持零依赖可离线。
