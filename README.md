# Geometric Intelligence for Math Competition Solving

## The Problem

An MoE math solver (gpt-oss-120B, 117B params, 5.1B active, single H100) scores 4/10 on the AIMO 3 reference bench. It solves AIMO2-level problems perfectly but fails ALL AIMO3-level problems. The gap to frontier models (10/10) is 6 problems.

The model has more than enough parameters. The question is how its existing capacity is ORGANIZED for mathematical reasoning.

## Richard Aragon's Geometric Paradigm

Eight articles in `aragon-research/` present a unified paradigm: **intelligence lives in the geometry of representations, not in the scale of parameters.** Key results:

1. **Structure > Scale** — Routing + orthogonality beats 4x parameters under task conflict (29% loss reduction). Scaling WITHOUT structure fails catastrophically when conflict increases.

2. **The Layer Below** — Steering latent trajectory geometry in real-time (5 geometric metrics) achieves 100% coverage vs 80% for domain knowledge. "The capabilities aren't in the weights... they're in the geometry of the trajectory through activation space."

3. **Partial Recoverability** — Readable structure ≠ computational structure. Probing a model for topic separation may succeed while the model doesn't actually compute along those dimensions.

4. **Grokking = Alignment** — Models often KNOW answers internally but can't decode them. The encoder builds correct geometry rapidly; the decoder struggles. Geometric Warmup (freeze encoder, train decoder) is the most effective fix.

5. **Ghost Basin** — Memorization and algorithmic understanding are competing attractors. Geometry precedes logic: structural reorganization happens BEFORE accuracy improves. Spectral sparsity detects which basin the model occupies.

6. **Amortized Learning** — Compress solved tasks into a geometric "pattern dictionary." New problems are solved by retrieval, not retraining. 85-92% accuracy at step 0.

## The Evidence (Beyond Aragon)

- `empirical-evidence/` — 23 prompt strategies tested on this model: NONE beat T=1.0, N=8, majority vote. Prompt diversity HURTS.
- `empirical-evidence/aimo3-model-evaluation.md` — 14 models on 10 problems. gpt-oss-120B at 4/10. DeepSeek-v3.1 at 9/10 (671B).
- `reference-problems/AIMO3_reference_problems.md` — The actual 10 reference problems with full solutions (28 pages). These are IMO-level, not textbook exercises.
- `current-system/` — How the solver works today: wave controller, topic classifier, prompt patches.
- `phase-17-infrastructure/` — Already-built: ablation matrix, interference detection, diminishing returns.
- `agent-findings/` — 30 KB findings on prompting, 15 on perturbation, critical tension analysis.

## Competition Scoring

50 problems (not 110). Notebook runs TWICE on private test:
- Both correct → 1.0
- One correct → 0.5
- Neither → 0.0

**Consistency is rewarded. Variance is penalized.** This favors deterministic strategies over diverse ones.

Full constraints: `constraints/competition-constraints.md`

## The Questions

We originally framed this as "should we route by topic?" That framing was too narrow. Aragon's work suggests deeper questions:

1. Is gpt-oss-120B's failure on AIMO3 problems a **capability gap** (the model doesn't know enough math) or an **alignment gap** (the model knows the math but can't decode it)? Evidence 4 and 6 suggest the latter is possible.

2. Can we detect whether the model is in its **memorization basin or algorithmic basin** during inference on each problem? If so, can we steer it toward algorithmic reasoning? Evidence 5 and 7.

3. Is prompt-level topic routing **operating on the wrong layer**? Evidence 2 says operate on latent trajectory geometry, not domain structure. Evidence 3 says readable structure ≠ computational structure. The 23-strategy paper's failure may be because all prompt interventions operate at the wrong level.

4. Given the two-run scoring, any strategy that introduces **variance between runs** is penalized. Geometric interventions that are **deterministic** (same exemplars, same structure every run) are safer than random ones (temperature diversity, prompt perturbation).

## Environment

Single H100 80GB, air-gapped Kaggle, 32K context, 5 hours for 50 problems (~6 min/problem), MoE architecture (5.1B active of 117B), no fine-tuning at runtime. Single operator with unlimited compute budget and frontier AI access (Azure + GPT-5.4-pro). Competition deadline April 15.

**Important:** Fine-tuning is possible OFFLINE (Azure) with adapter upload to Kaggle. Weight-level separation via LoRA is feasible if the architectural insight justifies it.

The evidence is all here. The form of the solution is up to you.
