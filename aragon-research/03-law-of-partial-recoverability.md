# The Law of Partial Recoverability (Mar 15, 2026)
Source: https://richardaragon.substack.com/p/the-law-of-partial-recoverability

## Core Principle
"Important variables are often recoverable from a model's internal state without being represented as universal, invariant, or causally isolated coordinates."

## Key Distinction (three things often conflated)
1. **Readable structure** — information extractable via probes
2. **Native computational structure** — how the system actually organizes internally
3. **Universal geometry** — consistent across architectures

These frequently do NOT align. Probing success ≠ understanding how the model works.

## Experimental Evidence (color autoencoders)
- **Lightness**: Highly readable, aligned to principal directions across architectures
- **Hue**: Recoverable but inconsistent topology; no universal color wheel emerged
- **Saturation**: Most architecture-dependent; entangled with texture and contrast

One beta-VAE reconstructed different input colors into nearly identical grayish outputs — distributed, not cleanly factorized.

## Implication for Topic Routing
If we probe gpt-oss-120B for "topic classification" and it appears to separate algebra from geometry in its representations, that does NOT mean the model actually USES that separation for computation. The readable structure may not be the computational structure. Routing based on probed structure could be steering the model in a direction it doesn't actually compute along.
