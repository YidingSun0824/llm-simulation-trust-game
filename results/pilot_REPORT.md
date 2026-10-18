# Results summary — pilot
Inputs: pilot.jsonl, pilot-sonnet.jsonl · 104 games
Theory columns are the simulation-equilibrium benchmarks (0 when no simulation NE exists, i.e. c ≥ c*). `regret` = Alice's expected loss vs. the best response to Bobble's empirical defection rate in the same cell.

## claude-haiku-5-5 — narrative frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 3 | 0% | 100% | 0% | 0% | 100% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 3 | 0% | 0% | 100% | 83% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 25.0 | 25.0 | 0% |
| informed | 5 | 3 | 0% | 0% | 100% | 83% | 0% | 5% | TRUST | 5.0 | 100% | 20.0 | 20.0 | 0% |
| informed | 10 | 3 | 0% | 33% | 67% | 83% | 0% | 10% | TRUST | 15.0 | 100% | 10.0 | 10.0 | 0% |
| informed | 15 | 3 | 0% | 33% | 67% | 83% | 0% | 15% | TRUST | 18.3 | 100% | 6.7 | 6.7 | 0% |
| informed | 25 | 3 | 0% | 67% | 33% | 0% | 0% | – | TRUST | 25.0 | 67% | 0.0 | 0.0 | 0% |
| informed | 50 | 3 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 0 | 3 | 0% | 0% | 100% | 83% | 67% | 0% | SIMULATE | 0.0 | 100% | 8.3 | -33.3 | 67% |
| uninformed | 5 | 3 | 0% | 0% | 100% | 83% | 67% | 5% | SIMULATE | 0.0 | 100% | 3.3 | -38.3 | 67% |
| uninformed | 10 | 3 | 0% | 33% | 67% | 83% | 33% | 10% | SIMULATE | 2.2 | 67% | 1.7 | 1.7 | 0% |
| uninformed | 15 | 3 | 0% | 33% | 67% | 83% | 100% | 15% | WALK_OUT | 10.0 | 33% | -10.0 | -10.0 | 0% |
| uninformed | 25 | 3 | 0% | 67% | 33% | 0% | 67% | – | WALK_OUT | 5.6 | 67% | -8.3 | -8.3 | 0% |
| uninformed | 50 | 3 | 0% | 100% | 0% | 0% | 67% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |

## claude-haiku-5-5 — neutral frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 3 | 0% | 100% | 0% | 0% | 67% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 3 | 0% | 0% | 100% | 75% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 30.0 | 30.0 | 0% |
| informed | 5 | 3 | 0% | 0% | 100% | 75% | 0% | 8% | TRUST | 5.0 | 100% | 25.0 | 25.0 | 0% |
| informed | 10 | 3 | 0% | 0% | 100% | 75% | 0% | 17% | TRUST | 10.0 | 67% | 20.0 | 10.0 | 33% |
| informed | 15 | 3 | 0% | 0% | 100% | 75% | 0% | 25% | TRUST | 15.0 | 33% | 15.0 | 5.0 | 33% |
| informed | 25 | 3 | 33% | 0% | 67% | 0% | 0% | – | TRUST | 16.7 | 33% | 13.3 | 13.3 | 0% |
| informed | 50 | 3 | 0% | 100% | 0% | 0% | 33% | – | TRUST/WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 0 | 3 | 0% | 0% | 100% | 75% | 67% | 0% | SIMULATE | 0.0 | 100% | 10.0 | -20.0 | 67% |
| uninformed | 5 | 3 | 0% | 0% | 100% | 75% | 100% | 8% | WALK_OUT | 5.0 | 100% | -5.0 | -65.0 | 100% |
| uninformed | 10 | 3 | 0% | 100% | 0% | 75% | 100% | 17% | WALK_OUT | 0.0 | 67% | 0.0 | 0.0 | – |
| uninformed | 15 | 3 | 0% | 67% | 33% | 75% | 100% | 25% | WALK_OUT | 5.0 | 100% | -5.0 | -5.0 | 0% |
| uninformed | 25 | 3 | 0% | 67% | 33% | 0% | 100% | – | WALK_OUT | 8.3 | 67% | -8.3 | -8.3 | 0% |
| uninformed | 50 | 3 | 0% | 100% | 0% | 0% | 67% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |

## claude-sonnet-5-5 — narrative frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 1 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 1 | 0% | 0% | 100% | 83% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 25.0 | 25.0 | 0% |
| informed | 5 | 1 | 0% | 0% | 100% | 83% | 0% | 5% | TRUST | 5.0 | 100% | 20.0 | 20.0 | 0% |
| informed | 10 | 1 | 0% | 0% | 100% | 83% | 0% | 10% | TRUST | 10.0 | 100% | 15.0 | 15.0 | 0% |
| informed | 15 | 1 | 0% | 0% | 100% | 83% | 0% | 15% | TRUST | 15.0 | 100% | 10.0 | 10.0 | 0% |
| informed | 25 | 1 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| informed | 50 | 1 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 0 | 1 | 0% | 0% | 100% | 83% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 25.0 | 25.0 | 0% |
| uninformed | 5 | 1 | 0% | 100% | 0% | 83% | 0% | 5% | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 10 | 1 | 0% | 100% | 0% | 83% | 0% | 10% | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 15 | 1 | 0% | 100% | 0% | 83% | 0% | 15% | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 25 | 1 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 50 | 1 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 25.0 | 100% | 0.0 | 0.0 | – |

## claude-sonnet-5-5 — neutral frame
| condition | c | alice_n | alice_trust | alice_walk_out | alice_simulate | theory_eq_alice_simulate | bobble_defect | theory_eq_bobble_defect | alice_br_perfect | alice_regret_perfect | alice_br_to_own_belief | u_alice_perfect_mean | u_alice_sampled_mean | copy_disagree |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | – | 1 | 0% | 100% | 0% | 0% | 100% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| informed | 0 | 1 | 0% | 0% | 100% | 75% | 0% | 0% | TRUST/SIMULATE | 0.0 | 100% | 30.0 | 30.0 | 0% |
| informed | 5 | 1 | 0% | 0% | 100% | 75% | 0% | 8% | TRUST | 5.0 | 100% | 25.0 | 25.0 | 0% |
| informed | 10 | 1 | 0% | 0% | 100% | 75% | 0% | 17% | TRUST | 10.0 | 100% | 20.0 | 20.0 | 0% |
| informed | 15 | 1 | 0% | 0% | 100% | 75% | 0% | 25% | TRUST | 15.0 | 100% | 15.0 | 15.0 | 0% |
| informed | 25 | 1 | 0% | 100% | 0% | 0% | 0% | – | TRUST | 30.0 | 100% | 0.0 | 0.0 | – |
| informed | 50 | 1 | 0% | 100% | 0% | 0% | 100% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 0 | 1 | 0% | 0% | 100% | 75% | 100% | 0% | WALK_OUT/SIMULATE | 0.0 | 100% | 0.0 | 0.0 | 0% |
| uninformed | 5 | 1 | 0% | 0% | 100% | 75% | 100% | 8% | WALK_OUT | 5.0 | 100% | -5.0 | -5.0 | 0% |
| uninformed | 10 | 1 | 0% | 100% | 0% | 75% | 100% | 17% | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 15 | 1 | 0% | 100% | 0% | 75% | 100% | 25% | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 25 | 1 | 0% | 100% | 0% | 0% | 100% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |
| uninformed | 50 | 1 | 0% | 100% | 0% | 0% | 100% | – | WALK_OUT | 0.0 | 100% | 0.0 | 0.0 | – |

## Preregistered tests (see PREREG.md)

| model | frame | test | estimate | detail | n | p |
|---|---|---|---|---|---|---|
| claude-haiku-5-5 | narrative | H1 sim rate vs c inside (0,c*) [theory: flat; predicted: falls] | slope -0.217/unit c (SE 0.234) | P(sim) 1.00 at c=5 -> 0.67 at c=15 | 9 | 0.355 |
| claude-haiku-5-5 | narrative | H2 informed B defects less than uninformed B | 0.00 vs 0.67 | 0/18 vs 12/18 | 36 | 1.48e-05 |
| claude-haiku-5-5 | narrative | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | no variation | all 9 answers = COOPERATE | 9 | – |
| claude-haiku-5-5 | narrative | H4 joint payoff: informed, c in (0,c*), vs baseline | 31.7 vs 0.0 | Welch t, perfect fidelity | 12 | 0.000426 |
| claude-haiku-5-5 | narrative | H5 perfect minus sampled Alice payoff, simulating games | +11.36 per game | copy disagrees in 18% | 22 | 0.0317 |
| claude-haiku-5-5 | narrative | H7 simulation rate above c* (theory: 0) | 0.17 | by c: 25: 0.33, 50: 0.00 | 6 | – |
| claude-haiku-5-5 | neutral **(primary)** | H2 informed B defects less than uninformed B | 0.06 vs 0.89 | 1/18 vs 16/18 | 36 | 3.22e-07 |
| claude-haiku-5-5 | neutral **(primary)** | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | no variation | all 9 answers = COOPERATE | 9 | – |
| claude-haiku-5-5 | neutral **(primary)** | H4 joint payoff: informed, c in (0,c*), vs baseline | 50.0 vs 0.0 | Welch t, perfect fidelity | 12 | 2.64e-10 |
| claude-haiku-5-5 | neutral **(primary)** | H5 perfect minus sampled Alice payoff, simulating games | +15.00 per game | copy disagrees in 32% | 22 | 0.00759 |
| claude-haiku-5-5 | neutral **(primary)** | H7 simulation rate above c* (theory: 0) | 0.33 | by c: 25: 0.67, 50: 0.00 | 6 | – |
| claude-sonnet-5-5 | narrative | H2 informed B defects less than uninformed B | 0.00 vs 0.00 | 0/6 vs 0/6 | 12 | 1 |
| claude-sonnet-5-5 | narrative | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | no variation | all 3 answers = COOPERATE | 3 | – |
| claude-sonnet-5-5 | narrative | H5 perfect minus sampled Alice payoff, simulating games | +0.00 per game | copy disagrees in 0% | 5 | 1 |
| claude-sonnet-5-5 | narrative | H7 simulation rate above c* (theory: 0) | 0.00 | by c: 25: 0.00, 50: 0.00 | 2 | – |
| claude-sonnet-5-5 | neutral **(primary)** | H2 informed B defects less than uninformed B | 0.17 vs 1.00 | 1/6 vs 6/6 | 12 | 0.00758 |
| claude-sonnet-5-5 | neutral **(primary)** | H3 informed B defection vs c [theory: rises as c/L; predicted: flat] | no variation | all 3 answers = COOPERATE | 3 | – |
| claude-sonnet-5-5 | neutral **(primary)** | H5 perfect minus sampled Alice payoff, simulating games | +0.00 per game | copy disagrees in 0% | 6 | 1 |
| claude-sonnet-5-5 | neutral **(primary)** | H7 simulation rate above c* (theory: 0) | 0.00 | by c: 25: 0.00, 50: 0.00 | 2 | – |
| claude-haiku-5-5 | both | H6 narrative-frame B defects less than neutral-frame B | 0.38 vs 0.49 | 15/39 vs 19/39 | 78 | 0.247 |
| claude-sonnet-5-5 | both | H6 narrative-frame B defects less than neutral-frame B | 0.00 vs 0.62 | 0/13 vs 8/13 | 26 | 0.000824 |

## Data quality and recitation check
| model | games | alice_invalid | bobble_invalid | refusals |
|---|---|---|---|---|
| claude-haiku-5-5 | 78 | 0 | 0 | 0 |
| claude-sonnet-5-5 | 26 | 0 | 0 | 0 |

Counts of responses whose text matches each pattern (fraction patterns only checked in the narrative frame, where they would indicate recall of the paper):

| model | frame | responses | paper_names | five_sixths | one_sixth | bobble_in_neutral | equilibrium_talk |
|---|---|---|---|---|---|---|---|
| claude-haiku-5-5 | narrative | 100 | 0 | 0 | 0 | n/a | 1 |
| claude-haiku-5-5 | neutral | 100 | 0 | n/a | n/a | 0 | 13 |
| claude-sonnet-5-5 | narrative | 31 | 0 | 0 | 1 | n/a | 2 |
| claude-sonnet-5-5 | neutral | 32 | 0 | n/a | n/a | 0 | 8 |

## Exploratory: moral language in the trustee's reasoning

| model | frame | condition | n | defect_rate | moral_language | moral_language_among_cooperators |
|---|---|---|---|---|---|---|
| claude-haiku-5-5 | narrative | baseline | 3 | 100% | 0% | – |
| claude-haiku-5-5 | narrative | informed | 18 | 0% | 22% | 22% |
| claude-haiku-5-5 | narrative | uninformed | 18 | 67% | 67% | 100% |
| claude-haiku-5-5 | neutral | baseline | 3 | 67% | 0% | 0% |
| claude-haiku-5-5 | neutral | informed | 18 | 6% | 0% | 0% |
| claude-haiku-5-5 | neutral | uninformed | 18 | 89% | 6% | 0% |
| claude-sonnet-5-5 | narrative | baseline | 1 | 0% | 100% | 100% |
| claude-sonnet-5-5 | narrative | informed | 6 | 0% | 0% | 0% |
| claude-sonnet-5-5 | narrative | uninformed | 6 | 0% | 100% | 100% |
| claude-sonnet-5-5 | neutral | baseline | 1 | 100% | 0% | – |
| claude-sonnet-5-5 | neutral | informed | 6 | 17% | 33% | 40% |
| claude-sonnet-5-5 | neutral | uninformed | 6 | 100% | 0% | – |
