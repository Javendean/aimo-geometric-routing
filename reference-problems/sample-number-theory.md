# Sample Number Theory Problems (IMO-level)

## Problem 1
Find the last three digits of $7^{999}$.

**Topic signals:** modular exponentiation, Euler's theorem
**Strategy hints:** $7^{\phi(1000)} = 7^{400} \equiv 1 \pmod{1000}$, then $7^{999} = 7^{400 \cdot 2 + 199}$. Compute $7^{199} \pmod{1000}$ by repeated squaring.

## Problem 2
Find all positive integers $n$ such that $n^2 + 1$ divides $n! + 1$.

**Topic signals:** divisibility, factorial, quadratic
**Strategy hints:** For large $n$, $n!$ grows much faster than $n^2$. Check small cases. Wilson's theorem may apply when $n^2 + 1$ is prime.

## Problem 3
Determine the number of integers $n$ with $1 \leq n \leq 2025$ such that $\gcd(n, 2025) = 1$.

**Topic signals:** Euler's totient, prime factorization
**Strategy hints:** $2025 = 3^4 \cdot 5^2$, so $\phi(2025) = 2025 \cdot (1 - 1/3)(1 - 1/5) = 1080$.
