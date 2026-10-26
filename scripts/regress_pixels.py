#!/usr/bin/env python3
"""像素门回归：对 examples/family-samples 下每个家族样本跑 G8，断言「锚线测得出来」。

用途：任何改动 check_pixels.py 的阈值/判据后必须跑本脚本——深色与玻璃家族的墨迹判定
曾因亮度阈值失效，导致 G8 空转（专家二轮审核 P0）。

用法: python3 regress_pixels.py [--min-anchors 1]
退出码: 0=全部样本测得锚线 1=有样本测不到 2=没有样本
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLES = HERE.parent / "examples" / "family-samples"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-anchors", type=int, default=1)
    args = ap.parse_args()
    shots = sorted(SAMPLES.glob("*/shot/*.png"))
    if not shots:
        print("[regress] 没有样本截图（examples/family-samples/*/shot/*.png）")
        return 2
    bad = []
    for s in shots:
        r = subprocess.run([sys.executable, str(HERE / "check_pixels.py"), "--shot", str(s), "--json"],
                           capture_output=True, text=True)
        try:
            j = json.loads(r.stdout)
        except json.JSONDecodeError:
            bad.append((s, "输出非 JSON")); continue
        d = j["details"][0]
        width = d["size"][0]
        # 分档判据：宽屏必须测到锚线；窄屏至少要有 2 档字号且有墨迹
        if width >= 1000:
            ok = len(d["anchors"]) >= args.min_anchors
            why = f"锚线 {len(d['anchors'])} < {args.min_anchors}"
        else:
            ok = d["font_levels"] >= 2
            why = f"字号层级 {d['font_levels']} < 2"
        # 溢出检测：fullPage 截图宽度不得超出断点
        if width > int(s.name.split("-")[-1].split(".")[0]) + 2:
            ok, why = False, f"横向溢出：实宽 {width}"
        print(f"  {s.parent.parent.name}/{s.name}: {width}px · 锚线 {len(d['anchors'])} · "
              f"字号 {d['font_levels']} 档 · 强调 {d['accent_ratio']*100:.1f}% → {'OK' if ok else 'FAIL'}")
        if not ok:
            bad.append((s, why))
    if bad:
        print(f"[regress] FAIL：{len(bad)} 个样本测不到锚线")
        return 1
    print(f"[regress] 通过：{len(shots)} 个样本均测得锚线")
    return 0


if __name__ == "__main__":
    sys.exit(main())
