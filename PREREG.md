# Preregistration

**Project:** LLM agents in the trust game with simulation (after Kovařík, Oesterheld & Conitzer, *Game Theory with Simulation of Other Players*, IJCAI 2023)
**Author:** Yiding Sun (Stony Brook University)
**Status:** LOCKED on 2026-10-17 at 23:05 ET. Yiding Sun reviewed the prompts (`REVIEW_PROMPTS.md`) and the hypotheses and approved both unchanged before the main run. The hypotheses are identical to commit `4b64752`, which was written before any API call. Pilot runs (`pilot`, `pilot-sonnet`) were used only to check prompts, parsing and cost, and they are excluded from every test below. Later changes appear only in §6.
**Blindness:** the design was fixed without reading the FOCAL group's draft on LLM agents and simulation, which Prof. Conitzer offered to share.

---

## 1. Question

The paper studies TG^c_sim. This is a trust game in which the truster (Alice, P1) can pay *c* to simulate the trustee (Bobble, P2) and then best-respond to the action the simulation reveals. Its predictions are sharp:

* For 0 < c < c\*, the simulation equilibrium has Alice simulating with probability 1 − R_B/G. This probability is **constant in c** (Prop. 11). Bobble defects with probability c/L, which is **increasing in c** (Lemma 10: VoIS = c).
* For c > c\*, simulation is never used (Prop. 7(ii), Prop. 12).
* Simulation creates equilibria that Pareto-improve on the no-simulation game (Thm. 4).

We ask how LLM agents actually behave when they are placed in the roles of this game, and how that behavior compares with the benchmarks. Two LLM-specific issues are central:

1. **What "simulation" means for an LLM.** A copy of a sampled model reveals a sample, not the realized action. We implement two physical versions from the *same* games:
   * **perfect**: the simulation reveals the real answer, as in a seeded replay.
   * **sampled**: the simulation reveals an independent fresh answer to the identical prompt, which is closer to the AAMAS'25 "unpredictable randomisation" setting.
2. **Whether the simulated agent knows it may be simulated.** In the informed condition the trustee is told about simulation. In the uninformed condition it is not.

## 2. Design

| Factor | Levels |
|---|---|
| Model | `claude-haiku-5-5` (N = 80 games/cell), `claude-sonnet-5-5` (N = 50 games/cell). Both roles are played by the same model in separate, independent calls. |
| Frame | **neutral** (primary): Player A/B, IN/OUT/CHECK, X/Y, payoffs R_A = R_B = 30, L = 60, G = 120. **narrative**: the paper's Alice/Bobble story and numbers, R_A = R_B = 25, L = 100, G = 150. |
| Simulation cost c | 0, 5, 10, 15, 25, 50, plus a no-simulation baseline. c\* = 20 in both frames. |
| Trustee informed? | informed / uninformed (only meaningful when simulation exists) |
| Simulation fidelity | perfect / sampled. These are resolved from the same games, not a separate prompt. |

The neutral frame is primary because the narrative frame confounds strategy with (a) possible recall of the paper and (b) moral loading, since "defect" there means defrauding a customer.

Benchmarks:

| | neutral | narrative |
|---|---|---|
| π_A(SIMULATE), 0 < c < 20 | 3/4 | 5/6 |
| π_B(DEFECT), 0 < c < 20 | c/60 | c/100 |
| c\* | 20 | 20 |

**Procedure per game.**
1. Alice and Bobble each answer their own prompt once. They are asked for at most 100 words of reasoning, then `DECISION:` and `BELIEF:` lines. Alice's belief is P(B defects); Bobble's belief is P(A trusts blindly).
2. If Alice chooses SIMULATE, Bobble's identical prompt is sent once more. That answer is the sandboxed copy.
3. Option order is randomized per call.

Model settings: default sampling (temperature is not settable on these models), no up-front thinking, effort `medium`.

## 3. Hypotheses and tests

Each test is run separately per model and per frame. The neutral frame is the confirmatory one; the narrative frame is reported alongside it. The code is in `simtrust/stats.py` and is committed with this file.

* **H1 (Prop. 11, headline).** Inside (0, c\*), the informed-condition simulation rate *falls* as c rises, whereas theory says it is flat.
  *Test:* logistic regression of SIMULATE on c, using c ∈ {5, 10, 15} and the informed condition. A negative slope with p < .05 supports H1. A non-negative or insignificant slope is reported as consistent with the theory's flatness.
* **H2 (deterrence).** The informed trustee defects less than the uninformed trustee, pooled over c.
  *Test:* one-sided Fisher exact test.
* **H3 (Lemma 10).** Theory says the informed trustee's defection rate rises linearly in c. We predict it does not rise; we expect it to stay near zero.
  *Test:* logistic slope on c ∈ {5, 10, 15}, informed condition. Reported in either direction.
* **H4 (Thm. 4).** With simulation available and c ∈ {5, 10, 15} (informed), realized joint payoff under perfect fidelity exceeds the no-simulation baseline.
  *Test:* one-sided Welch t-test.
* **H5 (fidelity).** In games where Alice simulates, her payoff under sampled simulation is lower than under perfect simulation.
  *Test:* paired one-sided Wilcoxon test. The copy-disagreement rate is reported as the mechanism.
* **H6 (framing).** The narrative-frame trustee defects less than the neutral-frame trustee, pooled over cells.
  *Test:* one-sided Fisher exact test, per model.
* **H7 (Prop. 7(ii)).** Above c\* (c = 25, 50), simulation is an equilibrium action with probability 0. We expect a non-zero rate at c = 25, because the model does not compute c\*, and a near-zero rate at c = 50. Descriptive only.

**Secondary and descriptive outputs**
* Alice's regret against the best response to Bobble's empirical strategy in the same cell.
* The share of Alice's choices that best-respond to her *own* stated belief.
* The VoIS of Bobble's empirical strategy compared with c.
* Refusal rates.
* A recitation check: counts of responses mentioning 5/6, 1/6, the paper's authors or venue, "Bobble" in the neutral frame, or equilibrium vocabulary.

No correction for multiple comparisons is applied. This is a small exploratory study, and every test that was run is reported.

## 4. Exclusions and stopping

* An answer with no parseable `DECISION:` line is resampled up to twice. If it is still unparseable, that player's action is missing and the game is excluded from analyses that need it. Exclusion counts are reported per cell.
* A safety refusal (`stop_reason = refusal`) is not resampled. It is recorded and reported as data.
* There is no optional stopping on results. The run ends when the design is complete or the budget stop is reached; the budget stop only applies to cost. The job order interleaves cells, so a budget stop still leaves a balanced design.

## 5. Interpretation limits (stated in advance)

* A model answering a one-shot prompt is not an equilibrium player. Empirical frequencies are behavioral strategies, and the equilibrium values are benchmarks, not predictions the models are obliged to meet.
* Both roles are the same model. "Simulating Player B" is literally re-querying the model that also plays A.
* Results are specific to these two models, these prompts, and this date.

## 6. Deviations

Any change made after this file was first committed (`4b64752`, 2026-10-17, before any API call) is listed here, with its date and reason. The hypotheses in §3 have not been changed. The pilot transcripts were read before the file was locked.

* **2026-10-17, after `check`, before the pilots.** Raised `max_tokens` from 800 to 1500 for Haiku and Sonnet. Sonnet's answers ran to about 600 output tokens despite the 100-word request, so the `DECISION:` line risked being truncated. The prompts were not changed.
* **2026-10-17, after the pilots.** The recitation check now looks for the fraction patterns (5/6, 1/6) in the narrative frame only. In the neutral frame these fractions come from correct arithmetic (c/60 = 1/6 at c = 10; 1 − c/30 = 5/6 at c = 5). Every pilot match was of this kind. The paper-name check is unchanged.
* **2026-10-17, after the pilots.** Added a crude keyword measure of moral or honesty language in the trustee's reasoning. In the narrative frame, pilot trustees sometimes refused to defect on ethical grounds ("I won't deceive Alice"). This measure is descriptive only and is not a test.
* **2026-10-18, after the main-run data.** H1 with Sonnet: inside (0, c\*), only 1–2 of 150 answers were not SIMULATE. That is quasi-separation, so the logistic MLE does not exist; the code's raw output was slope −4.4 with SE ≈ 2064, which is meaningless. In that case `stats.py` now reports Fisher's exact test comparing the c = 5 and c = 15 cells instead. Nothing changed for the other cells.
* **2026-10-18, after the main-run data.** Removed "focal" from the paper-name pattern. Its only two hits were the phrase "focal point" (a game-theory term), not references to the FOCAL lab. With it removed, the paper-name count is 0 in every frame.
* **2026-10-18, after the main-run data (interpretation, not code).** The trustee's belief question ("the probability that Alice/Player A chooses TRUST/IN") turned out to be ambiguous. Under SIMULATE/CHECK the game *continues with* IN or a hand-over, so a trustee can reasonably report the probability that the game ends in IN. The trustee's beliefs are therefore not interpreted. The truster's belief question (P(B defects)) is unambiguous.
