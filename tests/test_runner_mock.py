import asyncio
import json

from simtrust.agents import MockAgent
from simtrust.analysis import analyze
from simtrust.config import PRESETS, cells
from simtrust.runner import Runner


def test_pilot_preset_end_to_end(tmp_path):
    preset = PRESETS["pilot"]
    out = tmp_path / "raw" / "pilot.jsonl"
    runner = Runner({m: MockAgent(m) for m in preset["models"]}, out, budget=1.0, concurrency=4, verbose=False)
    summary = asyncio.run(runner.run(preset))
    n_expected = len(list(cells(preset))) * sum(preset["models"].values())
    assert summary["games_written"] == n_expected
    recs = [json.loads(l) for l in out.read_text().splitlines()]
    assert len({r["game_id"] for r in recs}) == n_expected
    for r in recs:
        if r["alice_action"] == "SIMULATE":
            assert r["copy_attempts"], "a simulating Alice must trigger a copy call"
        if not r["sim_available"]:
            assert r["alice_action"] in (None, "TRUST", "WALK_OUT")
        if r["alice_action"] and r["bobble_action"] and r["alice_action"] != "SIMULATE":
            assert r["u_alice_sampled"] == r["u_alice_perfect"]
    # resume: nothing left to do
    again = asyncio.run(Runner({m: MockAgent(m) for m in preset["models"]}, out, verbose=False).run(preset))
    assert again["games_written"] == 0
    # analysis runs on the output
    t = analyze([out], tmp_path, tag="t")
    assert len(t) == len(list(cells(preset)))
    assert (tmp_path / "t_REPORT.md").exists()


def test_budget_stop(tmp_path):
    class Pricey(MockAgent):
        def cost(self, i, o):
            return 0.01
    preset = PRESETS["pilot"]
    runner = Runner({m: Pricey(m) for m in preset["models"]}, tmp_path / "x.jsonl", budget=0.05, concurrency=1,
                    verbose=False)
    s = asyncio.run(runner.run(preset))
    assert s["stopped_because"] and "budget" in s["stopped_because"]
    assert s["spent_usd"] < 0.2
