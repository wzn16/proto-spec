#!/usr/bin/env python3
"""G4 可访问性门：tokens 语义色对的 WCAG 对比度机检（纯标准库）。

原理：读项目 tokens.css 的语义变量值，对「语义角色配对」逐对计算 WCAG 2.x 对比度。
正文用途 ≥4.5:1，大字/UI 用途 ≥3:1。配对表可按家族扩展（--pairs-json 覆盖）。

用法:
  python3 check_contrast.py --project <项目目录> [--pairs-json <文件>]

退出码: 0=通过  1=未通过  2=用法错误
报告:   <project>/qa/reports/g4.json
"""
from __future__ import annotations
import sys

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_config import load as load_cfg, get as cfg_get  # noqa: E402

# 语义角色配对（前景, 背景, 用途, 门槛）
# 门槛: 4.5 = 正文; 3.0 = 大字/UI 控件
DEFAULT_PAIRS = [
    ("--s-color-success-strong", "--s-bg-card", "状态文字/卡片底", 4.5),
    ("--s-color-error-strong", "--s-bg-card", "错误文字/卡片底", 4.5),
    ("--s-text-primary", "--s-bg-page", "正文/页面底", 4.5),
    ("--s-text-primary", "--s-bg-card", "正文/卡片底", 4.5),
    ("--s-text-secondary", "--s-bg-page", "辅助文字/页面底", 4.5),
    ("--s-text-secondary", "--s-bg-card", "辅助文字/卡片底", 4.5),
    ("--s-text-inverse", "--s-color-primary", "主钮文字/主钮底", 4.5),
]


def strip_comments(t: str) -> str:
    return re.sub(r"/\*.*?\*/", "", t, flags=re.S)


def load_tokens(p: Path) -> dict:
    defs: dict[str, str] = {}
    for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", strip_comments(p.read_text(encoding="utf-8"))):
        defs[m.group(1)] = m.group(2).strip()
    return defs


def resolve(name: str, defs: dict, depth: int = 0) -> str | None:
    """解析变量值，穿透一层 var() 引用。"""
    if depth > 4:
        return None
    v = defs.get(name)
    if v is None:
        return None
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*\)", v.strip())
    if m:
        return resolve(m.group(1), defs, depth + 1)
    return v.strip()


def norm_color(v: str | None) -> str | None:
    """归一化为 #rrggbb；无法识别返回 None。"""
    if not v:
        return None
    v = v.strip().lower()
    if re.fullmatch(r"#[0-9a-f]{6}", v):
        return v
    if re.fullmatch(r"#[0-9a-f]{3}", v):
        return "#" + "".join(c * 2 for c in v[1:])
    m = re.fullmatch(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,[^)]*)?\)", v)
    if m:
        r, g, b = (int(m.group(i)) for i in (1, 2, 3))
        return f"#{r:02x}{g:02x}{b:02x}"
    return None


def luminance(hex6: str) -> float:
    def chan(c: int) -> float:
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(int(hex6[i:i + 2], 16)) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main() -> int:
    ap = argparse.ArgumentParser(description="G4 可访问性对比度门")
    ap.add_argument("--project", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--pairs-json", default=None,
                    help="覆盖默认配对表（JSON 数组：[[fg,bg,用途,门槛],...]）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    project = Path(args.project).resolve()
    cfg = load_cfg(project, args.config)
    cfg_pairs = cfg_get(cfg, "contrast.pairs", None)
    TEXT_T = cfg_get(cfg, "contrast.text_threshold", 4.5)
    UI_T = cfg_get(cfg, "contrast.ui_threshold", 3.0)
    pairs = ([(p["fg"], p["bg"], p.get("usage", ""), TEXT_T if p.get("level", "text") == "text" else UI_T)
              for p in cfg_pairs] if cfg_pairs else DEFAULT_PAIRS)
    tokens = project / "assets" / "tokens.css"
    if not tokens.is_file():
        print("[G4] 找不到 assets/tokens.css", file=sys.stderr)
        return 2

    defs = load_tokens(tokens)
    if args.pairs_json and Path(args.pairs_json).is_file():
        pairs = [tuple(x) for x in json.loads(Path(args.pairs_json).read_text(encoding="utf-8"))]
    else:
        pairs = list(DEFAULT_PAIRS)
        # 条件配对：深色框架槽位存在时才检查（家族/项目自带侧栏 token）
        if "--s-bg-sidebar" in defs and "--s-text-on-dark-muted" in defs:
            pairs.append(("--s-text-on-dark-muted", "--s-bg-sidebar", "深底弱文字/侧栏底", 3.0))

    violations: list[dict] = []
    checked = 0
    for fg, bg, usage, threshold in pairs:
        fgv = norm_color(resolve(fg, defs))
        bgv = norm_color(resolve(bg, defs))
        checked += 1
        if fgv is None or bgv is None:
            violations.append({
                "pair": f"{fg} on {bg}", "usage": usage, "threshold": threshold,
                "actual": None, "fg": fgv or "未定义", "bg": bgv or "未定义",
                "verdict": "FAIL", "hint": f"{fg} 或 {bg} 无法解析为颜色（检查 tokens.css）"})
            continue
        ratio = round(contrast(fgv, bgv), 2)
        if ratio < threshold:
            violations.append({
                "pair": f"{fg} on {bg}", "usage": usage, "threshold": threshold,
                "actual": ratio, "fg": fgv, "bg": bgv, "verdict": "FAIL",
                "hint": f"对比度 {ratio}:1 < {threshold}:1，请加深 {fg} 或调整 {bg}"})

    report = {
        "gate": "G4",
        "pass": not violations,
        "summary": {"pairs": checked, "violations": len(violations)},
        "violations": violations,
    }
    out = project / "qa" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "g4.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif violations:
        print(f"[G4] FAIL：{len(violations)} 对不达标（共 {checked} 对）")
        for v in violations:
            print(f"  {v['pair']}  {v['actual']}  需要 ≥{v['threshold']}  {v['hint']}")
    else:
        print(f"[G4] 通过：{checked} 对语义配对全部达标（正文 ≥4.5:1 / UI ≥3:1）")
    return 0 if not violations else 1


if __name__ == "__main__":
    sys.exit(main())
