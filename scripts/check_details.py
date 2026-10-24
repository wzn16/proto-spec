#!/usr/bin/env python3
"""细节机检（G6）：重复动作 / 布局硬编码 / KPI 语义。

用法: python3 check_details.py --project <目录> [--json]
退出码: 0=通过 1=有违规 2=用法错误
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

KPI_BAN = ["字段数", "层级数", "模块数", "数据列", "节点数", "数据集", "列数"]
RE_HREF = re.compile(r'href="([^"#]+\.html[^"]*)"')
RE_MSG = re.compile(r'data-message="([^"]+)"')
RE_KPI = re.compile(r'class="c-kpi__label"[^>]*>([^<]+)<')
RE_MAXW = re.compile(r'max-width\s*:\s*\d+px')
RE_INLINE_W = re.compile(r'style="[^"]*width\s*:\s*\d+px')


def check_page(path: Path, root: Path):
    html = path.read_text(encoding="utf-8")
    name = path.relative_to(root).as_posix()
    out = []
    # 表格行内的行级动作不算重复入口：先剔除 tr 段
    stripped = re.sub(r"<tr[\s\S]*?</tr>", "", html)
    stripped = re.sub(r"<nav[\s\S]*?</nav>", "", stripped)
    for pattern, kind, hint in [
        (RE_HREF, "重复链接", "同一锚点在同页出现多次：合并为一个入口"),
        (RE_MSG, "重复动作", "同一提示动作重复：动作应只出现一次"),
    ]:
        seen = {}
        for m in pattern.finditer(stripped):
            v = m.group(1)
            if v.startswith("javascript:"):
                continue
            seen[v] = seen.get(v, 0) + 1
        for v, n in seen.items():
            if n >= 4:  # 导航/页脚复用允许 3 次，4 次以上视为重复入口
                out.append({"file": name, "kind": kind, "value": f"{v} ×{n}", "hint": hint})
    for m in RE_MAXW.finditer(html):
        out.append({"file": name, "kind": "布局硬编码", "value": m.group(0), "hint": "表格/容器不要用 max-width 限宽，改列宽"})
    for m in RE_INLINE_W.finditer(html):
        out.append({"file": name, "kind": "布局硬编码", "value": m.group(0)[:40], "hint": "内联像素宽度不可随视口变化，改用类"})
    # 主按钮数量：一页最多 2 个实底主按钮（页头 + 区块头）
    primary = len(re.findall(r'class="c-btn(?![^"]*c-btn--)[^"]*"', html))
    primary -= len(re.findall(r'<a class="c-btn(?![^"]*c-btn--)[^"]*"', html))  # 文字链不算
    if primary > 2:
        out.append({"file": name, "kind": "主操作超量", "value": f"{primary} 个实底按钮", "hint": "一页最多 2 个主按钮，其余降为 secondary/text"})

    # 列表/表格页必须有空态
    if ("c-data-table" in html or "p-table" in html) and "c-empty" not in html:
        out.append({"file": name, "kind": "缺空态", "value": "无 c-empty", "hint": "列表/表格页必须有三态之一的无数据表达"})

    # 宽表冻结首列
    if re.search(r"<th[^>]*>[^<]*编码", html) and len(re.findall(r"<th", html)) > 8 and "pin-first" not in html:
        out.append({"file": name, "kind": "宽表未冻结", "value": ">8 列且无 pin-first", "hint": "列数 >8 时启用 c-data-table--pin-first"})

    for m in RE_KPI.finditer(html):
        label = m.group(1).strip()
        if any(b in label for b in KPI_BAN):
            out.append({"file": name, "kind": "KPI 语义", "value": label, "hint": "KPI 要是可决策指标；元信息放页头副标题"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    pages = sorted([p for p in root.rglob("*.html") if "qa" not in p.parts])
    all_v = []
    for p in pages:
        all_v += check_page(p, root)
    report = {"gate": "G6", "pass": not all_v,
              "summary": {"pages": len(pages), "violations": len(all_v)},
              "violations": all_v}
    outdir = root / "qa" / "reports"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "g6-details.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif all_v:
        print(f"[G6] FAIL：{len(all_v)} 处（{len(pages)} 页）")
        for v in all_v[:12]:
            print(f"  {v['file']}  [{v['kind']}] {v['value']}  → {v['hint']}")
    else:
        print(f"[G6] 通过：{len(pages)} 页，无重复动作/布局硬编码/KPI 语义问题")
    return 0 if not all_v else 1


if __name__ == "__main__":
    sys.exit(main())
