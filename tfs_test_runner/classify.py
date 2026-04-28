"""Group cases into phases.

Default behavior (no config):
    Single phase "All cases" containing every case.

YAML override (recommended for organized execution):
    phases:
      - id: "p1"
        title: "Phase 1 — Smoke"
        level: easy
        desc: "Quick critical-path checks."
        case_ids: ["1234", "1235"]
      - id: "p2"
        title: "Phase 2 — Edge cases"
        level: hard
        desc: "Failure / boundary scenarios."
        match: ["fail", "error", "invalid"]   # substring match on title (case-insensitive)

Cases not matched by any phase fall into an "Others" phase appended at the end.

Levels: 'easy' / 'med' / 'hard' (purely informational, drives badge color).
"""
from __future__ import annotations
from typing import Any


def _case_matches(case: dict, criteria: dict) -> bool:
    """True if case is named in case_ids OR any match keyword appears in title."""
    cid = str(case.get("id", ""))
    ids = [str(x) for x in (criteria.get("case_ids") or [])]
    if cid in ids:
        return True
    title = (case.get("title_en") or case.get("title") or "").lower()
    for kw in criteria.get("match", []):
        if str(kw).lower() in title:
            return True
    return False


def assign_phases(cases: list[dict]) -> list[dict]:
    """Default: bundle every case into one 'All cases' phase."""
    if not cases:
        return []
    return [{
        "id": "all",
        "title": "All cases",
        "level": "med",
        "desc": "",
        "cases": list(cases),
    }]


def load_yaml_phases(path: str) -> list[dict]:
    """Load phase config from YAML. Returns the list under top-level 'phases' key."""
    import yaml  # type: ignore
    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    return cfg.get("phases") or []


def apply_yaml_phases(cases: list[dict], phase_cfg: list[dict]) -> list[dict]:
    """Apply phase config to cases. Unmatched cases land in 'Others' phase at end."""
    used: set[str] = set()
    out: list[dict] = []
    for p in phase_cfg:
        cs: list[dict] = []
        for c in cases:
            cid = str(c.get("id", ""))
            if cid in used:
                continue
            if _case_matches(c, p):
                cs.append(c)
                used.add(cid)
        if cs:
            out.append({
                "id": str(p.get("id", "")),
                "title": str(p.get("title", "")),
                "level": str(p.get("level", "med")),
                "desc": str(p.get("desc", "")),
                "cases": cs,
            })
    leftover = [c for c in cases if str(c.get("id", "")) not in used]
    if leftover:
        out.append({
            "id": "others",
            "title": "Others",
            "level": "med",
            "desc": "Cases not matched by YAML rules.",
            "cases": leftover,
        })
    return out
