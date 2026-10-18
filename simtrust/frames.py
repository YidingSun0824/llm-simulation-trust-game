"""Two presentations ("frames") of the same strategic structure.

narrative : the paper's own Alice / Bobble story and numbers (R_A=R_B=25, L=100, G=150, $k).
            Contamination probe: the IJCAI'23 paper is likely in the models' training data.
            Moral-loading probe: "defect" here means defrauding a customer.
neutral   : abstract Player A / Player B, labels IN/OUT/CHECK and X/Y, and DIFFERENT numbers
            (R_A=R_B=30, L=60, G=120, points).  Same breakpoint c* = 20, but different
            equilibrium mixtures (A checks 3/4 instead of 5/6; B defects c/60 instead of c/100),
            so a model reciting the paper's numbers in this frame is detectable.

Canonical action names (TRUST/WALK_OUT/SIMULATE, COOPERATE/DEFECT) are used everywhere in the
data; each frame only changes the words shown to the model.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .game import TrustGame


@dataclass(frozen=True)
class Frame:
    name: str
    game: TrustGame
    unit: str  # how payoffs are written
    alice_labels: Dict[str, str] = field(default_factory=dict)  # canonical -> shown label
    bobble_labels: Dict[str, str] = field(default_factory=dict)

    def alice_from_label(self, label: str) -> str:
        inv = {v.upper(): k for k, v in self.alice_labels.items()}
        return inv[label.upper()]

    def bobble_from_label(self, label: str) -> str:
        inv = {v.upper(): k for k, v in self.bobble_labels.items()}
        return inv[label.upper()]


NARRATIVE = Frame(
    name="narrative",
    game=TrustGame(R_A=25, R_B=25, L=100, G=150),
    unit="$k",
    alice_labels={"TRUST": "TRUST", "WALK_OUT": "WALK_OUT", "SIMULATE": "SIMULATE"},
    bobble_labels={"COOPERATE": "COOPERATE", "DEFECT": "DEFECT"},
)

NEUTRAL = Frame(
    name="neutral",
    game=TrustGame(R_A=30, R_B=30, L=60, G=120),
    unit="points",
    alice_labels={"TRUST": "IN", "WALK_OUT": "OUT", "SIMULATE": "CHECK"},
    bobble_labels={"COOPERATE": "X", "DEFECT": "Y"},
)

FRAMES = {f.name: f for f in (NARRATIVE, NEUTRAL)}

# Simulation costs. Both frames have c* = 20, so the same grid covers
# c = 0 (Prop. 7 boundary), three points inside (0, c*), and two above c*.
C_GRID = (0, 5, 10, 15, 25, 50)
