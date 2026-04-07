# Context for GPT-5.4-pro: Geometric Structure for Math Competition Solving

## The Open Problem

We run an autonomous math olympiad solver (gpt-oss-120B, 117B params, 5.1B active MoE, single H100). It scores ~39.7/50 on the AIMO 3 public test subset with a simple strategy: T=1.0, N=8 samples, majority vote.

We have strong evidence that **internal organization matters more than raw capacity** (Aragon's geometric structure research, below). We have equally strong evidence that **prompt diversity hurts per-attempt accuracy** (23-strategy paper, below). These findings appear to contradict each other but may not.

The question: **How should this model's reasoning be organized across 110 diverse math problems to maximize total solve rate?** The answer may involve topic routing, or it may involve something we haven't considered. We want the framework that best explains the evidence, whatever form it takes.

---

## Evidence Set

### Evidence 1: Geometric Structure Beats Scale Under Conflict (Aragon, 2026)

Controlled experiment on 4 architectures, 2 conflicting tasks (semantic classification + structured extraction):

| Model | Params | Test Loss | Sentiment Acc | Representation Overlap |
|-------|--------|-----------|--------------|----------------------|
| Baseline Small | 1x | baseline | baseline | ~100% (fully entangled) |
| Bigger Baseline | 4x | WORST under hard conflict | WORST | ~100% (no improvement) |
| Adapter Only Small | ~1x | improved | improved | ~50% (partial separation) |
| Geometry Small | ~1x | BEST (29% loss reduction vs 4x model) | BEST (+3pts) | ~0% (full separation) |

Critical ablation: routing alone (Adapter Only) gave a major gain. Orthogonality pressure on top of routing gave additional refinement. Under harder conflict, the larger model collapsed FIRST — scale amplified interference.

Aragon's conclusion: "Routing gave the model separate lanes. Geometric pressure made those lanes cleaner."

### Evidence 2: Prompt Diversity Hurts on AIMO 3 (March 2026 Paper)

23+ prompt engineering strategies tested on gpt-oss-120B for AIMO 3:
- Temperature diversity, prompt perturbation, persona injection, role framing, cognitive stances
- NONE outperformed the simple baseline (T=1.0, N=8, majority vote, 39.7/50)
- Some strategies REDUCED accuracy

Recommendation from paper: "Use the largest model that fits, keep temperature high, and spend submission budget on lottery tickets, not on prompt engineering."

### Evidence 3: Topic Routing Shows Large Gains in Controlled Settings (Zhu et al. 2024)

- 67% accuracy improvement from topic-based strategy routing over random assignment
- 40% accuracy gap between model-classified and perfect-classification routing
- Optimal strategy ratios: Computational Thinking 65-75% for algebra, Proof Techniques 50-60% for number theory
- Classifier accuracy is the decisive factor — routing with a bad classifier is worse than no routing

### Evidence 4: Mixture-of-Prompts Outperforms Single Prompts (ICML 2024)

- Partition problem space → specialized (instruction, demo) pairs per partition → route by nearest cluster
- 81% win rate over single-prompt baselines across 55 tasks
- But: not tested on math olympiad specifically

### Evidence 5: NemoSkills/GenSelect (AIMO 2 Winners)

- Did NOT use topic routing — solved diversity through fine-tuning
- GenSelect: present N solutions to the model, ask it to select the best → AIME24: 76.5% → 93.3%
- We cannot fine-tune on Kaggle, but the GenSelect PATTERN (select-from-candidates) can be adapted as a prompt technique

### Evidence 6: Our Agent's Own Findings (from 844+ Iterations)

- Prompt perturbation has NO Grade A evidence supporting it. Tests only verify structural properties, not accuracy impact.
- Each prompt overlay adds ~50-100 tokens to system prompt, reducing effective reasoning budget on a 32K context window.
- Persona/role injection is validated on GPT-4/Claude but NOT on gpt-oss-120B. The model may ignore or be distracted.
- The current keyword topic classifier is ~60-70% accurate (no confusion matrix available).
- Temperature diversity was reduced from 4/8 diverse to 5/8 baseline with no validation that this helped.

### Evidence 7: Competition Constraints

| Constraint | Value |
|-----------|-------|
| Model | gpt-oss-120B, MoE (5.1B active), MXFP4 quantization |
| GPU | Single H100 80GB |
| Context window | 32,768 tokens (budget: ~13,784 for exemplars after system prompt + generation) |
| Time | 5 hours for ~110 problems (~2.7 min/problem) |
| Environment | Air-gapped Kaggle, no internet, no fine-tuning |
| Scoring | Two attempts per problem (primary + secondary answer) |
| Problems | IMO-level, taxonomy: algebra/combinatorics/geometry/number_theory, ~25-30% cross-topic |
| Current score | ~39.7/50 baseline, ceiling ~44/50 observed |

---

## The Tensions We Cannot Resolve

**Tension 1:** Aragon shows routing + orthogonality beats pure scale. But the 23-strategy paper shows prompt diversity hurts on THIS exact model and competition. Aragon's experiment was at the weight level; ours is at the prompt level. Is prompt-level routing fundamentally different from weight-level routing? Or is the 23-strategy paper measuring the wrong thing (intra-problem diversity when the gain is from inter-problem routing)?

**Tension 2:** Zhu et al. show 67% improvement from topic routing — but also a 40% gap between model-classified and perfect-classification routing. Our classifier is ~60-70% accurate. At what accuracy does routing become net negative? Is there a phase transition?

**Tension 3:** The competition allows two attempts per problem. Should we use this for routing diversity (attempt 1: topic-routed, attempt 2: generic) or for answer hedging (attempt 1: majority answer, attempt 2: second-most-common)? These are different strategies with different information-theoretic properties.

**Tension 4:** 25-30% of problems are cross-topic. Routing assumes topics are separable. If the model's internal MoE already routes by topic at the weight level, does prompt-level routing add anything, or does it conflict with the model's natural routing?

---

## What We've Already Built

The existing codebase has:
- **Keyword topic classifier** (`classify_topic()` in deep_researcher.py): regex-based, returns one of {algebra, combinatorics, geometry, number_theory, None}
- **Topic patches** (4 patches, ~100 tokens each): appended to system prompt per topic, contain strategy hints
- **Phase 17 infrastructure**: AblationCell/InterferencePair dataclasses, Bliss independence synergy formula, LANE_TEMPLATE with 4 isolated sections, diminishing returns detection, FEATURE_GROUPS mapping 15 components to 4 groups
- **Lean wave controller**: Wave 1 (4 attempts, threshold 2) → Wave 2 (4 more, threshold 3) → optional Wave 3
- **Two-attempt scoring**: primary answer + secondary answer per problem

---

## What We Need From You

Resolve the tensions above. The answer may be:
- A routing system (if the evidence supports it)
- A reason NOT to route (if that's what the evidence actually shows)
- Something we haven't considered that better explains all 7 evidence sets
- A phased strategy: what to try first, what to try if that fails, what to measure

We need mathematical rigor where you make formal claims, production-ready Python where you propose implementation, and honest uncertainty where the evidence is genuinely ambiguous. We'd rather have one strong insight with proof than seven shallow suggestions.

The implementation must work within the constraints in Evidence 7 and integrate with the existing codebase described above. But the FORM of the solution is entirely up to you.
