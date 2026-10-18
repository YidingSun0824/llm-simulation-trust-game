"""Aggregate logged games into tables and figures, and compare them with the equilibrium benchmarks.

Interpretation caveat (also in PREREG.md): an LLM answering one prompt is not an equilibrium player.
We treat the empirical frequency of answers in a cell as that model's *behavioral strategy* and
compare it with the NE of the game it was told about.  The benchmarks are reference points, not
predictions the models are obliged to meet.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd

from .frames import FRAMES
from .game import best_responses

# ---------------------------------------------------------------- style (dataviz reference palette)
INK = "#0b0b0b"
INK_2 = "#52514e"
INK_3 = "#8a8984"
GRID = "#e6e5e0"
SURFACE = "#fcfcfb"
SERIES = {"informed": "#2a78d6", "uninformed": "#eb6834", "baseline": INK_3}
SERIES_FID = {"perfect": "#2a78d6", "sampled": "#eb6834"}

RECITATION = {
    "five_sixths": r"5\s*/\s*6|83\.3",
    "one_sixth": r"1\s*/\s*6|16\.7",
    "paper_names": r"kova[rř]|oesterheld|conitzer|ijcai",
    "bobble_in_neutral": r"bobble",
    "equilibrium_talk": r"equilibri|nash|indifferen|mixed strateg",
}


def wilson(k: int, n: int, z: float = 1.96):
    if n == 0:
        return (np.nan, np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def load(paths: Iterable[Path]) -> pd.DataFrame:
    rows = []
    for p in paths:
        for line in Path(p).read_text().splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise SystemExit("no records found in " + ", ".join(map(str, paths)))
    df = pd.DataFrame(rows)
    df["c_key"] = df["c"].apply(lambda v: "none" if v is None or (isinstance(v, float) and math.isnan(v)) else f"{v:g}")
    df["condition"] = np.where(~df["sim_available"], "baseline", np.where(df["informed"], "informed", "uninformed"))
    return df


def _last_text(attempts):
    if not attempts:
        return ""
    return attempts[-1].get("text") or ""


def _stop_reasons(attempts):
    return [a.get("stop_reason") for a in attempts or []]


# ---------------------------------------------------------------- per-cell table
def cell_table(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (model, frame, cell), g in df.groupby(["model", "frame", "cell"], sort=False):
        fr = FRAMES[frame]
        game = fr.game
        c = g["c"].iloc[0]
        c = None if c is None or (isinstance(c, float) and math.isnan(c)) else float(c)
        cond = g["condition"].iloc[0]
        th = game.theory_row(c)
        a = g["alice_action"].dropna()
        b = g["bobble_action"].dropna()
        na, nb = len(a), len(b)
        row = {"model": model, "frame": frame, "cell": cell, "condition": cond, "c": c, "games": len(g),
               "alice_n": na, "bobble_n": nb,
               "alice_invalid": len(g) - na, "bobble_invalid": len(g) - nb,
               "refusals": int(sum("refusal" in _stop_reasons(x) for x in g["alice_attempts"]) +
                               sum("refusal" in _stop_reasons(x) for x in g["bobble_attempts"]))}
        for act in ("TRUST", "WALK_OUT", "SIMULATE"):
            p, lo, hi = wilson(int((a == act).sum()), na)
            row[f"alice_{act.lower()}"] = p
            row[f"alice_{act.lower()}_lo"] = lo
            row[f"alice_{act.lower()}_hi"] = hi
        p, lo, hi = wilson(int((b == "DEFECT").sum()), nb)
        row.update({"bobble_defect": p, "bobble_defect_lo": lo, "bobble_defect_hi": hi})
        row["alice_belief_defect_mean"] = g["alice_belief_defect"].dropna().mean()
        row["bobble_belief_trust_mean"] = g["bobble_belief_trust"].dropna().mean()
        # copies: how often does an independent copy disagree with the real answer?
        both = g.dropna(subset=["copy_action", "bobble_action"])
        row["copy_n"] = len(both)
        row["copy_disagree"] = float((both["copy_action"] != both["bobble_action"]).mean()) if len(both) else np.nan
        for fid in ("perfect", "sampled"):
            for who in ("alice", "bobble"):
                col = f"u_{who}_{fid}"
                v = g[col].dropna()
                row[f"{col}_mean"] = v.mean()
                row[f"{col}_se"] = v.std(ddof=1) / math.sqrt(len(v)) if len(v) > 1 else np.nan
        # realized cooperation: Alice ends up dealing with Bobble and Bobble cooperates
        ok = g.dropna(subset=["alice_action", "bobble_action"])
        coop = ((ok["alice_action"] == "TRUST") | (ok["alice_action"] == "SIMULATE")) & (ok["bobble_action"] == "COOPERATE")
        row["outcome_cooperation"] = float(coop.mean()) if len(ok) else np.nan

        # ---- best-response analysis against the OTHER model's empirical behavior in this cell
        pB = row["bobble_defect"]
        if not np.isnan(pB):
            cc = c if c is not None else 0.0
            for fid, sampled in (("perfect", False), ("sampled", True)):
                vals = game.alice_action_values(pB, cc, sampled=sampled)
                if c is None:
                    vals.pop("SIMULATE")
                emp = sum(row[f"alice_{k.lower()}"] * v for k, v in vals.items() if not np.isnan(row[f"alice_{k.lower()}"]))
                row[f"alice_br_{fid}"] = "/".join(best_responses(vals))
                row[f"alice_regret_{fid}"] = max(vals.values()) - emp
            row["vois_empirical"] = game.vois(pB)
        if na:
            pi_a = {k: row[f"alice_{k.lower()}"] for k in ("TRUST", "WALK_OUT", "SIMULATE")}
            if not cond == "informed":
                # an uninformed Bobble faces the baseline game as it was described to it
                pass
            vb = game.bobble_action_values(pi_a)
            row["bobble_br"] = "/".join(best_responses(vb))

        # ---- does each Alice choice best-respond to her OWN stated belief?
        sub = g.dropna(subset=["alice_action", "alice_belief_defect"])
        if len(sub):
            hits = []
            for _, r in sub.iterrows():
                vals = game.alice_action_values(r["alice_belief_defect"], c or 0.0)
                if c is None:
                    vals.pop("SIMULATE")
                hits.append(r["alice_action"] in best_responses(vals, tol=1e-6))
            row["alice_br_to_own_belief"] = float(np.mean(hits))

        row.update({f"theory_{k}": v for k, v in th.items() if k != "c"})
        out.append(row)
    t = pd.DataFrame(out)
    t["c_sort"] = t["c"].fillna(-1)
    return t.sort_values(["model", "frame", "condition", "c_sort"]).drop(columns="c_sort")


def recitation_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, frame), g in df.groupby(["model", "frame"]):
        texts = [_last_text(x) for col in ("alice_attempts", "bobble_attempts", "copy_attempts") for x in g[col]
                 if x]
        row = {"model": model, "frame": frame, "responses": len(texts)}
        for name, pat in RECITATION.items():
            if name == "bobble_in_neutral" and frame != "neutral":
                continue
            rx = re.compile(pat, re.IGNORECASE)
            row[name] = int(sum(bool(rx.search(t)) for t in texts))
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- figures
def _style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK_3)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=INK_2, labelsize=9, length=3)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def _facets(t: pd.DataFrame):
    models = list(dict.fromkeys(t["model"]))
    frames = [f for f in ("neutral", "narrative") if f in set(t["frame"])]
    return models, frames


def _rate_figure(t, ycol, title, ylabel, theory_fn, path, baseline_note):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    models, frames = _facets(t)
    fig, axes = plt.subplots(len(models), len(frames), figsize=(4.6 * len(frames), 3.3 * len(models)),
                             squeeze=False, sharey=True)
    fig.patch.set_facecolor("white")
    for i, m in enumerate(models):
        for j, fr in enumerate(frames):
            ax = axes[i][j]
            _style(ax)
            sub = t[(t["model"] == m) & (t["frame"] == fr)]
            game = FRAMES[fr].game
            cstar = game.breakpoint()
            cmax = max(sub["c"].dropna().max() if sub["c"].notna().any() else 50, 50)
            # theory
            xs = np.linspace(0.001, cstar - 0.001, 50)
            ax.plot(xs, [theory_fn(game, x) for x in xs], color=INK_2, lw=1.6, ls="--", zorder=2)
            xs2 = np.linspace(cstar + 0.001, cmax * 1.05, 20)
            ax.plot(xs2, [theory_fn(game, x) for x in xs2], color=INK_2, lw=1.6, ls="--", zorder=2)
            ax.axvline(cstar, color=INK_3, lw=0.8, ls=":", zorder=1)
            ax.text(cstar, 1.02, f"c* = {cstar:g}", color=INK_2, fontsize=8, ha="center", va="bottom",
                    transform=ax.get_xaxis_transform())
            # baseline (only meaningful for quantities that exist without simulation)
            labels = []  # (y, text) for end-of-line direct labels, de-collided below
            base = sub[sub["condition"] == "baseline"]
            if baseline_note and len(base) and not np.isnan(base[ycol].iloc[0]):
                ax.axhline(base[ycol].iloc[0], color=SERIES["baseline"], lw=1.2, ls=(0, (1, 2)), zorder=1)
                labels.append([base[ycol].iloc[0], baseline_note])
            for cond in ("informed", "uninformed"):
                s = sub[sub["condition"] == cond].sort_values("c")
                if not len(s) or s[ycol].isna().all():
                    continue
                y = s[ycol].values
                lo, hi = s[ycol + "_lo"].values, s[ycol + "_hi"].values
                off = -0.6 if cond == "informed" else 0.6
                ax.errorbar(s["c"] + off, y, yerr=[y - lo, hi - y], color=SERIES[cond], lw=2, marker="o",
                            ms=6, mec="white", mew=1.2, capsize=0, elinewidth=1.2, zorder=3, label=cond)
                labels.append([y[-1], cond])
            # direct labels at the right edge, pushed apart so they never overlap; the legend backs them up
            labels.sort()
            for k in range(1, len(labels)):
                if labels[k][0] - labels[k - 1][0] < 0.075:
                    labels[k][0] = labels[k - 1][0] + 0.075
            for yv, txt in labels:
                ax.text(cmax * 1.05 + 1.5, yv, txt, color=INK_2, fontsize=8, va="center", ha="left")
            ax.set_ylim(-0.03, 1.08)
            ax.set_xlim(-3, cmax * 1.05 + 1)
            ax.set_xticks([0, 5, 10, 15, 20, 25, 50] if cmax <= 50 else ax.get_xticks())
            if i == len(models) - 1:
                ax.set_xlabel("simulation cost c", color=INK_2, fontsize=9)
            if j == 0:
                ax.set_ylabel(f"{m}\n{ylabel}", color=INK, fontsize=9)
            if i == 0:
                ax.set_title(f"{fr} frame", color=INK, fontsize=10, loc="left")
    handles = [plt.Line2D([], [], color=SERIES["informed"], marker="o", lw=2, label="informed (B told it may be simulated)"),
               plt.Line2D([], [], color=SERIES["uninformed"], marker="o", lw=2, label="uninformed"),
               plt.Line2D([], [], color=INK_2, ls="--", lw=1.6, label="equilibrium benchmark"),
               plt.Line2D([], [], color=SERIES["baseline"], ls=(0, (1, 2)), lw=1.2, label="no-simulation baseline")]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=8, labelcolor=INK_2,
               bbox_to_anchor=(0.5, -0.01))
    fig.suptitle(title, x=0.02, ha="left", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0.05, 0.96, 0.95))
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _theory_alice_sim(game, c):
    eq = game.simulation_equilibrium(c)
    return eq["pi_alice"]["SIMULATE"] if eq else 0.0


def _theory_bobble_defect(game, c):
    eq = game.simulation_equilibrium(c)
    return eq["pi_bobble"]["DEFECT"] if eq else np.nan


def _welfare_figure(t, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    models, frames = _facets(t)
    fig, axes = plt.subplots(len(models) * len(frames), 2, figsize=(9.2, 2.9 * len(models) * len(frames)),
                             squeeze=False)
    fig.patch.set_facecolor("white")
    r = 0
    for m in models:
        for fr in frames:
            sub = t[(t["model"] == m) & (t["frame"] == fr)]
            game = FRAMES[fr].game
            unit = FRAMES[fr].unit
            for j, who in enumerate(("alice", "bobble")):
                ax = axes[r][j]
                _style(ax)
                inf = sub[sub["condition"] == "informed"].sort_values("c")
                xs = np.linspace(0.001, game.breakpoint() - 0.001, 40)
                th = [(game.simulation_equilibrium(x) or {}).get(f"u_{who}", 0.0) for x in xs]
                ax.plot(xs, th, color=INK_2, ls="--", lw=1.6)
                ax.plot([game.breakpoint(), max(50, inf["c"].max() if len(inf) else 50)], [0, 0], color=INK_2, ls="--", lw=1.6)
                base = sub[sub["condition"] == "baseline"]
                if len(base):
                    ax.axhline(base[f"u_{who}_perfect_mean"].iloc[0], color=SERIES["baseline"], lw=1.2, ls=(0, (1, 2)))
                for fid, off in (("perfect", -0.6), ("sampled", 0.6)):
                    y = inf[f"u_{who}_{fid}_mean"].values
                    se = inf[f"u_{who}_{fid}_se"].fillna(0).values
                    if len(y):
                        ax.errorbar(inf["c"] + off, y, yerr=1.96 * se, color=SERIES_FID[fid], marker="o", ms=6,
                                    mec="white", mew=1.2, lw=2, elinewidth=1.2, capsize=0)
                ax.set_title(f"{m} · {fr} · {'Alice / A' if who == 'alice' else 'Bobble / B'} payoff ({unit})",
                             color=INK, fontsize=9, loc="left")
                ax.set_xlabel("simulation cost c (informed cells)", color=INK_2, fontsize=8)
            r += 1
    handles = [plt.Line2D([], [], color=SERIES_FID["perfect"], marker="o", lw=2, label="perfect simulation (replay)"),
               plt.Line2D([], [], color=SERIES_FID["sampled"], marker="o", lw=2, label="sampled simulation (fresh copy)"),
               plt.Line2D([], [], color=INK_2, ls="--", lw=1.6, label="simulation-equilibrium payoff"),
               plt.Line2D([], [], color=SERIES["baseline"], ls=(0, (1, 2)), lw=1.2, label="no-simulation baseline")]
    fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=8, labelcolor=INK_2)
    fig.suptitle("Realized payoffs (mean ± 95% CI)", x=0.02, ha="left", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    fig.savefig(path, dpi=180)
    plt.close(fig)


def _vois_figure(t, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    models, frames = _facets(t)
    fig, axes = plt.subplots(len(models), len(frames), figsize=(4.6 * len(frames), 3.3 * len(models)), squeeze=False)
    fig.patch.set_facecolor("white")
    for i, m in enumerate(models):
        for j, fr in enumerate(frames):
            ax = axes[i][j]
            _style(ax)
            sub = t[(t["model"] == m) & (t["frame"] == fr) & (t["condition"] != "baseline")]
            vmax = float(sub["vois_empirical"].max()) if len(sub) and sub["vois_empirical"].notna().any() else 0.0
            ytop = max(25.0, 1.3 * vmax)
            ax.plot([0, ytop], [0, ytop], color=INK_3, lw=1, ls=":")
            ax.text(ytop * 0.97, ytop * 0.97, "VoIS = c ", color=INK_2, fontsize=8, ha="right", va="bottom")
            ax.set_ylim(-1, ytop * 1.08)
            for cond in ("informed", "uninformed"):
                s = sub[sub["condition"] == cond]
                sizes = 30 + 220 * s["alice_simulate"].fillna(0)
                ax.scatter(s["c"], s["vois_empirical"], s=sizes, color=SERIES[cond], edgecolor="white", lw=1.2,
                           zorder=3, label=cond)
            ax.set_xlabel("simulation cost c", color=INK_2, fontsize=9)
            if j == 0:
                ax.set_ylabel(f"{m}\nVoIS of B's empirical strategy", color=INK, fontsize=9)
            if i == 0:
                ax.set_title(f"{fr} frame", color=INK, fontsize=10, loc="left")
    fig.legend(handles=[plt.Line2D([], [], color=SERIES[k], marker="o", lw=0, ms=7, label=k)
                        for k in ("informed", "uninformed")], loc="lower center", ncol=2, frameon=False,
               fontsize=8, labelcolor=INK_2)
    fig.suptitle("Is simulating worth it?  Above the line, simulation pays against B's actual behavior "
                 "(marker size = how often A simulated)", x=0.02, ha="left", color=INK, fontsize=10)
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    fig.savefig(path, dpi=180)
    plt.close(fig)


# ---------------------------------------------------------------- report
def _md_table(df: pd.DataFrame, cols: List[str], fmt: dict) -> str:
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    lines = []
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float) and np.isnan(v):
                cells.append("–")
            elif c in fmt:
                cells.append(fmt[c](v))
            else:
                cells.append(str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return head + "\n".join(lines) + "\n"


def analyze(inputs: List[Path], outdir: Path, tag: str = "") -> pd.DataFrame:
    outdir = Path(outdir)
    figdir = outdir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)
    pre = f"{tag}_" if tag else ""
    df = load(inputs)
    t = cell_table(df)
    t.to_csv(outdir / f"{pre}summary_by_cell.csv", index=False)
    rec = recitation_table(df)
    rec.to_csv(outdir / f"{pre}recitation_check.csv", index=False)

    _rate_figure(t, "alice_simulate", "How often does Alice (Player A) simulate?  (95% Wilson CIs)",
                 "P(simulate)", _theory_alice_sim, figdir / f"{pre}fig1_alice_simulation_rate.png",
                 "")
    _rate_figure(t, "bobble_defect", "How often does Bobble (Player B) defect?  (95% Wilson CIs)",
                 "P(defect)", _theory_bobble_defect, figdir / f"{pre}fig2_bobble_defection_rate.png",
                 "baseline")
    _welfare_figure(t, figdir / f"{pre}fig3_payoffs.png")
    _vois_figure(t, figdir / f"{pre}fig4_value_of_simulation.png")

    pct = lambda v: f"{100 * v:.0f}%"
    num = lambda v: f"{v:.1f}"
    cg = lambda v: "none" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:g}"
    report = [f"# Results summary{(' — ' + tag) if tag else ''}\n",
              f"Inputs: {', '.join(p.name for p in inputs)} · {len(df)} games\n",
              "Theory columns are the simulation-equilibrium benchmarks (0 when no simulation NE exists, "
              "i.e. c ≥ c*). `regret` = Alice's expected loss vs. the best response to Bobble's empirical "
              "defection rate in the same cell.\n"]
    for (m, fr), g in t.groupby(["model", "frame"], sort=False):
        report.append(f"\n## {m} — {fr} frame\n")
        report.append(_md_table(g, ["condition", "c", "alice_n", "alice_trust", "alice_walk_out", "alice_simulate",
                                    "theory_eq_alice_simulate", "bobble_defect", "theory_eq_bobble_defect",
                                    "alice_br_perfect", "alice_regret_perfect", "alice_br_to_own_belief",
                                    "u_alice_perfect_mean", "u_alice_sampled_mean", "copy_disagree"],
                                {"c": cg, "alice_trust": pct, "alice_walk_out": pct, "alice_simulate": pct,
                                 "theory_eq_alice_simulate": pct, "bobble_defect": pct,
                                 "theory_eq_bobble_defect": pct, "alice_regret_perfect": num,
                                 "alice_br_to_own_belief": pct, "u_alice_perfect_mean": num,
                                 "u_alice_sampled_mean": num, "copy_disagree": pct}))
    from .stats import run_tests, tests_markdown
    report.append("\n## Preregistered tests (see PREREG.md)\n\n")
    report.append(tests_markdown(run_tests(df)))
    report.append("\n## Data quality and recitation check\n")
    inv = t.groupby("model")[["games", "alice_invalid", "bobble_invalid", "refusals"]].sum().reset_index()
    report.append(_md_table(inv, list(inv.columns), {}))
    report.append("\nCounts of responses whose text matches each pattern:\n\n")
    report.append(_md_table(rec, list(rec.columns), {}))
    (outdir / f"{pre}REPORT.md").write_text("".join(report))
    print(f"[analyze] wrote {outdir / (pre + 'REPORT.md')}, summary CSV and 4 figures in {figdir}")
    return t
