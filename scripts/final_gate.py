#!/usr/bin/env python3
"""G5 交付前总验收：重跑全部子门 + 交付物检查，唯一放行门。

用法:
  python3 final_gate.py --project <项目目录>

退出码: 0=通过  1=未通过  2=用法错误
报告:   <project>/qa/reports/final-gate.json
"""
from __future__ import annotations

import argparse
import json, re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

MAX_HTML_BYTES = 500 * 1024
EXTERNAL = ("http://", "https://", "//")
HERE = Path(__file__).resolve().parent


class RefCollector(HTMLParser):
    """收集 href/src 引用。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.refs: list[tuple[str, str]] = []  # (tag, value)

    def handle_starttag(self, tag, attrs):
        d = {k.lower(): (v or "") for k, v in attrs}
        for a in ("href", "src"):
            if d.get(a):
                self.refs.append((tag, d[a].strip()))


def run_gate(script: str, project: Path, extra: list[str] | None = None):
    """子进程重跑子门，返回 (exit_code, 报告dict)。"""
    r = subprocess.run(
        [sys.executable, str(HERE / script), "--project", str(project), "--json"] + (extra or []),
        capture_output=True, text=True)
    try:
        report = json.loads(r.stdout)
    except json.JSONDecodeError:
        report = {"gate": script, "pass": False, "summary": {},
                  "violations": [{"file": script, "kind": "脚本异常",
                                  "value": (r.stderr or r.stdout)[:200],
                                  "hint": "子门脚本未能产出报告"}]}
    return r.returncode, report


def deliverable_checks(project: Path, mf: dict) -> list[dict]:
    bad: list[dict] = []
    for need in ("SPEC.md", "assets/tokens.css", "index.html"):
        if not (project / need).is_file():
            bad.append({"file": need, "kind": "交付物缺失", "value": need,
                        "hint": "必需文件不存在"})
    pages = sorted((project / "pages").glob("**/*.html")) if (project / "pages").is_dir() else []
    n_manifest = sum(1 + len(pg.get("states", [])) for pg in mf.get("pages", []))
    if len(pages) != n_manifest:
        bad.append({"file": "pages/", "kind": "页数不符",
                    "value": f"manifest {n_manifest} vs 实际 {len(pages)}",
                    "hint": "以 pages-manifest.json 为准"})
    # 外链与本地资源存在性 + 单页体积
    targets = ([project / "index.html"] if (project / "index.html").is_file() else []) + pages
    for f in targets:
        rel = f.relative_to(project).as_posix()
        if f.stat().st_size > MAX_HTML_BYTES:
            bad.append({"file": rel, "kind": "单页超限",
                        "value": f"{f.stat().st_size} 字节 > 500KB",
                        "hint": "检查是否塞了不该塞的内容"})
        c = RefCollector()
        c.feed(f.read_text(encoding="utf-8", errors="replace"))
        for tag, raw in c.refs:
            if raw.startswith(("mailto:", "tel:", "data:", "#")):
                continue
            if raw.startswith(EXTERNAL):
                bad.append({"file": rel, "kind": "外部引用", "value": f"<{tag}> {raw}",
                            "hint": "原型必须资源本地化（断网演示）"})
                continue
            path_part = raw.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            from urllib.parse import unquote
            target = (f.parent / unquote(path_part)).resolve()
            try:
                target.relative_to(project)
            except ValueError:
                continue
            if not target.is_file():
                bad.append({"file": rel, "kind": "本地资源缺失",
                            "value": raw, "hint": "引用的文件不存在"})
    return bad


def main() -> int:
    ap = argparse.ArgumentParser(description="G5 交付前总验收")
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    project = Path(args.project).resolve()

    mf_path = project / "pages-manifest.json"
    mf = json.loads(mf_path.read_text(encoding="utf-8")) if mf_path.is_file() else {}

    codes: dict[str, int] = {}
    reports: dict[str, dict] = {}
    for gate, script in (("g1", "check_tokens.py"), ("g3", "check_links.py"),
                         ("g4", "check_contrast.py"), ("g6", "check_details.py"),
                         ("g7", "check_visual_review.py")):
        codes[gate], reports[gate] = run_gate(script, project)

    # 家族保真（读 SPEC 的「家族 | F3」行）
    spec = project / "SPEC.md"
    fam = None
    if spec.is_file():
        m = re.search(r"\|\s*家族\s*\|\s*(F[0-9])", spec.read_text(encoding="utf-8"))
        fam = m.group(1) if m else None
    if fam:
        codes["g1f"], reports["g1f"] = run_gate("check_tokens.py", project, ["--family", fam])
    else:
        reports["g1f"] = {"pass": "skipped", "summary": {"reason": "SPEC 未声明家族"}}

    shots = project / "qa" / "screenshots"
    g8_state = "skipped"
    if shots.is_dir() and any(shots.iterdir()):
        codes["g8"], reports["g8"] = run_gate("check_pixels.py", project)
        g8_state = "pass" if codes["g8"] == 0 else "fail"
    g2_state = "skipped"
    if shots.is_dir() and any(shots.iterdir()):
        codes["g2"], reports["g2"] = run_gate("check_screens.py", project)
        g2_state = "pass" if codes["g2"] == 0 else "fail"

    # 5.5 待确认零残留：SPEC/页面正文不得残留未决标记
    import re as _re
    leftovers = []
    scan_targets = [p for p in [project / "SPEC.md", project / "index.html"] if p.is_file()]
    scan_targets += sorted((project / "pages").glob("**/*.html")) if (project / "pages").is_dir() else []
    for f in scan_targets:
        text = f.read_text(encoding="utf-8", errors="replace")
        for kw in ("待确认", "待定", "待拍板", "TODO"):
            if kw in text:
                leftovers.append({"file": f.relative_to(project).as_posix(), "kind": "待确认残留",
                                  "value": kw, "hint": "未决事项须会话问掉或登记待办，正文零残留"})
                break
    deliverables = deliverable_checks(project, mf)
    deliverables += leftovers
    g7s = reports.get("g7", {}).get("summary", {})
    g7_min = g7s.get("effective_min")
    if g7_min is not None and g7_min < 3:
        codes["g7"] = 1
    sub_ok = (codes.get("g1f", 0) == 0 and codes.get("g1") == 0 and codes.get("g3") == 0
              and codes.get("g4") == 0 and codes.get("g6") == 0 and codes.get("g7") == 0 and codes.get("g8", 0) == 0 and g2_state != "fail")
    ok = sub_ok and not deliverables

    summary = {
        "g1": reports["g1"].get("pass", False),
        "g2": g2_state,
        "g3": reports["g3"].get("pass", False),
        "g4": reports.get("g4", {}).get("pass", False),
        "g6": reports.get("g6", {}).get("pass", False),
        "g7": reports.get("g7", {}).get("pass", False),
        "g8": reports.get("g8", {}).get("pass", "skipped") if "g8" in reports else "skipped",
        "deliverables": not deliverables,
        "skipped": ([("G2（无截图，视觉门未执行）" if g2_state == "skipped" else None),
                     ("G8（无截图，像素门未执行）" if g8_state == "skipped" else None)]),

        "violations": len(deliverables),
    }
    report = {"gate": "G5", "pass": ok, "summary": summary,
              "violations": deliverables,
              "sub_reports": {k: v.get("summary") for k, v in reports.items()}}
    out = project / "qa" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "final-gate.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["[G5] 验收单"]
    g1s = reports["g1"].get("summary", {})
    g3s = reports["g3"].get("summary", {})
    lines.append(f"  G1 规范符合性 : {'PASS' if summary['g1'] else 'FAIL'}"
                 f"（violations={g1s.get('violations', '?')}）")
    if "g1f" in reports:
        st = reports["g1f"].get("pass")
        label = "PASS" if st is True else ("SKIPPED" if st == "skipped" else "FAIL")
        lines.append(f"  G1f 家族保真  : {label}（{fam or reports['g1f'].get('summary', {}).get('reason', '')}）")
    lines.append(f"  G3 交互完整性 : {'PASS' if summary['g3'] else 'FAIL'}"
                 f"（violations={g3s.get('violations', '?')}）")
    g4s = reports.get("g4", {}).get("summary", {})
    lines.append(f"  G4 可访问性   : {'PASS' if summary['g4'] else 'FAIL'}"
                 f"（violations={g4s.get('violations', '?')}）")
    g6s = reports.get("g6", {}).get("summary", {})
    lines.append(f"  G6 细节规则   : {'PASS' if summary.get('g6') else 'FAIL'}"
                 f"（violations={g6s.get('violations', '?')}）")
    g7s = reports.get("g7", {}).get("summary", {})
    lines.append(f"  G7 视觉评审   : {'PASS' if summary.get('g7') else 'FAIL'}"
                 f"（violations={g7s.get('violations', '?')}）")
    if "g8" in reports:
        g8s = reports.get("g8", {}).get("summary", {})
        lines.append(f"  G8 像素检查   : {'PASS' if reports['g8'].get('pass') else 'FAIL'}"
                     f"（violations={g8s.get('violations', '?')}）")
    if g2_state == "skipped":
        lines.append("  G2 截图验证   : SKIPPED（qa/screenshots 为空，视觉门未执行）")
    else:
        g2s = reports.get("g2", {}).get("summary", {})
        lines.append(f"  G2 截图验证   : {'PASS' if g2_state == 'pass' else 'FAIL'}"
                     f"（violations={g2s.get('violations', '?')}）")
    lines.append(f"  交付物检查    : {'PASS' if not deliverables else 'FAIL'}"
                 f"（差异 {len(deliverables)}）")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("\n".join(lines))
        for v in deliverables[:20]:
            print(f"  {v['file']}  [{v['kind']}] {v['value']}  {v['hint']}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
