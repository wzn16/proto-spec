#!/usr/bin/env python3
"""把 tokens.css 导出为开发可直接消费的资产：tokens.json / tokens.d.ts / tailwind.preset.js

用法: python3 export_tokens.py --tokens <tokens.css> --out <目录>
退出码: 0=成功 2=用法错误
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

GROUPS = ("g", "s", "c")


def parse(css: str) -> dict[str, dict[str, str]]:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out: dict[str, dict[str, str]] = {k: {} for k in GROUPS}
    for m in re.finditer(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", css, re.I):
        name, value = m.group(1).strip(), m.group(2).strip()
        parts = name.lstrip("-").split("-")
        if parts and parts[0] in GROUPS:
            out[parts[0]][name] = value
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    src = Path(args.tokens)
    if not src.is_file():
        print(f"[export] 找不到 {src}", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    groups = parse(src.read_text(encoding="utf-8"))

    total = sum(len(v) for v in groups.values())
    payload = {"$schema": "proto-spec/tokens@1", "generatedFrom": src.name,
               "count": total, "primitive": groups["g"], "semantic": groups["s"], "component": groups["c"]}
    (out / "tokens.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["// 由 proto-spec/scripts/export_tokens.py 生成，勿手改",
             "export declare const tokens: {"]
    for k, v in groups.items():
        lines.append(f"  /** {k} 层：{len(v)} 个 */")
        lines.append(f"  {k}: {{")
        for name in v:
            lines.append(f"    '{name}': string;")
        lines.append("  };")
    lines += ["};", "export type TokenName = keyof typeof tokens.semantic;", ""]
    (out / "tokens.d.ts").write_text("\n".join(lines), encoding="utf-8")

    tw = {"theme": {"extend": {
        "colors": {n.replace("--s-color-", "").replace("--g-", ""): f"var({n})"
                   for n in list(groups["s"]) + list(groups["g"]) if "color" in n or n.startswith("--g-")},
        "borderRadius": {n.replace("--g-radius-", ""): f"var({n})" for n in groups["g"] if "radius" in n},
        "spacing": {n.replace("--s-space-", ""): f"var({n})" for n in groups["s"] if "space" in n},
    }}}
    (out / "tailwind.preset.js").write_text(
        "// 由 proto-spec/scripts/export_tokens.py 生成\nmodule.exports = "
        + json.dumps(tw, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    print(f"[export] {total} 个 token → {out}/tokens.json · tokens.d.ts · tailwind.preset.js")
    print(f"  分层：g={len(groups['g'])} s={len(groups['s'])} c={len(groups['c'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
