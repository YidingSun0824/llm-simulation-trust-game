"""Parse a model's free-text answer into (canonical action, belief)."""
from __future__ import annotations

import re
from typing import Iterable, Optional, Tuple

_DECISION = re.compile(r"DECISION\s*[:：]\s*\**\s*<?\s*([A-Za-z_]+)", re.IGNORECASE)
_BELIEF = re.compile(r"BELIEF\s*[:：]\s*\**\s*<?\s*([0-9]+(?:\.[0-9]+)?)\s*(%?)", re.IGNORECASE)


def parse_decision(text: str, allowed_labels: Iterable[str]) -> Optional[str]:
    """Return the shown label (upper-case) from the LAST 'DECISION:' line, or None if absent/invalid."""
    allowed = {a.upper() for a in allowed_labels}
    hits = _DECISION.findall(text or "")
    for raw in reversed(hits):
        lab = raw.upper().strip("_")
        if lab in allowed:
            return lab
        # tolerate "WALK OUT" / "WALKOUT"
        compact = {a.replace("_", ""): a for a in allowed}
        if lab.replace("_", "") in compact:
            return compact[lab.replace("_", "")]
    return None


def parse_belief(text: str) -> Optional[float]:
    """Return the belief as a probability in [0, 1] from the LAST 'BELIEF:' line, or None."""
    hits = _BELIEF.findall(text or "")
    if not hits:
        return None
    num, _pct = hits[-1]
    v = float(num)
    if v > 100:
        return None
    if v <= 1 and "." in num and not _pct:
        # "0.2" written as a probability rather than a percentage
        return v
    return v / 100.0


def parse_response(text: str, allowed_labels: Iterable[str]) -> Tuple[Optional[str], Optional[float]]:
    return parse_decision(text, allowed_labels), parse_belief(text)
