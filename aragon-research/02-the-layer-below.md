# The Layer Below (Mar 22, 2026)
Source: https://richardaragon.substack.com/p/the-layer-below

## Core Claim
"If you want to improve an LLM agent's reasoning, operate on the geometry of its latent trajectory, not on the structure of the domain."

## Experiment
Aragon built a domain-knowledge system using differential geometry on program call graphs (Forman-Ricci curvature, spectral gap ratios, cyclomatic complexity) for binary analysis. Despite mathematical rigor, it failed — domain-level optimization doesn't transfer to latent-space decision-making.

He then tried Method B: monitor the model's hidden state trajectory with 5 real-time geometric metrics, and steer via natural-language interventions when metrics indicate stalling.

## Five Geometric Metrics
1. **Menger curvature** — how sharply representations turn
2. **Trajectory divergence** — new vs familiar regions
3. **Subspace concentration** — low-dimensional collapse detection
4. **Cosine similarity** — representation change between steps
5. **Velocity** — step size in embedding space

## Results
| Metric | Implicit (domain) | Latent-Geometric |
|--------|-------------------|------------------|
| Steps to sink | 3.40 | 2.40 |
| Sink reached | 80% | 100% |
| Vulnerability path coverage | 80% | 100% |
| Unique functions visited | 15.6 | 20.2 |
| Forward ratio | 0.12 | 0.17 |

Latent-geometric succeeded on `indirect_taint` (global variable data flows) where implicit failed after 3 steps.

## Trade-off
25% computational overhead from extracting hidden states.

## Key Quote
"The capabilities aren't in the weights, exactly... They're in the geometry of the trajectory through activation space."
