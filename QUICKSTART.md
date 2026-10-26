# 30 分钟做出第一版

> **为什么在根目录**：这是新用户第一个要打开的文件，必须与 SKILL.md 同级才被发现；详细规则都在 `references/`。

> 目标：从"想做一套原型"到"三页可点、八门能跑"。只走最短路径，细节等第二版再补。

## 0. 起骨架（2 分钟）

```bash
cp -R starter/ my-proto/ && cd my-proto/
# 或者直接复制一个已跑绿的完整示例：
# cp -R examples/demo-project/ my-proto/
```

`starter/` 是母版，**跑 G5 会红是正常的**（没有页面与评分单）。绿基线看 `examples/demo-project/`。

## 1. 只回答 5 个问题（5 分钟）

| 问题 | 例子 |
| --- | --- |
| 给谁用、在什么场合用 | 车间主管，班前会在投屏上看 |
| 最重要的一个决策是什么 | 今天哪些设备没点检 |
| 有几个页面 | 看板 / 台账 / 概览 |
| 有没有参考图或现成系统 | 有截图 / 没有 |
| 多久要 | 今天下午 |

**其余全部用默认**：家族 F0、中密度、8px 圆角、冷色、150ms 动效。不要在第一版纠结配色。

## 2. 写一页 SPEC（5 分钟）

复制 `starter/SPEC-lite.md` 到 `my-proto/SPEC.md`，填四行：家族、页面清单、每页一句话、已知限制。
有参考图时补附录 C（逐项确认）；没有就跳过。

## 3. 生成页面（10 分钟）

- 选模板：`starter/templates/tpl-list.html`（台账）/ `tpl-form.html`（表单）/ `tpl-single.html`（单页）/ `tpl-detail.html`（详情）/ `tpl-board.html`（看板）
- 复制到 `pages/`，改标题与内容，链到 `../index.html`
- 写 `pages-manifest.json`（照抄 `examples/demo-project/pages-manifest.json` 改路径）

**第一版不要做**：多角色、暗色、打印、图表动画、动态筛选联动。

## 4. 截图 + 自评（5 分钟）

```bash
python3 scripts/shoot.py --project . --sizes 1440x900,375x812   # 自带截图器
python3 scripts/check_pixels.py --project .                     # 像素指标
```

写 `qa/visual-review.md`：四个小节 + 六维打分（每维写"位置 + 现象"，≥6 字）。
没有独立评审就先写「未独立评审：<20 字理由>」。

## 5. 跑门（3 分钟）

```bash
python3 scripts/final_gate.py --project .
```

红哪条改哪条，通常就是这几类：裸色值、死链、缺空态、KPI 写成"字段数"、末列贴边。

## 6. 交付（可选，2 分钟）

```bash
python3 scripts/gen_delivery_readme.py --project .
python3 scripts/export_tokens.py --tokens assets/tokens.css --out dist/
```

## 什么时候不走这条路

- 需要 3 个以上方向对比 → 走完整流程（`references/design-direction.md`）
- 有严格品牌规范 → 走 `references/reference-to-spec.md` 取色量距
- 要交给甲方评审 → 必须补独立评审（`references/visual-review-protocol.md`）与三档截图
