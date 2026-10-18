import random

import pytest

from simtrust.frames import FRAMES, NARRATIVE, NEUTRAL
from simtrust.parse import parse_belief, parse_decision
from simtrust.prompts import alice_prompt, bobble_prompt


def test_parse_decision_variants():
    labs = ["TRUST", "WALK_OUT", "SIMULATE"]
    assert parse_decision("blah\nDECISION: SIMULATE\nBELIEF: 10", labs) == "SIMULATE"
    assert parse_decision("DECISION: WALKOUT", labs) == "WALK_OUT"
    assert parse_decision("**DECISION:** TRUST", labs) == "TRUST"
    assert parse_decision("I think TRUST.\nDECISION: <TRUST>", labs) == "TRUST"
    # last DECISION line wins
    assert parse_decision("DECISION: TRUST\n...on reflection\nDECISION: SIMULATE", labs) == "SIMULATE"
    assert parse_decision("no decision here", labs) is None
    assert parse_decision("DECISION: MAYBE", labs) is None
    assert parse_decision("DECISION: Y", ["X", "Y"]) == "Y"


def test_parse_belief():
    assert parse_belief("BELIEF: 20") == pytest.approx(0.2)
    assert parse_belief("BELIEF: 7.5%") == pytest.approx(0.075)
    assert parse_belief("BELIEF: 0.3") == pytest.approx(0.3)
    assert parse_belief("BELIEF: 100") == pytest.approx(1.0)
    assert parse_belief("BELIEF: 250") is None
    assert parse_belief("nothing") is None


@pytest.mark.parametrize("frame", list(FRAMES.values()))
@pytest.mark.parametrize("c", [None, 0, 7, 25])
@pytest.mark.parametrize("informed", [True, False])
def test_prompts_render_and_are_consistent(frame, c, informed):
    _, a, ma = alice_prompt(frame, c, informed, random.Random(0))
    _, b, mb = bobble_prompt(frame, c, informed, random.Random(0))
    sim_label = frame.alice_labels["SIMULATE"]
    # Alice sees the simulation option iff it exists
    assert (sim_label in a) == (c is not None)
    # Bobble is told about simulation iff informed and it exists
    told = c is not None and informed
    assert ("sandbox" in b) == told
    # no leakage of theory or the paper
    for text in (a, b):
        low = text.lower()
        for banned in ("equilibri", "nash", "ijcai", "conitzer", "kovar", "oesterheld", "5/6", "1/6"):
            assert banned not in low
    # neutral frame must not mention the story
    if frame is NEUTRAL:
        for word in ("Alice", "Bobble", "savings", "$"):
            assert word not in a and word not in b
    # the decision line lists exactly the available actions
    assert len(ma["order"]) == (3 if c is not None else 2)
    assert set(mb["order"]) == {"COOPERATE", "DEFECT"}


def test_option_order_is_randomized():
    orders = {tuple(alice_prompt(NARRATIVE, 7, True, random.Random(s))[2]["order"]) for s in range(40)}
    assert len(orders) == 6


def test_payoff_numbers_in_tables():
    _, a, _ = alice_prompt(NARRATIVE, 7, True, random.Random(1))
    assert "(+18, +25)" in a and "(-7, 0)" in a and "(-100, +150)" in a
    _, a, _ = alice_prompt(NEUTRAL, 7, True, random.Random(1))
    assert "(+23, +30)" in a and "(-60, +120)" in a
