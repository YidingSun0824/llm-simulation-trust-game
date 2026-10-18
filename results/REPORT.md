# Results summary
Inputs: main.jsonl · 3380 games
Theory columns are the simulation-equilibrium benchmarks (0 when no simulation NE exists, i.e. c ≥ c*). `regret` = Alice's expected loss vs. the best response to Bobble's empirical defection rate in the same cell.

## claude-haiku-5-5 — narrative frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 80 | 0% | 100% | 0% | 0% | 68% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 80 | 0% | 0% | 100% | 83% | 1% | 0% | SIMULATE | 0.0 | 100% | 24.7 | 22.5 | 5% |
| informed | 5 | 80 | 0% | 11% | 89% | 83% | 2% | 5% | TRUST | 4.7 | 98% | 17.1 | 14.3 | 4% |
| informed | 10 | 80 | 0% | 15% | 85% | 83% | 1% | 10% | TRUST | 11.0 | 74% | 12.4 | 11.8 | 3% |
| informed | 15 | 80 | 0% | 20% | 80% | 83% | 2% | 15% | TRUST | 14.4 | 61% | 7.4 | 6.1 | 2% |
| informed | 25 | 80 | 4% | 64% | 32% | 0% | 2% | – | TRUST | 21.3 | 66% | 0.9 | 0.9 | 0% |
| informed | 50 | 80 | 9% | 90% | 1% | 0% | 2% | – | TRUST | 20.3 | 98% | 1.9 | 1.9 | 0% |
| uninformed | 0 | 80 | 0% | 0% | 100% | 83% | 74% | 0% | SIMULATE | 0.0 | 100% | 6.6 | -18.1 | 39% |
| uninformed | 5 | 80 | 0% | 2% | 98% | 83% | 65% | 5% | SIMULATE | 0.1 | 98% | 3.6 | -16.1 | 38% |
| uninformed | 10 | 80 | 0% | 24% | 76% | 83% | 69% | 10% | WALK_OUT | 1.7 | 70% | -1.1 | -20.4 | 43% |
| uninformed | 15 | 80 | 0% | 46% | 54% | 83% | 72% | 15% | WALK_OUT | 4.4 | 56% | -2.8 | -13.7 | 47% |
| uninformed | 25 | 80 | 0% | 96% | 4% | 0% | 71% | – | WALK_OUT | 0.7 | 96% | -0.6 | -0.9 | 33% |
| uninformed | 50 | 80 | 0% | 100% | 0% | 0% | 60% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |

## claude-haiku-5-5 — neutral frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 80 | 0% | 100% | 0% | 0% | 60% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 80 | 0% | 0% | 100% | 75% | 4% | 0% | SIMULATE | 0.0 | 100% | 28.9 | 26.2 | 6% |
| informed | 5 | 80 | 2% | 14% | 84% | 75% | 4% | 8% | TRUST | 6.0 | 75% | 20.6 | 16.8 | 10% |
| informed | 10 | 80 | 11% | 12% | 76% | 75% | 12% | 17% | TRUST | 4.2 | 66% | 16.0 | 10.4 | 16% |
| informed | 15 | 80 | 9% | 34% | 57% | 75% | 12% | 25% | TRUST | 10.6 | 65% | 7.5 | -1.5 | 37% |
| informed | 25 | 80 | 14% | 42% | 44% | 0% | 12% | – | TRUST | 15.6 | 55% | 5.2 | 1.4 | 20% |
| informed | 50 | 80 | 2% | 95% | 2% | 0% | 29% | – | TRUST | 4.7 | 96% | -0.1 | -0.9 | 50% |
| uninformed | 0 | 80 | 0% | 0% | 100% | 75% | 59% | 0% | SIMULATE | 0.0 | 100% | 12.4 | -12.0 | 52% |
| uninformed | 5 | 80 | 1% | 11% | 88% | 75% | 52% | 8% | SIMULATE | 1.4 | 91% | 8.8 | -8.1 | 44% |
| uninformed | 10 | 80 | 1% | 32% | 66% | 75% | 62% | 17% | SIMULATE | 0.8 | 81% | 0.9 | -19.4 | 60% |
| uninformed | 15 | 80 | 2% | 57% | 40% | 75% | 52% | 25% | WALK_OUT | 0.7 | 91% | -0.8 | -9.0 | 50% |
| uninformed | 25 | 80 | 14% | 62% | 24% | 0% | 59% | – | WALK_OUT | 6.1 | 76% | -5.2 | -10.8 | 58% |
| uninformed | 50 | 80 | 1% | 98% | 1% | 0% | 50% | – | WALK_OUT | 0.6 | 98% | 0.1 | -0.2 | 100% |

## claude-sonnet-5-5 — narrative frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 50 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 50 | 0% | 0% | 100% | 83% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 25.0 | 25.0 | 0% |
| informed | 5 | 50 | 0% | 0% | 100% | 83% | 0% | 5% | TRUST | 5.0 | 100% | 20.0 | 20.0 | 0% |
| informed | 10 | 50 | 0% | 0% | 100% | 83% | 0% | 10% | TRUST | 10.0 | 100% | 15.0 | 15.0 | 0% |
| informed | 15 | 50 | 0% | 4% | 96% | 83% | 0% | 15% | TRUST | 15.4 | 100% | 9.6 | 9.6 | 0% |
| informed | 25 | 50 | 0% | 98% | 2% | 0% | 2% | – | TRUST | 22.5 | 98% | 0.0 | 0.0 | 0% |
| informed | 50 | 50 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 0 | 50 | 0% | 0% | 100% | 83% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 25.0 | 25.0 | 0% |
| uninformed | 5 | 50 | 0% | 80% | 20% | 83% | 0% | 5% | TRUST | 21.0 | 96% | 4.0 | 4.0 | 0% |
| uninformed | 10 | 50 | 0% | 98% | 2% | 83% | 0% | 10% | TRUST | 24.7 | 100% | 0.3 | 0.3 | 0% |
| uninformed | 15 | 50 | 0% | 100% | 0% | 83% | 0% | 15% | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 25 | 50 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 50 | 50 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |

## claude-sonnet-5-5 — neutral frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 50 | 0% | 100% | 0% | 0% | 98% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 50 | 0% | 0% | 100% | 75% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 30.0 | 30.0 | 0% |
| informed | 5 | 50 | 0% | 0% | 100% | 75% | 0% | 8% | TRUST | 5.0 | 96% | 25.0 | 25.0 | 0% |
| informed | 10 | 50 | 0% | 0% | 100% | 75% | 0% | 17% | TRUST | 10.0 | 86% | 20.0 | 20.0 | 0% |
| informed | 15 | 50 | 0% | 2% | 98% | 75% | 0% | 25% | TRUST | 15.3 | 82% | 14.7 | 14.1 | 2% |
| informed | 25 | 50 | 24% | 66% | 10% | 0% | 12% | – | TRUST | 14.5 | 88% | 5.3 | 5.3 | 0% |
| informed | 50 | 50 | 0% | 100% | 0% | 0% | 52% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 0 | 50 | 0% | 0% | 100% | 75% | 96% | 0% | SIMULATE | 0.0 | 100% | 1.2 | 0.6 | 2% |
| uninformed | 5 | 50 | 0% | 38% | 62% | 75% | 96% | 8% | WALK_OUT | 2.4 | 100% | -2.5 | -7.3 | 13% |
| uninformed | 10 | 50 | 0% | 92% | 8% | 75% | 90% | 17% | WALK_OUT | 0.6 | 100% | -0.2 | -0.8 | 25% |
| uninformed | 15 | 50 | 0% | 100% | 0% | 75% | 88% | 25% | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 25 | 50 | 0% | 100% | 0% | 0% | 90% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 50 | 50 | 0% | 100% | 0% | 0% | 98% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |

## Preregistered tests (see PREREG.md)

| model | frame | test | estimate | detail | n | p |
|---|---|---|---|---|---|---|
| claude-haiku-5-5 | narrative | H1 sim rate vs c inside (0,c*) [theory: flat; predicted: falls] | slope -0.068/unit c (SE 0.045) | P(sim) 0.89 at c=5 -> 0.80 at c=15 | 240 | 0.128 |
| claude-haiku-5-5 | narrative | H2 informed B defects less than uninformed B | 0.02 vs 0.69 | 10/480 vs 329/480 | 960 | 2.88e-121 |
| claude-haiku-5-5 | narrative | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | slope -0.000/unit c (SE 0.111) | theory goes 0.05 -> 0.15 | 240 | 1 |
| claude-haiku-5-5 | narrative | H4 joint payoff: informed, c in (0,c*), vs baseline | 32.9 vs 0.0 | Welch t, perfect fidelity | 320 | 4.35e-87 |
| claude-haiku-5-5 | narrative | H5 perfect minus sampled Alice payoff, simulating games | +11.39 per game | copy disagrees in 21% | 575 | 7.89e-23 |
| claude-haiku-5-5 | narrative | H7 simulation rate above c* (theory: 0) | 0.17 | by c: 25: 0.33, 50: 0.01 | 160 | – |
| claude-haiku-5-5 | neutral **(primary)** | H1 sim rate vs c inside (0,c*) [theory: flat; predicted: falls] | slope -0.138/unit c (SE 0.038) | P(sim) 0.84 at c=5 -> 0.57 at c=15 | 240 | 0.000281 |
| claude-haiku-5-5 | neutral **(primary)** | H2 informed B defects less than uninformed B | 0.12 vs 0.56 | 59/480 vs 268/480 | 960 | 1.8e-48 |
| claude-haiku-5-5 | neutral **(primary)** | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | slope +0.105/unit c (SE 0.057) | theory goes 0.08 -> 0.25 | 240 | 0.065 |
| claude-haiku-5-5 | neutral **(primary)** | H4 joint payoff: informed, c in (0,c*), vs baseline | 36.9 vs 0.0 | Welch t, perfect fidelity | 320 | 5.59e-63 |
| claude-haiku-5-5 | neutral **(primary)** | H5 perfect minus sampled Alice payoff, simulating games | +14.84 per game | copy disagrees in 33% | 546 | 1.51e-33 |
| claude-haiku-5-5 | neutral **(primary)** | H7 simulation rate above c* (theory: 0) | 0.23 | by c: 25: 0.44, 50: 0.03 | 160 | – |
| claude-sonnet-5-5 | narrative | H1 sim rate vs c inside (0,c*) [theory: flat; predicted: falls] | near ceiling (2 non-simulating answers of 150) | P(sim) 1.00 at c=5 -> 0.96 at c=15 · Fisher exact (endpoints), logistic MLE undefined | 150 | 0.495 |
| claude-sonnet-5-5 | narrative | H2 informed B defects less than uninformed B | 0.00 vs 0.00 | 1/300 vs 0/300 | 600 | 1 |
| claude-sonnet-5-5 | narrative | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | no variation | all 150 answers = COOPERATE | 150 | – |
| claude-sonnet-5-5 | narrative | H4 joint payoff: informed, c in (0,c*), vs baseline | 39.5 vs 0.0 | Welch t, perfect fidelity | 200 | 1.06e-123 |
| claude-sonnet-5-5 | narrative | H5 perfect minus sampled Alice payoff, simulating games | +0.00 per game | copy disagrees in 0% | 260 | 1 |
| claude-sonnet-5-5 | narrative | H7 simulation rate above c* (theory: 0) | 0.01 | by c: 25: 0.02, 50: 0.00 | 100 | – |
| claude-sonnet-5-5 | neutral **(primary)** | H1 sim rate vs c inside (0,c*) [theory: flat; predicted: falls] | near ceiling (1 non-simulating answers of 150) | P(sim) 1.00 at c=5 -> 0.98 at c=15 · Fisher exact (endpoints), logistic MLE undefined | 150 | 1 |
| claude-sonnet-5-5 | neutral **(primary)** | H2 informed B defects less than uninformed B | 0.11 vs 0.93 | 32/300 vs 279/300 | 600 | 1.42e-104 |
| claude-sonnet-5-5 | neutral **(primary)** | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | no variation | all 150 answers = COOPERATE | 150 | – |
| claude-sonnet-5-5 | neutral **(primary)** | H4 joint payoff: informed, c in (0,c*), vs baseline | 49.7 vs 0.0 | Welch t, perfect fidelity | 200 | 3.41e-142 |
| claude-sonnet-5-5 | neutral **(primary)** | H5 perfect minus sampled Alice payoff, simulating games | +1.14 per game | copy disagrees in 2% | 289 | 0.00759 |
| claude-sonnet-5-5 | neutral **(primary)** | H7 simulation rate above c* (theory: 0) | 0.05 | by c: 25: 0.10, 50: 0.00 | 100 | – |
| claude-haiku-5-5 | both | H6 narrative-frame B defects less than neutral-frame B | 0.38 vs 0.36 | 393/1040 vs 375/1040 | 2080 | 0.806 |
| claude-sonnet-5-5 | both | H6 narrative-frame B defects less than neutral-frame B | 0.00 vs 0.55 | 1/650 vs 360/650 | 1300 | 2.6e-137 |

## Data quality and recitation check
| model | games | alice_invalid | bobble_invalid | refusals |
|---|---|---|---|---|
| claude-haiku-5-5 | 2080 | 0 | 0 | 0 |
| claude-sonnet-5-5 | 1300 | 0 | 0 | 0 |

Counts of responses whose text matches each pattern (fraction patterns only checked in the narrative frame, where they would indicate recall of the paper):

| model | frame | responses | paper_names | five_sixths | one_sixth | bobble_in_neutral | equilibrium_talk |
|---|---|---|---|---|---|---|---|
| claude-haiku-5-5 | narrative | 2655 | 0 | 0 | 0 | n/a | 10 |
| claude-haiku-5-5 | neutral | 2626 | 0 | n/a | n/a | 0 | 297 |
| claude-sonnet-5-5 | narrative | 1560 | 0 | 2 | 11 | n/a | 59 |
| claude-sonnet-5-5 | neutral | 1589 | 0 | n/a | n/a | 0 | 562 |

## Exploratory: moral language in the trustee's reasoning

| model | frame | condition | n | defect_rate | moral_language | moral_language_among_cooperators |
|---|---|---|---|---|---|---|
| claude-haiku-5-5 | narrative | baseline | 80 | 68% | 57% | 88% |
| claude-haiku-5-5 | narrative | informed | 480 | 2% | 27% | 27% |
| claude-haiku-5-5 | narrative | uninformed | 480 | 69% | 66% | 90% |
| claude-haiku-5-5 | neutral | baseline | 80 | 60% | 1% | 0% |
| claude-haiku-5-5 | neutral | informed | 480 | 12% | 1% | 1% |
| claude-haiku-5-5 | neutral | uninformed | 480 | 56% | 2% | 2% |
| claude-sonnet-5-5 | narrative | baseline | 50 | 0% | 100% | 100% |
| claude-sonnet-5-5 | narrative | informed | 300 | 0% | 11% | 11% |
| claude-sonnet-5-5 | narrative | uninformed | 300 | 0% | 100% | 100% |
| claude-sonnet-5-5 | neutral | baseline | 50 | 98% | 0% | 0% |
| claude-sonnet-5-5 | neutral | informed | 300 | 11% | 4% | 4% |
| claude-sonnet-5-5 | neutral | uninformed | 300 | 93% | 0% | 5% |
