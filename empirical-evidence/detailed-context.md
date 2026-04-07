# Context for GPT-5.4-pro: Geometric Structure for Math Topic Routing

## Your Task

Design a mathematically optimal, production-grade topic routing system for a math olympiad solver running gpt-oss-120B on a single Kaggle H100 GPU. The system must route IMO-level problems (algebra, combinatorics, geometry, number theory) to topic-specific prompt configurations that maximize solve rate while preventing cross-topic interference.

**You must produce:**

1. A **Bayes-optimal routing algorithm** with formal proof of optimality under the stated assumptions. Not a sketch -- a proof.
2. A **prompt-level orthogonality metric** that quantifies interference between topic-specific prompt strategies, analogous to representation overlap in neural networks.
3. A **cross-topic handling strategy** for the 20-30% of IMO problems that span multiple categories (e.g., combinatorial number theory, algebraic geometry).
4. **Complete Python implementation** (not pseudocode) that integrates into the existing codebase described below. Every function, every data structure, every constant -- ready to paste into the repository.
5. **Exemplar bank specifications** with exact token budgets, selection criteria, and 2-3 worked exemplar templates per topic.

Do NOT produce generic advice about "consider using topic routing." Everything here has already been researched. What is needed is the mathematical rigor and implementation detail that goes beyond what research can provide.

---

## Background: Geometric Structure vs Pure Scale (Richard Aragon)

### The Core Finding

Richard Aragon ran controlled experiments comparing four model architectures on a multitask interference benchmark:

| Model | Architecture | Parameter Count |
|-------|-------------|-----------------|
| Baseline Small | Shared encoder, both tasks use same pooled representation | 1x |
| Bigger Baseline | Same shared architecture, 4x parameters | 4x |
| Adapter Only Small | Small encoder + task-specific adapter branches (routing, no orthogonality) | ~1x |
| Geometry Small | Adapter branches + orthogonality pressure (routing + separation) | ~1x |

Tasks were intentionally chosen to create conflict: Task 1 was sentiment-like binary classification (semantic), Task 2 was counting/structured extraction (exact). Both competed for representational resources on the same input sequences.

### Headline Results

- **29% loss reduction**: Geometry Small beat Bigger Baseline (4x parameters) on test loss
- **Representation overlap driven to near-zero**: Shared baselines remained at ~100% overlap (representations indistinguishable). Geometry Small drove overlap to ~0% (representations fully separated).
- **Bigger model collapsed FIRST under hard conflict**: When task conflict was increased (stronger anti-correlation, more noise), the 4x larger shared model had the WORST loss, WORST accuracy, and remained fully entangled. Scale amplified the problem.
- **Sentiment accuracy improvement**: ~3 percentage points gain for Geometry Small over Bigger Baseline.

### The Ablation That Matters

The critical ablation separated routing from orthogonality:

- **Adapter Only (routing, no orthogonality)**: Major improvement over shared baselines. Reduced representation overlap from ~100% to ~50%. Proved that routing alone changes the game.
- **Geometry Small (routing + orthogonality)**: Further improvement beyond routing alone. Drove overlap to near-zero. Better test loss, better calibration, stronger latent factorization.

**Key conclusion**: "Routing gave the model separate lanes. Geometric pressure made those lanes cleaner." Branching alone is necessary but not sufficient. Orthogonality on top of branching provides additional refinement gain.

### Why This Matters for Our System

We cannot modify gpt-oss-120B's weights. But we can achieve analogous separation at the prompt level:

- **Routing** = topic classification + topic-specific prompts (already exists, but weak)
- **Orthogonality pressure** = ensuring that prompts for different topics produce maximally diverse reasoning traces, not just textually different instructions

The question is: how do we formalize "prompt-level orthogonality" and make it mathematically rigorous?

### Aragon's Key Insight for Scaling

"The more you scale, the more you need geometric structure as a design principle. If the bottleneck is shared representation conflict, more parameters mostly enlarge the problem. Routing and separation make the capacity usable."

Applied to our setting: gpt-oss-120B has 117B parameters (5.1B active, MoE architecture). The capacity exists. The question is whether our prompting strategy causes the model to use that capacity in conflicting ways across different math topics.

---

## Current System Architecture

### How Problems Are Solved Today

The submission notebook (`notebook/kaggle_notebook_submission.py`) initializes a `DeepResearcher` instance with these parameters:

```python
researcher = DeepResearcher(
    model_path=build_model_path(),  # gpt-oss-120B
    time_limit_hours=4.5,
    num_samples=10,
    max_retries=1,
    enable_tir=True,           # Tool-Integrated Reasoning (code execution)
    enable_nl_verify=False,    # Natural language verifier disabled
    max_generate_tokens=16384,
    patch_text=None,
    submission_mode=True,      # Uses lean wave-based controller
)
```

### The Solving Flow (submission_mode=True)

```
Problem arrives via predict(id_, question) callback
    |
    v
research_problem(problem)
    |
    +---> classify_topic(problem_text)  # Keyword-based, returns algebra|combinatorics|geometry|number_theory|None
    |
    +---> If topic found: system_prompt = build_system_prompt(TOPIC_PATCHES[topic])
    |     Else: use baseline system prompt (no topic patch)
    |
    +---> If geometry: run AlphaGeometry backend first (separate path)
    |
    +---> _research_problem_lean(problem, trace, ...)  # Lean wave-based controller
              |
              +---> Wave 1: 4 attempts via _majority_vote_wave()
              |     Each attempt: system_prompt + user_prompt -> gpt-oss-120B -> extract answer
              |     Check: 3+ support, 60%+ share -> early stop
              |
              +---> Wave 2: 4 more attempts (total 8)
              |     Check: 4+ support, 50%+ share -> early stop
              |
              +---> Bounded repair (1 attempt) if leader has dirty traces
              |
              +---> Wave 3: 4 more (if time budget allows)
              |
              +---> Final: _select_answer_from_attempts() via AnswerSelector
```

### Current Topic Classification (the weak link)

```python
# agent/prompts.py - classify_topic()

_TOPIC_KEYWORDS = {
    "algebra": [
        "polynomial", "equation", "inequality", "root", "coefficient",
        "variable", "solve for", "function f", "f(x)", "real number",
        "complex number", "quadratic", "cubic", "system of equations",
    ],
    "combinatorics": [
        "color", "tiling", "tiled", "tile", "permut", "combin", "arrange",
        "board", "grid", "graph", "path", "tournament", "game", "strategy",
        "player", "move", "winning", "sequence of moves", "bijection",
        "counting", "how many ways",
    ],
    "geometry": [
        "triangle", "circle", "angle", "perpendicular", "parallel",
        "midpoint", "circumscri", "inscri", "tangent", "chord",
        "area", "perimeter", "diameter", "radius", "polygon",
    ],
    "number_theory": [
        "divisible", "prime", "gcd", "lcm", "modulo", "remainder",
        "integer", "digit", "factorial", "coprime", "congruent",
        "divides", "perfect square", "perfect cube",
    ],
}

def classify_topic(problem_text: str) -> str | None:
    """Returns topic if >= 2 keyword matches, else None."""
    text_lower = problem_text.lower()
    scores = {}
    for topic, keywords in _TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[topic] = score
    if not scores:
        return None
    best_topic = max(scores, key=scores.get)
    if scores[best_topic] >= 2:
        return best_topic
    return None
```

**Known problems:**
- Estimated 60-70% accuracy (from literature on keyword classifiers for math)
- No confidence score -- it either returns a topic or None
- Cannot handle cross-topic problems (returns the single best match)
- The code itself documents the weakness: "Simple keyword matching is highly brittle. Words like 'variable' might appear in geometry or combinatorics problems."

### Current Topic Patches (injected into system prompt)

```python
TOPIC_PATCHES = {
    "algebra": """
## Algebra-Specific Strategies
- Try substitution first for systems of equations
- For polynomials, consider Vieta's formulas and factor theorem
- For inequalities, try AM-GM, Cauchy-Schwarz, or Jensen's inequality
- For functional equations, test f(x)=ax+b but PROVE uniqueness
- Check if the problem has symmetry you can exploit""",

    "combinatorics": """
## Combinatorics-Specific Strategies
- Search for an INVARIANT or MONOVARIANT first
- Consider bijections to simpler counting problems
- Try small cases (n=1,2,3) first, then generalize with induction
- Apply pigeonhole principle when items > containers
- For coloring/tiling: look for parity arguments""",

    "geometry": """
## Geometry-Specific Strategies
- Try coordinate geometry if the problem has specific labeled points
- Use trigonometric identities for angle-based problems
- Apply Stewart's theorem, power of a point, or radical axes
- For optimization, look at reflection principles
- Use the law of cosines / law of sines as computational tools""",

    "number_theory": """
## Number Theory-Specific Strategies
- Check modular arithmetic for divisibility constraints
- Factor the expression and analyze prime factor structure
- Apply Fermat's little theorem, Euler's theorem as appropriate
- For Diophantine equations, bound the solutions then check
- Use Legendre's formula for prime factorizations of factorials""",
}
```

These patches are SHORT (5 bullet points each). They are strategy hints, not full prompt templates. They do not include worked examples.

### Current Approach Diversity System

The codebase also has 4 approach frameworks and 4 cognitive stances:

```python
APPROACH_FRAMEWORKS = {
    "algebraic": { "directive": "Approach this problem ALGEBRAICALLY..." },
    "computational": { "directive": "Approach this problem COMPUTATIONALLY..." },
    "case_analysis": { "directive": "Approach this problem via CASE ANALYSIS..." },
    "number_theoretic": { "directive": "Approach this problem NUMBER-THEORETICALLY..." },
}

# Framework-topic routing:
_FRAMEWORK_TOPICS = {
    "algebraic":       frozenset({"algebra"}),
    "computational":   frozenset({"algebra", "combinatorics", "geometry", "number_theory"}),
    "case_analysis":   frozenset({"combinatorics"}),
    "number_theoretic": frozenset({"number_theory"}),
}

# If a problem's topic is OUTSIDE a framework's domain, use the cognitive stance instead:
COGNITIVE_STANCES = {
    "algebraic": { "name": "Structure-First", "directive": "Identify core mathematical structure..." },
    "computational": { "name": "Computation-First", "directive": "(same as computational framework)" },
    "case_analysis": { "name": "Backward / Key-Lemma", "directive": "Work backwards from the key claim..." },
    "number_theoretic": { "name": "Representation Shift", "directive": "Find a better representation..." },
}
```

**Critical observation:** In submission_mode=True (lean controller), the approach-diverse system is NOT used. The lean controller uses `_majority_vote_wave()` which generates all N attempts with the same base prompt (system_prompt + GENERATE_PROMPT). The approach diversity only activates in GVR mode (non-submission).

This means the current submission notebook generates 10 attempts all with the same prompt (plus topic patch), relying solely on temperature=0.6 for diversity. This is exactly the "shared representation" problem that Aragon's research shows fails under task conflict.

### System Prompt Structure

The full system prompt is ~1500 tokens and includes:
- Model identity and role (math competition expert)
- Mandatory rules: never do mental arithmetic, verify with code, edge case checklist
- Anti-confirmation bias protocol: attempt to disprove your answer
- Output format: `**ANSWER: N**`
- Technical constraints for code execution
- Patch slot (where topic patches are injected)

### Inference Engine

- **Model:** gpt-oss-120B (117B params, 5.1B active, MoE, MXFP4 quantized)
- **Engine:** vLLM 0.10.2 via HarmonyServer (OpenAI-compatible HTTP API)
- **Encoding:** Harmony format (required by gpt-oss -- model produces garbage without it)
- **Parameters:** temperature=0.6, max_tokens=16384, min_p=0.02, seed=42
- **Context window:** 32,768 tokens (configured via max_model_len)
- **Stop tokens:** Harmony-specific stop tokens
- **Logprobs:** 5 (for DeepConf confidence scoring)

---

## What's Already Been Built (Phase 17: Geometric Intelligence)

Phase 17 implemented the mathematical infrastructure for geometric analysis but did NOT integrate it into the submission pipeline.

### Ablation Matrix (GEO-01, GEO-02)

```python
@dataclass(frozen=True)
class AblationCell:
    feature_a: str
    feature_b: str
    accuracy_with_both: float | None
    accuracy_a_only: float | None
    accuracy_b_only: float | None
    accuracy_neither: float | None
    synergy_score: float | None    # Bliss independence: acc_both - acc_a - acc_b + baseline
    sample_count: int

@dataclass(frozen=True)
class InterferencePair:
    feature_a: str
    feature_b: str
    synergy_score: float           # Negative = destructive interference
    weaker_feature: str
    individual_accuracy_a: float
    individual_accuracy_b: float
```

Synergy computation uses Bliss independence formula:
```
synergy = accuracy_with_both - accuracy_a_only - accuracy_b_only + accuracy_neither
```
Positive = synergistic, negative = interfering.

### Lane-Separated Prompting (GEO-03)

```python
LANE_TEMPLATE = """
[ANALYSIS]
Analyze the following competition math problem. Identify the problem type, \
key constraints, and mathematical domain. Do NOT attempt a solution yet.

Problem: {problem}

{analysis_instructions}

[STRATEGY]
Based on your analysis, select and justify a solution strategy. \
Do NOT start solving yet -- only plan your approach.

{strategy_instructions}

[CODE]
Implement your strategy in Python code. The code must be self-contained \
and print the final answer clearly.

{code_instructions}

[EXTRACTION]
Review your work above. Extract the final numerical answer. \
Double-check by re-reading the original problem statement.

{extraction_instructions}
"""
```

The 4 lanes ([ANALYSIS], [STRATEGY], [CODE], [EXTRACTION]) have isolated instructions with no cross-lane mixing. This was validated by test assertions.

### Diminishing Returns Detection (GEO-04)

Uses numpy degree-1 polynomial fit on a sliding window of accuracy measurements:
```python
def detect_diminishing_returns(results, window=10, threshold=-0.01):
    """Returns DiminishingReturns signal when marginal gain slope < threshold."""
    if len(results) < window:
        return None
    recent = results[-window:]
    x = np.arange(len(recent))
    slope, _ = np.polyfit(x, recent, 1)
    if slope < threshold:
        return DiminishingReturns(slope=slope, window=window, ...)
    return None
```

### Feature Grouping (GEO-05)

```python
FEATURE_GROUPS = {
    # reasoning_modifier: changes how the model reasons
    "prompt_perturbation": "reasoning_modifier",
    "blueprint_generator": "reasoning_modifier",
    "deep_researcher": "reasoning_modifier",
    # selection_modifier: changes which answer is selected
    "answer_selector": "selection_modifier",
    "confidence_scorer": "selection_modifier",
    "genselect": "selection_modifier",
    "majority_vote": "selection_modifier",
    "two_attempt": "selection_modifier",
    # verification_modifier: changes how answers are verified
    "verification_pipeline": "verification_modifier",
    "flaw_detector": "verification_modifier",
    # sampling_modifier: changes how samples are generated
    "temperature_schedule": "sampling_modifier",
    "approach_diversity": "sampling_modifier",
    "num_samples": "sampling_modifier",
    "tir_rounds": "sampling_modifier",
    "max_tokens": "sampling_modifier",
}
```

Cross-group pairs are prioritized over within-group pairs for exploration (maximum information gain).

### GeometricIntelligence Facade

```python
class GeometricIntelligence:
    """Facade composing KB + ResearchSurfacer for all geometric analysis."""
    
    def analyze_iteration(self, iteration_log):
        """Run interference detection, diminishing returns, system interference."""
        ...
    
    def get_interference_pairs(self):
        """Return all detected interference pairs from KB."""
        ...
```

**What is NOT built:** Integration with the submission pipeline. The geometric intelligence module is a research-loop tool, not a real-time inference component. Phase 19 is meant to bridge this gap.

---

## Research Findings

### The "Model Capability Dominates" Paper (arxiv:2603.27844)

This is the most important external finding. 23+ experiments on AIMO 3 with gpt-oss-120B:

| Strategy | Score | vs Baseline (39.7 mean) |
|----------|-------|-------------------------|
| Baseline (original prompt, T=1.0, N=8) | 39.7 mean | -- |
| Best single run (lucky) | 44/50 | +4.3 (noise) |
| Code-First strategy | 37.7 mean | -2.0 (worse) |
| 8x Small Cases prompt | 37/50 | -2.7 |
| 8x Classify prompt | 36/50 | -3.7 |
| 8x Work Backwards | 39/50 | -0.7 |
| Temperature 0.5 | 38/50 | -1.7 |
| Temperature 1.2 | 37/50 | -2.7 |
| Nemotron-Super-120B (alt model) | 23/50 | -16.7 |
| 20B variant | 26/50 | -13.7 |

**Why prompt diversity failed:** Temperature T=1.0 already decorrelates errors (pairwise correlation ~-0.113, near zero). Every alternative prompt LOWERED per-attempt accuracy more than it reduced correlation. Net effect: diversity strategies hurt.

**The paper's conclusion:** "Use the largest model that fits, keep temperature high, and spend submission budget on lottery tickets, not on prompt engineering."

**CRITICAL TENSION:** This paper says prompt diversity hurts. Aragon says geometric structure helps. These are NOT contradictory -- the paper tested naive prompt diversity (different system prompts for different ATTEMPTS on the SAME problem). Aragon's routing is about matching the right prompt to the right PROBLEM TYPE. The distinction is:

- **What the paper tested (and found harmful):** Different prompts for different ATTEMPTS on the same problem (intra-problem diversity)
- **What Aragon found beneficial:** Different prompts for different PROBLEM TYPES (inter-problem routing)

Our routing system must NOT increase intra-problem prompt diversity (already shown to hurt). It MUST improve per-problem prompt accuracy by ensuring the RIGHT prompt matches the RIGHT problem type.

### Zhu et al. 2024 -- Categorization and Strategy Tailoring

Key findings directly applicable:

- **Classification accuracy is the critical bottleneck:** With perfect classification, 28% accuracy. With model-based (84%), 20%. With random strategy, 12%. This is a 67% improvement from categorization vs random.
- **Optimal Chain-of-Thought vs Program-of-Thought ratio per topic:**
  - Geometry: 90% CoT / 10% PoT (geometry is visual/logical)
  - Combinatorics: 35% CoT / 65% PoT (combinatorics is enumerative)
  - Number Theory: similar to combinatorics
  - Algebra: balanced

### NemoSkills (AIMO 2 Winner, 34/50)

- Did NOT use topic routing. Solved diversity through fine-tuning (distillation from DeepSeek-R1 and QwQ-32B).
- GenSelect (trained solution selector) achieved 93.3% on AIME24 vs lower with majority voting.
- We cannot fine-tune, but the GenSelect PATTERN (present multiple solutions, ask model to select best) can be adapted as a prompt technique.

### Mixture-of-Prompts (MoP, ICML 2024)

- Cluster problems in embedding space, develop specialized (instruction, demo) pair per cluster.
- 81% win rate over single-prompt baselines across 55 tasks.
- Application: replace K-means with the known A/C/G/N taxonomy. For each topic, develop a full prompt template.

### MOORE -- Mixture of Orthogonal Experts (ICLR 2024)

- Enforces orthogonality via Gram-Schmidt orthogonalization of expert representations on the Stiefel manifold.
- At weight level, this produces orthonormal basis vectors. At prompt level, the analogy is: each approach framework's output should be as dissimilar as possible from other approaches' outputs.

---

## Agent's Learned Evidence (from Knowledge Base)

The autonomous research agent has accumulated evidence about prompting and topic routing across 135+ iterations. Key findings:

1. **Prompt perturbation is unverified:** Multiple findings (Grade B) flag that prompt diversity has NO Grade A evidence supporting it. The claim that perturbation "breaks inter-attempt correlation" has never been tested against actual competition problems. Tests only verify structural properties (round-robin determinism), not accuracy impact.

2. **Perturbation adds context overhead:** Each overlay adds ~50-100 tokens to system prompt per attempt. On 32K context window, this reduces effective reasoning budget. No measurement gate verifies this doesn't degrade accuracy.

3. **Inconsistent perturbation application:** GVR mode applies only system perturbation. Majority-vote mode applies both system AND user perturbation. The asymmetry is unexplained.

4. **Persona/role injection is unvalidated:** Variants assume gpt-oss-120B responds meaningfully to "world-class olympiad coach" persona injection. This is validated on GPT-4/Claude but NOT on gpt-oss-120B. The model may ignore or be distracted by these overlays.

5. **Temperature diversity reduction:** The notebook changed from 4/8 diverse to 5/8 baseline (T=0.7), reducing diversity from 4 diverse slots to 3. No measurement gate validated this improves accuracy.

6. **System prompt mutation is thread-unsafe:** The save-mutate-restore pattern for topic patches races if concurrent execution occurs.

---

## Competition Constraints (Hard Limits)

| Constraint | Value | Implication |
|-----------|-------|-------------|
| Model | gpt-oss-120B (117B params, 5.1B active MoE, MXFP4) | Cannot switch models, cannot fine-tune |
| GPU | Single H100 80GB | Cannot run two models simultaneously |
| Engine | vLLM 0.10.2 (pinned by Kaggle Docker image) | Cannot upgrade vLLM |
| Context window | 32,768 tokens | Must budget: ~1500 system prompt + ~500 problem + exemplars + 16384 generation |
| Time budget | 5 hours total (~4.5 hours for inference) | ~2.7 min per problem for 110 problems (with overhead) |
| Environment | Air-gapped Kaggle, no internet | All exemplars must be embedded in code, no API calls |
| Encoding | Harmony format required | Must use HarmonyServer, OpenAI completions API with token IDs |
| Quantization | MXFP4 (more compressed than FP8) | Native H100 support, cannot go to FP16 |
| Answer format | Integer 0-99999 via `**ANSWER: N**` pattern | Extraction regex is fixed |
| Scoring | Two-attempt: primary answer + secondary answer | Can hedge with two different answers per problem |
| Problems | 110 problems, A/C/G/N taxonomy, national olympiad to IMO difficulty | 25-30% cross-topic |
| Current baseline | ~39-40/50 on public test subset | Ceiling observed at 44/50 (lucky run) |

**Context budget analysis (critical for exemplar design):**
```
Available: 32,768 tokens
- System prompt:        ~1,500 tokens
- Problem text:           ~500 tokens (varies, can be 200-1000)
- Topic patch:            ~100 tokens (current, should grow)
- Exemplar(s):            ~??? tokens (TO BE DETERMINED)
- Generation budget:   16,384 tokens (max_generate_tokens)
- Safety margin:          ~500 tokens
----------------------------------------------
Available for exemplars: 32,768 - 1,500 - 500 - 100 - 16,384 - 500 = 13,784 tokens
```

So we have ~13,784 tokens for exemplars before we start eating into generation budget. However, if problems are long (1000 tokens) or we increase generation budget, this shrinks fast. Conservative budget: **2,000 tokens max for exemplars** (leaves generous margin).

---

## Specific Questions to Answer

### Q1: Bayes-Optimal Routing

Define the routing problem formally. Given:
- Problem text x
- Topic space T = {algebra, combinatorics, geometry, number_theory}
- Prompt configuration space C (topic patch + approach directive + exemplars)
- Reward: R(x, c) = 1 if correct, 0 if incorrect

Prove that the Bayes-optimal routing policy is:
```
c*(x) = argmax_c E[R(x, c) | x] = argmax_c P(correct | x, c)
```

Then show how to estimate P(correct | x, c) from:
(a) the model's own classification confidence (self-classification),
(b) historical routing data from the research loop,
(c) a prior derived from the Zhu et al. CT/PT ratios.

Address the exploration-exploitation tradeoff: in a 5-hour window with 110 problems, we cannot explore. How do we set the prior optimally?

### Q2: Prompt-Level Orthogonality Metric

Define a metric O(p_i, p_j) that measures the "orthogonality" between two prompt configurations p_i and p_j. Requirements:
- O should be computable from the outputs (solution texts), since we cannot access model internals.
- O = 0 means prompts produce identical reasoning; O = 1 means maximally diverse reasoning.
- The metric should distinguish between GOOD diversity (different valid approaches to the same problem) and BAD diversity (one prompt confuses the model).

Provide the mathematical definition, prove it satisfies the metric axioms (or explain why it doesn't need to), and show how to compute it efficiently at inference time (budget: <1 second per problem).

### Q3: Cross-Topic Problem Handling

20-30% of IMO problems span multiple categories. For example:
- "Find all integers n such that n^2 + 2n + 5 divides n^3 + 7" is both algebra AND number theory.
- "Count the number of lattice points inside a circle of radius r" is both combinatorics AND geometry.

Design the routing strategy for these problems. Specifically:
(a) How to detect cross-topic problems (what signal from the classifier?).
(b) What prompt configuration to use (union of patches? separate passes? specialized cross-topic templates?).
(c) How to weight answers from different routing decisions.

### Q4: Self-Classification Integration

The research recommends using gpt-oss-120B itself to classify problems (88-92% accuracy on similar models). Design the self-classification mechanism:
(a) Should classification be a separate inference call, or embedded in the first generation step? (Separate call costs ~2-5 seconds per problem. Embedded classification is free but harder to extract.)
(b) What prompt produces the most accurate and well-calibrated classification?
(c) How to extract a confidence score (not just a label) from the classification.
(d) What is the fallback when confidence is below threshold?

### Q5: Exemplar Bank Design

Design the exemplar bank for each topic. Constraints:
- Max 2,000 tokens total for exemplars per problem.
- Max 2 exemplars per problem (to leave reasoning budget).
- Each exemplar must demonstrate a REASONING PATTERN, not just arrive at an answer.
- Exemplars should come from different competitions than AIMO 3 (no contamination risk).

For each topic (A/C/G/N), provide:
(a) 2-3 exemplar templates showing the format and content level.
(b) Selection criteria: how to pick which exemplars to include for a given problem.
(c) Token budget per exemplar.

### Q6: Integration with Existing Lean Controller

The lean controller runs Wave 1 (4 attempts) -> Wave 2 (4 more) -> optional Wave 3. Currently all attempts use the same prompt. Design the integration:
(a) Should different waves use different routing strategies? (e.g., Wave 1 uses topic-routed prompt, Wave 2 uses generic for diversity)
(b) How to integrate approach diversity without hurting per-attempt accuracy (the paper's warning).
(c) Should the two-attempt answer selection (primary + secondary) leverage routing information?

### Q7: Formal Interference Model

Build a mathematical model of prompt interference that explains:
(a) Why the paper found that diverse prompts hurt (intra-problem diversity reduces per-attempt accuracy).
(b) Why Aragon found that routing helps (inter-problem routing reduces cross-task interference).
(c) The precise condition under which topic routing has positive expected value vs a single generic prompt.

Express this as an inequality involving: classifier accuracy p_c, per-topic accuracy gain delta_t, per-attempt accuracy loss from routing overhead delta_r, and number of attempts N.

---

## Expected Output Format

Structure your response as:

```
## 1. Formal Problem Statement
[Mathematical formulation of the routing problem]

## 2. Bayes-Optimal Routing Algorithm
[Theorem + proof + algorithm]

## 3. Orthogonality Metric
[Definition + properties + computation]

## 4. Cross-Topic Handling
[Detection + routing + weighting]

## 5. Self-Classification Design
[Prompt + extraction + calibration]

## 6. Exemplar Bank
[Per-topic exemplars with exact content]

## 7. Interference Model
[Formal model + the key inequality]

## 8. Complete Implementation
[Python code for every component, ready to integrate]

## 9. Integration Guide
[How to wire this into the existing lean controller]
```

Every section must contain mathematical rigor where claimed and production-ready code where implementation is requested. No hand-waving. No "exercise left to the reader."
