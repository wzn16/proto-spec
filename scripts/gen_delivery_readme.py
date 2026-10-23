#!/usr/bin/env python3
"""生成项目级交付 README：页面地图 + 质量门摘要 + 已知占位声明。

用法:
  python3 gen_delivery_readme.py --project <项目目录> [--out README.md]

读取 pages-manifest.json / SPEC.md / qa/reports/*.json，生成面向甲方与演示者的人读 README。
不修改任何其它文件；已存在 README 时默认拒绝覆盖（--force 显式覆盖）。
退出码: 0=成功  1=失败  2=用法错误
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def read_manifest(p: Path) -> dict:
    f = p / "pages-manifest.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}


def read_spec_meta(p: Path) -> dict:
    """从 SPEC.md 提取版本与状态（§0 表格）。"""
    f = p / "SPEC.md"
    meta = {"version": "—", "status": "—", "family": "—"}
    if not f.is_file():
        return meta
    text = f.read_text(encoding="utf-8")
    m = re.search(r"\|\s*版本\s*\|\s*([^|\n]+)\|", text)
    if m:
        meta["version"] = m.group(1).strip()
    m = re.search(r"\|\s*状态\s*\|\s*([^|\n]+)\|", text)
    if m:
        meta["status"] = m.group(1).strip()
    m = re.search(r"家族\s*id\s*[：:]\s*([F\d]+)", text)
    if m:
        meta["family"] = m.group(1)
    return meta


def read_reports(p: Path) -> dict:
    out = {}
    d = p / "qa" / "reports"
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
            out[f.stem] = r
        except Exception:
            continue
    return out


def fmt_report(name: str, r: dict) -> tuple[str, str]:
    s = r.get("summary", {}) or {}
    ok = r.get("pass")
    cells = ", ".join(f"{k}={v}" for k, v in s.items())
    return ("PASS" if ok else "FAIL"), cells or "—"


def main() -> int:
    ap = argparse.ArgumentParser(description="生成交付 README")
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", default="README.md")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    project = Path(args.project).resolve()
    out_path = project / args.out
    if out_path.exists() and not args.force:
        print(f"[README] 已存在 {out_path.name}，如需覆盖请加 --force", file=sys.stderr)
        return 2

    mf = read_manifest(project)
    meta = read_spec_meta(project)
    reports = read_reports(project)
    notes = reports.get("notes", {}).get("notes", [])

    lines = [f"# {mf.get('project', '原型项目')} · 交付包", ""]
    lines.append("> 打开方式：双击 `index.html`（建议 Chrome / Edge）。全程离线，无外部请求。")
    lines.append("> **页面数据均为虚构示例**，用于演示与评审，不代表真实业务数据。")
    lines.append("")
    lines.append(f"- 版本：{meta['version']}（{meta['status']}）")
    lines.append(f"- 美学家族：{meta['family']}")
    lines.append("")

    lines.append("## 页面地图")
    lines.append("")
    lines.append("| 页面 | 路径 | 状态页 |")
    lines.append("| --- | --- | --- |")
    for pg in mf.get("pages", []):
        states = "、".join(pg.get("states") or []) or "—"
        title = (pg.get("title") or "").split(" | ")[0]
        lines.append(f"| {title} | `{pg.get('path')}` | {states} |")
    lines.append("")

    if reports:
        lines.append("## 质量门摘要（引报告计数字段）")
        lines.append("")
        lines.append("| 门 | 结果 | 关键计数 |")
        lines.append("| --- | --- | --- |")
        order = ["g1", "g3", "g4", "g2", "final-gate"]
        for key in order:
            if key in reports:
                verdict, cells = fmt_report(key, reports[key])
                lines.append(f"| {key.upper()} | {verdict} | {cells} |")
        lines.append("")

    lines.append("## 已知占位与说明")
    lines.append("")
    if notes:
        lines.append(f"- 页面内交接注记 {len(notes)} 条（明细见 `qa/reports/notes.json`）。")
    skipped = (reports.get("final-gate", {}).get("summary", {}) or {}).get("skipped") or []
    for s in skipped:
        lines.append(f"- {s}")
    if not notes and not skipped:
        lines.append("- 无（全部页面状态与交互已按规范生成）。")
    lines.append("")
    lines.append("## 交付物")
    lines.append("")
    lines.append("- `index.html` 站点地图（演示入口）")
    lines.append("- `pages/` 全部原型页面与状态页")
    lines.append("- `SPEC.md` 冻结设计规范 + `pages-manifest.json` 页面清单")
    lines.append("- `qa/` 质量门报告与截图证据")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[README] 已生成 {out_path.name}（页面 {len(mf.get('pages', []))}，报告 {len(reports)}，注记 {len(notes)}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
