# Cross-Topic Problems (25-30% of AIMO 3)

These problems span multiple categories. They test whether routing to a single topic helps or hurts.

## Problem 1: Combinatorial Number Theory
How many integers from 1 to 1000 can be expressed as the difference of two perfect squares?

**Topics:** number theory (perfect squares, parity) + combinatorics (counting)
**Routing challenge:** A number theory strategy focuses on modular arithmetic. A combinatorics strategy focuses on enumeration. The optimal approach uses the algebraic identity $a^2 - b^2 = (a+b)(a-b)$ and then counts — a hybrid.

## Problem 2: Algebraic Geometry
In the coordinate plane, find the area of the region bounded by $|x| + |y| \leq 4$ and $x^2 + y^2 \leq 8$.

**Topics:** geometry (area, curves) + algebra (inequalities, intersection)
**Routing challenge:** Pure geometry uses integration. Pure algebra uses substitution. The fastest approach is geometric reasoning (the diamond inscribes the circle) with algebraic verification.

## Problem 3: Number Theory + Combinatorics
How many ordered triples $(a, b, c)$ of positive integers satisfy $\text{lcm}(a, b, c) = 2^3 \cdot 3^2 \cdot 5$?

**Topics:** number theory (prime factorization, lcm) + combinatorics (counting via exponent vectors)
**Routing challenge:** The problem decomposes into independent choices per prime ($\max(a_p, b_p, c_p) = e_p$), making it combinatorial once the number-theoretic structure is seen.

## Implications for Routing

Cross-topic problems are 25-30% of AIMO 3. If routing assigns them to a single topic, it may:
- Miss the hybrid strategy that's fastest
- Apply topic-specific exemplars that are only partially relevant
- Waste the exemplar token budget on irrelevant examples

Options:
1. Route to dominant topic, accept suboptimality on cross-topic
2. Don't route cross-topic problems (use generic baseline)
3. Route to MULTIPLE topics (inject exemplars from both, double the token cost)
4. Use a "cross-topic" strategy specifically designed for hybrid problems
