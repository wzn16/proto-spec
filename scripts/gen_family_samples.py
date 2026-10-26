#!/usr/bin/env python3
"""为每个美学家族生成像素/对比度回归样本（examples/family-samples/fN/）。

做法：复制 starter/assets → 把家族 manifest 的 identity 覆写成 :root 覆盖层 → 用 tpl-list 生成一页。
用法: python3 gen_family_samples.py [--families F1 F2 ...] [--force]
"""
from __future__ import annotations
import argparse, json, re, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FAM_DIR = ROOT / "references" / "families"
OUT = ROOT / "examples" / "family-samples"


def manifest(fam_file: Path) -> dict:
    t = fam_file.read_text(encoding="utf-8")
    m = re.search(r"```json family-manifest([\s\S]*?)```", t)
    return json.loads(m.group(1))


def build(fam: str, force: bool) -> Path:
    src = sorted(FAM_DIR.glob(f"{fam}-*.md"))
    if not src:
        raise SystemExit(f"找不到家族文件 {fam}")
    data = manifest(src[0])
    name = src[0].stem.split("-", 1)[1]
    d = OUT / fam.lower()
    if d.exists() and not force:
        return d
    if d.exists():
        # 保留已拍的回归截图（shot/），其余重建
        for sub in d.iterdir():
            if sub.name == "shot":
                continue
            shutil.rmtree(sub) if sub.is_dir() else sub.unlink()
        (d / "pages").mkdir(exist_ok=True)
    (d / "pages").mkdir(parents=True, exist_ok=True)
    if (d / "assets").exists():
        shutil.rmtree(d / "assets")
    shutil.copytree(ROOT / "starter" / "assets", d / "assets")
    tokens = (d / "assets" / "tokens.css").read_text(encoding="utf-8")
    override = "\n:root{\n" + "".join(f"  {k}:{v};\n" for k, v in data["identity"].items()) + "}\n"
    (d / "assets" / "tokens.css").write_text(tokens + override, encoding="utf-8")
    page = (ROOT / "starter" / "templates" / "tpl-list.html").read_text(encoding="utf-8")
    page = re.sub(r"<title>[^<]*</title>", f"<title>{fam} 家族回归 - {name}</title>", page, count=1)
    (d / "pages" / "list.html").write_text(page, encoding="utf-8")
    (d / "index.html").write_text(
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>{f} 回归</title>'
        '<link rel="stylesheet" href="assets/tokens.css"><link rel="stylesheet" href="assets/base.css">'
        '<link rel="stylesheet" href="assets/shell.css"><link rel="stylesheet" href="assets/components.css">'
        '<link rel="stylesheet" href="assets/family.css"></head><body><main class="l-page">'
        '<div class="l-page-head"><h1 class="u-text-headline">{f} {n}</h1></div>'
        '<div class="c-card"><div class="c-card__body"><p><a href="pages/list.html">列表页</a></p></div></div>'
        "</main></body></html>".format(f=fam, n=name), encoding="utf-8")
    return d


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="*", default=None)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    fams = args.families or [f"F{i}" for i in range(10)]
    for fam in fams:
        d = build(fam, args.force)
        print(f"[samples] {fam} → {d.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
