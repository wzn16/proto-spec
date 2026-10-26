#!/usr/bin/env python3
"""tokens.css → 开发可直接消费的资产：tokens.json / tokens.d.ts / tokens.js / tailwind.preset.js

用法:
  python3 export_tokens.py --tokens <tokens.css> --out <目录> [--override <extra.css>]

产出：
  tokens.json         结构化（含 resolved 值：var() 链已解析）
  tokens.d.ts         TypeScript 类型（键名可索引，能被 tsc 编译）
  tokens.js           CommonJS 运行时模块（resolved 值，可直接内联使用）
  tailwind.preset.js  Tailwind v3 预设（colors/fontSize/radius/spacing/shadow/zIndex/transition）

分组：g 基元 / s 语义 / c 组件 / motion 动效（--motion-* / --c-motion-*） / ease 缓动
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

GROUP_RULES = [
    ("g", lambda n: n.startswith("--g-")),
    ("s", lambda n: n.startswith("--s-")),
    ("c", lambda n: n.startswith("--c-")),
    ("motion", lambda n: n.startswith("--motion-") or n.startswith("--c-motion-")),
    ("ease", lambda n: n.startswith("--ease")),
]


def parse(css_paths: list[Path]) -> tuple[dict[str, str], list[str]]:
    text = "\n".join(p.read_text(encoding="utf-8") for p in css_paths)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    defs: dict[str, str] = {}
    warnings: list[str] = []
    # 只收 :root 与 [data-*] 内的声明；扫描非 root 段以给警告
    for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", text):
        selector, body = block.group(1).strip(), block.group(2)
        if ":root" not in selector and not selector.startswith("."):
            for name in re.findall(r"(--[\w-]+)\s*:", body):
                if name not in defs:
                    warnings.append(f"{name} 定义在非 :root 选择器（{selector[:30]}），可能不生效")
        for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);", body):
            defs[m.group(1)] = m.group(2).strip()
    return defs, warnings


def resolve(name: str, defs: dict[str, str], depth: int = 0, seen: set[str] | None = None) -> str:
    seen = seen or set()
    if depth > 6 or name in seen:
        return defs.get(name, "")
    seen.add(name)
    v = defs.get(name, "")
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)", v.strip())
    return resolve(m.group(1), defs, depth + 1, seen) if m else v


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokens", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--override", default=None, help="额外的覆盖文件（如项目覆盖层）")
    args = ap.parse_args()
    paths = [Path(args.tokens)]
    if args.override:
        paths.append(Path(args.override))
    if not paths[0].is_file():
        print(f"[export] 找不到 {paths[0]}", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    defs, warnings = parse(paths)

    groups: dict[str, dict[str, str]] = {k: {} for k, _ in GROUP_RULES}
    for name, value in defs.items():
        for gname, test in GROUP_RULES:
            if test(name):
                groups[gname][name] = value
                break
    resolved = {k: {n: resolve(n, defs) for n in v} for k, v in groups.items()}
    total = sum(len(v) for v in groups.values())

    payload = {"$schema": "proto-spec/tokens@2", "sources": [str(p) for p in paths],
               "count": total, "resolved": resolved, "raw": groups, "warnings": warnings}
    (out / "tokens.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    dts = ["// 由 proto-spec/scripts/export_tokens.py 生成，勿手改",
           "export interface TokenGroups {",]
    for gname, v in groups.items():
        dts.append(f"  /** {gname} 层：{len(v)} 个 */")
        dts.append(f"  {gname}: {{")
        dts += [f"    '{n}': string;" for n in v]
        dts.append("  };")
    dts += ["}", "",
            "export declare const tokens: TokenGroups;",
            "export declare const resolved: { [K in keyof TokenGroups]: { [P in keyof TokenGroups[K]]: string } };",
            "export type TokenName = { [K in keyof TokenGroups]: keyof TokenGroups[K] }[keyof TokenGroups] & string;",
            ""]
    (out / "tokens.d.ts").write_text("\n".join(dts), encoding="utf-8")

    (out / "tokens.js").write_text(
        "// 由 proto-spec/scripts/export_tokens.py 生成（resolved：var() 已解析）\n"
        "module.exports = " + json.dumps(resolved, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8")

    def pick(prefix: str, *, keep=lambda n: True):
        return {n.replace(prefix, ""): f"var({n})"
                for n in defs if n.startswith(prefix) and keep(n)}
    preset = {"theme": {"extend": {
        "colors": pick("--s-color-", keep=lambda n: "color" in n) | {n.replace("--g-", ""): f"var({n})"
                                                                    for n in defs if n.startswith("--g-") and "color" in n},
        "fontSize": pick("--s-fs-"),
        "spacing": pick("--s-space-"),
        "borderRadius": pick("--g-radius-"),
        "boxShadow": pick("--s-shadow-") | pick("--g-shadow-"),
        "zIndex": pick("--c-z-"),
        "transitionDuration": pick("--motion-") | pick("--c-motion-"),
        "transitionTimingFunction": pick("--ease-"),
        "height": pick("--c-row-h"),
        "minWidth": pick("--c-drawer-"),
    }}}
    (out / "tailwind.preset.js").write_text(
        "// Tailwind v3 preset（由 export_tokens.py 生成）\nmodule.exports = "
        + json.dumps(preset, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    print(f"[export] {total} 个 token → {out}/tokens.json · tokens.d.ts · tokens.js · tailwind.preset.js")
    print("  分层：" + " ".join(f"{k}={len(v)}" for k, v in groups.items()))
    if warnings:
        print(f"  ⚠ {len(warnings)} 个变量定义在非 :root 选择器：" + "; ".join(warnings[:3]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
