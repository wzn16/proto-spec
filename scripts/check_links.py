#!/usr/bin/env python3
"""G3 交互完整性检查：死链=0、裸 # =0、外链=0、manifest↔文件↔索引三方对账。

用法:
  python3 check_links.py --project <项目目录>

退出码: 0=通过  1=未通过  2=用法错误
报告:   <project>/qa/reports/g3.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

LINK_ATTRS = {"a": "href", "area": "href", "form": "action"}
RES_TAGS = {"img", "script", "link", "iframe", "source", "video", "audio"}
EXTERNAL = ("http://", "https://", "//")


class Collector(HTMLParser):
    """收集链接、资源引用、id 与 title。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[int, str, str]] = []
        self.resources: list[tuple[int, str, str]] = []
        self.ids: set[str] = set()
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        d = {k.lower(): (v or "") for k, v in attrs}
        if d.get("id"):
            self.ids.add(d["id"])
        attr = LINK_ATTRS.get(tag)
        if attr and d.get(attr):
            self.links.append((line, tag, d[attr].strip()))
        if tag in RES_TAGS:
            for a in ("src", "href"):
                if d.get(a):
                    self.resources.append((line, tag, d[a].strip()))
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def scan(f: Path) -> Collector:
    c = Collector()
    c.feed(f.read_text(encoding="utf-8", errors="replace"))
    return c


def resolve_link(base_file: Path, raw: str, project: Path):
    """解析为 (目标绝对路径或 None=越界, fragment)。"""
    path_part, _, frag = raw.partition("#")
    if not path_part:
        return base_file.resolve(), frag
    target = base_file.parent / unquote(path_part)
    try:
        resolved = target.resolve()
        resolved.relative_to(project)
    except ValueError:
        return None, frag
    return resolved, frag


def main() -> int:
    ap = argparse.ArgumentParser(description="G3 交互完整性检查")
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    project = Path(args.project).resolve()

    index = project / "index.html"
    pages = sorted(project.glob("pages/**/*.html"))
    violations: list[dict] = []
    data: dict = {}

    def add(file: str, line: int, kind: str, value: str, hint: str) -> None:
        violations.append({"file": file, "line": line, "type": kind,
                           "value": value[:100], "hint": hint})

    # ---- 链接与资源扫描 ----
    index_page_links: set[str] = set()
    targets = ([index] if index.is_file() else []) + pages
    for f in targets:
        rel = f.relative_to(project).as_posix()
        c = scan(f)
        for line, tag, raw in c.links:
            if raw.startswith(EXTERNAL):
                add(rel, line, "外链", raw, "原型禁止外部 http(s) 链接")
                continue
            if raw == "#":
                add(rel, line, "裸#占位", raw, "占位交互必须有真实目标")
                continue
            target, frag = resolve_link(f, raw, project)
            if target is None:
                add(rel, line, "越界链接", raw, "链接目标越出项目根")
                continue
            if raw.startswith("#"):
                if frag and frag not in c.ids:
                    add(rel, line, "死锚点", raw, f"同页找不到 id={frag}")
                continue
            if not target.is_file():
                add(rel, line, "死链", raw, "目标文件不存在")
                continue
            if frag:
                tc = scan(target)
                if frag not in tc.ids:
                    add(rel, line, "死锚点", raw, f"目标页找不到 id={frag}")
            if f == index:
                tp = target.relative_to(project).as_posix()
                if tp.startswith("pages/"):
                    index_page_links.add(tp)
        for line, tag, raw in c.resources:
            if raw.startswith(EXTERNAL):
                add(rel, line, "外链资源", f"<{tag}> {raw}",
                    "原型必须资源本地化（G5 也会拦）")

    # ---- 三方对账 ----
    mf_path = project / "pages-manifest.json"
    expected: set[str] = set()
    titles: dict[str, str] = {}
    if mf_path.is_file():
        try:
            data = json.loads(mf_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            add("pages-manifest.json", 0, "manifest 解析失败", str(e), "修复 JSON")
            data = {"pages": []}
        for pg in data.get("pages", []):
            p = Path(pg.get("path", ""))
            if not p.as_posix():
                continue
            expected.add(p.as_posix())
            titles[p.as_posix()] = pg.get("title", "")
            for st in pg.get("states", []):
                expected.add(p.with_name(f"{p.stem}.{st}.html").as_posix())
    else:
        add("pages-manifest.json", 0, "manifest 缺失", "pages-manifest.json",
            "G3 对账基准不存在")

    actual = {p.relative_to(project).as_posix() for p in pages}
    for miss in sorted(expected - actual):
        add("pages/", 0, "缺页", miss, "manifest 声明了但文件不存在")
    for extra in sorted(actual - expected):
        add(extra, 0, "多页", extra, "文件存在但未登记 manifest")
    for orphan in sorted(expected - index_page_links):
        add("index.html", 0, "孤儿页", orphan, "manifest 有但站点地图未链接")
    for ghost in sorted(index_page_links - expected):
        add("index.html", 0, "索引多链", ghost, "站点地图链接了清单外文件")

    # ---- 3.6 菜单一致性：侧边栏只准链接 nav != false 的页面 ----
    nav_flag = {Path(pg.get("path", "")).as_posix(): bool(pg.get("nav", True))
                for pg in (data.get("pages", []) if isinstance(data, dict) else [])}
    for f in pages:
        text = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'<nav class="l-sidebar">(.*?)</nav>', text, re.S)
        if not m:
            continue
        rel = f.relative_to(project).as_posix()
        for href in re.findall(r'href="([^"#]+)"', m.group(1)):
            target = (f.parent / unquote(href)).resolve()
            try:
                trel = target.relative_to(project).as_posix()
            except ValueError:
                continue
            if trel in nav_flag and nav_flag[trel] is False:
                add(rel, 0, "菜单越权", href,
                    "nav=false 的隐藏页（如表单）不得进侧边栏菜单，应由台账按钮触发")

    # ---- title 一致性 ----
    for rel, want in sorted(titles.items()):
        f = project / rel
        if not f.is_file():
            continue
        got = scan(f).title.strip()
        if not got:
            add(rel, 0, "title 缺失", "<title> 为空", "每页必须有非空 title")
        elif got != want.strip():
            add(rel, 0, "title 不一致", got, f"manifest 期望：{want}")

    report = {
        "gate": "G3",
        "pass": not violations,
        "summary": {"pages": len(pages), "violations": len(violations)},
        "violations": violations,
    }
    out_dir = project / "qa" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "g3.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif violations:
        print(f"[G3] FAIL：{len(violations)} 处差异（pages {len(pages)} 页）")
        for v in violations[:40]:
            print(f"  {v['file']}:{v['line']}  [{v['type']}] {v['value']}  {v['hint']}")
        if len(violations) > 40:
            print(f"  …其余见 qa/reports/g3.json")
    else:
        print(f"[G3] 通过：{len(pages)} 页，死链/占位/外链/对账差异均为 0")
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
