# Cross-Topic Analysis of AIMO 3 Reference Problems

The 10 reference problems demonstrate why naive topic routing is hard.

## Key Observation from Model Evaluation

gpt-oss-120B solves Problems 1-4 (AIMO2 difficulty) but NONE of Problems 5-10 (AIMO3 difficulty). This means any routing strategy must be evaluated on Problems 5-10, not 1-4 — the model already solves the easy ones regardless of routing.

## Topic Classification Challenges

Several reference problems resist single-topic classification:

- **Problem 2** (rectangles with unique perimeters): combinatorics (construction) + number theory (semi-perimeter bounds) + optimization (proving maximality)
- **Problem 4** (polynomial with integer roots): algebra (polynomial factoring) + number theory (divisor analysis) + combinatorics (counting valid factorizations)
- **Problem 10** (adapted existing problem): likely draws on multiple techniques

## Implications for Routing

1. **Topic overlap**: At IMO level, most problems require techniques from 2+ topics. Routing to a single topic's exemplars may provide the WRONG strategy hints.

2. **Difficulty-dependent routing**: Problems 1-4 don't need routing (model solves them anyway). Problems 5-10 are where routing could help — but these are exactly the problems where topic classification is most ambiguous.

3. **Exemplar selection**: If routing provides worked examples, the examples must be at AIMO3 difficulty level. Providing AMC-level examples for an IMO-level problem wastes context tokens on irrelevant strategies.

4. **The real question**: Is the gain from topic-specific strategy hints (inter-problem routing) enough to overcome the cost of misclassification on cross-topic problems?
