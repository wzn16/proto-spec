#!/usr/bin/env python3
"""G7 评审门：自评 + 独立评审 + 分歧处理，按「自评/他评取小」判定，并分级处置。

分级（有效分 = min(自评, 他评)）：
  1 分 → 无条件 FAIL（不允许任何理由放行）
  2 分 → 必须他评单存在，且该维写「改后 3–5」；否则 FAIL
  3 分 → 允许「不采纳 + 去符号后 ≥15 字理由」，或「改后 4–5」
  ≥4 分 → 通过

其它规则：
  - 无他评单时，自评单必须同行写「未独立评审：<去符号后 ≥20 字>」（不跨行抓取）
  - 同维差 ≥2 分 → 自评单必须有「分歧」小节
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_config import load as load_cfg, get as cfg_get  # noqa: E402

DIMS = ["层级", "节奏", "焦点", "密度", "一致性", "可信度"]   # 默认值，运行时被配置覆盖
SECTIONS = ["三秒测试", "锚线", "改进项", "保留"]
MIN_REASON = 20
SYM = re.compile(r"[|\s*_`\-—:：]")

def clean(t: str) -> str:
    return SYM.sub("", t or "")

def rows(text: str) -> dict[str, tuple[int, str]]:
    out = {}
    for d in DIMS:
        m = re.search(r"^\|\s*" + d + r"\s*\|\s*([1-5])\s*\|(.*)$", text, re.M)
        if m:
            out[d] = (int(m.group(1)), m.group(2))
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()
    root = Path(args.project).resolve()
    cfg = load_cfg(root, args.config)
    global DIMS, SECTIONS, MIN_REASON
    DIMS = cfg_get(cfg, "review.dims", DIMS)
    SECTIONS = cfg_get(cfg, "review.sections", SECTIONS)
    MIN_BASIS = cfg_get(cfg, "review.min_basis_chars", 6)
    MIN_REASON = cfg_get(cfg, "review.min_reason_chars", 15)
    MIN_NO_PEER = cfg_get(cfg, "review.min_no_peer_reason_chars", 20)
    PASS_SCORE = cfg_get(cfg, "review.pass_score", 4)
    BLOCK_SCORE = cfg_get(cfg, "review.block_score", 1)
    GAP = cfg_get(cfg, "review.divergence_gap", 2)
    self_f = root / "qa" / "visual-review.md"
    peer_f = root / "qa" / "visual-review-peer.md"
    problems: list[dict] = []

    self_text = self_f.read_text(encoding="utf-8") if self_f.is_file() else ""
    if not self_f.is_file():
        problems.append({"file": "qa/visual-review.md", "kind": "缺失", "value": "未找到",
                         "hint": "每轮完成后必须写视觉评分单（references/visual-scorecard.md）"})
    else:
        for s in SECTIONS:
            if s not in self_text:
                problems.append({"file": "qa/visual-review.md", "kind": "缺小节", "value": s,
                                 "hint": f"必须包含「{s}」小节"})

    self_scores = rows(self_text)
    for d in DIMS:
        if d not in self_scores:
            problems.append({"file": "qa/visual-review.md", "kind": "缺评分", "value": d,
                             "hint": "六维每项必须给 1–5 分"})
        else:
            # 依据列必须有内容（原「位置 + 现象」要求）
            cells = [c.strip() for c in self_scores[d][1].split("|")]
            basis = cells[0] if cells else ""
            if len(clean(basis)) < MIN_BASIS:
                problems.append({"file": "qa/visual-review.md", "kind": "缺依据", "value": f"{d}",
                                 "hint": "该维「依据」列必须写位置 + 现象（≥6 个有效字符）"})

    peer_scores: dict[str, tuple[int, str]] = {}
    peer_present = peer_f.is_file()
    if not peer_present:
        m = re.search(r"未独立评审[:：]\s*([^\n]*)", self_text)
        reason = clean(m.group(1)) if m else ""
        if len(reason) < MIN_NO_PEER:
            problems.append({"file": "qa/visual-review-peer.md", "kind": "缺独立评审", "value": "未找到",
                             "hint": "派发独立评审并存评分单；确无执行者时在同一行写「未独立评审：<≥20 字理由>」"})
    else:
        peer_text = peer_f.read_text(encoding="utf-8")
        for s in SECTIONS:
            if s not in peer_text:
                problems.append({"file": "qa/visual-review-peer.md", "kind": "缺小节", "value": s,
                                 "hint": f"独立评审单必须包含「{s}」"})
        peer_scores = rows(peer_text)
        # 自评与他评不得同一份（同分同文视为抄写）
        for d in DIMS:
            if d in self_scores and d in peer_scores:
                if self_scores[d][0] == peer_scores[d][0] and \
                   clean(self_scores[d][1].split("|")[0]) == clean(peer_scores[d][1].split("|")[0]) and \
                   clean(self_scores[d][1].split("|")[0]):
                    problems.append({"file": "qa/visual-review-peer.md", "kind": "评审未独立",
                                     "value": f"{d} 同分同文", "hint": "他评不得与自评逐字相同"})

    effective: dict[str, int] = {}
    for d in DIMS:
        if d in self_scores:
            s = self_scores[d][0]
            p = peer_scores.get(d, (s, ""))[0]
            effective[d] = min(s, p)

    for d, v in effective.items():
        row = self_scores.get(d, (0, ""))[1]
        if v >= PASS_SCORE:
            continue
        if v == BLOCK_SCORE:
            problems.append({"file": "qa/visual-review.md", "kind": "1 分不得放行", "value": d,
                             "hint": "出现 1 分说明该维不合格：必须重做，不接受任何理由或复评"})
            continue
        if v == 2:
            if not peer_present:
                problems.append({"file": "qa/visual-review.md", "kind": "2 分缺他评", "value": d,
                                 "hint": "2 分维度必须有独立评审的「改后 3–5」"})
            elif not re.search(r"改后\s*[3-5]", row):
                problems.append({"file": "qa/visual-review.md", "kind": "2 分未复评", "value": d,
                                 "hint": "2 分维度必须在该行写「改后 3–5」并说明改了什么"})
            continue
        # v == 3
        ok = (("不采纳" in row and len(clean(row)) >= 15)
              or re.search(r"改后\s*[4-5]", row))
        if not ok:
            problems.append({"file": "qa/visual-review.md", "kind": "3 分未处置", "value": d,
                             "hint": "3 分维度必须「不采纳 + 去符号后 ≥15 字理由」或「改后 4–5」"})

    gaps = {d: abs(self_scores[d][0] - peer_scores[d][0])
            for d in DIMS if d in self_scores and d in peer_scores}
    big = {d: g for d, g in gaps.items() if g >= GAP}
    if big and "分歧" not in self_text:
        problems.append({"file": "qa/visual-review.md", "kind": "分歧未处理",
                         "value": ", ".join(f"{d}差{g}分" for d, g in big.items()),
                         "hint": "同维差 ≥2 分必须有「分歧」小节写明处理方式"})

    report = {"gate": "G7", "pass": not problems,
              "summary": {"self": {d: self_scores[d][0] for d in self_scores},
                          "peer": {d: peer_scores[d][0] for d in peer_scores},
                          "peer_present": peer_present,
                          "effective": effective,
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
        print(f"[G7] 通过：有效分 {lo}–{max(effective.values()) if effective else 0}（独立评审：{'有' if peer_present else '无'}）")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
