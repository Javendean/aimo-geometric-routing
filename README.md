# AIMO Geometric Routing

An autonomous math olympiad solver (gpt-oss-120B, 117B params, 5.1B active MoE, single H100) scores ~39.7/50 on AIMO 3 with a simple strategy: T=1.0, N=8 samples, majority vote. The ceiling observed so far is ~44/50.

We have strong evidence pointing in contradictory directions about whether and how to organize the model's reasoning differently across problem types. This repository contains all the evidence.

## Four Tensions We Cannot Resolve

**Tension 1:** Aragon (2026) shows routing + orthogonality beats 4x scale under task conflict (29% loss reduction). But a March 2026 paper tested 23+ prompt strategies on THIS exact model and competition — none beat the baseline. Aragon's experiment was at the weight level; ours would be at the prompt level. Is prompt-level routing fundamentally different from weight-level routing?

**Tension 2:** Zhu et al. (2024) show 67% accuracy improvement from topic routing — but also a 40% gap between model-classified and perfect-classification routing. Our classifier is ~60-70% accurate. At what accuracy does routing become net negative?

**Tension 3:** The private test runs the notebook TWICE and scores by penalized accuracy: both correct = 1.0, one correct = 0.5, neither = 0.0. This means consistency is rewarded and diversity is penalized. If routing introduces variance (different answers between runs), it costs 0.5 points per disagreement. Does the accuracy gain from routing outweigh the consistency cost?

**Tension 4:** 25-30% of problems are cross-topic. The model is MoE (5.1B active of 117B). If the model's internal MoE already routes by topic at the weight level, does prompt-level routing add anything, or does it conflict?

## What This Repository Contains

- `theory/` — Aragon's geometric structure research transcript and analysis
- `current-system/` — The current solver: deep_researcher.py (~3000 lines), prompts.py with classify_topic() and TOPIC_PATCHES, the wave controller
- `phase-17-infrastructure/` — Ablation matrix, interference detection, prompt lane separation, diminishing returns (already built but not validated)
- `empirical-evidence/` — 7 evidence sets with specific numbers: Aragon's 4-model table, 23-strategy paper results, Zhu et al. routing ratios, Mixture-of-Prompts, NemoSkills/GenSelect, agent KB findings, competition constraints
- `constraints/` — Token budgets, time budgets, two-attempt strategy implications

## The Question

How should this model's reasoning be organized across 50 math problems to maximize total score under penalized accuracy?

The answer may involve topic routing, or it may involve something we haven't considered. We want the framework that best explains all 7 evidence sets, whatever form it takes.

Environment: Single H100 80GB, air-gapped Kaggle, 32K context window (~13,784 tokens for exemplars), 5 hours for 50 problems (~6 min/problem), MoE architecture (5.1B active), notebook runs TWICE on private test (both correct=1.0, one correct=0.5, neither=0.0), no fine-tuning. Single operator with unlimited frontier AI access and compute budget. Competition deadline April 15 — the architectural insight is more valuable than the timeline.

The evidence is all here. Challenge any assumption. We'd rather discover that routing is wrong than implement routing badly.
