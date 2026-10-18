"""Reproduce every number in Kovarik, Oesterheld & Conitzer (IJCAI'23), Section 1.1 and Fig. 2."""
from fractions import Fraction as F

import pytest

from simtrust.frames import NARRATIVE, NEUTRAL
from simtrust.game import TrustGame

TG = NARRATIVE.game  # R_A = R_B = 25, L = 100, G = 150


def test_paper_c7_numbers():
    eq = TG.simulation_equilibrium(7)
    assert eq["pi_bobble"]["DEFECT"] == pytest.approx(7 / 100)          # pi_B(D) = 7/100
    assert eq["pi_alice"]["SIMULATE"] == pytest.approx(1 - 25 / 150)     # pi_A(S) = 5/6
    assert eq["pi_alice"]["TRUST"] == pytest.approx(25 / 150)            # pi_A(T) = 1/6
    assert eq["pi_alice"]["WALK_OUT"] == 0
    # "better off by $16.25k, resp. $25k relative to the (defect, walk-out) equilibrium"
    assert eq["u_alice"] == pytest.approx(16.25)
    assert eq["u_bobble"] == pytest.approx(25)
    assert TG.is_nash(eq["pi_alice"], eq["pi_bobble"], c=7)


def test_breakpoint_is_20():
    assert TG.breakpoint() == pytest.approx(20)
    assert NEUTRAL.game.breakpoint() == pytest.approx(20)


@pytest.mark.parametrize("c", [0.5, 3, 7, 12.5, 19.9])
def test_simulation_eq_family_fig2(c):
    """Fig. 2, row (0, 20): (25/150, 0, 1-25/150) and (1 - c/100, c/100)."""
    eq = TG.simulation_equilibrium(c)
    assert eq["pi_bobble"]["DEFECT"] == pytest.approx(c / 100)
    assert TG.is_nash(eq["pi_alice"], eq["pi_bobble"], c=c)
    # Lemma 10: in a NE where the simulator mixes, VoIS(pi_2) = c
    assert TG.vois(eq["pi_bobble"]["DEFECT"]) == pytest.approx(c)


@pytest.mark.parametrize("c", [20.5, 25, 50])
def test_no_simulation_eq_above_breakpoint(c):
    assert TG.simulation_equilibrium(c) is None
    # the would-be simulation profile is not an equilibrium there
    t = 25 / 150
    pi_a = {"TRUST": t, "WALK_OUT": 0, "SIMULATE": 1 - t}
    pi_b = {"COOPERATE": 1 - c / 100, "DEFECT": min(c / 100, 1)}
    assert not TG.is_nash(pi_a, pi_b, c=c)


def test_walkout_family_fig2():
    # (0, 20): walk-out with pi_B(C) = c/25 at the boundary, i.e. p = 1 - c/25
    for c in (2, 10, 18):
        p = TG.walkout_equilibria_min_defect(c)
        assert p == pytest.approx(1 - c / 25)
        assert TG.is_nash({"WALK_OUT": 1}, {"COOPERATE": 1 - p, "DEFECT": p}, c=c)
        assert not TG.is_nash({"WALK_OUT": 1}, {"COOPERATE": 1 - p + 0.01, "DEFECT": p - 0.01}, c=c)
    # (20, inf): walk-out and (100/125, 25/125)
    for c in (25, 50):
        p = TG.walkout_equilibria_min_defect(c)
        assert p == pytest.approx(25 / 125)
        assert TG.is_nash({"WALK_OUT": 1}, {"COOPERATE": 1 - p, "DEFECT": p}, c=c)


def test_no_sim_trust_game_has_only_walkout_equilibria():
    # In TG itself, Bobble defects with prob >= 1/5 and Alice walks out.
    assert TG.is_nash({"WALK_OUT": 1}, {"COOPERATE": 0.8, "DEFECT": 0.2}, c=None)
    assert TG.is_nash({"WALK_OUT": 1}, {"DEFECT": 1}, c=None)
    assert not TG.is_nash({"TRUST": 1}, {"COOPERATE": 1}, c=None)  # Bobble would defect


def test_negative_cost_is_commitment():
    # Prop. 7(i): with subsidized simulation, (SIMULATE, COOPERATE) is the outcome.
    assert TG.is_nash({"SIMULATE": 1}, {"COOPERATE": 1}, c=-1)
    assert not TG.is_nash({"TRUST": 1}, {"COOPERATE": 1}, c=-1)


def test_prop11_simulator_strategy_constant_in_c():
    """Prop. 11 corollary: inside (0, c*), Alice's simulation rate does not depend on c."""
    rates = {TG.simulation_equilibrium(c)["pi_alice"]["SIMULATE"] for c in (1, 5, 10, 15, 19)}
    assert len({round(r, 12) for r in rates}) == 1


def test_neutral_frame_numbers_differ_from_paper():
    g = NEUTRAL.game
    eq = g.simulation_equilibrium(10)
    assert eq["pi_alice"]["SIMULATE"] == pytest.approx(3 / 4)
    assert eq["pi_bobble"]["DEFECT"] == pytest.approx(10 / 60)
    assert g.is_nash(eq["pi_alice"], eq["pi_bobble"], c=10)


def test_sampled_simulation_values():
    # With an independent copy, SIMULATE is worth (1-p)*value(TRUST) - c.
    p, c = 0.1, 7
    v = TG.alice_action_values(p, c, sampled=True)
    trust = 0.9 * 25 - 0.1 * 100
    assert v["SIMULATE"] == pytest.approx(0.9 * trust - c)
    # deterministic Bobble => sampled == perfect
    assert TG.alice_action_values(0.0, c, sampled=True)["SIMULATE"] == pytest.approx(
        TG.alice_action_values(0.0, c)["SIMULATE"])


def test_exact_fractions():
    g = TrustGame(R_A=F(25), R_B=F(25), L=F(100), G=F(150))
    eq = g.simulation_equilibrium(F(7))
    assert eq["pi_alice"]["SIMULATE"] == F(5, 6)
    assert eq["pi_bobble"]["DEFECT"] == F(7, 100)
    assert eq["u_alice"] == F(65, 4)


def test_payoff_table():
    assert TG.payoff("SIMULATE", "COOPERATE", 7) == (18, 25)
    assert TG.payoff("SIMULATE", "DEFECT", 7) == (-7, 0)
    assert TG.payoff("TRUST", "DEFECT") == (-100, 150)
    assert TG.payoff_sampled("SIMULATE", "DEFECT", "COOPERATE", 7) == (-107, 150)
    assert TG.payoff_sampled("SIMULATE", "COOPERATE", "DEFECT", 7) == (-7, 0)
