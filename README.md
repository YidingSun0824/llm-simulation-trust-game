# LLM agents in the trust game with simulation

A small behavioral experiment built on Kovařík, Oesterheld & Conitzer, [*Game Theory with Simulation of Other Players*](https://www.cs.cmu.edu/~conitzer/simulationIJCAI23.pdf) (IJCAI 2023). Claude models play both roles of the paper's trust game. The truster can pay *c* to run a copy of the trustee before deciding. We compare the agents' behavior with the paper's equilibrium benchmarks.

**Results at a glance** (3,380 games, Claude Haiku 5.5 and Sonnet 5.5; full note: [`writeup/note.pdf`](writeup/note.pdf), numbers: [`results/REPORT.md`](results/REPORT.md)):

* With no simulation available, the truster walks out in every game. With cheap simulation, 56–100% of games end in cooperation, as Thm. 4 predicts qualitatively.
* The cooperation does not come from the mixed equilibrium. The trustee essentially commits to cooperate instead of randomizing. The truster rarely trusts blindly and pays for verification it does not need. Play resembles the c → 0⁺ limit equilibrium at every c < c\*.
* Sonnet's simulation rate is flat in c on (0, c\*), as Prop. 11 predicts, but sits near 100% rather than 3/4. Haiku's rate falls with c, and Haiku keeps simulating above c\*.
* How good a "copy" of an LLM is as a simulation depends on the model's output entropy. A fresh Haiku copy disagrees with the real answer up to 37% of the time; Sonnet's copies almost never do.

* **Design, hypotheses and tests:** [`PREREG.md`](PREREG.md), committed before any main-run data.
* **The game theory, exactly:** [`simtrust/game.py`](simtrust/game.py). Unit tests in [`tests/test_game.py`](tests/test_game.py) reproduce every number in the paper's Section 1.1 and Fig. 2: π_A(S) = 5/6, π_B(D) = 7/100, the $16.25k / $25k gains, c\* = 20, and the walk-out families.
* **The prompts:** [`simtrust/prompts.py`](simtrust/prompts.py). This is where experimental bias would hide, so it is worth reading first.

## Quick start (first time using an API)

You need Python 3.10+ and an Anthropic API key from [platform.claude.com](https://platform.claude.com/settings/keys). Set a spend limit on the Billing page.

```bash
git clone git@github.com:<you>/llm-simulation-trust-game.git
cd llm-simulation-trust-game
python3 -m venv .venv && source .venv/bin/activate      # Windows: py -m venv .venv; .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # then open .env and paste your key after ANTHROPIC_API_KEY=
python -m pytest -q                                    # 40 tests, no API calls
```

Then run, in this order:

| Step | Command | What it does | Cost |
|---|---|---|---|
| 1 | `python -m simtrust check` | One real Alice and one Bobble call per model. Confirms the key and request settings work. | < $0.01 |
| 2 | `python -m simtrust run --preset pilot` | Every cell, 3 games, Haiku | ~$0.05 |
| 3 | `python -m simtrust show --n 10` | **Read the transcripts.** Check for refusals, misunderstanding, or recitation of the paper. | free |
| 4 | `python -m simtrust run --preset pilot-sonnet` | Every cell once on Sonnet | ~$0.30 |
| 5 | `python -m simtrust estimate --preset main` | Cost estimate from the pilots' measured tokens | free |
| 6 | `python -m simtrust run --preset main --budget 25` | The experiment, ~3.4k games. Resumable: if it stops, run it again. | ~$15–20 |
| 7 | `python -m simtrust analyze` | `results/REPORT.md`, `results/summary_by_cell.csv`, `results/figures/*.png` | free |

Every invocation of `run` has a hard `--budget` stop, and your Console spend limit is a second fuse. Re-running a preset only plays the games that are missing.

You can try the whole pipeline with no key and no cost:

```bash
python -m simtrust run --preset main --mock
python -m simtrust analyze --input results/raw/main-mock.jsonl --tag mock
```

The mock agent has planted effects: Alice simulates less as c rises, and Bobble defects less when it is informed. There is no frame effect. The preregistered tests should recover the first two and find nothing for the third, and they do.

## Design in one paragraph

Cells are frame (neutral, which is primary, or narrative, the paper's own story) × c ∈ {0, 5, 10, 15, 25, 50} × trustee informed/uninformed, plus a no-simulation baseline per frame. That gives 26 cells per model.

In each game, Alice and Bobble answer independently. If Alice simulates, Bobble's identical prompt is sent again to produce the sandboxed copy. The same game is then scored under two physical notions of simulating an LLM:

* **perfect:** the copy shows the real answer, like a seeded replay.
* **sampled:** the copy is a fresh run, so it can disagree with the real answer.

The neutral frame uses different payoffs (30/30, −60/120). Its benchmarks are therefore 3/4 and c/60 rather than the paper's 5/6 and c/100, so recited paper numbers can be detected.

## Repository map

```
simtrust/game.py        TG^c_sim: payoffs, best responses, VoIS, closed-form equilibria, NE checker
simtrust/frames.py      neutral and narrative presentations, cost grid
simtrust/prompts.py     prompt templates (randomized option order)
simtrust/parse.py       DECISION / BELIEF parsing
simtrust/agents.py      Anthropic API client; mock agent for tests
simtrust/runner.py      async game loop, resume, budget stop, JSONL logging
simtrust/stats.py       the preregistered tests
simtrust/analysis.py    per-cell tables, best-response / regret / VoIS analysis, figures, REPORT.md
results/raw/*.jsonl     every game, including full model outputs, one JSON object per line
results/prompts/*.txt   every distinct prompt actually sent (referenced by hash from the logs)
```

## How this was built

The design is mine. The game-theoretic details follow the paper, and the operationalization questions (what counts as simulation, and whether the trustee knows) come from my reading note. The code was written with Claude (Anthropic) as a coding assistant. I reviewed the prompts, the hypotheses and the equilibrium code. Model outputs are logged verbatim.
