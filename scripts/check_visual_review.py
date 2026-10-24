#!/usr/bin/env python3
"""G7 视觉评审门：强制检查 qa/visual-review.md 的完整性与分数。

用法: python3 check_visual_review.py --project <目录> [--json]
退出码: 0=通过 1=未通过 2=用法错误
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

DIMS = ["层级", "节奏", "焦点", "密度", "一致性", "可信度"]
SECTIONS = ["三秒测试", "锚线", "改进项", "保留"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    f = root / "qa" / "visual-review.md"
    problems = []
    scores = {}
    if not f.is_file():
        problems.append({"file": "qa/visual-review.md", "kind": "缺失", "value": "未找到", "hint": "每轮完成后必须写视觉评分单（见 references/visual-scorecard.md）"})
    else:
        text = f.read_text(encoding="utf-8")
        for s in SECTIONS:
            if s not in text:
                problems.append({"file": "qa/visual-review.md", "kind": "缺小节", "value": s, "hint": f"必须包含「{s}」小节"})
        for d in DIMS:
            m = re.search(r"\|\s*" + d + r"\s*\|\s*([1-5])\s*\|", text)
            if not m:
                problems.append({"file": "qa/visual-review.md", "kind": "缺评分", "value": d, "hint": "六维每项必须给 1–5 分"})
            else:
                scores[d] = int(m.group(1))
        low = {d: v for d, v in scores.items() if v < 4}
        if low and "不采纳" not in text:
            for d, v in low.items():
                problems.append({"file": "qa/visual-review.md", "kind": "低分未处理", "value": f"{d}={v}", "hint": "低于 4 分必须改，或写「不采纳 + 理由」"})
    report = {"gate": "G7", "pass": not problems,
              "summary": {"scores": scores, "violations": len(problems)},
              "violations": problems}
    out = root / "qa" / "reports"
    out.mkdir(parents=True, exist_ok=True)
    (out / "g7-visual.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif problems:
        print(f"[G7] FAIL：{len(problems)} 处")
        for p in problems[:10]:
            print(f"  {p['file']}  [{p['kind']}] {p['value']} → {p['hint']}")
    else:
        print(f"[G7] 通过：六维评分 {min(scores.values())}–{max(scores.values())} 分，评分单完整")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
