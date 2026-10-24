#!/usr/bin/env python3
"""G7 评审门：自评 + 独立评审 + 分歧处理，按「较小值」判定。

规则：
  1) 自评单 qa/visual-review.md 必须含四小节与六维分数（1–5）。
  2) 独立评审 qa/visual-review-peer.md 必须存在；缺失时自评单需写
     「未独立评审 + ≥20 字理由」。
  3) 有效分 = min(自评, 他评)；有效分 <4 的维度，必须在该维度同一行内写
     「不采纳 + ≥20 字理由」，或写「复评」并给出改后分。
  4) 同维差 ≥2 分时，自评单必须有「分歧」小节。

用法: python3 check_visual_review.py --project <目录> [--json]
退出码: 0=通过 1=未通过 2=用法错误
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

DIMS = ["层级", "节奏", "焦点", "密度", "一致性", "可信度"]
SECTIONS = ["三秒测试", "锚线", "改进项", "保留"]
MIN_REASON = 20


def rows(text: str) -> dict[str, tuple[int, str]]:
    """提取 | 维度 | 分数 | 其余… | 行，返回 {维度: (分, 行内其余文本)}。"""
    out: dict[str, tuple[int, str]] = {}
    for d in DIMS:
        m = re.search(r"^\|\s*" + d + r"\s*\|\s*([1-5])\s*\|(.*)$", text, re.M)
        if m:
            out[d] = (int(m.group(1)), m.group(2))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    self_f = root / "qa" / "visual-review.md"
    peer_f = root / "qa" / "visual-review-peer.md"
    problems: list[dict] = []

    if not self_f.is_file():
        problems.append({"file": "qa/visual-review.md", "kind": "缺失", "value": "未找到",
                         "hint": "每轮完成后必须写视觉评分单（references/visual-scorecard.md）"})
        self_text = ""
    else:
        self_text = self_f.read_text(encoding="utf-8")
        for s in SECTIONS:
            if s not in self_text:
                problems.append({"file": "qa/visual-review.md", "kind": "缺小节", "value": s,
                                 "hint": f"必须包含「{s}」小节"})

    self_scores = rows(self_text) if self_text else {}
    for d in DIMS:
        if d not in self_scores:
            problems.append({"file": "qa/visual-review.md", "kind": "缺评分", "value": d,
                             "hint": "六维每项必须给 1–5 分"})

    peer_scores: dict[str, tuple[int, str]] = {}
    if not peer_f.is_file():
        m = re.search(r"未独立评审[:：]?\s*(.{0,200})", self_text, re.S)
        reason = (m.group(1).strip() if m else "")
        if len(reason) < MIN_REASON:
            problems.append({"file": "qa/visual-review-peer.md", "kind": "缺独立评审", "value": "未找到",
                             "hint": f"派发独立评审并保存评分单；确无执行者时在自评单写「未独立评审：<{MIN_REASON} 字以上理由>」"})
    else:
        peer_text = peer_f.read_text(encoding="utf-8")
        for s in SECTIONS:
            if s not in peer_text:
                problems.append({"file": "qa/visual-review-peer.md", "kind": "缺小节", "value": s,
                                 "hint": f"独立评审单必须包含「{s}」"})
        peer_scores = rows(peer_text)

    # 有效分 = 较小值
    effective: dict[str, int] = {}
    for d in DIMS:
        if d in self_scores:
            s = self_scores[d][0]
            p = peer_scores.get(d, (s, ""))[0]
            effective[d] = min(s, p)

    for d, v in effective.items():
        if v >= 4:
            continue
        row_text = self_scores.get(d, (0, ""))[1]
        handled = (("不采纳" in row_text and len(row_text.strip()) >= MIN_REASON)
                   or re.search(r"复评\s*[1-5]", row_text))
        if not handled:
            peer_note = f"（他评 {peer_scores[d][0]} 分）" if d in peer_scores else ""
            problems.append({"file": "qa/visual-review.md", "kind": "低分未处理", "value": f"{d}={v}{peer_note}",
                             "hint": "低于 4 分的维度必须在该行写「不采纳 + ≥20 字理由」或「复评 + 改后分」"})

    gaps = {d: abs(self_scores[d][0] - peer_scores[d][0])
            for d in DIMS if d in self_scores and d in peer_scores}
    big = {d: g for d, g in gaps.items() if g >= 2}
    if big and "分歧" not in self_text:
        problems.append({"file": "qa/visual-review.md", "kind": "分歧未处理",
                         "value": ", ".join(f"{d}差{g}分" for d, g in big.items()),
                         "hint": "同维差 ≥2 分必须有「分歧」小节写明处理方式"})

    report = {"gate": "G7", "pass": not problems,
              "summary": {"self": {d: self_scores[d][0] for d in self_scores},
                          "peer": {d: peer_scores[d][0] for d in peer_scores},
                          "effective_min": min(effective.values()) if effective else None,
                          "violations": len(problems)},
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
        lo = min(effective.values()) if effective else 0
        print(f"[G7] 通过：有效分（自评/他评取小）{lo}–{max(effective.values()) if effective else 0} 分")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
