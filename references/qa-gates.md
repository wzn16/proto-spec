# 质量门体系（G1–G5）

> 上级入口：SKILL.md 步骤 6。设计原则：确定性优先（能脚本判定的绝不目测）、证据落盘（报告 JSON + exit code）、失败即阻断、判据全量化、豁免只能由用户明示给出。

## 目录导航

- [报告与退出码](#报告与退出码)
- [G1 规范符合性](#g1-规范符合性)
- [G3 交互完整性](#g3-交互完整性)
- [G2 截图验证（可选）](#g2-截图验证可选)
- [G5 总验收](#g5-总验收)
- [执行流水线](#执行流水线)

## 报告与退出码

统一 schema，写入 `<项目>/qa/reports/<gate>.json`：

```json
{
  "gate": "G1",
  "pass": false,
  "summary": { "checked": 12, "violations": 3 },
  "violations": [
    { "file": "pages/login.html", "line": 42, "property": "padding", "value": "17px", "nearestToken": "var(--s-space-4) 16px", "hint": "是否应为 token？" }
  ]
}
```

退出码：`0` 通过；`1` 未通过；`2` 用法错误。AI 声明「通过」必须引用报告中的计数字段原文。

## G1 规范符合性

脚本：`scripts/check_tokens.py`。扫描范围：`index.html`、`pages/*.html`、`templates/*.html`、`assets/snippets/*.html` 的 `<style>` 块与 `style=""` 属性，以及这些页面 `<link>` 引用的本地 CSS 文件（`assets/tokens.css` 除外）。

| 检查 | 口径 |
| --- | --- |
| 颜色 | `color` / `background(-color)` / `border-*-color` / `fill` / `stroke` / `outline-color` 只允许 tokens 变量；裸 hex/rgb 违规 |
| 字号 | `font-size` 只允许 tokens 档位（12/13/14/16/20/24/30px） |
| 圆角 | `border-radius` 档位以项目 tokens.css 登记值为准（基准家族 6/8/12/9999px；50% 正圆例外）——家族可收紧（如雷沃 4/8/12），以 tokens 变量引用为准 |
| 间距 | `padding*` / `margin*` / `gap` 只允许 4/8/12/16/20/24/32/48px |
| 变量卫生 | 页面内定义 `--*` 变量违规；引用未定义变量违规；`calc(` 违规 |

- 允许值集合从 `assets/tokens.css` 解析，归一化比较（hex 大小写、3↔6 位、rgb↔hex）。
- 结构性例外：`0`、`1px`、`-1px`（细线微调）、`100%`、`50%`、`auto`、`none`、`transparent`、`currentColor`、`inherit`。
- PASS：`violations = 0`。单页模式：`--page pages/xxx.html`。

## G3 交互完整性

脚本：`scripts/check_links.py`。

| # | 判据 | 标准 |
| --- | --- | --- |
| 3.1 | 内部死链 = 0 | `a[href]` / `form[action]` / `area[href]` 指向的文件存在；同页锚点 `id` 存在 |
| 3.2 | 裸 `#` 占位 = 0 | 占位交互必须有真实目标（v0.1 不设登记豁免） |
| 3.3 | 外链 = 0 | 禁止 `http(s)://` 链接与外链资源（`img/script/link` 的 src/href） |
| 3.4 | 三方对账差异 = 0 | `pages-manifest.json` ↔ `pages/*.html` 文件集 ↔ `index.html` 页面链接，三个集合完全一致（缺页/多页/孤儿页都算差异） |
| 3.5 | title 一致 | 每页 `<title>` 非空且等于 manifest 的 title |
| 3.6 | 菜单一致性 | 侧边栏链接只准指向 manifest `nav != false` 的页面；表单等隐藏页（nav=false）不得出现在任何侧边栏 |

## G2 截图验证（可选）

脚本：`scripts/check_screens.py`。**能力接口**：仅当运行环境具备截图/浏览器能力、且已把截图存入 `<项目>/qa/screenshots/`（命名 `<页面id>-<宽>.png`，断点 1440/768/375，fullPage）时运行；否则跳过并在验收单声明。

| # | 判据 | 标准 |
| --- | --- | --- |
| 2.1 | 矩阵完整 | PNG 数 = manifest 页数 × 3，缺一即 FAIL |
| 2.2 | 无空白页 | 单文件 < 20KB 即 FAIL |
| 2.3 | 无横向溢出 | 375 断点 PNG 实宽 > 375 即 FAIL（读 PNG IHDR，fullPage 捕获 scrollWidth） |
| 2.4 | 覆盖对账 | 截图页面集合与 manifest 一致，多截/漏截都算差异 |

修复后全量重截，不允许只补失败页。

## G4 可访问性门（v0.4 新增）

脚本：`scripts/check_contrast.py`。读项目 `assets/tokens.css`，对**语义角色配对**计算 WCAG 2.x 对比度：

| 配对 | 门槛 |
| --- | --- |
| `--s-text-primary` on `--s-bg-page` / `--s-bg-card` | ≥4.5:1（正文） |
| `--s-text-secondary` on `--s-bg-page` / `--s-bg-card` | ≥4.5:1（辅助文字） |
| `--s-text-inverse` on `--s-color-primary` | ≥4.5:1（主钮文字） |
| `--s-text-on-dark-muted` on `--s-bg-sidebar`（仅当两者存在） | ≥3:1（深底弱文字） |

PASS：全部配对达标或未定义（未定义记 FAIL 并在 hint 指出）。可用 `--pairs-json` 按家族扩展配对表。

## G5 总验收

脚本：`scripts/final_gate.py`。**重跑** G1/G3/G4 全部检查（不读旧报告），`qa/screenshots/` 存在时加跑 G2，否则标 `skipped`；再查交付物：

| # | 判据 | 标准 |
| --- | --- | --- |
| 5.1 | 子门全 PASS | 重跑结果 pass=true（G2 允许 skipped，但必须在验收单声明） |
| 5.2 | 交付包完整 | `SPEC.md`、`assets/tokens.css`、`index.html` 存在；页面数 = manifest 数 |
| 5.3 | 资源本地化 | 外部 `http(s)` 引用 = 0；本地引用资源文件存在 |
| 5.4 | 单页体积 | 每个 .html ≤ 500KB |
| 5.5 | 待确认零残留 | SPEC.md / index.html / pages 检索「待确认、待定、待拍板、TODO」= 0 处；有未决事项必须在会话问掉或登记待办，禁止默认处理不留痕 |
| 5.6 | 一票否决 | 任一项 FAIL 即总 FAIL，禁止降级交付 |

输出 `qa/reports/final-gate.json` + 人读验收单（PASS 项 + 证据路径 + 计数原文）。

## 执行流水线

1. 冻结完成时：`SPEC.md` + `assets/tokens.css` + `pages-manifest.json` 就位，缺任一禁止生成；
   **有参照截图时，元素对账单必须已经用户逐项确认（留痕于 SPEC 附录 C），否则禁止生成。**
2. 每页生成完：G1 单页检，exit 0 才算该页完成。
3. 全部页面完成：G1 全量复检 → G3。
4. 有截图能力：按断点截图入 `qa/screenshots/` → G2。
5. 交付前：G5 总验收 → exit 0 → 验收单 → 交付。

失败协议：exit ≠ 0 → 按报告逐条修复 → 重跑该门全量 → 直至 exit 0。禁止跳过、禁止口头豁免、禁止先交付再修。
