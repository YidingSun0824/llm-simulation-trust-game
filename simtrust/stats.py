"""The preregistered tests (PREREG.md), as code.  Committed before any main-run data exists.

Every test is run separately for each model; the PRIMARY slice is the neutral frame.
"""
from __future__ import annotations

import math
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy import stats

from .frames import FRAMES

INSIDE = (5, 10, 15)  # simulation costs strictly inside (0, c*) on the grid


def logistic_slope(x: np.ndarray, y: np.ndarray, iters: int = 50) -> Dict[str, float]:
    """Logistic regression y ~ 1 + x by Newton-Raphson; returns slope, Wald SE and two-sided p."""
    X = np.column_stack([np.ones_like(x, dtype=float), x.astype(float)])
    beta = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ beta))
        W = p * (1 - p)
        H = X.T @ (X * W[:, None]) + 1e-9 * np.eye(2)
        step = np.linalg.solve(H, X.T @ (y - p))
        beta += step
        if np.max(np.abs(step)) < 1e-10:
            break
    p = 1 / (1 + np.exp(-X @ beta))
    cov = np.linalg.inv(X.T @ (X * (p * (1 - p))[:, None]) + 1e-9 * np.eye(2))
    se = math.sqrt(cov[1, 1])
    z = beta[1] / se if se > 0 else float("nan")
    return {"slope": float(beta[1]), "se": se, "z": z, "p_two_sided": float(2 * stats.norm.sf(abs(z))),
            "n": int(len(y))}


def _fisher(a_k, a_n, b_k, b_n, alternative):
    table = [[a_k, a_n - a_k], [b_k, b_n - b_k]]
    _, p = stats.fisher_exact(table, alternative=alternative)
    return p


def run_tests(df: pd.DataFrame) -> List[dict]:
    out = []
    for model, gm in df.groupby("model"):
        for frame, g in gm.groupby("frame"):
            tag = {"model": model, "frame": frame, "primary": frame == "neutral"}
            inf = g[g["condition"] == "informed"]
            uninf = g[g["condition"] == "uninformed"]
            base = g[g["condition"] == "baseline"]

            # H1: Alice's simulation rate is flat in c inside (0, c*) under theory; we predict it falls.
            s = inf[inf["c"].isin(INSIDE)].dropna(subset=["alice_action"])
            if len(s) > 5 and s["alice_action"].nunique() > 1:
                r = logistic_slope(s["c"].values, (s["alice_action"] == "SIMULATE").astype(float).values)
                lo = s[s["c"] == min(INSIDE)]
                hi = s[s["c"] == max(INSIDE)]
                out.append({**tag, "test": "H1 sim rate vs c inside (0,c*) [theory: flat; predicted: falls]",
                            "estimate": f"slope {r['slope']:+.3f}/unit c (SE {r['se']:.3f})",
                            "detail": f"P(sim) {(lo['alice_action']=='SIMULATE').mean():.2f} at c={min(INSIDE)} -> "
                                      f"{(hi['alice_action']=='SIMULATE').mean():.2f} at c={max(INSIDE)}",
                            "p": r["p_two_sided"], "n": r["n"]})

            # H2: simulation deters defection: informed B defects less than uninformed B (all c).
            bi, bu = inf.dropna(subset=["bobble_action"]), uninf.dropna(subset=["bobble_action"])
            if len(bi) and len(bu):
                ki, ku = int((bi["bobble_action"] == "DEFECT").sum()), int((bu["bobble_action"] == "DEFECT").sum())
                out.append({**tag, "test": "H2 informed B defects less than uninformed B",
                            "estimate": f"{ki/len(bi):.2f} vs {ku/len(bu):.2f}",
                            "detail": f"{ki}/{len(bi)} vs {ku}/{len(bu)}",
                            "p": _fisher(ki, len(bi), ku, len(bu), "less"), "n": len(bi) + len(bu)})

            # H3: theory says informed B's defection rises linearly (c/L) inside (0,c*); we predict no rise.
            sb = inf[inf["c"].isin(INSIDE)].dropna(subset=["bobble_action"])
            if len(sb) > 5 and sb["bobble_action"].nunique() > 1:
                r = logistic_slope(sb["c"].values, (sb["bobble_action"] == "DEFECT").astype(float).values)
                L = FRAMES[frame].game.L
                out.append({**tag, "test": "H3 informed B defection vs c [theory: rises as c/L; predicted: flat]",
                            "estimate": f"slope {r['slope']:+.3f}/unit c (SE {r['se']:.3f})",
                            "detail": f"theory goes {min(INSIDE)/L:.2f} -> {max(INSIDE)/L:.2f}",
                            "p": r["p_two_sided"], "n": r["n"]})
            elif len(sb):
                out.append({**tag, "test": "H3 informed B defection vs c [theory: rises as c/L; predicted: flat]",
                            "estimate": "no variation", "detail": f"all {len(sb)} answers = {sb['bobble_action'].iloc[0]}",
                            "p": float("nan"), "n": len(sb)})

            # H4 (Theorem 4): with cheap simulation, joint payoff beats the no-simulation baseline.
            ji = inf[inf["c"].isin(INSIDE)].dropna(subset=["u_alice_perfect"])
            jb = base.dropna(subset=["u_alice_perfect"])
            if len(ji) > 1 and len(jb) > 1:
                a = ji["u_alice_perfect"] + ji["u_bobble_perfect"]
                b = jb["u_alice_perfect"] + jb["u_bobble_perfect"]
                t = stats.ttest_ind(a, b, equal_var=False, alternative="greater")
                out.append({**tag, "test": "H4 joint payoff: informed, c in (0,c*), vs baseline",
                            "estimate": f"{a.mean():.1f} vs {b.mean():.1f}", "detail": "Welch t, perfect fidelity",
                            "p": float(t.pvalue), "n": len(a) + len(b)})

            # H5: sampled simulation costs Alice relative to perfect simulation (paired, same games).
            pf = g[g["alice_action"] == "SIMULATE"].dropna(subset=["u_alice_perfect", "u_alice_sampled"])
            if len(pf) > 1:
                d = pf["u_alice_perfect"] - pf["u_alice_sampled"]
                disagree = (pf["copy_action"] != pf["bobble_action"]).mean()
                p = float(stats.wilcoxon(d, alternative="greater").pvalue) if (d != 0).any() else 1.0
                out.append({**tag, "test": "H5 perfect minus sampled Alice payoff, simulating games",
                            "estimate": f"{d.mean():+.2f} per game", "detail": f"copy disagrees in {disagree:.0%}",
                            "p": p, "n": len(pf)})

            # H7: above c*, simulation is never an equilibrium action.
            ab = inf[inf["c"] > FRAMES[frame].game.breakpoint()].dropna(subset=["alice_action"])
            if len(ab):
                k = int((ab["alice_action"] == "SIMULATE").sum())
                out.append({**tag, "test": "H7 simulation rate above c* (theory: 0)",
                            "estimate": f"{k/len(ab):.2f}", "detail": "by c: " + ", ".join(
                                f"{c:g}: {(x['alice_action']=='SIMULATE').mean():.2f}" for c, x in ab.groupby("c")),
                            "p": float("nan"), "n": len(ab)})

    # H6: framing — narrative-frame B defects less than neutral-frame B (moral loading), per model.
    for model, gm in df.groupby("model"):
        bn = gm[gm["frame"] == "narrative"].dropna(subset=["bobble_action"])
        bz = gm[gm["frame"] == "neutral"].dropna(subset=["bobble_action"])
        if len(bn) and len(bz):
            kn, kz = int((bn["bobble_action"] == "DEFECT").sum()), int((bz["bobble_action"] == "DEFECT").sum())
            out.append({"model": model, "frame": "both", "primary": False,
                        "test": "H6 narrative-frame B defects less than neutral-frame B",
                        "estimate": f"{kn/len(bn):.2f} vs {kz/len(bz):.2f}", "detail": f"{kn}/{len(bn)} vs {kz}/{len(bz)}",
                        "p": _fisher(kn, len(bn), kz, len(bz), "less"), "n": len(bn) + len(bz)})
    return out


def tests_markdown(rows: List[dict]) -> str:
    lines = ["| model | frame | test | estimate | detail | n | p |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        p = "–" if r["p"] is None or (isinstance(r["p"], float) and math.isnan(r["p"])) else f"{r['p']:.3g}"
        star = " **(primary)**" if r.get("primary") else ""
        lines.append(f"| {r['model']} | {r['frame']}{star} | {r['test']} | {r['estimate']} | {r['detail']} | {r['n']} | {p} |")
    return "\n".join(lines) + "\n"
