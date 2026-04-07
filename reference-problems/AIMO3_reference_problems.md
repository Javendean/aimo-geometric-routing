# AIMO 3 Reference Problems (Official)

Source: AIMO Progress Prize 3 Reference Bench (November 2025)
10 problems with solutions. gpt-oss-120B solves only Problems 1-4.

---

AIMO Progress Prize 3 – Reference Problems and Solutions∗
November 2025
Overview
This document contains a collection of 10 reference problems, the “AIMO3 Reference Bench”, each
accompanied by a detailed solution. These correspond to the problems provided in reference.csv
on Kaggle. The purpose of this set is threefold:
1. To verify that your Kaggle notebook works correctly before submitting it to run on the public1
problem set.
2. To familiarise you with the style and format of AIMO3 problems, including answer extraction
conventions (note the move from 3 to 5 digits in the final answer) and the types of intermediate
calculations that may be required.
3. To provide a compact benchmark for preliminary testing of models. (Because of its small size,
this set is obviously not suitable for model training or fine-tuning.)
Before publication, we evaluated these problems using leading models available via API and ollama.
Since these problems had never been exposed to any model before testing, the results represent
uncontaminated performance. The results are shown on the next page.
About the Problems
With the exception of Problem 10, which adapts an existing problem, all problems in this reference
set are entirely original and have not been publicly released before the launch of AIMO3.
Problems 1–4 are drawn from the AIMO2 benchmark. Each includes a brief remark summarising
observed results from the AIMO2 Kaggle competition, and for Problems 2 and 3, references to the
OpenAI evaluation on the public AIMO2 set (OpenAI x AIMO eval: The gap is shrinking). Problems
3 and 4 are taken from the private AIMO2 set which was not part of the OpenAI evaluation. The six-
letter problem identifiers (eg “SWEETS”) correspond to those used in the linked analysis. Problem
1 is deliberately straightforward—it is mainly intended as a quick check and should be solvable by
any competent model.
Problems 5–9 are challenging, novel problems designed to reflect the style and difficulty of the
upcoming AIMO3 dataset. Their difficulty is intentionally higher than that of AIMO2 to ensure the
problems continue to challenge the strongest current open-source models.
Problem 10 is an adaptation of a problem from the International Mathematical Olympiad (IMO)
Shortlist.
It illustrates the process of converting a traditional olympiad-style question into the
answer-only format used in AIMO. All problems in the AIMO public and private sets are fully
original; we chose to adapt this one to preserve the hardest original material for the competition
datasets.
About the Solutions
Solutions are written for clarity rather than brevity. Where a result depends on a standard the-
orem or lemma, a brief reference is provided when possible. The goal is to make each argument
straightforward to follow, while acknowledging that the problems themselves are challenging. Only
one solution path is shown for each problem, though multiple valid approaches may exist.
∗To cite these problems, please refer to the citation of the associated Kaggle competition.
1Public is somewhat of a misnomer here as the problem set is not publicly available. Instead, ‘public’ refers to
the problems being used for the public leaderboard on Kaggle.
1


Model Evaluation Results
We evaluated 14 leading language models on the 10-problem AIMO3 Reference Bench, including
both commercial APIs and open-weight models. The results reveal a significant performance gap
that AIMO3 aims to close.2
The strongest commercial models—GPT-5 Pro and GPT-5.1 (high)—solved all 10 problems, with
GPT-5 (high), Grok-4, and Gemini 2.5 Pro each solving 9 out of 10 (failing only on the hardest
Problem 10). In contrast, most open-weight models struggled beyond the easier AIMO2 problems
(Problems 1–4). The best-performing non-DeepSeek open-weight model, gpt-oss-120b, solved only
these four problems and none of the harder Problems 5–10.
A notable exception is DeepSeek-v3.1-terminus (thinking), which matched the performance of
second-tier commercial models by solving 9 out of 10 problems. However, this is a substantially
larger model (671B parameters) compared to other open-weight entries, and still falls short of the
top commercial systems on the hardest problem.
Creating problems that challenge frontier models while working within AIMO’s format presents
a significant design challenge. The competition requires IMO-style problems with non-guessable
integer answers for automated evaluation. Most olympiad problems, however, are proof-based and
either have no numerical answer at all, or have answers that are easily guessable (eg, small integers)
or binary (yes/no). While challenging problems meeting AIMO’s criteria do exist, they are much
harder to identify and create. Proof-based evaluation would open up significantly more options for
difficult olympiad problems, but remains challenging to implement in a scalable and reliable way.
The near-perfect performance of frontier commercial models on this reference set demonstrates
what’s possible: closing this gap across the full 50-problem public set could yield scores in the high
40s. This would represent a substantial leap from the mid-30s winning scores in AIMO1 and AIMO2,
marking a major milestone in open-source mathematical reasoning capabilities.
Closing this gap is the core challenge of AIMO3. Can your submission demonstrate that open-weight
models can match frontier commercial performance on advanced mathematical reasoning?
2Model outputs are non-deterministic, so results may vary across runs. Additionally, models accessed via API
may be updated over time, potentially affecting performance.
2


Problem 1
Problem: Alice and Bob are each holding some integer number of sweets. Alice says to Bob: “If
we each added the number of sweets we’re holding to our (positive integer) age, my answer would
be double yours. If we took the product, then my answer would be four times yours.” Bob replies:
“Why don’t you give me five of your sweets because then both our sum and product would be equal.”
What is the product of Alice and Bob’s ages?
Answer: 50
Solution: Let Alice and Bob’s ages be xA and xB, respectively. After Alice gives Bob five sweets,
let Alice have yA sweets and Bob have yB sweets. We have
(
S = xA + yA = xB + yB
P = xAyA = xByB
.
The unordered pairs {xA, yA} and {xB, yB} each form the set of roots of the quadratic z2−Sz+P = 0.
Hence the sets are equal (possibly with the elements swapped). We consider the two cases.
Case 1 xA = xB = x, yA = yB = y
Before the exchange, Alice holds y + 5 sweets and Bob y −5 so the conditions become
(
(x + y + 5) = 2(x + y −5) =⇒x + y = 15
x(y + 5) = 4x(y −5) =⇒x(3y −25) = 0
.
The second condition forces either x = 0 or 3y = 25, both of which violate the ages being positive
integers.
Case 2 xA = yB = x, yA = xB = y
Before the exchange, Alice holds y + 5 sweets and Bob x −5 so the conditions become:
(
(x + y + 5) = 2(x + y −5) =⇒x + y = 15
x(y + 5) = 4y(x −5) =⇒3xy −20y −5x = 0
=⇒0 = 3x(15 −x) −20(15 −x) −5x = −3(x −10)2 =⇒x = 10.
We then have y = 15 −x = 5. It is easy to verify that if at the start, Alice is aged 10 and holds 10
sweets and Bob is aged 5 and holds 5 sweets then the conditions are satisfied. Therefore, the answer
we report is 5 × 10 = 50 .
Remark: This problem was part of the AIMO2 private set (“SWEETS”) and was solved by approx-
imately 85% of submissions, including all of the top 100. We include it as an example of a problem
that current models are expected to solve easily, which may assist in testing your model using the
reference set on Kaggle. This problem is easier than any problem used in AIMO3, so the problems
below should be used instead to give an indication of difficulty.
3


Problem 2
Problem: A 500 × 500 square is divided into k rectangles, each having integer side lengths. Given
that no two of these rectangles have the same perimeter, the largest possible value of k is K. What
is the remainder when K is divided by 105?
Answer: 520
Solution: We first show that the square can be divided into 520 rectangles subject to the constraints,
and then prove that this is the maximum number possible.
In the bottom 249 rows, place 249 pairs of rectangles 1 × i and 1 × (500 −i) for i = 1, . . . , 249.
Then, place a single 1 × 500 rectangle in the row above to complete the bottom half. For the top
half, place a 1 × 250 rectangle vertically along the left side and then 20 more horizontal rectangles
i × 499 for i = 3, 4, . . . , 22 (note that 3 + 4 + · · · + 22 = 1
2 · 22 · 23 −3 = 250).
The rectangles in the bottom half have perimeters 4, 6, . . . , 500, 504, 506, . . . , 1000, 1002 whilst the
rectangles in the top half have perimeters 502, 1004, 1006, . . . , 1042 so all these perimeters are dif-
ferent. In total we have placed (2 × 249) + 1 + 1 + 20 = 520 rectangles proving the lower bound.
To show that 520 is optimal, assume we can place k ≥521 rectangles subject to the constraint.
First, note that the perimeters are all even integers and equal to 2s where s is the semi-perimeter of
the rectangle. If the two sides of the rectangle are x and y, then s = x+y and the area of the rectangle
is A = xy = x(s −x). Since this is a downwards-pointing quadratic in x, A is minimised when x
takes either its minimum or maximum value. Noting that 1 ≤x ≤500 and 1 ≤y = s −x ≤500, we
see
max {1, s −500} ≤x ≤min {500, s −1}.
If s ≤500, this bound is simply 1 ≤x ≤s −1 and we see both the minimum and maximum values
for x give A = s −1 meaning that A ≥s −1 whenever s ≤500.
If s ≥501, the bound becomes s −500 ≤x ≤500 and we see both the minimum and maximum
values for x give A = 500(s −500) meaning that A ≥500(s −500) whenever s ≥501.
Define
f(s) =
(
s −1
1 ≤s ≤500
500(s −500)
s ≥501
.
Observing that 500 −1 = 499 < 500(501 −500), we see that f(s) is an increasing function. Further-
more, the above shows a rectangle with semi-perimeter s has area A ≥f(s).
Now suppose the 521 rectangles have semi-perimeters 2 ≤s1 < s2 < · · · < s521 and areas
A1, . . . , A521.
By considering the total area of the rectangles and using that f(s) is increasing,
we have
5002 = A1 + · · · + A521 ≥f(s1) + · · · + f(s521) ≥f(2) + f(3) + · · · + f(522).
We can then calculate
5002 ≥
500
X
s=2
f(s) +
522
X
s=501
f(s) =
500
X
s=2
(s −1) +
522
X
s=501
500(s −500) = 124,750 + 126,500 > 5002
which is a contradiction.
Thus, 520 is indeed the optimal number of rectangles and this is the answer we report.
4


Remark 1: As this problem demonstrates, some answers are already smaller than the modulus for
which the remainder is requested. In this case, the model should simply return the answer with no
further calculations required.
Remark 2: This problem was part of the AIMO2 public set (“RECTIL”) and was solved by only
a handful of the top 100 teams, and by none of the ultimate top 5. Interestingly, in the OpenAI
x AIMO eval, the high compute run did not return the correct answer in its top response though
lower compute runs did return the correct answer.
5


Problem 3
Problem: Let ABC be an acute-angled triangle with integer side lengths and AB < AC. Points
D and E lie on segments BC and AC, respectively, such that AD = AE = AB. Line DE intersects
AB at X. Circles BXD and CED intersect for the second time at Y ̸= D. Suppose that Y lies
on line AD. There is a unique such triangle with minimal perimeter. This triangle has side lengths
a = BC, b = CA, and c = AB. Find the remainder when abc is divided by 105.
Answer: 336
Solution: As Y lies on line AD, we see A lies on line DY which is the radical axis of circles BXD
and CED. We therefore have AE · AC = AB · AX, which gives AX = AC since AE = AB. These
two results together show pairs (B, E) and (X, C) are reflections across the bisector of ∠BAC so D
must be the intersection of this bisector with BC. We can run this argument in reverse to see that
D lying on the angle bisector is also a sufficient condition for Y to lie on line AD.
A
B
D
C
E
X
Y
If we define D′ as the intersection of the internal angle bisector of ∠BAC with side BC, the above
shows that Y lies on AD if and only if AD′ = AB (and therefore D = D′).
From angle bisector theorem, we have BD′ =
ac
b+c and CD′ =
ab
b+c. Define d = AD′. We can apply
Stewart’s theorem to triangle ABC with cevian AD to get
a ·
ac
b + c ·
ab
b + c + ad2 = b2 ·
ac
b + c + c2 ·
ab
b + c = abc =⇒d2 = bc
 (b + c)2 −a2
(b + c)2
.
AD′ = AB is equivalent to d = c which we can express as
c2 = bc
 (b + c)2 −a2
(b + c)2
⇐⇒

a
b + c
2
= b −c
b
.
We are told that a, b, c are positive integers with c < b. We want to find the minimum such values
that are the sides of a triangle and satisfy these conditions.
6


Write g = gcd(b, c) and b = gb′, c = gc′ where gcd(b′, c′) = 1. The above then becomes
· · · ⇐⇒

a
g (b′ + c′)
2
= b′ −c′
b′
.
Since the numerator and denominator are coprime and positive, we must have b′ −c′ = y2 and
b′ = x2 for coprime positive integers x and y with x > y then
· · · =⇒
a
g (2x2 −y2) = y
x =⇒a = gy
 2x2 −y2
x
.
Note that gcd
 2x2 −y2, x

= gcd
 y2, x

= 1 so, for a to be an integer, we must have x | g. Write
g = kx for a positive integer k. We can then summarise the solutions as
(a, b, c) =
 ky
 2x2 −y2
, kx3, kx
 x2 −y2
.
(■)
Triangle inequality is equivalent to:
b + c > a ⇐⇒(x −y)
 2x2 −y2
> 0
a + c > b ⇐⇒y
 2x2 −xy −y2
> 0
a + b > c ⇐⇒y(x + y)(2x −y) > 0.
These will always be satisfied for coprime positive integers x and y with x > y. We can also check
b > c ⇐⇒x2 > x
 x2 −y2
⇐⇒xy2 > 0
which will be satisfied for x, y ≥1.
Lastly, note that all the steps above are reversible so the family given in (■) exactly characterises
triangles with the desired property.
What remains is to find the triangle with minimal perimeter. Since k simply scales the perimeter,
we must have k = 1 for the triangle with minimal perimeter and then
a + b + c = y
 2x2 −y2
+ x2 + x
 x2 −y2
= (x + y)
 2x2 −y2
.
This is an increasing function of x so to minimise the perimeter, we will choose x = y + 1 (which
means x and y will be coprime). The above becomes
· · · = (2y + 1)
 y2 + 4y + 2

which is an increasing function of y so is minimised at y = 1.
The pair x = 2, y = 1 corresponds to (a, b, c) = (7, 8, 6) which has all of the required properties (the
triangle is acute since 82 < 72 + 62). The answer we report is
7 × 8 × 6 = 336 .
Remark: This problem was also part of the AIMO2 public set (“MINPER”) and was again solved
by only a handful of the top 100 teams, and by none of the ultimate top 5. This problem was solved
in the OpenAI x AIMO eval by all compute levels.
7


Problem 4
Problem: Let f : Z≥1 →Z≥1 be a function such that for all positive integers m and n,
f(m) + f(n) = f(m + n + mn).
Across all functions f such that f(n) ≤1000 for all n ≤1000, how many different values can f(2024)
take?
Answer: 580
Solution: Let Z≥2 = {2, 3, . . .} be the set of positive integers greater than or equal to 2. Define a
function g: Z≥2 →Z≥1 by g(n) = f(n −1) for n ≥2. From the given relation for f we have, for
n, m ≥2,
g(m) + g(n) = f(m −1) + f(n −1) = f(m −1 + n −1 + (m −1)(n −1)) = f(mn −1) = g(mn). (∗)
Repeatedly applying (∗), we see that if n = pα1
1 · · · pαk
k
is the prime factorisation of n ≥2 then
g(n) = g(pα1
1 ) + · · · + g(pαk
k ) = α1 · g(p1) + · · · + αk · g(pk).
(▲)
We have f(2024) = g(2025) and the prime factorisation of 2025 is 2025 = 34 · 52 so
f(2024) = g(2025) = 4g(3) + 2g(5).
We are left to consider the possible values for the above quantity subject to the condition that
g(n) = f(n −1) ≤1000 for 2 ≤n ≤1001.
Claim: 1 ≤g(3) ≤166 and 1 ≤g(5) ≤250. For each choice of g(3) and g(5) in these ranges, we
can construct a function g satisfying (∗).
Proof. Firstly, from (▲), we have
1000 ≥g(729) = g
 36
= 6g(3) =⇒g(3) ≤
1000
6

= 166
1000 ≥g(625) = g
 54
= 4g(5) =⇒g(5) ≤
1000
4

= 250
which proves the bounds.
Next, let 1 ≤s ≤166 and 1 ≤t ≤250. For a positive integer n ≥2, let n = 3α · 5β · pγ1
1 · · · pγk
k
be
its prime factorisation with pi ̸= 3, 5 and possibly with α or β being 0. Define a function g by
g(n) = g
 3α · 5β · pγ1
1 · · · pγk
k

= αs + βt + γ1 + · · · + γk.
This can easily be seen to satisfy (∗) and also has g(3) = s, g(5) = t.
Let n ≤1001, it remains to check g(n) ≤1000. Define γ = γ1 + · · · + γk then
1001 ≥n ≥2γ · 3α · 5β
and
g(n) = αs + βt + γ ≤166α + 250β + γ.
(■)
We now consider the possible values for β. Since 5β ≤n ≤1001, we have 0 ≤β ≤4.
• β = 4: Since 54 = 625, (■) forces α = γ = 0 so g(n) ≤250 × 4 = 1000.
8


• β = 3: Similarly, 53 = 125 so from (■), α ≤1 and γ ≤3 so
g(n) ≤166 × 1 + 250 × 3 + 3 = 919 ≤1000.
• β = 2: If α = 3, then 1001 ≥n = 2γ · 33 · 52 = 675 · 2γ so γ = 0. From (■),
g(n) ≤3 × 166 + 2 × 250 + 0 = 998 ≤1000.
Otherwise, α ≤2 and, as γ ≤5,
g(n) ≤166 × 2 + 250 × 2 + 5 = 837 ≤1000.
• β = 1: 51 = 5 and from (■), α ≤4, γ ≤7 so
g(n) ≤166 × 4 + 250 × 1 + 7 = 921 ≤1000.
• β = 0: If α = 6, then γ = 0 and g(n) ≤6 × 166 = 996 ≤1000. Otherwise, α ≤5 and also
γ ≤9 leading to
g(n) ≤166 × 5 + 250 × 0 + 9 = 839 ≤1000.
In any case, we see the condition on g will be satisfied so we can reverse the process to get a valid
function f.
From the Claim, we have f(2024) = 4s + 2t = 2(2s + t) with 1 ≤s ≤166 and 1 ≤t ≤250. (2s + t)
can take any value between 3 and 250 + 2 × 166 = 582 and f(2024) is equal to double this so, in
total, there are 582 −3 + 1 = 580 possible values which is the answer we report.
Remark: This problem was part of the AIMO2 private set (“FUNVAL”) and was solved by about
2% of all submissions, including roughly 20% of the top 100 (though not all of the top 5). This
highlights the trade-offs made by top-ranking models, which may fail to solve certain problems that
a larger fraction of lower-ranked models can, yet they still achieve higher overall performance.
9


Problem 5
Problem: A tournament is held with 220 runners each of which has a different running speed. In
each race, two runners compete against each other with the faster runner always winning the race.
The competition consists of 20 rounds with each runner starting with a score of 0. In each round,
the runners are paired in such a way that in each pair, both runners have the same score at the
beginning of the round. The winner of each race in the ith round receives 220−i points and the loser
gets no points.
At the end of the tournament, we rank the competitors according to their scores. Let N denote the
number of possible orderings of the competitors at the end of the tournament. Let k be the largest
positive integer such that 10k divides N. What is the remainder when k is divided by 105?
Answer: 21818
Solution: Since the points received in a given round are strictly greater than the points available
in all subsequent rounds (from 2k > 2k −1 = 2k−1 + 2k−2 + · · · + 1), each runner must be paired
with another runner with an identical win/loss record in the preceding rounds (so they have the
same score). Thus, in round i there are 2i−1 groups (based on the possible win/loss sequences in the
previous i −1 rounds) each consisting of 221−i runners. Also, a runner’s (ordered) win/loss record
across the rounds uniquely determines their final position by uniqueness of binary expansions.
Consider a group with the same score in a particular round and let there be 2n runners in that group.
We need to count the number of valid ways to choose n winners from these 2n runners. Label the
runners from 1 (fastest) to 2n (slowest), and record the outcome of each race in a left-to-right string
of parentheses, where:
• ( indicates that runner wins the race,
• ) indicates that runner loses.
In a valid string, each ( must match with a later ), corresponding to a race between a faster and
slower runner. For example, when n = 3, the string (()()) represents the matches: 1 beats 6, 2 beats
3, and 4 beats 5.
It is well-known that the number of such valid parenthesis strings is the nth Catalan number
Cn =
1
n + 1
2n
n

=
(2n)!
n!(n + 1)!.
Now in round i, we have 2i−1 groups each consisting of 221−i runners. By the above, there are

C220−i
2i−1
=
 
 221−i
!
(220−i)! (220−i + 1)!
!2i−1
ways to choose the winners in this round. Since each choice of winners across the different groups
will lead to a different final position (by the comment at the top about the win/loss records uniquely
determining the final position), the number of possible orderings is equal to the product of the above
10


quantity over the rounds 1 ≤i ≤20 which is
N =
20
Y
i=1
 
 221−i
!
(220−i)! (220−i + 1)!
!2i−1
=
20
Y
i=1
1
(220−i + 1)2i−1 ·
  221−i
!
2i−1
((220−i)!)2i
=
" 20
Y
i=1
1
(220−i + 1)2i−1
#
·
  220
!
20
((219)!)21 ·
  219
!
21
((218)!)22 · · ·
  21
!
219
((20)!)220
=
 220
! ·
20
Y
i=1
1
(220−i + 1)2i−1
We are then left to determine the highest power of 10 dividing N. Applying Legendre’s Formula,
we can compute the highest power of 2 and 5 dividing
 220
! as
ν2
  220
!

=
∞
X
k=1
220
2k

= 219 + 218 + · · · + 21 + 20 = 220 −1
ν5
  220
!

=
∞
X
k=1
220
5k

=
220
5

+
220
52

+ · · · +
220
58

= 262,140 .
We can also see that all the terms in the denominator in the expression for N are odd except the
final one for i = 20. Thus,
ν2(N) =
 220 −1

−ν2

2220−1
=
 220 −1

−219 = 219 −1 .
Since powers of 2 cycle with period 4 modulo 5, we have that 220−i + 1 will be divisible by 5 if and
only if 20 −i ≡2 mod 4 which is equivalent to i = 4k + 2 for some non-negative integer k. In this
case, we can write
220−i + 1 = 220−(4k+2) + 1 = 22(9−2k) + 1 = 49−2k + 1 .
We can apply the Lifting the Exponent Lemma (or just directly compute given the small number of
possibilities for k) that
ν5
 49−2k + 1

= ν5(4 + 1) + ν5(9 −2k) = 1 + ν5(9 −2k) =
(
1
k ∈{0, 1, 3, 4}
2
k = 2
.
Now introducing the powers in the denominator, we get
ν5
 20
Y
i=1
 220−i + 1
2i−1!
= 22−1 + 26−1 + 210−1 · 2 + 214−1 + 218−1 = 140,322 .
Thus,
ν5(N) = 262,140 −140,322 = 121,818 .
To get a factor of 10 in N, we must have a factor of 2 and a factor of 5. Noting that 219 −1 =
524,287 > 121,818, we see that factors of 5 are the limiting ones. We therefore have
k = ν5(N) = 121,818 ≡21818
(mod 105)
which is the answer we report.
11


Problem 6
Problem: Define a function f : Z≥1 →Z≥1 by
f(n) =
n
X
i=1
n
X
j=1
j1024
1
j + n −i
n

.
Let M = 2 · 3 · 5 · 7 · 11 · 13 and let N = f
 M 15
−f
 M 15 −1

. Let k be the largest non-negative
integer such that 2k divides N. What is the remainder when 2k is divided by 57?
Answer: 32951
Solution: We make use of two identities. Define σk(n) = P
d|n
dk.
Claim 1: (Hermite’s Identity). For any x ∈R and positive integer n, we have
n
X
i=1

x + n −i
n

= ⌊nx⌋.
Proof. Let
d(x) = ⌊nx⌋−
n
X
i=1

x + n −i
n

.
Then,
d

x + 1
n

= ⌊nx + 1⌋−
n
X
i=1

x + n + 1 −i
n

= ⌊nx⌋+ 1 −
 n
X
i=1

x + n −i
n
!
−1 = d(x),
hence d is periodic with period 1
n. Since all floors are 0 for x ∈

0, 1
n

, this gives d ≡0 in general.
Claim 2: For any positive integer n,
n
X
j=1
σk(j) =
n
X
d=1
dk jn
d
k
.
(■)
Proof. We count
S =
n
X
j=1
X
d|j
dk
in two ways. The LHS of (■) comes from the definition of σk.
For d = 1, 2, . . . , n, we have
 n
d

multiples of d at most n, hence this is the number of times dk is
summed. This gives the RHS of (■). Thus, both sides of (■) are equal to S so in particular, are
equal to each other.
Flipping the order of summation in f, we have
f(n) =
n
X
j=1
j1024
n
X
i=1
1
j + n −i
n

Claim 1
=
n
X
j=1
j1024
n
j

Claim 2
=
n
X
j=1
σ1024(j).
12


We therefore have
N = f
 M 15
−f
 M 15 −1

= σ1024
 M 15
.
Define P = {2, 3, 5, 7, 11, 13} so M = Q
p∈P
p. By considering the possibilities for the prime factorisa-
tion of d in the definition of σ1024 and raising these to the power of k we get
N = σ1024
 M 15
=
Y
p∈P
 1 + p1024 + p2·1024 + · · · + p15·1024
=
Y
p∈P
p16·1024 −1
p1024 −1 .
We want to count the number of factors of 2 in this expression. For p = 2, the expression will be
odd so it suffices to consider the odd p. We apply the Lifting the Exponent Lemma in the even
power case to get
ν2
 p102416 −1

−ν2
 p1024 −1

= ν2
 p1024 + 1

+ ν2(16) −1 = 1 + 4 −1 = 4.
where we have used p2 ≡1 mod 4 for all odd p so p1024 + 1 ≡2 mod 4 is divisible by 2 but not 4.
Since there are 5 odd elements of P, we get
k = ν2(N) = 5 · 4 = 20.
Lastly, we compute
2k = 220 ≡32951
(mod 57)
which is the answer we report.
Remark: The choice of 57 as the modulus in this problem is intended to emphasise that models
should be able to handle a variety of moduli—not just 105 or 99991 which are the most commonly
used (the latter is used when a prime modulus is desirable). For AIMO3, all problem statements
have the modulus included explicitly (unlike for AIMO1 and AIMO2 where there was an implicit
step of taking your answer modulo 1000).
13


Problem 7
Problem: Let ABC be a triangle with AB ̸= AC, circumcircle Ω, and incircle ω. Let the contact
points of ω with BC, CA, and AB be D, E, and F, respectively. Let the circumcircle of AFE meet
Ωat K and let the reflection of K in EF be K′. Let N denote the foot of the perpendicular from D
to EF. The circle tangent to line BN and passing through B and K intersects BC again at T ̸= B.
Let sequence (Fn)n≥0 be defined by F0 = 0, F1 = 1 and for n ≥2, Fn = Fn−1 + Fn−2. Call ABC
n-tastic if BD = Fn, CD = Fn+1, and KNK′B is cyclic. Across all n-tastic triangles, let an denote
the maximum possible value of CT ·NB
BT ·NE . Let α denote the smallest real number such that for all
sufficiently large n, a2n < α. Given that α = p + √q for rationals p and q, what is the remainder
when

pqp
is divided by 99991?
Answer: 57447
Solution: We assume AB < AC since all n-tastic triangles have this property and that is where we
are working towards. For now however, we consider all triangles with this property and will impose
the n-tastic condition later.
A
B
C
D
E
F
K
K′
N
σ
Γ
Σ
P
T ′
P ′
Denote circle KNK′ and KND by σ and Σ, respectively. Let EF intersect BC at T ′. Next, let σ
and Σ intersect line BN again at P ̸= N and P ′ ̸= N, respectively.
14


From its definition, K is the centre of spiral similarity taking FE →BC. Denote this spiral similarity
by f so f(F) = B, f(E) = C, and f(K) = K. We recall some well-known results:
• K is also the centre of spiral similarity taking BF →CE.
• T ′BFK is cyclic—denote this circle by Γ.
Claim 1: f(N) = D.
Proof. This is a well-known result but for completeness, we provide a proof.
Firstly, recall that lines AD, BE, and CF concur at the Gergonne point of triangle ABC. Thus,
we can apply Ceva’s and Menelaus’s theorem to get
BT ′
T ′C
Menelaus
=
−AE
EC · BF
FA
Ceva
=
−BD
DC
where we are using directed lengths so if a point lies outside the segment, the ratio is negative. This
means that (B, C; T ′, D) = −1 where the term in brackets denotes the cross ratio of the four points.
We have ∠T ′ND = 90◦and it is well-known (eg see here) that these two properties combined imply
that ND and T ′N bisect ∠BNC (internally and externally, respectively).
From this, we get ∠FNB = ∠CNE. Since AE = AF, ∠AEF = ∠EFA which implies ∠BFN =
∠NEC. Combining these two results shows triangle BFN and CEN are similar hence
FN
NE = BF
CE = BD
DC
where we have used that BF and BD are both tangents from B to the incircle so have equal length,
and similarly for C.
Since f(FE) = BC and N and D split these segments in the same ratio, the claim follows.
A consequence of Claim 1 and properties of spiral similarities is that Σ passes through T ′. Since
∠T ′ND = 90◦, this also shows Σ has diameter T ′D.
Claim 2: P lies on Γ.
Proof. Firstly, note that σ is uniquely defined as the circle passing through K and N that has centre
on line EF (which is equivalent to σ passing through K′). Applying the transformation f, we see
f(σ) is uniquely defined as the circle passing through f(K) = K and f(N) = D (Claim 1) that has
centre on line f(EF) = BC. But from the comment above, this precisely defines Σ, thus f(σ) = Σ.
Next, we see that
∠FNP = ∠T ′NP ′ = ∠T ′DP ′ = ∠BDP ′.
Since f(FN) = BD and f(σ) = Σ, this shows f(P) = P ′. Thus,
∠FPK = ∠f(F)f(P)f(K) = ∠BP ′K = ∠NP ′K = ∠NT ′K = ∠FT ′K
which shows that P lies on circle FT ′K ie Γ.
15


Claim 3: For an n-tastic triangle, T = T ′ and BNEC is cyclic.
Proof. For these triangles B lies on σ so we must in fact have P = B. It then follows (by considering
P moving towards B along line BN) that Γ is tangent to BN at B. Since Γ also passes through
K, this must be the circle described at the bottom of the first paragraph in the question. Since Γ
intersects BC again at T ′ ̸= B, the first part of the claim follows.
For the second part, applying the alternate segment theorem using the tangency of Γ to BN we get
∠CBN = ∠TBP ′ = ∠TFB = ∠EFA = ∠AEF = 180◦−∠NEC
which proves that BNEC is cyclic.
A
B = P
C
D
E
F
K
K′
N
T = T ′
We now consider n-tastic triangles and use T and T ′ interchangeably since they are the same point.
Recalling from Claim 1 that triangles BFN and CEN are similar and then using Claim 3 we get
∠EBN = ∠ECN = ∠NBF = ∠BTN
where in the last step we used that BN is tangent to Γ. We also have
∠CBE = ∠CNE = ∠FNB = 180◦−∠BNE = ∠ECB
so EC = EB.
Applying the sine rule to triangles EBN and ETB, we get
NB
NE = sin ∠NEB
sin ∠EBN = sin ∠TEB
sin ∠BTE = BT
BE = BT
CE = BT
CD.
We can use this to rewrite the target expression in the question as
CT · NB
BT · NE = CT
BT · BT
CD = CT
CD.
16


We are told that BD = Fn and CD = Fn+1 so BC = BD + CD = Fn+2.
Returning to the
calculations in Claim 1 (and this time using undirected lengths), we have
CD
BD = Fn+1
Fn
= CT
BT =
CT
CT −BC =
CT
CT −Fn+2
=⇒CT = Fn+1Fn+2
Fn−1
.
This allows us to write (noting that the quantity in the question is constant across all n-tastic
triangles)
an = CT · NB
BT · NE = CT
CD = Fn+2
Fn−1
.
Let φ = (1 +
√
5)/2 be the golden ratio. Using Binet’s formula, we can write
an = φn+2 −(−φ)−(n+2)
φn−1 −(−φ)−(n−1) .
Now specialising to n even, we have
a2n = φ2n+2 −φ−(2n+2)
φ2n−1 + φ−(2n−1) = φ3 · 1 −φ−4n−4
1 + φ−4n+2
|
{z
}
(∗)
< φ3.
Since φ > 1, we have (∗) →1
1 = 1 as n →∞, thus the smallest real number α with the desired
property is φ3. We can compute
φ3 = 2 +
√
5 =⇒p = 2 , q = 5
so the answer we report is
252 = 33554432 ≡57447
(mod 99991).
Remark: Because of the problem’s conditional structure—and that it concerns a family of triangles
rather than one specific configuration—brute-force approaches that attempt to construct one or
more diagrams and compute all lengths numerically are unlikely to succeed.
17


Problem 8
Problem: On a blackboard, Ken starts off by writing a positive integer n and then applies the
following move until he first reaches 1. Given that the number on the board is m, he chooses a base
b, where 2 ≤b ≤m, and considers the unique base-b representation of m,
m =
∞
X
k=0
ak · bk
where ak are non-negative integers and 0 ≤ak < b for each k. Ken then erases m on the blackboard
and replaces it with
∞
P
k=0
ak.
Across all choices of 1 ≤n ≤10105, the largest possible number of moves Ken could make is M.
What is the remainder when M is divided by 105?
Answer: 32193
Solution: Consider the directed graph G with positive integers as vertices and a directed edge from
n to every output of a move from n. We completely determine G.
Claim 1: The outgoing neighbours of n are exactly {⌈n/2⌉, ⌈n/2⌉−1, . . . , 2, 1}.
Proof. These are achievable by bases ⌊n/2⌋+ 1, ⌊n/2⌋+ 2, . . . , n, respectively since for a base
⌊n/2⌋+ 1 ≤b ≤n, n has two digits in base-b, 1 and n −b, so the digit sum is n + 1 −b.
Next we show that there are no other neighbours. Equivalently, we need to prove that if there is an
edge from n to r (that is, if for some base b with 2 ≤b ≤n the sum of the base-b digits of n equals
r), then r ≤⌈n/2⌉. We can verify this directly for n ≤10, so henceforth assume n > 10.
Consider n in base-b, where 2 ≤b < n. Since we wish to maximise the sum of the base-b digits, we
can replace bk with b copies of bk−1 as this will always increase the sum of the digits. Repeating this
process for all powers bk for k ≥2, we reduce n to having only 2 base-b digits, the largest of which
must be ⌊n/b⌋so we can write
n =
jn
b
k
b +

n −b
jn
b
k
.
Thus, in general
r = Sum of base-b digits of n ≤
jn
b
k
+

n −b
jn
b
k
=
jn
b
k
+ (n mod b)
where the final term should take the remainder in the range 0 to b −1.
For b = 2, this gives ⌈n/2⌉.
For 3 ≤b ≤⌊n/2⌋−2, we have the bound
r ≤
jn
b
k
+ (n mod b) ≤n
b + b −1.
For fixed n, consider f(b) = (n/b) + b. Since
f(b + 1) −f(b) = −
n
b(b + 1) + 1,
18


f will be decreasing up to a certain value (possibly no values) and then will be increasing from that
point on. This means f(b) will be maximised at an endpoint. By rearranging, we have
f(3) = (n/3) + 3 ≤⌈n/2⌉+ 1 ⇐⇒
(
n ≥12
n even
n ≥9
n odd
which are both true since n > 10.
For b = ⌊n/2⌋−2, we have
f(⌊n/2⌋−2) =
n
⌊n/2⌋−2 + ⌊n/2⌋−2 ≤⌈n/2⌉+ 1 ⇐⇒
(
n ≥12
n even
n ≥10
n odd
which are both true since n > 10. Thus, we have shown f(b) ≤⌈n/2⌉+ 1 for b in the given range
meaning
r ≤f(b) −1 ≤⌈n/2⌉
as desired.
We are left to consider ⌊n/2⌋−1 ≤b ≤n.
For ⌊n/2⌋−1 ≤b ≤⌊n/2⌋, n in base-b will have two digits, the first being a 2 and the second being
0, 1, 2, or 3. Thus the sum of the digits is ≤5 ≤⌈n/2⌉(since n > 10).
For ⌊n/2⌋+ 1 ≤b ≤n, n in base-b will be two digits, the first of which is 1 and the second of which
is n −b. Thus,
r = 1 + (n −b) ≤n + 1 −(⌊n/2⌋+ 1) = n −⌊n/2⌋= ⌈n/2⌉
since b ≥⌊n/2⌋+ 1. This completes the proof.
Claim 2: The length of the longest path from n to 1 has length ⌈log2(n)⌉.
Proof. Note that a move strictly decreases the value on the blackboard. Let f(n) denote the length
of the longest path from n to 1 in G. By considering the first move and using Claim 1, we get
f(n) = 1 + max{f(⌈n/2⌉), f(⌈n/2⌉−1), . . . , f(2), f(1)}.
This Claim then follows by induction, using ⌈log2(2n + 1)⌉= ⌈log2(2n)⌉= 1 + ⌈log2(n)⌉for n ≥1
since 2n + 1 is not a power of 2.
Thus, we extract the answer
l
log2

10105m
=

105 · log2 (10)

= 332193 ≡32193
(mod 105)
which is the number we report.
Remark: In order to prevent direct enumeration approaches, many of the numbers that appear in
problems for AIMO3 are very large. We expect models to be able to handle calculations such as the
above when calculating answers.
19


Problem 9
Problem: Let F be the set of functions α: Z →Z for which there are only finitely many n ∈Z
such that α(n) ̸= 0.
For two functions α and β in F, define their product α ⋆β to be P
n∈Z
α(n) · β(n). Also, for n ∈Z,
define a shift operator Sn : F →F by Sn(α)(t) = α(t + n) for all t ∈Z.
A function α ∈F is called shifty if
• α(m) = 0 for all integers m < 0 and m > 8 and
• There exists β ∈F and integers k ̸= l such that for all n ∈Z
Sn(α) ⋆β =
(
1
n ∈{k, l}
0
n ̸∈{k, l} .
How many shifty functions are there in F?
Answer: 160
Solution: For α ∈F, we define two functions
Pα(x) =
X
k∈Z
α(k) · xk
Qα(x) =
X
k∈Z
α(k) · x−k.
The conditions on F ensure that both sums only have finitely many non-zero terms and so Pα is
a polynomial of degree at most 8 and Qα is a finite Laurent polynomial (an extension of a normal
polynomial to include negative powers of x).
Let α ∈F be shifty and let β be such that Sn(α)⋆β is of the form defined in the question statement.
We have
Sn(α) ⋆β =
X
k∈Z
Sn(α)(k)β(k) =
X
k∈Z
α(k + n)β(k).
We can write
Pα(x) =
X
k∈Z
α(k + n)xk+n = xn X
k∈Z
α(k + n)xk.
For a Laurent polynomial R and integer p, let [xp] R denote the xp coefficient in R. Using the above,
we can write
Sn(α) ⋆β = [xn] Pα · Qβ =⇒xk + xl =
X
n∈Z
Sn(α) ⋆β = Pα(x)Qβ(x)
where k and l are as in the condition in the problem statement.
Note that multiplying Q by a power of x (which is the same as shifting β to the right) will just
increase the integers k and l (by the same amount). Thus, we can assume that Qβ is in fact a
polynomial and k and l are non-negative integers.
The question now becomes how many polynomials P of degree at most 8 divide a polynomial of the
form xk + xl for non-negative integers 0 ≤k < l. Setting b = l −k ≥1, this is equivalent to dividing
a polynomial of the form
xa  xb + 1

for non-negative integers a and b.
20


Let Φn(x) denote the nth cyclotomic polynomial which has integer coefficients and degree φ(n) where
φ is the Euler totient function. This is well-known to be irreducible and also we have
xn −1 =
Y
d|n
Φd(x).
Therefore, we can write
xa  xb + 1

= xa · x2b −1
xb −1 = xa ·
Y
d|2b , d∤b
Φd(x).
As the Φd are all irreducible, a polynomial P will divide a polynomial of the above form if and only
if it can be written as
P(x) = ±xm Y
d∈S
Φd(x)
(■)
for a non-negative integer m and a (possibly empty) set S which has the property that all its elements
have the same largest power of 2 dividing them and that power is at least 21 (to enable us to choose
a positive integer n such that S ⊂{d : d|2n, d ∤n}). We will count the number of choices with a +
sign and then double the count at the end to allow for the choices with a −sign. Note that P is not
identically 0 so these choices of sign will yield different polynomials.
Claim: φ(n) ≤8 if and only if 1 ≤n ≤10 or
n ∈{12, 14, 15, 16, 18, 20, 24, 30}.
Proof. It is easy to check all the n in the given set give φ(n) ≤8. Now, for contradiction, assume
there is a positive integer n not on our list with φ(n) ≤8.
If n has at least three odd prime divisors p1 < p2 < p3 then
φ(n) ≥(p1 −1) (p2 −1) (p3 −1) ≥(3 −1)(5 −1)(7 −1) = 48 > 8.
If n has two odd prime divisors p1 < p2 then if p2 ≥7 we have
φ(n) ≥(p1 −1) (p2 −1) ≥(3 −1)(7 −1) = 12 > 8.
Otherwise, p1 = 3 and p2 = 5 so 15 | n. n ∈{15, 30} are already on our list so n/15 must be divisible
by at least one of 3, 4 or 5 which means
φ(n) ≥2 · φ(n/15) ≥2(3 −1)(5 −1) = 16 > 8.
If n has one odd prime divisor, say p with νp(n) = k for a positive integer k then
φ(n) ≥φ
 pk
= pk−1(p −1) ≥2 · 3k−1.
For k ≥3, this is > 8.
For k = 2, if p ≥5, this is ≥5 · (5 −1) > 8 so the only possibility is p = 3. n ∈{9, 18} are already
on our list so n must be divisible by 4 as well as 9 which means
φ(n) ≥2 · φ(9) = 2 · 6 > 8.
21


For k = 1, if p ≥11 then we have φ(n) ≥p−1 > 8. Checking the remaining possibilities p ∈{3, 5, 7}
and noting that for φ(n), the largest power of 2 dividing n is at most 23, 22, and 21, respectively,
we recover the n already on our list.
The last case is n = 2α and since φ (2α) = 2α−1, we require α ≤4 for φ(n) ≤8 and we get the
remaining n from our list.
We now split into cases based on the largest power of 2 dividing elements of S (which is the same
for all elements of S as noted above).
To avoid double-counting across cases, we exclude the 9
polynomials corresponding to S empty (P(x) = 1, x, . . . , x8) and add these back in at the end.
Case 1: All elements of S are divisible by 2 but not 4
From the Claim above, the only options for s ∈S such that φ(s) ≤8 are in S1 = {2, 6, 10, 14, 18, 30}.
This is in turn equal to
8
X
t=0

yt
"
 1 + y + · · · + y8
·
 Y
s∈S1

1 + yφ(s)!#
.
Here the choice of t correspond to the degree of P, the choice of a summand in (1 + y + · · · + y8)
corresponds to m in (■), and the choice of 1 or yφ(s) in
 1 + yφ(s)
corresponds to whether Φs(x)
appears in the factorization of P(x) (since deg Φs = φ(s)). For now we include the 9 choices for P
where S is empty and will exclude these at the end.
Expanding the polynomial above, discarding terms of degree ≥9 (denoted by O
 y9
) we get
· · · =
 1 + y + · · · + y8
(1 + y)
 1 + y2  1 + y4  1 + y62  1 + y8
=
 1 + y + · · · + y8  1 + y + y2 + y3  1 + y4  1 + 2y6 + y8
+ O
 y9
=
 1 + y + · · · + y8  1 + y + y2 + y3  1 + y4 + 2y6 + y8
+ O
 y9
=
 1 + y + · · · + y8  1 + y + y2 + y3 + y4 + y5 + 3y6 + 3y7 + 3y8
+ O
 y9
.
We can then sum all coefficients of terms of degree ≤8 to get
9 + 8 + 7 + 6 + 5 + 4 + 3(3 + 2 + 1) = 57.
We must now subtract the 9 polynomials that have S empty giving 57 −9 = 48 possibilities for P
from this case.
Case 2: All elements of S are divisible by 4 but not 8
From the Claim above, the only options for s ∈S such that φ(s) ≤8 are in S2 = {4, 12, 20}. The
degrees of Φs for s ∈S2 is 2, 4, and 8, respectively. To ensure P has degree at most 8, we can choose
S = {4}, {12}, {20}, {4, 12}
which gives (counting the possibilities for m of which there are 9 minus the sum of the degrees of
Φs since we can have m = 0)
7 + 5 + 1 + 3 = 16
possibilities for P.
22


Case 3: All elements of S are divisible by 8 but not 16
From the Claim, we must choose S ⊂{8, 24} and we have φ(8) = 4, φ(24) = 8. S must therefore
be a singleton set and we get 5 + 1 = 6 possibilities (counting the possibilities for m as above).
Case 4: All elements of S are divisible by 16 but not 32
In this case we have S = {16} giving a single possibility for P since φ(16) = 8 so m = 0.
Combining the four cases and adding in the 9 possibilities for P where S is empty, we get
48 + 16 + 6 + 1 + 9 = 80
possibilities for P with a positive leading coefficient. We then need to double this to allow for a
negative leading coefficient giving
2 × 80 = 160
choices in total which is the answer we report.
23


Problem 10
Problem: Let n ≥6 be a positive integer. We call a positive integer n-Norwegian if it has three
distinct positive divisors whose sum is equal to n. Let f(n) denote the smallest n-Norwegian positive
integer. Let M = 32025! and for a non-negative integer c define
g(c) =
1
2025!
2025!f(M + c)
M

.
We can write
g(0) + g(4M) + g(1848374) + g(10162574) + g(265710644) + g(44636594) = p
q
where p and q are coprime positive integers. What is the remainder when p + q is divided by 99991?
Answer: 8687
Solution: In our solution to this problem, we include an extended commentary at the end that
explains how we design problems to effectively evaluate a model’s mathematical understanding within
the constraints of an answer-only competition.
Let N be n-Norwegian for n odd and write the three divisors of N as
n = N
p + N
q + N
r
where
1 ≤p < q < r
and
p, q, r | N.
Minimising N is equivalent to maximising 1
p + 1
q + 1
r subject to the resulting equation having an
integer solution for N with p, q, r | N. We will provide a classification of the minimal N for all n
odd.
We first consider the case when p = 1 and q = 2. We consider the possibilities for r based on whether
it is odd and, in the even case, its remainder mod 4.
N = n · 2(2s + 1)
6s + 5
(r = 2s + 1)
N = n ·
4s
6s + 1
(r = 4s)
N = n · 2s + 1
3s + 2
(r = 4s + 2)
Note in the last case, we have N odd (since n and 2s + 1 are odd) so q = 2 ∤N meaning this will
not give an integer solution for N.
In the first two cases, the fraction is written in lowest terms so the denominator must divide n.
Provided this is satisfied, we have q, r | N so this will yield a valid N.
Thus, if d1 and d5 are the smallest divisors of n that are ≥6 and are 1 and 5 mod 6, respectively
then we have two candidates for minimal N from choosing d1 = 6s+1 or d5 = 6s+5 (since we want
to minimise r which is equivalent to minimising s). These give the following values for N:
2
3 · d1 −1
d1
· n
or
2
3 · d5 −2
d5
· n.
(▲)
Now we turn our attention to the case p = 1 and q = 3. Working through the small cases:
24


• r = 4 gives N = 12n
19 which forces 19 | n. We get the same answer then by taking p = 1, q = 2,
and r = 12 so this is already covered by the first case.
• r = 5 gives N = 15n
23 which forces 23 | n. We get a smaller N = 14n
23 by taking p = 1, q = 2,
and r = 7 so this is already covered by the first case.
• r = 6 gives N = 2n
3 . For the divisibility condition q, r | N to be satisfied, we require 9 | n.
• If r ≥7, then we have
N = n ·
3r
4r + 3 = n
3
4 −
9
16r + 12

≥n
3
4 −
9
16 · 7 + 12

= 21n
31 > 2n
3
Putting the cases for q = 2 together with the case for q = 3 and r = 6, we have shown that if n has
a divisor ≥6 that is ±1 mod 6 or if 9 | n then we can find an n-Norwegian integer ≤2n
3 . For this
not to be the case, the only possibilities for prime factors of odd n are 3 and 5 and these must each
occur with multiplicity 1 (otherwise we could use 52 ≡1 mod 6). Thus, the only odd n ≥6 that
doesn’t satisfy this condition is n = 15 and we can manually check that the minimum 15-Norwegian
integer is 12 (12 + 2 + 1 = 15).
In all other cases, we claim one of the cases we’ve covered is optimal. This is true because
• We have already covered the cases for p = 1, q ∈{2, 3} that give N ≤2n
3 .
• If p = 1, q ≥4 then 1
p + 1
q + 1
r < 1 + 1
4 + 1
5 < 3
2 so N > 2n
3 .
• If p ≥2 then 1
p + 1
q + 1
r ≤1
2 + 1
3 + 1
4 < 3
2 so N > 2n
3 .
Define d1 and d5 to be equal to ∞if no such divisors of n exist. Taking the optimal cases from what
we have considered above, we can write
f(n) =







12
if
n = 15
min
n
2n
3 , 2
3 · d1−1
d1
· n, 2
3 · d5−2
d5
· n
o
if
9 | n
min
n
2
3 · d1−1
d1
· n, 2
3 · d5−2
d5
· n
o
otherwise
where we have used that if 9 ∤n and n ̸= 15, then n has at least one factor that is ±1 mod 6 by a
similar argument to the one used above.
We can further simplify this. If we define p1 and p5 to be the smallest prime divisors of n that are
≥7 and are 1 and 5 mod 6, respectively (and set pi = ∞if these don’t exist) then
f(n) =











12
if
n = 15
2n/3
if
n = 3α, 5 · 3α for α ≥2
16n/25
if
25 | n and p1 ≥31 and p5 ≥53
min
n
2
3 · p1−1
p1
· n, 2
3 · p5−2
p5
· n
o
otherwise
(■)
The bounds in the third case come from considering first when d1 = 25. This will occur if and only
if p1 > 25 which is the same as p1 ≥31 (the first prime that is 1 mod 6 and greater than 25). In
this case, setting d1 = 25 in (▲) gives
N = 2
3 · d1 −1
d1
· n = 2
3 · 25 −1
25
· n = 16
25 · n.
25


We then consider when d5 could give a smaller value of N in (▲) which requires
2
3 · d5 −2
d5
< 16
25 ⇐⇒d5 < 50.
This will happen if and only if p5 < 50 (noting that 125 > 50 so we cannot get a suitable d5 from
powers of 5). Thus, for N = 16n/25 to be optimal, we require p5 ≥50 which is equivalent to p5 ≥53
as that is the smallest prime that is 5 mod 6 and greater than or equal to 50.
When setting this question, we want to test that the models can produce a correct answer across a
wide range of cases. This reduces the risk of a model simply getting the correct answer via crude
pattern spotting from small values of n.
From the classification in (■), there are at least six cases that we would want to test:
(i) n = 3α for α ≥2;
(ii) n = 5 · 3α for α ≥3 (there is little value in testing n = 15 since this falls to a direct
computation);
(iii) n = 25k where k has only ‘large’ prime divisors (so the third case holds);
(iv) Case where 25 | n but n is also divisible by a smaller prime so we move into the fourth case;
(v) Case where the minimum is the first term in the fourth case;
(vi) Case where the minimum is the second term in the fourth case (and we can create further
challenge by choosing an example where p5 > p1).
For cases (iii) to (vi), we may be tempted to use factorials to ensure no small prime divisors eg ask
for f(2025! + 125). However, this suffers from the issue that this is also equal to f(125) so a model
could stumble on the correct answer by simply omitting the factorial term. Instead, we appeal to
modular arithmetic starting with M = 32025! which, by the Fermat–Euler Theorem, has M ≡1
(mod k) for k ≤2025 with gcd(k, 3) = 1 since φ(k) ≤2025 and hence φ(k) | 2025!.
Thus, for a positive integer c and positive integer k ≤2025 with gcd(k, 3) = 1, we have
k | M + c ⇐⇒k | 1 + c.
Also, since 3 | M and 3 ∤c, 3 ∤M + c. The factors of M + c that are ≤2025 will therefore be the
same as the factors of 1+c. This allows us to calculate the ‘small’ factors of n = M +c even though
M is very large which in turn allows us to determine which case we fall into in (■).
Now we select n to cover each of the cases described above:
(i) n = M — f(n) = 2n/3;
(ii) n = 5M — f(n) = 2n/3;
(iii) n = M + 1848374 (1 + 1848374 = 32 · 53 · 31 · 53) — f(n) = 16n/25;
(iv) n = M + 10162574 (1 + 10162574 = 32 · 52 · 312 · 47) — f(n) = (2/3)(45/47)n;
(v) n = M + 265710644 (1 + 265710644 = 33 · 5 · 97 · 103 · 197) — f(n) = (2/3)(96/97)n;
197 −2
197
= 195
197 > 96
97 = 97 −1
97
.
26


(vi) n = M + 44636594 (1 + 44636594 = 3 · 5 · 103 · 167 · 173) — f(n) = (2/3)(165/167)n.
167 −2
167
= 165
167 < 102
103 = 103 −1
103
.
All models are allowed access to a calculator (and much more) which makes the factorisations
straightforward (this would still be possible for a human given the modest prime factors but this
would be somewhat arduous). We choose to keep the numbers large so even if the model has the idea
of replacing M with 1, the cases are still challenging to compute directly.
In cases (iii) to (vi), the expressions are of the form f(M + c) = (s/t)(M + c) for positive integers
s and t. Noting that M ≫c, M ≫2025! and t | 2025! we have
g(c) =
1
2025!
2025!f(M + c)
M

=
1
2025!
2025!
t
· s + 2025!sc
tM

(0 < 2025!sc
tM
< 1)
=
1
2025! · 2025!
t
· s
= s
t .
We constructed g in the problem statement precisely to have this property of extracting the fraction
in front of n which is the ‘interesting’ part of the answer.
In cases (i) and (ii), we have
g(0) =
1
2025!
2025!f(M)
M

=
1
2025!
2025!(2M/3)
M

=
1
2025!
2 · 2025!
3

=
1
2025! · 2 · 2025!
3
= 2
3
g(4M) =
1
2025!
2025!f(5M)
M

=
1
2025!
2025!(10M/3)
M

=
1
2025!
10 · 2025!
3

=
1
2025! · 10 · 2025!
3
= 10
3 .
Putting this all together,
g(0) + g(4M) + g(1848374) + g(10162574) + g(265710644) + g(44636594)
= 2
3 + 10
3 + 16
25 + 2
3 · 45
47 + 2
3 · 96
97 + 2
3 · 165
167
= 125561848
19033825 .
We then have
p = 125,561,848 , q = 19,033,825 =⇒p + q = 144,595,673 ≡8687
(mod 99991)
which is the answer we report.
27


Remark 1: This problem was adapted from Problem N1 of the International Mathematical Olympiad
(IMO) Shortlist 2022 which can be found here. The original version simply asked for f(2022).
All problems used in AIMO3 are entirely original; this adaptation is included solely to illustrate
the process behind designing a challenging problem within the answer-only format. We reserve our
original hard problems for the public and private Kaggle leaderboards, given the significant effort
involved in creating them. The original problem itself is unsuitable for an answer-only setting, as
it can be solved directly by enumerating possible positive integers and their divisor sums, leading
straightforwardly to the correct answer of 1344.
Remark 2: Careful examination of the official solution provided in the shortlist reveals that it
ultimately depends on expressing 2022 as 6(6k + 1), where 6k + 1 is prime. The answer is then 24k
(with 24k + 12k + 6 = 6(6k + 1)). Motivated by this, a simpler reformulation that removes any
straightforward computational path is:
Problem: p = 2·330 +1 is prime. A positive integer is called Norwegian if it has three distinct
positive divisors whose sum is equal to 6p. Let N be the smallest Norwegian positive integer.
What is the remainder when N is divided by 99991?
Answer: 15245
However, this version tests only a single family of values for f(n). A model might still conjecture a
pattern by examining smaller primes, though this is complicated by the differing answers depending
on whether p ≡±1 mod 6. The final version of the problem in the reference set generalises across
a broader range of cases, making it extremely difficult to identify a solution pattern even from
extensive numerical experimentation.
28


