"""Models, prices and run presets.

Prices: USD per million tokens, from https://platform.claude.com/docs/en/about-claude/pricing
(checked 2026-10-17).  Sampling parameters (temperature/top_p) are NOT sent: recent Claude
models reject them, so every call uses the model's default sampling, which is stochastic --
that stochasticity is exactly what makes "sampled" simulation differ from "perfect" simulation.
"""
from __future__ import annotations

from .frames import C_GRID

MODELS = {
    "claude-haiku-5-5": {
        "price_in": 0.10, "price_out": 0.50, "max_tokens": 1500,
        # no up-front thinking: the visible <=100-word reasoning is what we log and analyse
        "extra_body": {"output_config": {"effort": "medium"}, "thinking": {"type": "disabled"}},
    },
    "claude-sonnet-5-5": {
        "price_in": 2.00, "price_out": 10.00, "max_tokens": 1500,
        # "between_tools" is Sonnet 5.5's lowest thinking setting (= no up-front thinking)
        "extra_body": {"output_config": {"effort": "medium"}, "thinking": {"type": "between_tools"}},
    },
    "claude-opus-5-5": {
        "price_in": 4.00, "price_out": 20.00, "max_tokens": 6000,
        # Opus 5.5 thinking cannot be disabled; keep it cheap with low effort
        "extra_body": {"output_config": {"effort": "low"}},
    },
}

ALL_FRAMES = ("narrative", "neutral")

PRESETS = {
    # one cell, two games: proves the key and the request parameters work (~$0.001)
    "smoke": {"models": {"claude-haiku-5-5": 2}, "frames": ("neutral",), "c_grid": (10,),
              "include_baseline": False, "informed": (True,)},
    # every cell, a few games, cheap model: read the transcripts before spending real money (~$0.05)
    "pilot": {"models": {"claude-haiku-5-5": 3}, "frames": ALL_FRAMES, "c_grid": C_GRID,
              "include_baseline": True, "informed": (True, False)},
    # every cell once on Sonnet: check its behaviour and token use (~$0.30)
    "pilot-sonnet": {"models": {"claude-sonnet-5-5": 1}, "frames": ALL_FRAMES, "c_grid": C_GRID,
                     "include_baseline": True, "informed": (True, False)},
    # the real experiment (~$15-20 total; run `estimate` after the pilot for a measured number)
    "main": {"models": {"claude-haiku-5-5": 80, "claude-sonnet-5-5": 50}, "frames": ALL_FRAMES,
             "c_grid": C_GRID, "include_baseline": True, "informed": (True, False)},
    # optional: a stronger model on the primary (neutral, informed) slice only
    "opus": {"models": {"claude-opus-5-5": 30}, "frames": ("neutral",), "c_grid": (5, 10, 15, 25),
             "include_baseline": True, "informed": (True,)},
}


def cells(preset: dict):
    """Yield (frame, c, informed) for every experimental cell of a preset."""
    for frame in preset["frames"]:
        if preset.get("include_baseline", True):
            yield frame, None, False
        for c in preset["c_grid"]:
            for informed in preset["informed"]:
                yield frame, c, informed


def cell_id(frame: str, c, informed: bool) -> str:
    if c is None:
        return f"{frame}|baseline"
    return f"{frame}|c={c:g}|{'informed' if informed else 'uninformed'}"
