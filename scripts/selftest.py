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
    review = proj / "qa" / "visual-review.md"
    review.parent.mkdir(parents=True, exist_ok=True)
    (proj / "qa" / "visual-review-peer.md").write_text(
        "# 独立视觉评审\n\n## 一、三秒测试\n- 像工业后台；第一眼落在表格首列。\n\n"
        "## 二、锚线检查\n- 3 条锚线，表内文本偏左 4px。\n\n## 三、六维打分\n\n"
        "| 维度 | 分数 | 依据 | 改法 |\n| --- | --- | --- | --- |\n"
        "| 层级 | 4 | 标题与正文层级清楚 | — |\n"
        "| 节奏 | 4 | 区块间距成组 | — |\n"
        "| 焦点 | 4 | 主操作可见 | — |\n"
        "| 密度 | 4 | 一屏 12 行合适 | — |\n"
        "| 一致性 | 5 | 同类控件同规格 | — |\n"
        "| 可信度 | 4 | 编号与时间可信 | — |\n\n"
        "## 四、改进项\n1. 无。\n\n## 五、保留\n1. 表格密度。\n\n## 六、结论\n- 最低分 4。\n", encoding="utf-8")

    review.write_text(
        "# 视觉评分单（G7）\n\n## 一、三秒测试\n- 像 2020s 企业后台；第一眼看到表格。\n\n"
        "## 二、锚线检查\n- 2 条锚线。\n\n"
        "## 三、六维打分\n\n| 维度 | 分数 | 依据 | 改法 |\n| --- | --- | --- | --- |\n"
        "| 层级 | 4 | 页标题 24 与正文 13 可辨 | — |\n"
        "| 节奏 | 4 | 组间 16 组内 8 成组 | — |\n"
        "| 焦点 | 4 | 页头唯一主按钮 | — |\n"
        "| 密度 | 4 | 行高 40 与任务匹配 | — |\n"
        "| 一致性 | 5 | 组件同规格无例外 | — |\n"
        "| 可信度 | 4 | 数据与文案自洽 | — |\n\n"
        "## 四、改进项\n1. 无。\n\n## 五、保留\n1. 表格密度。\n\n"
        "## 六、结论\n- 最低分 4。\n", encoding="utf-8")

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


G7_BAD_ALL_ONE = """# 自评
## 一、三秒测试\n像模板\n## 二、锚线检查\n3 条\n## 三、六维打分
| 维度 | 分数 | 依据 | 改法 |
| --- | --- | --- | --- |
| 层级 | 1 | 页面很乱没有层次 | 复评5 |
| 节奏 | 1 | 间距不均节奏差 | 复评5 |
| 焦点 | 1 | 没有主操作焦点 | 复评5 |
| 密度 | 1 | 密度失衡太挤 | 复评5 |
| 一致性 | 1 | 规格不统一 | 复评5 |
| 可信度 | 1 | 像模板不像产品 | 复评5 |
## 四、改进项\n1. 全改\n## 五、保留\n1. 无\n## 六、结论\n已复评
"""

G7_BAD_PIPE = """# 自评
## 一、三秒测试\n像模板\n## 二、锚线检查\n3 条\n## 三、六维打分
| 维度 | 分数 | 依据 | 改法 |
| --- | --- | --- | --- |
| 层级 | 3 | 页面层次偏弱 | 不采纳 |||||||||||||||||
| 节奏 | 4 | 间距成组 | — |
| 焦点 | 4 | 主操作唯一 | — |
| 密度 | 4 | 与任务匹配 | — |
| 一致性 | 4 | 规格统一 | — |
| 可信度 | 4 | 数据自洽 | — |
## 四、改进项\n1. 无\n## 五、保留\n1. 无\n## 六、结论\n不采纳
"""


def g7_negative() -> list[str]:
    """G7 必须拦住：全 1 分、竖线填充理由、缺他评无理由。"""
    errs = []
    import tempfile, shutil
    for label, body in (("全 1 分", G7_BAD_ALL_ONE), ("竖线填充", G7_BAD_PIPE)):
        d = Path(tempfile.mkdtemp())
        (d / "qa").mkdir(parents=True)
        (d / "qa" / "visual-review.md").write_text(body, encoding="utf-8")
        r = subprocess.run([sys.executable, str(HERE / "check_visual_review.py"), "--project", str(d)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            errs.append(f"G7 未拦住「{label}」")
        shutil.rmtree(d, ignore_errors=True)
    return errs


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
        # G7 对抗负例：全 1 分 / 竖线填充 不得通过
        import tempfile as _tf, shutil as _sh
        for label, body in (("全 1 分", G7_BAD_ALL_ONE), ("竖线填充", G7_BAD_PIPE)):
            d = Path(_tf.mkdtemp())
            (d / "qa").mkdir(parents=True)
            (d / "qa" / "visual-review.md").write_text(body, encoding="utf-8")
            c7, _ = run("check_visual_review.py", d)
            checks.append((f"G7 拦截「{label}」", c7 == 1, f"exit={c7}"))
            _sh.rmtree(d, ignore_errors=True)

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
