"""The trust game with simulation, TG^c_sim (Kovarik, Oesterheld & Conitzer, IJCAI 2023).

Players
-------
Alice (P1, the truster / simulator):  TRUST, WALK_OUT, and (if simulation is available) SIMULATE
Bobble (P2, the trustee / simulated): COOPERATE, DEFECT

Generalized payoffs (Alice, Bobble):
                  COOPERATE        DEFECT
    TRUST         (R_A, R_B)       (-L, G)
    WALK_OUT      (0, 0)           (0, 0)
    SIMULATE      (R_A - c, R_B)   (-c, 0)      # simulate, then best-respond to what is seen

The paper's running example is R_A = R_B = 25, L = 100, G = 150 (in $k).

Everything here is exact closed-form game theory; nothing in this module touches an LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

ALICE_ACTIONS = ("TRUST", "WALK_OUT", "SIMULATE")
BOBBLE_ACTIONS = ("COOPERATE", "DEFECT")


@dataclass(frozen=True)
class TrustGame:
    R_A: float  # Alice's gain when she trusts and Bobble cooperates
    R_B: float  # Bobble's gain when Alice trusts and Bobble cooperates
    L: float  # Alice's loss (positive number) when she trusts and Bobble defects
    G: float  # Bobble's gain when Alice trusts and Bobble defects

    def __post_init__(self):
        if not (self.R_A > 0 and self.R_B > 0 and self.L > 0 and self.G > self.R_B):
            raise ValueError("need R_A, R_B, L > 0 and G > R_B (defection must be tempting)")

    # ------------------------------------------------------------------ payoffs
    def payoff(self, a: str, b: str, c: float = 0.0) -> Tuple[float, float]:
        """(u_Alice, u_Bobble) for pure actions in TG^c_sim (perfect simulation)."""
        if a == "TRUST":
            return (self.R_A, self.R_B) if b == "COOPERATE" else (-self.L, self.G)
        if a == "WALK_OUT":
            return (0.0, 0.0)
        if a == "SIMULATE":
            # Alice sees b and best-responds: trust a cooperator, walk out on a defector.
            return (self.R_A - c, self.R_B) if b == "COOPERATE" else (-c, 0.0)
        raise ValueError(a)

    def payoff_sampled(self, a: str, b_real: str, b_copy: Optional[str], c: float) -> Tuple[float, float]:
        """Payoffs when SIMULATE runs an *independent* copy of Bobble (sampled simulation).

        Alice best-responds to the copy's action b_copy, but the real outcome is
        determined by the real action b_real.  For a != SIMULATE this equals payoff().
        """
        if a != "SIMULATE":
            return self.payoff(a, b_real, c)
        follow = "TRUST" if b_copy == "COOPERATE" else "WALK_OUT"
        ua, ub = self.payoff(follow, b_real, 0.0)
        return (ua - c, ub)

    # ------------------------------------------------------- expected payoffs
    def alice_action_values(self, p_defect: float, c: float, sampled: bool = False) -> Dict[str, float]:
        """Alice's expected payoff of each pure action against Bobble's mixed strategy."""
        p = p_defect
        trust = (1 - p) * self.R_A - p * self.L
        sim_perfect = (1 - p) * self.R_A - c
        # sampled: Alice trusts iff the independent copy cooperates (prob 1-p), then faces the real Bobble
        sim_sampled = (1 - p) * trust - c
        return {"TRUST": trust, "WALK_OUT": 0.0, "SIMULATE": sim_sampled if sampled else sim_perfect}

    def bobble_action_values(self, pi_alice: Dict[str, float]) -> Dict[str, float]:
        """Bobble's expected payoff of each pure action against Alice's mixed strategy (perfect sim)."""
        t = pi_alice.get("TRUST", 0.0)
        s = pi_alice.get("SIMULATE", 0.0)
        return {"COOPERATE": (t + s) * self.R_B, "DEFECT": t * self.G}

    # ------------------------------------------------------ key quantities
    def breakpoint(self) -> float:
        """c* : simulation equilibria exist exactly for 0 < c < c*.

        Alice must weakly prefer TRUST to WALK_OUT at Bobble's indifference-inducing
        defection rate p = c / L, i.e. R_A - p (R_A + L) >= 0  <=>  c <= L R_A / (R_A + L).
        (Paper example: 100 * 25 / 125 = 20.)
        """
        return self.L * self.R_A / (self.R_A + self.L)

    def trust_threshold(self) -> float:
        """Defection rate at which Alice is indifferent between TRUST and WALK_OUT (no simulation)."""
        return self.R_A / (self.R_A + self.L)

    def vois(self, p_defect: float) -> float:
        """Value of information of simulation (Def. 8) against Bobble's mixed strategy (p_defect).

        VoIS = E_b[max_a u_A(a, b)] - max_a E_b[u_A(a, b)], over Alice's ORIGINAL actions {TRUST, WALK_OUT}.
        """
        p = p_defect
        informed = (1 - p) * self.R_A + p * 0.0
        uninformed = max((1 - p) * self.R_A - p * self.L, 0.0)
        return informed - uninformed

    # ------------------------------------------------------ equilibria
    def simulation_equilibrium(self, c: float) -> Optional[dict]:
        """The (unique) simulation NE of TG^c_sim for 0 < c < c*; None otherwise.

        Bobble's indifference pins down Alice:   R_B (t + s) = G t, t + s = 1  =>  t = R_B / G.
        Alice's indifference pins down Bobble:   TRUST ~ SIMULATE  =>  p L = c  =>  p = c / L.
        (Paper: t = 25/150 = 1/6, s = 5/6, p = c/100.)
        """
        if not (0 < c < self.breakpoint()):
            return None
        t = self.R_B / self.G
        p = c / self.L
        pi_a = {"TRUST": t, "WALK_OUT": 0.0, "SIMULATE": 1 - t}
        pi_b = {"COOPERATE": 1 - p, "DEFECT": p}
        u_a = self.R_A - p * (self.R_A + self.L)  # = value of TRUST = value of SIMULATE
        u_b = self.R_B
        return {"pi_alice": pi_a, "pi_bobble": pi_b, "u_alice": u_a, "u_bobble": u_b}

    def walkout_equilibria_min_defect(self, c: Optional[float]) -> float:
        """Smallest Bobble defection rate consistent with an equilibrium where Alice walks out.

        WALK_OUT >= TRUST     <=>  p >= R_A / (R_A + L)
        WALK_OUT >= SIMULATE  <=>  p >= 1 - c / R_A          (only if simulation is available)
        Any p in [this value, 1] gives a NE with payoffs (0, 0).  (Paper Fig. 2: (c/25, 1 - c/25).)
        """
        lo = self.trust_threshold()
        if c is not None:
            lo = max(lo, 1 - c / self.R_A)
        return min(max(lo, 0.0), 1.0)

    def is_nash(self, pi_a: Dict[str, float], pi_b: Dict[str, float], c: Optional[float], tol: float = 1e-9) -> bool:
        """Check a profile is a NE of TG (c=None, no SIMULATE action) or TG^c_sim (perfect simulation)."""
        actions_a = ["TRUST", "WALK_OUT"] + ([] if c is None else ["SIMULATE"])
        if c is None and pi_a.get("SIMULATE", 0.0) > tol:
            return False
        p = pi_b.get("DEFECT", 0.0)
        va = self.alice_action_values(p, 0.0 if c is None else c)
        va = {a: va[a] for a in actions_a}
        ua = sum(pi_a.get(a, 0.0) * va[a] for a in actions_a)
        if max(va.values()) > ua + tol:
            return False
        vb = self.bobble_action_values(pi_a)
        ub = (1 - p) * vb["COOPERATE"] + p * vb["DEFECT"]
        return max(vb.values()) <= ub + tol

    def theory_row(self, c: Optional[float]) -> dict:
        """Benchmark predictions for one experimental cell (c=None means no simulation available)."""
        row = {
            "c": c,
            "c_star": self.breakpoint(),
            "trust_threshold": self.trust_threshold(),
            "walkout_min_defect": self.walkout_equilibria_min_defect(c),
        }
        eq = None if c is None else self.simulation_equilibrium(c)
        if c is not None and c <= 0:
            # c -> 0+ limit of the simulation equilibrium (Lemma 14); at c = 0 the outcome is cooperation.
            t = self.R_B / self.G
            eq = {"pi_alice": {"TRUST": t, "WALK_OUT": 0.0, "SIMULATE": 1 - t},
                  "pi_bobble": {"COOPERATE": 1.0, "DEFECT": 0.0},
                  "u_alice": self.R_A, "u_bobble": self.R_B}
        if eq:
            row.update({
                "sim_eq_exists": True,
                "eq_alice_trust": eq["pi_alice"]["TRUST"],
                "eq_alice_simulate": eq["pi_alice"]["SIMULATE"],
                "eq_bobble_defect": eq["pi_bobble"]["DEFECT"],
                "eq_u_alice": eq["u_alice"],
                "eq_u_bobble": eq["u_bobble"],
            })
        else:
            row.update({"sim_eq_exists": False, "eq_alice_trust": 0.0, "eq_alice_simulate": 0.0,
                        "eq_bobble_defect": None, "eq_u_alice": 0.0, "eq_u_bobble": 0.0})
        return row


def best_responses(values: Dict[str, float], tol: float = 1e-9) -> List[str]:
    m = max(values.values())
    return [a for a, v in values.items() if v >= m - tol]
