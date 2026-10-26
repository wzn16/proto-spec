#!/usr/bin/env python3
"""G7 评审门：自评 + 独立评审，按「自评/他评取小」判定，分级处置且底线不可配置。

底线（硬编码，配置不能放松）：
  - 有效分 == 1 → 无条件 FAIL
  - pass_score 只允许 3–5；block_score 固定 1；有效分地板 min_effective_for_pass ≥3
分级：
  - 有效分 2 → 需他评存在且该维写「改后 3–5」
  - 有效分 3 → 需改法列写「不采纳 + ≥15 有效字」或「改后 4–5」
  - ≥ pass_score → 通过
他评要求：六维必须齐全、每维依据 ≥6 有效字、不得与自评同文（相似度 <0.85）。
解析：只在「六维打分」小节内取表格，忽略代码块与表头示例行。
"""
from __future__ import annotations
import argparse, json, re, sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_config import load as load_cfg, get as cfg_get  # noqa: E402

DEFAULT_DIMS = ["层级", "节奏", "焦点", "密度", "一致性", "可信度"]
DEFAULT_SECTIONS = ["三秒测试", "锚线", "改进项", "保留"]
SYM = re.compile(r"[|\s*_`\-—:：。，、；！？]")
FENCE = re.compile(r"```[\s\S]*?```")


def clean(t: str) -> str:
    return SYM.sub("", t or "")


def section_text(text: str, name: str) -> str:
    """取某个 `##` 小节正文（到下一个同级标题为止）。"""
    m = re.search(rf"^#{{1,6}}\s*[^\n]*{re.escape(name)}[^\n]*$([\s\S]*?)(?=^#{{1,6}}\s|\Z)", text, re.M)
    return m.group(1) if m else ""


def rows(text: str, dims: list[str]) -> dict[str, tuple[int, str]]:
    body = FENCE.sub("", text)
    body = section_text(body, "六维") or body
    out: dict[str, tuple[int, str]] = {}
    for d in dims:
        # 只认「| 维度 | 数字 |」，取该维最后一条（真表通常在示例之后）
        found = re.findall(r"^\|\s*" + re.escape(d) + r"\s*\|\s*([1-5])\s*\|(.*)$", body, re.M)
        if found:
            score, rest = found[-1]
            out[d] = (int(score), rest)
    return out


def basis_of(rest: str) -> str:
    cells = [c.strip() for c in rest.split("|")]
    return cells[0] if cells else ""


def fix_of(rest: str) -> str:
    cells = [c.strip() for c in rest.split("|") if c.strip()]
    return cells[-1] if cells else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--config", default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.project).resolve()
    cfg = load_cfg(root, args.config)

    DIMS = cfg_get(cfg, "review.dims", DEFAULT_DIMS)
    SECTIONS = cfg_get(cfg, "review.sections", DEFAULT_SECTIONS)
    MIN_BASIS = int(cfg_get(cfg, "review.min_basis_chars", 6))
    MIN_REASON = int(cfg_get(cfg, "review.min_reason_chars", 15))
    MIN_NO_PEER = int(cfg_get(cfg, "review.min_no_peer_reason_chars", 20))
    PASS_SCORE = int(cfg_get(cfg, "review.pass_score", 4))
    FLOOR = int(cfg_get(cfg, "review.min_effective_for_pass", 3))

    # 底线钳制：配置只能更严，不能更松
    problems: list[dict] = []
    if not (3 <= PASS_SCORE <= 5):
        print("[G7] 配置非法：review.pass_score 只允许 3–5", file=sys.stderr)
        return 2
    if FLOOR < 3:
        problems.append({"file": "qa/gates.config.json", "kind": "配置非法",
                         "value": f"min_effective_for_pass={FLOOR}", "hint": "有效分地板不得低于 3"})
        FLOOR = 3

    self_f = root / "qa" / "visual-review.md"
    peer_f = root / "qa" / "visual-review-peer.md"
    self_text = self_f.read_text(encoding="utf-8") if self_f.is_file() else ""
    if not self_f.is_file():
        problems.append({"file": "qa/visual-review.md", "kind": "缺失", "value": "未找到",
                         "hint": "每轮完成后必须写视觉评分单（references/visual-scorecard.md）"})
    else:
        for s in SECTIONS:
            if not re.search(rf"^#+\s*[^\n]*{re.escape(s)}", self_text, re.M):
                problems.append({"file": "qa/visual-review.md", "kind": "缺小节", "value": s,
                                 "hint": f"必须有以「{s}」为标题的小节"})

    self_scores = rows(self_text, DIMS)
    for d in DIMS:
        if d not in self_scores:
            problems.append({"file": "qa/visual-review.md", "kind": "缺评分", "value": d,
                             "hint": "六维每项必须给 1–5 分"})
        elif len(clean(basis_of(self_scores[d][1]))) < MIN_BASIS:
            problems.append({"file": "qa/visual-review.md", "kind": "缺依据", "value": d,
                             "hint": f"该维「依据」需写位置+现象（≥{MIN_BASIS} 个有效字符）"})

    peer_scores: dict[str, tuple[int, str]] = {}
    peer_present = peer_f.is_file()
    if not peer_present:
        m = re.search(r"未独立评审[:：]\s*([^\n]*)", self_text)
        if len(clean(m.group(1) if m else "")) < MIN_NO_PEER:
            problems.append({"file": "qa/visual-review-peer.md", "kind": "缺独立评审", "value": "未找到",
                             "hint": f"派发独立评审；确无执行者时同一行写「未独立评审：<≥{MIN_NO_PEER} 字理由>」"})
    else:
        peer_text = peer_f.read_text(encoding="utf-8")
        for s in SECTIONS:
            if not re.search(rf"^#+\s*[^\n]*{re.escape(s)}", peer_text, re.M):
                problems.append({"file": "qa/visual-review-peer.md", "kind": "缺小节", "value": s,
                                 "hint": f"独立评审单必须有「{s}」小节"})
        peer_scores = rows(peer_text, DIMS)
        for d in DIMS:
            if d not in peer_scores:
                problems.append({"file": "qa/visual-review-peer.md", "kind": "他评缺该维", "value": d,
                                 "hint": "独立评审必须逐维给分，缺维不能顶替自评"})
                continue
            if len(clean(basis_of(peer_scores[d][1]))) < MIN_BASIS:
                problems.append({"file": "qa/visual-review-peer.md", "kind": "他评缺依据", "value": d,
                                 "hint": f"他评每维依据也需 ≥{MIN_BASIS} 个有效字符"})
            if d in self_scores:
                a, b = basis_of(self_scores[d][1]), basis_of(peer_scores[d][1])
                if self_scores[d][0] == peer_scores[d][0] and clean(a) and clean(b) and \
                   SequenceMatcher(None, clean(a), clean(b)).ratio() >= 0.85:
                    problems.append({"file": "qa/visual-review-peer.md", "kind": "评审未独立",
                                     "value": f"{d} 同分同文", "hint": "他评不得与自评高度相似（≥0.85）"})

    effective: dict[str, int] = {}
    for d in DIMS:
        if d in self_scores:
            s = self_scores[d][0]
            p = peer_scores.get(d, (s, ""))[0] if peer_present else s
            effective[d] = min(s, p)

    for d, v in effective.items():
        fix = fix_of(self_scores.get(d, (0, ""))[1])
        if v <= 1:  # 底线：任何配置都不能放行 1 分
            problems.append({"file": "qa/visual-review.md", "kind": "1 分不得放行", "value": d,
                             "hint": "1 分必须重做该维，不接受复评或理由"})
            continue
        if v < FLOOR:
            problems.append({"file": "qa/visual-review.md", "kind": f"{v} 分不得放行", "value": d,
                             "hint": f"有效分低于地板 {FLOOR}：本轮不放行，需改后重新评审"})
            continue
        if v >= PASS_SCORE:
            continue
        if v == 2:
            if not (peer_present and re.search(r"改后\s*[3-5]", fix)):
                problems.append({"file": "qa/visual-review.md", "kind": "2 分未复评", "value": d,
                                 "hint": "2 分需他评存在且改法列写「改后 3–5」"})
            continue
        ok = ("不采纳" in fix and len(clean(fix)) >= MIN_REASON) or re.search(r"改后\s*[4-5]", fix)
        if not ok:
            problems.append({"file": "qa/visual-review.md", "kind": "3 分未处置", "value": d,
                             "hint": f"3 分需改法列写「不采纳 + ≥{MIN_REASON} 有效字」或「改后 4–5」"})

    gaps = {d: abs(self_scores[d][0] - peer_scores[d][0])
            for d in DIMS if d in self_scores and d in peer_scores}
    big = {d: g for d, g in gaps.items() if g >= 2}
    if big and not re.search(r"^#+\s*[^\n]*分歧", self_text, re.M):
        problems.append({"file": "qa/visual-review.md", "kind": "分歧未处理",
                         "value": ", ".join(f"{d}差{g}分" for d, g in big.items()),
                         "hint": "同维差 ≥2 分必须有以「分歧」为标题的小节"})

    report = {"gate": "G7", "pass": not problems,
              "summary": {"self": {d: self_scores[d][0] for d in self_scores},
                          "peer": {d: peer_scores[d][0] for d in peer_scores},
                          "peer_present": peer_present, "effective": effective,
                          "effective_min": min(effective.values()) if effective else None,
                          "floor": FLOOR, "pass_score": PASS_SCORE,
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
        print(f"[G7] 通过：有效分 {lo}–{max(effective.values()) if effective else 0}"
              f"（独立评审：{'有' if peer_present else '无'}，地板 {FLOOR}）")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main())
