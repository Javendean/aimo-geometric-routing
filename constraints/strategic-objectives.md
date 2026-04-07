# Strategic Objectives (AIMO 3)

## Three Objectives (Ranked)

### 1. Score >= 47/50 consistently (minimum threshold)
The model must score at least 47 on EVERY submission. This is a hard floor, not an expected value target. Current baseline: 39.7/50. Gap: 7.3 points (~7 more problems correct).

**Implication for variance:** Even though the scoring mechanism is expectation-neutral (E[score] = p), the minimum threshold objective makes variance harmful. A solver with E=48 and high variance might realize 44 (below threshold). A solver with E=47.5 and low variance is safer.

**Implication for strategy:** The first priority is reliability on the problems the model CAN solve. Zero dropped points on easy/medium problems. Then push accuracy on hard problems.

### 2. Score 50/50 (ultimate goal)
Solve every problem in both runs. This requires solving problems that gpt-oss-120B currently CANNOT solve (reference bench: 4/10, fails all AIMO3-level problems). The gap from 4/10 to 10/10 may require a fundamentally different approach, not just optimization.

### 3. Win the $30,000 Hard Problem Prize
Awarded to the highest-ranked team that solved the most difficult problem(s) in the private test set.

**Rules:**
- Problem difficulty = average accuracy across all selected submissions
- Example: if the hardest problem has 1.7% average accuracy, the highest-ranked solver of that problem wins $30K
- If multiple problems tie for hardest, prize split equally among their respective highest-ranked solvers
- Tiebreaker: submission time (first to submit wins)

**Implication:** This rewards:
1. Solving problems nobody else can solve (novelty > reliability)
2. Submitting EARLY (tiebreaker = time)
3. Disproportionate compute on the hardest problems

## Strategic Tensions

### Tension A: Reliability vs Hard Problem Prize
- 47/50 floor requires LOW variance on easy problems (don't drop points)
- Hard problem prize requires HIGH investment in the hardest problems (novel approaches)
- With 6 min/problem average, these can coexist: rush easy problems (2 min), invest in hard ones (15+ min)

### Tension B: Expected Score vs Minimum Threshold
- The scoring mechanism is expectation-neutral (E[score] = p regardless of variance)
- But the 47/50 floor makes variance harmful even when E[score] > 47
- Optimal: maximize p on each problem while minimizing variance across the portfolio

### Tension C: First-to-Submit vs Accuracy
- Hard problem prize tiebreaker = earliest submission
- But submitting too early might mean lower total score (not enough iteration)
- Optimal: submit a strong baseline EARLY, then iterate for improvements

## The Math Gap

Current: 39.7/50 (baseline), 4/10 on reference bench
Target: 47/50 minimum, 50/50 goal

This is NOT a 7-point gap — it's a CAPABILITY gap. The model fails ALL 6 AIMO3-level reference problems. Going from 0/6 to 6/6 on hard problems requires:
- Either a fundamental capability improvement (fine-tuning, LoRA adapters)
- Or a radically different inference strategy (Aragon's geometric interventions?)
- Or both

Prompt optimization alone (routing, exemplars, temperature) has been empirically shown to NOT work on this model (23-strategy paper: all failed).
