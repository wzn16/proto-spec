#!/usr/bin/env python3
"""解析 SPEC.md：状态、家族、章节完整性、附录 C 确认情况、占位符残留。"""
from __future__ import annotations
import re
from pathlib import Path

REQUIRED_FULL = ["语境", "规范", "页面", "已知限制"]
PLACEHOLDER = re.compile(r"<[^>]{1,20}>")


def parse(path: Path) -> dict:
    if not path.is_file():
        return {"exists": False}
    text = path.read_text(encoding="utf-8")
    status = None
    m = re.search(r"\|\s*状态\s*\|\s*([^|\n]+)", text)
    if m:
        status = m.group(1).strip().lower()
    fam = None
    m = re.search(r"\|\s*家族\s*(?:id)?\s*\|\s*([A-Z][A-Z0-9-]*)", text)
    if m:
        fam = m.group(1)
    heads = re.findall(r"^#{1,3}\s*(.+)$", text, re.M)
    missing = [s for s in REQUIRED_FULL if not any(s in h for h in heads)]
    # 附录 C：有则每行需「已确认」标记
    appc_rows, appc_missing = 0, 0
    if "附录 C" in text:
        block = text.split("附录 C", 1)[1]
        for line in block.split("\n"):
            if line.strip().startswith("|") and "---" not in line and "元素" not in line:
                cells = [c.strip() for c in line.strip("|").split("|")]
                if not any(cells):
                    continue
                appc_rows += 1
                if not any("已确认" in c for c in cells):
                    appc_missing += 1
    placeholders = sorted(set(PLACEHOLDER.findall(text)))
    return {"exists": True, "status": status, "family": fam, "missingSections": missing,
            "appendixC": {"rows": appc_rows, "unconfirmed": appc_missing},
            "placeholders": placeholders}
