#!/usr/bin/env python3
"""门禁配置加载：默认 config/gates.json ← 项目 <项目>/qa/gates.config.json 覆盖。

不写死阈值：任何项目可在自己的 qa/gates.config.json 里改写同名键，脚本读取合并结果。
用法：
  from gate_config import load, get
  cfg = load(project_dir)          # project_dir 可为 None
  max_anchors = get(cfg, "pixels.max_anchors", 4)
"""
from __future__ import annotations
import json, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_CFG = HERE.parent / "config" / "gates.json"


def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if k.startswith("$"):
            continue
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


def load(project: Path | str | None = None, extra: Path | str | None = None) -> dict:
    cfg: dict = {}
    if SKILL_CFG.is_file():
        cfg = json.loads(SKILL_CFG.read_text(encoding="utf-8"))
    proj_cfg = None
    if project:
        p = Path(project) / "qa" / "gates.config.json"
        if p.is_file():
            proj_cfg = json.loads(p.read_text(encoding="utf-8"))
    if extra:
        proj_cfg = _merge(proj_cfg or {}, json.loads(Path(extra).read_text(encoding="utf-8")))
    return _merge(cfg, proj_cfg or {})


def get(cfg: dict, path: str, default=None):
    cur = cfg
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def band_for_width(cfg: dict, width: int) -> tuple[float, float, str]:
    """按宽度取强调面积区间（配置里按 min_width 降序匹配）。"""
    bands = sorted(get(cfg, "pixels.accent_bands", []), key=lambda b: -b.get("min_width", 0))
    for b in bands:
        if width >= b.get("min_width", 0):
            lo, hi = float(b["lo"]), float(b["hi"])
            return lo, hi, f"{lo * 100:.1f}–{hi * 100:.0f}%"
    return 0.002, 0.02, "0.2–2%"
