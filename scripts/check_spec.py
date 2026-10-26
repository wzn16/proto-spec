#!/usr/bin/env python3
"""G0 SPEC 门：冻结状态、章节完整性、附录 C 逐项确认、占位符零残留。

用法: python3 check_spec.py --project <目录> [--json]
退出码: 0=通过 1=不通过 2=用法错误 3=跳过（无 SPEC）
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from spec_meta import parse  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    meta = parse(root / "SPEC.md")
    problems = []
    if not meta["exists"]:
        print("[G0] SKIP：没有 SPEC.md")
        return 3
    if meta["status"] not in ("frozen", "冻结"):
        problems.append({"kind": "未冻结", "value": str(meta["status"]),
                         "hint": "SPEC 状态须为 frozen 才允许交付"})
    for s in meta["missingSections"]:
        problems.append({"kind": "缺章节", "value": s, "hint": f"SPEC 缺「{s}」章节"})
    if meta["appendixC"]["unconfirmed"]:
        problems.append({"kind": "对账单未确认", "value": f"{meta['appendixC']['unconfirmed']} 行",
                         "hint": "附录 C 每行需写「已确认 + 日期」"})
    if meta["placeholders"]:
        problems.append({"kind": "占位符残留", "value": ", ".join(meta["placeholders"][:5]),
                         "hint": "替换 <项目名> 这类占位符"})
    report = {"gate": "G0", "pass": not problems,
              "summary": {"status": meta["status"], "family": meta["family"],
                          "sections": len(meta["missingSections"]),
                          "violations": len(problems)},
              "violations": problems}
    out = root / "qa" / "reports"; out.mkdir(parents=True, exist_ok=True)
    (out / "g0.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif problems:
        print(f"[G0] FAIL：{len(problems)} 处")
        for p in problems:
            print(f"  SPEC.md  [{p['kind']}] {p['value']} → {p['hint']}")
    else:
        print(f"[G0] 通过：状态 frozen（{meta['status']}），家族 {meta['family']}，无占位符")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
