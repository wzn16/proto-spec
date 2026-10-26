# 门禁配置与自定义家族

> 读时机：项目要求的阈值与本 skill 默认不同时；要新增自己的美学家族时。
> 原则：**脚本里不写死阈值，也不写死家族数量。**

## 一、阈值：三层覆盖

| 层 | 位置 | 作用 |
| --- | --- | --- |
| 默认 | `config/gates.json` | skill 自带基线（锚线 ≤4、字号 ≥3 档、强调面积按断点分档…） |
| 项目 | `<项目>/qa/gates.config.json` | 覆盖同名键，只影响本项目 |
| 家族 | `references/families/Fx-*.md` 的 `family-manifest.identity` | 覆盖 tokens 值（色、圆角、行高…），由 G1f 校验 |

合并规则：默认 ← 项目覆盖（深合并，数组整体替换）。脚本都支持 `--config <file>` 再叠一层。

### 常用覆盖示例

```json
{
  "pixels": {
    "max_anchors": 3,
    "min_font_levels": 4,
    "min_right_margin": 16,
    "accent_bands": [
      { "min_width": 1200, "lo": 0.003, "hi": 0.015 },
      { "min_width": 0, "lo": 0.005, "hi": 0.03 }
    ]
  },
  "review": {
    "dims": ["层级", "节奏", "焦点", "密度", "一致性", "可信度", "品牌感"],
    "pass_score": 4
  },
  "details": { "kpi_banned": ["字段数", "今日订单", "完成率"] },
  "contrast": {
    "text_threshold": 7.0
  }
}
```

实测过的效果：把 `pixels.min_font_levels` 改成 9，G8 立刻按 9 档判定；把 `review.dims` 加一维「品牌感」，G7 立刻要求该维评分；把 `details.kpi_banned` 换成「今日订单」，G6 立刻拦下该 KPI。

## 二、自定义家族（不是只能用 F0–F9）

1. 复制任一 `references/families/Fx-*.md`，改 `family-manifest`：

```json
{
  "id": "FX1",
  "version": "0.1",
  "identity": {
    "--s-bg-page": "#F3F4F6",
    "--s-color-primary": "#7C2D12",
    "--s-text-primary": "#1C1917"
  }
}
```

2. 写四段内容：① 调性 ② tokens 覆盖表 ③ 组件规则 ④ 场景边界 ⑤ 身份特征与禁忌。
3. 深色家族**必须**同时给 `--s-text-primary/secondary/inverse`、`--s-bg-card`、`--s-border`、`--s-bg-sidebar` 与亮色状态字——只换底色会让正文对比度掉到 1.1:1（G4 会拦）。
4. 建样本并回归：

```bash
python3 scripts/gen_family_samples.py            # 扫描 families/ 目录，自动跳过已被项目覆盖的家族
python3 scripts/regress_pixels.py                # 三断点回归
python3 scripts/gen_regression_doc.py --write    # 把实测矩阵写回 pixel-rules.md
```

家族数量、样本数量、矩阵行数都由目录决定，不再有 `range(10)` 之类的写死清单。

## 三、哪些东西仍然"固定"

- 组件类名与 token 三层（`--g-* / --s-* / --c-*`）：这是契约，写死是为了可校验。
- 六维默认名单：可覆盖，默认给一组通用的。
- 脚本的算法本身（锚线聚类、墨迹判定）：不是阈值，不开放配置；要改就改脚本并跑回归。
