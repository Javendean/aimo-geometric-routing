# Skipping the Learning Curve (Mar 7, 2026)
Source: https://richardaragon.substack.com/p/skipping-the-learning-curve-how-ai

## Core Concept
Amortized meta-learning: compress solved tasks into a "pattern dictionary," then instantly adapt to new problems with ZERO gradient steps.

## Three-Step Method
1. **Teacher Bank** — train models on dozens of synthetic puzzles, creating a library of solved solutions
2. **Pattern Dictionary** — compress trained models into generalized library; diverse solutions share underlying structural similarities
3. **Set Encoder** — specialized AI analyzes a handful of examples and maps to closest solution in the master library

## Results (Step-0, no training)
- Breast cancer classification: 85-92%
- Wine classification: 92%
- Handwritten digit recognition: 87%

These instantly-generated models outperformed random initializations even after additional training.

## Implication for AIMO 3
Could we create a "math strategy dictionary" — a compressed library of solving approaches indexed by geometric structure? For each new competition problem, the solver would:
1. Encode the problem into geometric features
2. Look up the nearest solved strategy in the dictionary
3. Apply that strategy with zero adaptation

This is NOT topic routing — it's strategy RETRIEVAL from a compressed geometric space. The strategies might not align with traditional topic boundaries.
