# Sample Combinatorics Problems (IMO-level)

## Problem 1
A frog starts at position 0 on the number line and can jump +1 or +2 at each step. In how many ways can the frog reach position $n = 12$?

**Topic signals:** counting paths, recurrence, Fibonacci-type
**Strategy hints:** Let $f(n) = f(n-1) + f(n-2)$ with $f(0)=1, f(1)=1$. Answer: $f(12) = 233$.

## Problem 2
How many permutations of $\{1, 2, \ldots, 8\}$ have no fixed point (derangements)?

**Topic signals:** derangement, inclusion-exclusion, permutation
**Strategy hints:** $D_n = n! \sum_{k=0}^{n} (-1)^k / k!$. Answer: $D_8 = 14833$.

## Problem 3
A committee of 5 people is to be chosen from 6 men and 4 women such that at least 2 women are included. How many ways?

**Topic signals:** binomial coefficients, constrained selection
**Strategy hints:** $\binom{4}{2}\binom{6}{3} + \binom{4}{3}\binom{6}{2} + \binom{4}{4}\binom{6}{1} = 120 + 60 + 6 = 186$
