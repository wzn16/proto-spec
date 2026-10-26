#!/usr/bin/env python3
"""G1 规范符合性检查：页面只准引用 tokens，不准发明值。

用法:
  python3 check_tokens.py --project <项目目录> [--page pages/xxx.html]

退出码: 0=通过  1=存在违规  2=用法错误
报告:   <project>/qa/reports/g1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# ---- 检查口径常量（与 references/qa-gates.md 保持一致） ----
COLOR_PROPS = {
    "color", "background", "background-color", "background-image",
    "fill", "stroke", "outline", "outline-color",
    "text-decoration-color", "caret-color", "column-rule-color",
}
SPACING_PREFIX = ("padding", "margin")
SPACING_PROPS = {"gap", "row-gap", "column-gap"}
FONT_SIZES = {12.0, 13.0, 14.0, 16.0, 20.0, 24.0, 30.0}
RADII = {6.0, 8.0, 12.0, 9999.0}
SPACING = {4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 32.0, 48.0}
EXCEPTIONS = {"0", "1px", "-1px", "100%", "50%", "auto", "none", "transparent",
              "currentcolor", "inherit", "initial", "unset"}
NAMED_COLORS = {"white", "black", "red", "green", "blue", "gray", "grey",
                "orange", "yellow", "silver", "purple", "pink", "brown"}
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB_RE = re.compile(r"rgba?\(", re.I)
VAR_RE = re.compile(r"var\(\s*(--[\w-]+)")

SCAN_GLOBS = ["index.html", "pages/**/*.html", "templates/*.html",
              "assets/snippets/*.html"]


def strip_css_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", "", text, flags=re.S)


def parse_css_decls(css: str, base_line: int):
    """把 CSS 文本拆成 (行号, 属性, 值) 列表；行号相对文件尽力对齐。"""
    css = strip_css_comments(css)
    blocks = list(re.finditer(r"\{([^{}]*)\}", css))
    segments = [(m.start(1), m.group(1)) for m in blocks] or [(0, css)]
    out = []
    for offset, segment in segments:
        for m in re.finditer(r"(--[\w-]+|[A-Za-z][\w-]*)\s*:\s*([^;]+)", segment):
            line = base_line + css.count("\n", 0, offset + m.start())
            out.append((line, m.group(1).lower(), m.group(2).strip()))
    return out


class PageCollector(HTMLParser):
    """收集页面里的样式声明、资源引用、id 与 title，带行号。"""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.decls: list[tuple[int, str, str]] = []
        self.refs: list[tuple[int, str, str]] = []  # (line, attr, value)
        self.css_links: list[str] = []
        self.ids: set[str] = set()
        self.title = ""
        self._style_buf: list[str] | None = None
        self._style_line = 0
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        line = self.getpos()[0]
        d = {}
        for k, v in attrs:
            d[k.lower()] = v or ""
        if tag == "style":
            self._style_buf = []
            self._style_line = line
        elif tag == "title":
            self._in_title = True
        if d.get("id"):
            self.ids.add(d["id"])
        if d.get("style"):
            self.decls.extend(parse_css_decls(d["style"], line))
        for attr in ("href", "src", "action"):
            if attr in d and d[attr]:
                self.refs.append((line, attr, d[attr].strip()))
        if tag == "link" and "stylesheet" in (d.get("rel") or "").lower():
            if d.get("href"):
                self.css_links.append(d["href"])

    def handle_endtag(self, tag):
        if tag == "style" and self._style_buf is not None:
            self.decls.extend(
                parse_css_decls("\n".join(self._style_buf), self._style_line))
            self._style_buf = None
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        elif self._style_buf is not None:
            self._style_buf.append(data)


def load_tokens(tokens_path: Path):
    """解析 tokens.css：变量定义表 + 全部字面 hex（供最近色建议）。"""
    text = strip_css_comments(tokens_path.read_text(encoding="utf-8"))
    defs: dict[str, str] = {}
    for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", text):
        defs[m.group(1)] = m.group(2).strip()
    hexes = {h.lower() for h in HEX_RE.findall(text)}
    return defs, hexes


def norm_hex(h: str) -> str:
    h = h.lower()
    if len(h) == 4:  # #abc -> #aabbcc
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def hex_to_rgb(h: str):
    h = norm_hex(h)[1:]
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def px_of(part: str):
    m = re.fullmatch(r"(\d+(?:\.\d+)?)px", part.strip())
    return float(m.group(1)) if m else None


def nearest(values, v):
    return min(values, key=lambda s: abs(s - v))


def nearest_hex(hexes, h: str):
    try:
        rgb = hex_to_rgb(h)
    except Exception:
        return ""
    best, dist = "", 1 << 30
    for cand in hexes:
        try:
            c = hex_to_rgb(cand)
        except Exception:
            continue
        d = sum((a - b) ** 2 for a, b in zip(rgb, c))
        if d < dist:
            best, dist = cand, d
    return best


def check_value(file: str, line: int, prop: str, value: str,
                defs: dict, hexes) -> list[dict]:
    """对一条 CSS 声明做 G1 判定，返回违规列表。"""
    bad: list[dict] = []

    def add(msg: str, nearest: str = "", hint: str = "") -> None:
        bad.append({"file": file, "line": line, "property": prop,
                    "value": value[:80], "nearestToken": nearest,
                    "hint": hint or msg})

    low = value.lower()

    # 全局：calc / 自定义属性定义 / 未定义变量 / --g-* 直用
    if "calc(" in low:
        add("禁用 calc()", hint="需要新值时先回 tokens.css 建档位")
        return bad
    if prop.startswith("--"):
        add("页面不得定义 CSS 变量", hint="变量只许在 tokens.css 定义")
        return bad
    for ref in VAR_RE.findall(value):
        if ref not in defs:
            add(f"引用未定义变量 {ref}", hint="变量必须在 tokens.css 定义")
        elif ref.startswith("--g-"):
            add(f"页面直接使用了基元层 {ref}", hint="改用对应的 --s-* 语义变量")

    # 圆角档位（须先于 border* 颜色分支判定）
    if prop == "border-radius":
        for part in value.split():
            p = part.lower()
            if p in EXCEPTIONS or VAR_RE.search(part):
                continue
            v = px_of(part)
            if v is None or v not in RADII:
                near = nearest(RADII, v) if v is not None else ""
                add(f"圆角 {part} 不在档位",
                    nearest=f"--s-radius-* ({near:g}px)" if near else "--s-radius-*",
                    hint="档位：6/8/12/9999px 或 50%，请用 var(--s-radius-*)")
        return bad

    # 颜色类：裸色值违规（含渐变、阴影里的字面色）
    if prop in COLOR_PROPS or prop.startswith("border") or prop.startswith("background"):
        if "url(" not in low:  # 背景图资源交给 G3/G5 管
            for m in HEX_RE.findall(value):
                add("裸色值（必须用 tokens 变量）",
                    nearest=nearest_hex(hexes, m), hint=f"是否应为 {nearest_hex(hexes, m)}？")
            for m in RGB_RE.finditer(value):
                add("裸色值 rgb()/rgba()（必须用 tokens 变量）")
            for w in re.findall(r"[a-z]+", low):
                if w in NAMED_COLORS:
                    add(f"裸色值单词 {w}（必须用 tokens 变量）")
                    break
        return bad

    if prop == "font-size":
        for part in value.split():
            p = part.lower()
            if p in EXCEPTIONS or VAR_RE.search(part):
                continue
            v = px_of(part)
            if v is None or v not in FONT_SIZES:
                near = nearest(FONT_SIZES, v) if v is not None else ""
                add(f"字号 {part} 不在档位",
                    nearest=f"--s-fs-* ({near:g}px)" if near else "--s-fs-*",
                    hint=f"档位：12/13/14/16/20/24/30，请用 var(--s-fs-*)")
        return bad

    if prop == "border-radius":
        for part in value.split():
            p = part.lower()
            if p in EXCEPTIONS or VAR_RE.search(part):
                continue
            v = px_of(part)
            if v is None or v not in RADII:
                near = nearest(RADII, v) if v is not None else ""
                add(f"圆角 {part} 不在档位",
                    nearest=f"--s-radius-* ({near:g}px)" if near else "--s-radius-*",
                    hint="档位：6/8/12/9999px 或 50%，请用 var(--s-radius-*)")
        return bad

    if prop.startswith(SPACING_PREFIX) or prop in SPACING_PROPS:
        for part in re.split(r"\s+", value.strip()):
            p = part.lower()
            if not p or p in EXCEPTIONS or VAR_RE.search(part):
                continue
            v = px_of(part)
            if v is None or v not in SPACING:
                near = nearest(SPACING, v) if v is not None else ""
                add(f"间距 {part} 不在档位",
                    nearest=f"var(--s-space-*) ({near:g}px)" if near else "--s-space-*",
                    hint="档位：4/8/12/16/20/24/32/48px")
        return bad

    if prop == "box-shadow":
        if low != "none" and not VAR_RE.search(value):
            add("阴影必须用 var(--s-shadow-card/overlay)")
        return bad

    return bad


def collect_files(project: Path, single: str | None):
    """返回待扫描 HTML 文件列表。"""
    if single:
        f = (project / single).resolve()
        if not f.is_file():
            raise FileNotFoundError(single)
        return [f]
    files: list[Path] = []
    for pattern in SCAN_GLOBS:
        files.extend(sorted(project.glob(pattern)))
    seen, uniq = set(), []
    for f in files:
        rp = f.resolve()
        if rp not in seen:
            seen.add(rp)
            uniq.append(f)
    return uniq


def family_fidelity(project: Path, family_id: str, defs: dict):
    """家族保真检查：项目 tokens 的身份特征槽位 diff 必须为 0。

    家族登记值存于 references/families/<id>-*.md 的 ```json family-manifest``` 块。
    返回 (violations, checked_count)。
    """
    import glob as _glob
    fam_dir = Path(__file__).resolve().parent.parent / "references" / "families"
    files = [f for f in fam_dir.glob(f"{family_id}-*.md")]
    if not files:
        return [{"file": f"references/families/{family_id}-*", "kind": "家族未建档",
                 "value": family_id, "hint": "找不到该家族的定义文件"}], 0
    text = files[0].read_text(encoding="utf-8")
    m = re.search(r"```json\s+family-manifest\s*\n(\{.*?\})\s*```", text, re.S)
    if not m:
        return [{"file": files[0].name, "kind": "manifest 缺失", "value": family_id,
                 "hint": "家族文件缺少 family-manifest JSON 块"}], 0
    manifest = json.loads(m.group(1))
    violations = []

    def resolve_slot(name: str, d: dict, depth: int = 0) -> str | None:
        v = d.get(name)
        if v is None or depth > 4:
            return v
        m2 = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", v.strip())
        return resolve_slot(m2.group(1), d, depth + 1) if m2 else v.strip()

    violations = []
    for slot, registered in manifest.get("identity", {}).items():
        actual = resolve_slot(slot, defs)
        if actual is None:
            violations.append({"file": f"family:{family_id}", "line": 0, "kind": "身份槽位缺失",
                               "value": slot, "hint": f"登记值 {registered}，项目 tokens 未定义"})
            continue
        norm = lambda s: re.sub(r"\s+", " ", s.strip().lower())
        if norm(actual) != norm(registered):
            violations.append({"file": f"family:{family_id}", "line": 0, "kind": "身份漂移",
                               "value": f"{slot}: {actual}",
                               "hint": f"登记值 {registered}——身份特征不得被项目覆盖，冲突请改选家族"})
    return violations, len(manifest.get("identity", {}))


def dangling_refs(project: Path) -> list[dict]:
    """tokens.css 内 var(--x) 引用必须能在本文件定义。"""
    f = project / "assets" / "tokens.css"
    if not f.is_file():
        return []
    text = re.sub(r"/\*.*?\*/", "", f.read_text(encoding="utf-8"), flags=re.S)
    defined = set(re.findall(r"(--[\w-]+)\s*:", text))
    used = set(re.findall(r"var\(\s*(--[\w-]+)", text))
    return [{"file": "assets/tokens.css", "line": 0, "property": "var()", "kind": "悬空变量引用",
             "value": v, "hint": "该变量在 tokens.css 未定义（可能落在 :root 之外）"}
            for v in sorted(used - defined)]


def main() -> int:
    ap = argparse.ArgumentParser(description="G1 规范符合性检查")
    ap.add_argument("--project", required=True)
    ap.add_argument("--page", default=None, help="只查单个文件（相对项目根）")
    ap.add_argument("--family", default=None, help="家族保真检查（如 F3），与 --page 互斥")
    ap.add_argument("--json", action="store_true", help="只输出 JSON")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    tokens = project / "assets" / "tokens.css"
    if not tokens.is_file():
        print(f"[G1] 找不到 {tokens}", file=sys.stderr)
        return 2
    defs, hexes = load_tokens(tokens)
    dangling = dangling_refs(project)

    if args.family:
        violations, n_slots = family_fidelity(project, args.family, defs)
        report = {"gate": "G1-family", "pass": not violations,
                  "summary": {"family": args.family, "slots": n_slots, "violations": len(violations)},
                  "violations": violations}
        out = project / "qa" / "reports"
        out.mkdir(parents=True, exist_ok=True)
        (out / "g1-family.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif violations:
            print(f"[G1-family] FAIL：{args.family} 身份特征漂移 {len(violations)} 处")
            for v in violations:
                print(f"  {v['value']}  {v['hint']}")
        else:
            print(f"[G1-family] 通过：{args.family} 身份特征 {n_slots} 槽位 diff=0")
        return 0 if not violations else 1

    try:
        targets = collect_files(project, args.page)
    except FileNotFoundError as e:
        print(f"[G1] 文件不存在：{e}", file=sys.stderr)
        return 2

    violations: list[dict] = []
    n_files, n_decls = 0, 0
    for f in targets:
        rel = f.relative_to(project).as_posix()
        n_files += 1
        c = PageCollector()
        c.feed(f.read_text(encoding="utf-8", errors="replace"))
        n_decls += len(c.decls)
        for line, prop, value in c.decls:
            violations.extend(check_value(rel, line, prop, value, defs, hexes))
        # 页面 <link> 引用的本地 CSS 一并扫描（tokens.css 除外）
        for href in c.css_links:
            if href.startswith(("http://", "https://", "//")):
                continue
            css_path = (f.parent / href.split("#")[0].split("?")[0]).resolve()
            try:
                css_path.relative_to(project)
            except ValueError:
                continue
            if not css_path.is_file() or css_path == tokens:
                continue
            css_rel = css_path.relative_to(project).as_posix()
            text = css_path.read_text(encoding="utf-8", errors="replace")
            for line, prop, value in parse_css_decls(text, 1):
                n_decls += 1
                violations.extend(
                    check_value(css_rel, line, prop, value, defs, hexes))

    violations += dangling

    report = {

        "gate": "G1",
        "pass": not violations,
        "summary": {"files": n_files, "declarations": n_decls,
                    "violations": len(violations)},
        "violations": violations,
    }
    out_dir = project / "qa" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "g1.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif violations:
        print(f"[G1] FAIL：{len(violations)} 处违规（{n_files} 文件 / {n_decls} 声明）")
        for v in violations[:40]:
            near = v.get("nearestToken") or "-"
            print(f"  {v['file']}:{v['line']}  {v.get('property', '-')}: {v.get('value', '')}"
                  f"  → {near}  {v.get('hint', '')}")
        if len(violations) > 40:
            print(f"  …其余 {len(violations) - 40} 条见 qa/reports/g1.json")
    else:
        print(f"[G1] 通过：{n_files} 文件 / {n_decls} 条声明，violations=0")
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
