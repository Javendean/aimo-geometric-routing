# The Search for the Ghost Basin (Jan 25, 2026)
Source: https://richardaragon.substack.com/p/the-search-for-the-ghost-basin-a

## Core Concept
Neural networks contain two competing attractors during training:
1. **Shortcut Basin (Memorization)** — lookup table, disorganized manifold, high-entropy weights
2. **Ghost Basin (Algorithmic Rule)** — true mathematical symmetry, sparse and symmetrical, fewer active weights

## Detection: Spectral Sparsity
Monitor Fourier domain projections of embedding weights:
- **Memorizing**: white noise, uniform frequency distribution
- **Algorithmic understanding**: specific frequencies "glow" (harmonics of the underlying structure)

**Key finding: "Geometry Precedes Logic"** — sparsity ratios climb BEFORE validation accuracy improves. The geometric structure forms before the model can output correct answers.

## Resonant Booster
When spectral sparsity exceeds 3.8, perform unitary projections to suppress noise and redirect weights toward resonant frequencies. This accelerates the transition from memorization to algorithmic understanding.

## Discovery: Discrete-Log Isomorphism
In modular multiplication experiments, the model achieved perfect accuracy while linear spectral probes showed noise. The model had constructed a "Slide Rule" — mapping numbers to discrete logarithms, converting multiplication into addition. Log-spectral sparsity jumped from 1.07 to 5.48.

The model discovered the mathematical isomorphism ITSELF without being taught it.

## Implication for AIMO 3
gpt-oss-120B is a pre-trained model — we can't modify its training. But the Ghost Basin concept applies to INFERENCE:
- On each problem, the model may initially "memorize" (pattern-match to training data) or "reason" (find the algorithmic structure)
- More inference-time compute (more samples, longer chains of thought) may help the model transition from its shortcut basin to its ghost basin FOR THAT SPECIFIC PROBLEM
- The question: can we detect which basin the model is in during inference, and steer it toward the ghost basin?
