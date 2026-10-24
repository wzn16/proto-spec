#!/usr/bin/env python3
"""G8 像素级 UI 检查：在截图上量锚线、贴边裁切、强调色面积与字号层级。

用法:
  python3 check_pixels.py --project <目录> [--json]
  python3 check_pixels.py --shot <png> [--json]

依赖：Pillow + numpy（DSH 自带）。没有截图时直接跳过（exit 0）。
判据（默认阈值，可在阈值项自行调整）：
  anchors    正文与标题左缘应归到 2–3 条锚线；≥4 条告警
  clipping   文本墨迹距卡片右边线 ≤3px 视为贴边/裁切
  accent     强调色像素面积 ≤10%；实心强调色块 ≤2
  fontlevels 字号层级 4–6 档为宜；<3 表示层级不足
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except Exception as e:  # pragma: no cover
    print(f"[G8] SKIP：缺少 Pillow/numpy（{e}）")
    sys.exit(0)

INK_LUMA = 120          # 深色文字判定
ACCENT_SAT = 0.45       # 强调色饱和度下限
ACCENT_VAL = 0.35
MAX_ANCHORS = 3
CLIP_PX = 3
ACCENT_RATIO = 0.10
MAX_ACCENT_BLOBS = 2
MIN_FONT_LEVELS = 3
MIN_RIGHT_MARGIN = 12


def load(p: Path):
    im = Image.open(p).convert("RGB")
    return np.asarray(im, dtype=np.int32), im.size


def ink_mask(a: np.ndarray, x0: int) -> np.ndarray:
    lum = (a[:, :, 0] * 299 + a[:, :, 1] * 587 + a[:, :, 2] * 114) // 1000
    m = lum <= INK_LUMA
    m[:, :x0] = False          # 排除侧栏
    m[:120, :] = False         # 排除顶栏与页签（深色按钮底会被误判为墨迹）
    return m


def bands(mask: np.ndarray) -> list[tuple[int, int, int]]:
    """按行聚合墨迹，返回 [(y0, y1, 左缘x)]。"""
    rows = mask.any(axis=1)
    out, y = [], 0
    H = mask.shape[0]
    while y < H:
        if rows[y]:
            y2 = y
            while y2 + 1 < H and rows[y2 + 1]:
                y2 += 1
            xs = np.where(mask[y:y2 + 1].any(axis=0))[0]
            if len(xs):
                out.append((y, y2, int(xs.min())))
            y = y2 + 1
        else:
            y += 1
    return out


def cluster(values: list[int], tol: int = 4) -> list[tuple[int, int]]:
    """把左缘值聚成锚线，返回 [(中位x, 出现次数)]。"""
    if not values:
        return []
    values = sorted(values)
    groups, cur = [], [values[0]]
    for v in values[1:]:
        if v - cur[-1] <= tol:
            cur.append(v)
        else:
            groups.append(cur); cur = [v]
    groups.append(cur)
    return [(int(np.median(g)), len(g)) for g in groups]


def glyph_heights(mask: np.ndarray) -> list[int]:
    """统计竖笔画连续长度（≈字高），返回排序后的样本。"""
    H, W = mask.shape
    heights = []
    for x in range(0, W, 2):
        col = mask[:, x]
        y = 0
        while y < H:
            if col[y]:
                y2 = y
                while y2 + 1 < H and col[y2 + 1]:
                    y2 += 1
                h = y2 - y + 1
                if 6 <= h <= 60:
                    heights.append(h)
                y = y2 + 1
            else:
                y += 1
    return heights


def font_levels(mask: np.ndarray) -> int:
    hs = glyph_heights(mask)
    if not hs:
        return 0
    bins: dict[int, int] = {}
    for h in hs:
        k = int(round(h / 2) * 2)
        bins[k] = bins.get(k, 0) + 1
    total = sum(bins.values())
    # 只统计占比 ≥2% 的档位，避免噪声
    return sum(1 for v in bins.values() if v / total >= 0.02)


def accent_stats(a: np.ndarray):
    mx = a.max(axis=2).astype(np.float32)
    mn = a.min(axis=2).astype(np.float32)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    mask = (sat >= ACCENT_SAT) & (mx / 255.0 >= ACCENT_VAL)
    ratio = float(mask.mean())
    # 下采样连通块计数
    small = mask[::4, ::4]
    seen = np.zeros_like(small, dtype=bool)
    blobs = 0
    H, W = small.shape
    for y in range(0, H, 1):
        for x in range(0, W, 1):
            if not small[y, x] or seen[y, x]:
                continue
            stack = [(y, x)]; seen[y, x] = True; area = 0
            while stack:
                cy, cx = stack.pop(); area += 1
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and small[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; stack.append((ny, nx))
            if area >= 300 // 16:
                blobs += 1
    return ratio, blobs


def card_right_edges(a: np.ndarray, x0: int) -> list[dict]:
    """检测竖向卡片边线，返回 [{x, y0, y1}]：只在该边线真实存在的纵向区间内使用。"""
    H, W, _ = a.shape
    lum = (a[:, :, 0] * 299 + a[:, :, 1] * 587 + a[:, :, 2] * 114) // 1000
    edges = []
    for x in range(x0 + 10, W - 4):
        col = lum[120:, x]
        l3 = lum[120:, x - 3]
        r3 = lum[120:, x + 3]
        diff_left = np.abs(col - l3)
        diff_right = np.abs(col - r3)
        frac = float(((diff_left > 8) & (diff_right > 8)).mean())
        if frac > 0.55:
            edges.append(x)
    # 合并相邻列，并记录每条边线的纵向跨度
    merged = []
    for x in edges:
        if merged and x - merged[-1][-1] <= 2:
            merged[-1].append(x)
        else:
            merged.append([x])
    out = []
    for group in merged:
        x = int(np.median(group))
        col = lum[120:, x]
        l3 = lum[120:, x - 3]
        r3 = lum[120:, x + 3]
        on = (np.abs(col - l3) > 8) & (np.abs(col - r3) > 8)
        # 取最长连续段作为该边线真实跨度（避免被零散文字污染）
        best, cur_start = (0, 0), None
        for i, v in enumerate(on):
            if v and cur_start is None:
                cur_start = i
            elif not v and cur_start is not None:
                if i - cur_start > best[1] - best[0]:
                    best = (cur_start, i)
                cur_start = None
        if cur_start is not None and len(on) - cur_start > best[1] - best[0]:
            best = (cur_start, len(on))
        if best[1] - best[0] < 40:
            continue
        out.append({"x": x, "y0": best[0] + 120, "y1": best[1] - 1 + 120})
    return out


def right_margins(a: np.ndarray, m: np.ndarray, edges: list[dict], x0: int) -> list[int]:
    """每张卡片内（限定该边线的纵向区间），内容墨迹到卡片右边界的最小留白。"""
    lum = (a[:, :, 0] * 299 + a[:, :, 1] * 587 + a[:, :, 2] * 114) // 1000
    out = []
    rights = [e for e in edges
              if e["x"] + 6 < a.shape[1] and float(lum[e["y0"]:e["y1"] + 1, e["x"] + 6].mean()) > 200]
    for e in rights:
        ex = e["x"]
        region = m[e["y0"]:e["y1"] + 1, max(x0, ex - 400):max(x0 + 1, ex - 1)]
        cols = np.where(region.any(axis=0))[0]
        if len(cols) == 0:
            continue
        last_ink = max(x0, ex - 400) + int(cols.max())
        out.append(int(ex - last_ink))
    return out


def row_pitch(mask: np.ndarray) -> dict:
    """表格行距一致性：相邻文本带顶部的间距统计（只报告，不参与门禁）。"""
    tops = [b[0] for b in bands(mask)]
    if len(tops) < 6:
        return {"samples": 0}
    diffs = [tops[i + 1] - tops[i] for i in range(len(tops) - 1)]
    diffs = [d for d in diffs if 8 <= d <= 80]
    if len(diffs) < 5:
        return {"samples": len(diffs)}
    import statistics as st
    med = st.median(diffs)
    sd = st.pstdev(diffs)
    return {"samples": len(diffs), "median": round(med, 1), "stdev": round(sd, 1),
            "cv": round(sd / med, 3) if med else 0}


def check(p: Path) -> dict:
    a, (W, H) = load(p)
    x0 = 240 if W > 900 else 0
    m = ink_mask(a, x0)
    bs = bands(m)
    anchors = cluster([b[2] for b in bs])
    strong = [x for x, n in anchors if n >= 3]
    ratio, blobs = accent_stats(a)
    levels = font_levels(m)
    edges = card_right_edges(a, x0)
    lum = (a[:, :, 0] * 299 + a[:, :, 1] * 587 + a[:, :, 2] * 114) // 1000
    right_edges = []
    for e in edges:
        x = e["x"]
        if x + 6 >= W:
            continue
        right_bright = float(lum[e["y0"]:e["y1"] + 1, x + 6].mean()) > 200
        left_has_ink = float(m[e["y0"]:e["y1"] + 1, max(0, x - 30):max(1, x - 6)].mean()) > 0.02
        if right_bright and left_has_ink:
            right_edges.append(e)
    clipped = []
    for e in right_edges:
        ex = e["x"]
        seg = m[e["y0"]:e["y1"] + 1, max(0, ex - CLIP_PX):ex]
        if seg.sum() > 20:
            clipped.append(ex)
    margins = right_margins(a, m, edges, x0)
    tight = [x for x in margins if x < MIN_RIGHT_MARGIN]
    pitch = row_pitch(m)

    violations = []
    if tight:
        violations.append({"kind": "右缘留白不足", "value": f"{len(tight)} 张卡片留白 {min(tight)}px",
                           "hint": f"内容距卡片右边线应 ≥{MIN_RIGHT_MARGIN}px：末列加右内边距或收列宽"})
    if len(strong) > MAX_ANCHORS + 1:
        violations.append({"kind": "锚线过多", "value": f"{len(strong)} 条（{strong}）",
                           "hint": f"正文/标题左缘应归到 ≤{MAX_ANCHORS + 1} 条锚线，检查表内文本与统计卡是否与卡片标题同线"})
    if clipped:
        violations.append({"kind": "文本贴边/裁切", "value": f"边线 x={clipped}",
                           "hint": "文本墨迹距卡片右边线 ≤3px：改列宽或给单元格留右内边距"})
    if ratio > ACCENT_RATIO:
        violations.append({"kind": "强调色超量", "value": f"{ratio * 100:.1f}%",
                           "hint": f"强调色面积应 ≤{ACCENT_RATIO * 100:.0f}%，把次要控件降为描边/文字"})
    # 实心强调块只报告（主操作超量由 G6 执法；块计数受图标/标签影响，不设门）
    if levels < MIN_FONT_LEVELS:
        violations.append({"kind": "字号层级不足", "value": f"{levels} 档",
                           "hint": f"至少 {MIN_FONT_LEVELS} 档（标题/正文/辅助）；拉开层级差"})
    return {"file": p.name, "size": [W, H], "anchors": strong, "accent_ratio": round(ratio, 4),
            "right_margins": margins, "row_pitch": pitch,
            "accent_blobs": blobs, "font_levels": levels, "card_edges": [e["x"] for e in edges[-6:]],
            "violations": violations}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project")
    ap.add_argument("--shot")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    shots = []
    root = None
    if args.shot:
        shots = [Path(args.shot)]
    elif args.project:
        root = Path(args.project).resolve()
        d = root / "qa" / "screenshots"
        shots = sorted(d.glob("*1440*.png")) or sorted(d.glob("*.png"))[:3] if d.is_dir() else []
    if not shots:
        print("[G8] SKIP：没有 1440 宽截图")
        return 0
    results = [check(p) for p in shots]
    viol = [v | {"file": r["file"]} for r in results for v in r["violations"]]
    report = {"gate": "G8", "pass": not viol,
              "summary": {"shots": len(results), "violations": len(viol),
                          "anchors": {r["file"]: len(r["anchors"]) for r in results},
                          "accent": {r["file"]: r["accent_ratio"] for r in results}},
              "violations": viol, "details": results}
    if root:
        out = root / "qa" / "reports"
        out.mkdir(parents=True, exist_ok=True)
        (out / "g8-pixels.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif viol:
        print(f"[G8] FAIL：{len(viol)} 处（{len(results)} 张）")
        for v in viol[:10]:
            print(f"  {v['file']}  [{v['kind']}] {v['value']} → {v['hint']}")
    else:
        print(f"[G8] 通过：{len(results)} 张，锚线/贴边/强调面积/字号层级均达标")
        for r in results:
            print(f"  {r['file']}: 锚线 {len(r['anchors'])} 条 {r['anchors']} · 强调 {r['accent_ratio']*100:.1f}% · 块 {r['accent_blobs']} · 字号 {r['font_levels']} 档")
    return 0 if not viol else 1


if __name__ == "__main__":
    sys.exit(main())
