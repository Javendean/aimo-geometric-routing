# Two-Run Scoring Strategy Analysis

## CORRECTION: "Two attempts" = Two Complete Notebook Runs

The previous analysis assumed two attempts within a single notebook run. This is WRONG.

The actual scoring: the notebook runs TWICE independently on the private test set. Both sets of predictions are concatenated and scored by penalized accuracy.

## Scoring Math

For each problem $i$, let $c_1^i, c_2^i \in \{0, 1\}$ indicate whether run 1 and run 2 got the correct answer.

$$\text{score}_i = \begin{cases} 1.0 & \text{if } c_1^i = c_2^i = 1 \\ 0.5 & \text{if } c_1^i + c_2^i = 1 \\ 0.0 & \text{if } c_1^i = c_2^i = 0 \end{cases}$$

$$\text{Total} = \sum_{i=1}^{50} \text{score}_i$$

## Key Insight: Variance Penalty

If the solver has per-problem accuracy $p_i$, and the two runs are independent:

$$E[\text{score}_i] = p_i^2 \cdot 1.0 + 2p_i(1-p_i) \cdot 0.5 + (1-p_i)^2 \cdot 0.0 = p_i$$

So in expectation, the score equals the per-problem accuracy. But the VARIANCE matters for the actual score realized on one submission:

- A solver with $p = 0.8$ on all 50 problems: $E = 40.0$
- A solver with $p = 0.9$ on 40 problems and $p = 0.5$ on 10: $E = 41.0$ but higher variance

**The two-run scoring is actually neutral in expectation** — it doesn't penalize or reward diversity. The penalty only applies when you submit and one specific realization occurs.

## Implications for Routing

1. **Routing that increases accuracy on some problems but decreases it on others is fine IF the net is positive.** The two-run scoring doesn't change the expected value — only the variance.

2. **Deterministic answers win.** If the solver produces the same answer every time (deterministic), both runs agree and the score is exactly the accuracy. No variance. This argues for lower temperature on problems where the model is confident.

3. **Random elements hurt on easy problems.** For a problem with $p = 0.95$ (easy for the model), adding randomness between runs could cause one run to get it wrong → 0.5 instead of 1.0.

4. **Random elements are neutral on hard problems.** For a problem with $p = 0.1$ (hard), both runs will likely fail regardless of randomness.

5. **The sweet spot for diversification is medium-difficulty problems** ($p \approx 0.5$) where the two independent draws give you a second chance.

## What This Means for Routing Strategy

If routing INCREASES per-problem accuracy (e.g., from $p = 0.3$ to $p = 0.5$ on problems the model otherwise struggles with), it's unambiguously good — even with the two-run scoring.

If routing DECREASES consistency (e.g., the routed prompt sometimes works brilliantly and sometimes fails badly), the expected score is the same but the realized score has higher variance.

**The optimal strategy under this scoring is: routing that increases average accuracy while keeping answer variance low.** Topic-specific exemplars (same every run) achieve this better than random prompt perturbation (different every run).
