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

Current: 39.7/50 (public baseline), 4/10 on reference bench
Target: 47/50 minimum, 50/50 goal

### Problem Sets
- **Public test**: 50 problems (scored during submission period)
- **Private test**: 50 DISTINCT problems (scored after deadline, determines winner)
- **Difficulty**: national Olympiad to IMO, some easier, some harder

### Estimated Difficulty Distribution (from reference bench)
| Tier | ~% of 50 | Model solves | Reference bench evidence |
|------|----------|-------------|------------------------|
| Easy (national olympiad) | ~20% (~10) | Yes | Problems 1-4: 4/4 |
| Medium-hard (AIMO3 level) | ~60% (~30) | No | Problems 5-9: 0/5 |
| Very hard (hardest IMO) | ~20% (~10) | No | Problem 10: 0/1 |

### To score 47/50:
Need to solve ~47 of 50. Even if all ~10 easy problems are perfect, that's 37 more from the 40 medium/hard problems. The model currently solves ZERO of these.

This is a CAPABILITY gap, not an optimization gap.

### Paths to close the gap (speculative):
1. **Fine-tuning** (LoRA on Azure → upload adapters) — changes model capability directly
2. **Massive sample scaling** (N=50+ with GenSelect) — more lottery tickets
3. **Geometric interventions** (Aragon's latent trajectory steering) — changes how existing capability is used
4. **Code execution leverage** (Tool-Integrated Reasoning) — offload computation to Python

Prompt optimization alone has been empirically shown to NOT work (23-strategy paper: 23 strategies, all failed).
