#!/usr/bin/env python3
"""扫描家族样本，实测各门结果，把矩阵写进 references/pixel-rules.md 的标记区。

- 家族清单来自 references/families/*.md（可加项目本地 families/），不写死数量
- 结果来自实际跑脚本，不是手抄
用法: python3 gen_regression_doc.py [--write]
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FAM_DIR = ROOT / "references" / "families"
SAMPLES = ROOT / "examples" / "family-samples"
DOC = ROOT / "references" / "pixel-rules.md"
BEGIN, END = "<!-- REGRESSION:BEGIN -->", "<!-- REGRESSION:END -->"


def run(args) -> tuple[bool, dict]:
    r = subprocess.run([sys.executable, *args], capture_output=True, text=True)
    try:
        return r.returncode == 0, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode == 0, {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="写回 pixel-rules.md")
    args = ap.parse_args()
    fams = sorted({p.name.split("-")[0] for p in FAM_DIR.glob("F*.md")})

    def sample_for(fam: str) -> Path | None:
        cand = SAMPLES / fam.lower()
        if cand.is_dir():
            return cand
        for spec in (ROOT / "examples").glob("*/SPEC.md"):
            m = re.search(r"\|\s*家族\s*\|\s*(F[0-9])", spec.read_text(encoding="utf-8"))
            if m and m.group(1) == fam:
                return spec.parent
        return None
    rows = []
    for fam in fams:
        proj = sample_for(fam)
        if proj is None:
            rows.append(f"| {fam} | 无样本 | — | — | — | — | — |")
            continue
        g1, _ = run(["scripts/check_tokens.py", "--project", str(proj)])
        g1f, _ = run(["scripts/check_tokens.py", "--project", str(proj), "--family", fam])
        g4, _ = run(["scripts/check_contrast.py", "--project", str(proj)])
        shot_dir = proj / "shot" if (proj / "shot").is_dir() else proj / "qa" / "screenshots"
        shots = sorted(shot_dir.glob("*.png")) if shot_dir.is_dir() else []
        wide = [s for s in shots if "1440" in s.name]
        narrow = [s for s in shots if "375" in s.name]
        anchors = levels = accent = "—"
        overflow = "无"
        if wide:
            ok, j = run(["scripts/check_pixels.py", "--shot", str(wide[0]), "--json"])
            d = j["details"][0]
            anchors, levels, accent = len(d["anchors"]), d["font_levels"], f"{d['accent_ratio']*100:.1f}%"
        if narrow:
            ok, j = run(["scripts/check_pixels.py", "--shot", str(narrow[0]), "--json"])
            d = j["details"][0]
            if d["size"][0] > 377:
                overflow = f"溢出 {d['size'][0]}px"
        mark = lambda x: "✓" if x else "✗"
        rows.append(f"| {fam} | `{proj.name}` | {mark(g1)} | {mark(g1f)} | {mark(g4)} | {anchors} | {levels} | {accent} | {overflow} |")
    table = "\n".join([
        BEGIN,
        "| 家族 | 样本 | G1 | G1f | G4 | 1440 锚线 | 字号档 | 强调 | 375 溢出 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        *rows,
        "",
        "> 本表由 `scripts/gen_regression_doc.py --write` 实测生成，家族数量随 `references/families/` 目录变化。",
        END,
    ])
    text = DOC.read_text(encoding="utf-8")
    if BEGIN in text and END in text:
        text = re.sub(rf"{BEGIN}[\s\S]*?{END}", table, text)
    else:
        text = text.rstrip() + "\n\n## 回归矩阵（实测生成）\n\n" + table + "\n"
    if args.write:
        DOC.write_text(text, encoding="utf-8")
        print(f"[regression] 已写入 {DOC.relative_to(ROOT)}（{len(rows)} 个家族）")
    else:
        print(table)
    return 0


if __name__ == "__main__":
    sys.exit(main())
