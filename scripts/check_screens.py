#!/usr/bin/env python3
"""G2 截图矩阵检查（可选门：需环境先把截图放入 qa/screenshots/）。

用法:
  python3 check_screens.py --project <项目目录>

约定: 截图由宿主截图能力生成，命名 <页面id>-<断点宽>.png（fullPage），
     断点来自 pages-manifest.json 的 breakpoints（缺省 [1440, 768, 375]）。
退出码: 0=通过  1=未通过  2=用法错误
报告:   <project>/qa/reports/g2.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MIN_BYTES = 20 * 1024
DEFAULT_BREAKPOINTS = [1440, 768, 375]


def png_width(data: bytes):
    """读 PNG IHDR 宽度；非 PNG 返回 None。"""
    if len(data) < 24 or not data.startswith(PNG_MAGIC):
        return None
    return int.from_bytes(data[16:20], "big")


def main() -> int:
    ap = argparse.ArgumentParser(description="G2 截图矩阵检查")
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    project = Path(args.project).resolve()

    mf = project / "pages-manifest.json"
    if not mf.is_file():
        print("[G2] pages-manifest.json 不存在", file=sys.stderr)
        return 2
    data = json.loads(mf.read_text(encoding="utf-8"))
    breakpoints = data.get("breakpoints") or DEFAULT_BREAKPOINTS

    ids: list[str] = []
    for pg in data.get("pages", []):
        stem = Path(pg.get("path", "x.html")).stem
        ids.append(stem)
        for st in pg.get("states", []):
            ids.append(f"{stem}.{st}")

    shots = project / "qa" / "screenshots"
    expected = {f"{i}-{w}.png" for i in ids for w in breakpoints}
    actual = {p.name for p in shots.glob("*.png")} if shots.is_dir() else set()

    violations: list[dict] = []
    for name in sorted(expected - actual):
        violations.append({"file": f"qa/screenshots/{name}", "kind": "缺图",
                           "value": name, "hint": "每页 × 每断点一张，fullPage"})
    for name in sorted(actual - expected):
        violations.append({"file": f"qa/screenshots/{name}", "kind": "多图",
                           "value": name, "hint": "截图与 manifest×断点不一致"})
    for name in sorted(actual & expected):
        f = shots / name
        raw = f.read_bytes()
        w = png_width(raw)
        if w is None:
            violations.append({"file": f.name, "kind": "非PNG", "value": name,
                               "hint": "文件头不是 PNG"})
            continue
        want = int(name.rsplit("-", 1)[1].split(".")[0])
        if w > want:
            violations.append({"file": f.name, "kind": "横向溢出",
                               "value": f"实宽 {w} > 断点 {want}",
                               "hint": "fullPage 宽度超出视口即破版"})
        if len(raw) < MIN_BYTES:
            violations.append({"file": f.name, "kind": "疑似空白页",
                               "value": f"{len(raw)} 字节", "hint": "< 20KB 视为空白"})

    report = {
        "gate": "G2",
        "pass": not violations,
        "summary": {"expected": len(expected), "found": len(actual),
                    "violations": len(violations)},
        "violations": violations,
    }
    out = project / "qa" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "g2.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif violations:
        print(f"[G2] FAIL：{len(violations)} 处差异（期望 {len(expected)} 张）")
        for v in violations[:30]:
            print(f"  {v['file']}  [{v['kind']}] {v['value']}  {v['hint']}")
    else:
        print(f"[G2] 通过：{len(expected)} 张截图矩阵完整，无空白/溢出")
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
