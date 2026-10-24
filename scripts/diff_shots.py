#!/usr/bin/env python3
"""截图差异工具（非门禁）：对比两版截图，指出变了哪些区块、整体指标怎么变。

用法:
  python3 diff_shots.py --before old.png --after new.png [--out report.json] [--json]

输出:
  - 变化面积占比、变化区块列表（按变化量排序，给 bbox 与幅度）
  - 指标变化：锚线条数、强调色面积、实心块、字号层级（复用 check_pixels）
用途: 调优循环里回答"这轮改好了还是改坏了"，不参与 G5 放行。
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

try:
    from PIL import Image
    import numpy as np
except Exception as e:  # pragma: no cover
    print(f"[diff] SKIP：缺少 Pillow/numpy（{e}）")
    sys.exit(0)

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from check_pixels import check as pixel_check  # 复用指标
except Exception:
    pixel_check = None

CELL = 32          # 差异网格
DIFF_T = 18        # 单元格平均色差阈值


def load(p: Path):
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int32)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--before", required=True)
    ap.add_argument("--after", required=True)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    a, b = load(Path(args.before)), load(Path(args.after))
    if a.shape != b.shape:
        print(f"[diff] 尺寸不同：{a.shape[1]}×{a.shape[0]} vs {b.shape[1]}×{b.shape[0]}，先统一视口再比")
        return 2

    H, W, _ = a.shape
    gy, gx = H // CELL, W // CELL
    d = np.abs(a - b).mean(axis=2)
    grid = d[:gy * CELL, :gx * CELL].reshape(gy, CELL, gx, CELL).mean(axis=(1, 3))
    changed = grid > DIFF_T
    ratio = float(changed.mean())

    # 连通区块
    seen = np.zeros_like(changed)
    blocks = []
    for y in range(gy):
        for x in range(gx):
            if not changed[y, x] or seen[y, x]:
                continue
            stack = [(y, x)]; seen[y, x] = True
            cells = []
            while stack:
                cy, cx = stack.pop(); cells.append((cy, cx))
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < gy and 0 <= nx < gx and changed[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True; stack.append((ny, nx))
            ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
            mag = float(grid[min(ys):max(ys) + 1, min(xs):max(xs) + 1].max())
            blocks.append({"bbox": [min(xs) * CELL, min(ys) * CELL,
                                    (max(xs) - min(xs) + 1) * CELL, (max(ys) - min(ys) + 1) * CELL],
                           "cells": len(cells), "max_diff": round(mag, 1)})
    blocks.sort(key=lambda b: b["cells"], reverse=True)

    metrics = None
    if pixel_check:
        try:
            pa, pb = pixel_check(Path(args.before)), pixel_check(Path(args.after))
            metrics = {
                "anchors": [len(pa["anchors"]), len(pb["anchors"])],
                "accent_ratio": [pa["accent_ratio"], pb["accent_ratio"]],
                "accent_blobs": [pa["accent_blobs"], pb["accent_blobs"]],
                "font_levels": [pa["font_levels"], pb["font_levels"]],
                "violations": [len(pa["violations"]), len(pb["violations"])],
            }
        except Exception:
            metrics = None

    report = {"changed_ratio": round(ratio, 4), "blocks": blocks[:8],
              "blocks_total": len(blocks), "metrics": metrics}
    if args.out:
        Path(args.out).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[diff] 变化面积 {ratio * 100:.1f}%，区块 {len(blocks)} 个（前 5 个按面积）")
        for b in blocks[:5]:
            print(f"  bbox={b['bbox']}  单元格 {b['cells']}  峰值差 {b['max_diff']}")
        if metrics:
            print(f"[diff] 指标 锚线 {metrics['anchors'][0]}→{metrics['anchors'][1]} · "
                  f"强调 {metrics['accent_ratio'][0]*100:.1f}%→{metrics['accent_ratio'][1]*100:.1f}% · "
                  f"块 {metrics['accent_blobs'][0]}→{metrics['accent_blobs'][1]} · "
                  f"字号 {metrics['font_levels'][0]}→{metrics['font_levels'][1]} · "
                  f"问题 {metrics['violations'][0]}→{metrics['violations'][1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
