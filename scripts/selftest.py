#!/usr/bin/env python3
"""selftest —— proto-spec 脚本自测（也是装机后的验证工具）。

在临时目录构造迷你原型项目（合规 + 违规两套），断言各质量门行为符合预期。

用法:
  python3 selftest.py [--keep]

退出码: 0=全部断言通过  1=存在失败
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
GOOD_PAGE_A = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>页面A - 演示 | 自测项目</title>
<link rel="stylesheet" href="../assets/tokens.css">
<link rel="stylesheet" href="../assets/base.css">
<link rel="stylesheet" href="../assets/shell.css">
<link rel="stylesheet" href="../assets/components.css">
</head><body>
<a href="b.html#sec" id="go">去B页</a>
<p style="color:var(--s-text-secondary);padding:0 var(--s-space-4);border-radius:var(--s-radius-control)">合规内容</p>
<div class="proto-bar"><a href="../index.html">返回站点地图</a><span>pages/a.html</span></div>
</body></html>
"""
GOOD_PAGE_B = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>页面B - 演示 | 自测项目</title>
<link rel="stylesheet" href="../assets/tokens.css">
</head><body>
<a href="a.html" id="sec">回A页</a>
</body></html>
"""
BAD_PAGE_PATCH = '<style>.x{color:#FF0000;padding:17px;font-size:15px}</style><a href="#">占位</a><img src="https://example.com/x.png" alt="">'


def run(script: str, project: Path):
    r = subprocess.run(
        [sys.executable, str(HERE / script), "--project", str(project), "--json"],
        capture_output=True, text=True)
    try:
        return r.returncode, json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.returncode, {}


def build_fixture(root: Path, bad: bool) -> Path:
    proj = root / ("bad" if bad else "good")
    shutil.copytree(SKILL / "starter" / "assets", proj / "assets")
    pages = proj / "pages"
    pages.mkdir(parents=True)
    a = GOOD_PAGE_A + (BAD_PAGE_PATCH if bad else "")
    (pages / "a.html").write_text(a, encoding="utf-8")
    (pages / "b.html").write_text(GOOD_PAGE_B, encoding="utf-8")
    (proj / "SPEC.md").write_text("# SPEC — 自测项目\n状态：frozen\n", encoding="utf-8")
    (proj / "index.html").write_text(
        '<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
        "<title>站点地图 - 自测项目</title></head><body>"
        '<a href="pages/a.html">A</a><a href="pages/b.html">B</a></body></html>',
        encoding="utf-8")
    (proj / "pages-manifest.json").write_text(json.dumps({
        "project": "自测项目", "specVersion": "0.1.0", "specStatus": "frozen",
        "breakpoints": [1440, 768, 375],
        "pages": [
            {"id": "a", "path": "pages/a.html",
             "title": "页面A - 演示 | 自测项目", "type": "list", "states": []},
            {"id": "b", "path": "pages/b.html",
             "title": "页面B - 演示 | 自测项目", "type": "detail", "states": []},
        ]}, ensure_ascii=False, indent=2), encoding="utf-8")
    return proj


def main() -> int:
    ap = argparse.ArgumentParser(description="proto-spec 脚本自测")
    ap.add_argument("--keep", action="store_true", help="保留临时目录便于排查")
    args = ap.parse_args()

    root = Path(tempfile.mkdtemp(prefix="proto-spec-selftest-"))
    checks: list[tuple[str, bool, str]] = []
    try:
        good = build_fixture(root, bad=False)
        bad = build_fixture(root, bad=True)

        c, r = run("check_tokens.py", good)
        checks.append(("合规项目 G1 通过", c == 0,
                       f"exit={c} violations={r.get('summary', {}).get('violations')}"))
        c, r = run("check_links.py", good)
        checks.append(("合规项目 G3 通过", c == 0,
                       f"exit={c} violations={r.get('summary', {}).get('violations')}"))
        c, r = run("final_gate.py", good)
        skipped = r.get("summary", {}).get("skipped", [])
        checks.append(("合规项目 G5 通过（G2 skipped）",
                       c == 0 and any("G2" in s for s in skipped),
                       f"exit={c} summary={r.get('summary')}"))

        c1, r1 = run("check_tokens.py", bad)
        n1 = r1.get("summary", {}).get("violations", 0)
        checks.append(("违规项目 G1 拦截（违规数≥3）", c1 == 1 and n1 >= 3,
                       f"exit={c1} violations={n1}"))
        c3, r3 = run("check_links.py", bad)
        checks.append(("违规项目 G3 拦截", c3 == 1,
                       f"exit={c3} violations={r3.get('summary', {}).get('violations')}"))
        c5, _ = run("final_gate.py", bad)
        checks.append(("违规项目 G5 一票否决", c5 == 1, f"exit={c5}"))

        ok = all(passed for _, passed, _ in checks)
        print(f"proto-spec selftest：{'PASS' if ok else 'FAIL'}（临时目录 {root}）")
        for name, passed, detail in checks:
            print(f"  {'✓' if passed else '✗'} {name}  {detail if not passed else ''}")
        return 0 if ok else 1
    finally:
        if args.keep:
            print(f"临时目录已保留：{root}")
        else:
            shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
