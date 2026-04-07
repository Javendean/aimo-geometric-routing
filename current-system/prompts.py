"""
Prompt Templates for the DeepResearcher Agent (v2).

Upgraded prompts for the AIMO3 competition with:
- Balanced prompting (anti-confirmation bias, from Gemini Deep Think)
- Tool-Integrated Reasoning (TIR) support
- Natural Language Verifier prompt
- Multiple chat template support (Qwen + Llama)
- Higher token budget awareness

The PATCH_SLOT in the system prompt is where "System Prompt Patches" from
the local analysis pipeline get injected between runs.
"""

from __future__ import annotations

import re

try:
    from src.verification.answer_validator import extract_canonical_answer as _extract_canonical_answer
except Exception:  # pragma: no cover - fallback for stripped-down notebook environments
    _extract_canonical_answer = None


# =============================================================================
# CHAT TEMPLATES — Auto-detect model family and format correctly
# =============================================================================

def detect_model_family(model_path: str) -> str:
    """Detect model family from path/name for correct chat template.

    Args:
        model_path (str): The file path or name of the model being used.

    Returns:
        str: A string indicating the detected model family ('qwen' or 'llama').
             Defaults to 'qwen' if the family cannot be explicitly determined.
    """
    path_lower = model_path.lower()
    if "qwen" in path_lower or "qwq" in path_lower or "klear" in path_lower:
        return "qwen"
    elif "llama" in path_lower or "meta" in path_lower:
        return "llama"
    elif "deepseek" in path_lower:
        # DeepSeek-R1-Distill-Qwen → qwen, DeepSeek-R1-Distill-Llama → llama
        if "qwen" in path_lower:
            return "qwen"
        elif "llama" in path_lower:
            return "llama"
        return "qwen"  # Default DeepSeek to Qwen template
    elif "gpt-oss" in path_lower or "gpt_oss" in path_lower:
        return "gpt_oss"
    return "qwen"  # Safe default


def format_chat_prompt(
    system_prompt: str,
    user_prompt: str,
    model_family: str = "qwen",
    assistant_prefix: str = "",
) -> str:
    """Format a chat prompt using the correct template for the model family.

    Args:
        system_prompt (str): The system prompt text.
        user_prompt (str): The user prompt text.
        model_family (str, optional): The target model family ('qwen' or 'llama'). Defaults to "qwen".
        assistant_prefix (str, optional): Optional text to pre-fill the assistant's response. Defaults to "".

    Returns:
        str: The fully formatted chat prompt string ready for inference.
    """
    if model_family == "qwen":
        return _format_qwen(system_prompt, user_prompt, assistant_prefix)
    elif model_family == "llama":
        return _format_llama(system_prompt, user_prompt, assistant_prefix)
    else:
        return _format_qwen(system_prompt, user_prompt, assistant_prefix)


def _format_qwen(system: str, user: str, asst_prefix: str = "") -> str:
    """Qwen / Qwen2.5 / QwQ / DeepSeek-R1-Distill-Qwen chat template.

    Args:
        system (str): The system prompt text.
        user (str): The user prompt text.
        asst_prefix (str, optional): Optional text to pre-fill the assistant's response. Defaults to "".

    Returns:
        str: The formatted Qwen-style chat prompt.
    """
    prompt = (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        f"<|im_start|>assistant\n{asst_prefix}"
    )
    return prompt


def _format_llama(system: str, user: str, asst_prefix: str = "") -> str:
    """Llama 3 / DeepSeek-R1-Distill-Llama chat template.

    Args:
        system (str): The system prompt text.
        user (str): The user prompt text.
        asst_prefix (str, optional): Optional text to pre-fill the assistant's response. Defaults to "".

    Returns:
        str: The formatted Llama-style chat prompt.
    """
    prompt = (
        f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n"
        f"{system}<|eot_id|>"
        f"<|start_header_id|>user<|end_header_id|>\n\n"
        f"{user}<|eot_id|>"
        f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        f"{asst_prefix}"
    )
    return prompt


def format_tir_continuation(
    model_family: str,
    execution_result: str,
) -> str:
    """Format code execution output for Tool-Integrated Reasoning (TIR) injection mid-generation.

    Args:
        model_family (str): The model family, though currently unused in the formatting logic.
        execution_result (str): The string output from the executed Python code.

    Returns:
        str: A markdown block containing the execution output, formatted for the model to continue generation.
    """
    # This is injected as if the assistant paused and received tool output
    result_block = f"\n```output\n{execution_result}\n```\n"
    return result_block


# =============================================================================
# SYSTEM PROMPT — The agent's identity and reasoning instructions (v2)
# =============================================================================

SYSTEM_PROMPT = """\
You are a world-class mathematician competing in the AI Mathematical Olympiad.
Your goal is to solve competition-level math problems with perfect accuracy.

## Reasoning Protocol

1. **Read carefully.** Identify what is being asked. Note ALL constraints.
2. **Plan multiple approaches.** Consider at least 2 different solution \
strategies before committing. Briefly outline each.
3. **Show all work.** Write out every step of your reasoning. Never skip steps.
4. **Verify as you go.** After each major step, sanity-check the result.
5. **Write Python verification code.** You MUST write Python code in \
```python ... ``` blocks to verify your reasoning computationally. This is \
mandatory, not optional. The code will be executed and the output shown to you.
6. **Challenge your answer.** Before accepting, briefly try to find a \
counterexample or a flaw in your reasoning. If you fail to disprove it, \
your confidence should increase.
7. **State your final answer clearly** on its own line in the format:
   **ANSWER: [your answer]**

## Mathematical Tools Available
- Python with `math`, `sympy`, `itertools`, `functools`, `fractions`, `decimal`
- NumPy for numerical computation
- No file I/O, no network access, no external libraries beyond the above

## Common Pitfalls to Avoid
- Off-by-one errors in counting problems
- Forgetting edge cases (n=0, n=1, empty sets)
- Confusing permutations with combinations
- Not checking all cases in modular arithmetic
- Assuming commutativity/associativity where it doesn't hold
- Circular reasoning: ensure your proof doesn't assume what it's proving
- Sign errors in algebraic manipulation
- Forgetting to check that a solution actually satisfies the original constraints

## CRITICAL Rules (Mistake Prevention)
1. **NEVER do arithmetic in your head.** Even simple calculations like 7×13 \
MUST be verified in a Python code block. Mental arithmetic in long reasoning \
chains is the #1 source of propagated errors. Always ```python print(7*13) ```.
2. **Before finalizing, run this edge case checklist:**
   - Did I consider x=0? Negative values? The trivial case?
   - Did I check boundary conditions at the extremes of the domain?
   - Does my answer satisfy ALL original constraints (re-read the problem)?
   - If the problem asks "find ALL solutions," did I prove there are no others?
3. **Never assume functional forms without proof.** If you try f(x)=ax+b and \
it works, you have NOT proven it is the ONLY solution. You must show no other \
form is possible, or your answer gets 0 points even if correct.
4. **For combinatorics with state transitions:** Explicitly look for an \
INVARIANT — a quantity that does not change under the allowed operations. \
Test candidate invariants in code before building your proof around one.

## Technical Constraints (Code Execution)
1. **NO Nested Backticks**: Do NOT put ` ```python ` or ` ``` ` inside your \
code blocks. This breaks the parsing engine.
2. **Raw Strings for LaTeX**: When printing LaTeX or regex, ALWAYS use raw \
strings `r"..."` to prevent `SyntaxError: unicode error`.
   - BAD: `print("\\frac{{1}}{{2}}")` (Crashes)
   - GOOD: `print(r"\\frac{{1}}{{2}}")` (Works)
3. **Complete Code**: Do not truncate or summarize code. It must be executable.

## Anti-Confirmation Bias Protocol
When you reach a candidate answer:
1. Spend 2-3 sentences attempting to DISPROVE your answer
2. Try at least one edge case or boundary value
3. If your disproof attempt fails, state why and accept the answer
4. If your disproof succeeds, revise your approach entirely

## Self-Containment & Output Format (MANDATORY)
- This problem is **fully self-contained**. Do NOT ask for prior context, \
do NOT reference earlier results, do NOT say "continue from where you left off". \
Solve it completely from scratch.
- Never claim there was prior conversation, hidden context, previous attempts, \
or missing history. If it is not in the current prompt, you do not know it.
- When you have determined the final answer, you MUST write it on its own line \
in **exactly** this format: `**ANSWER: N**` (where N is the integer, no other text). \
Formats like "the answer is N" or "m+n = N" will NOT be recorded.
- Do NOT include internal tool syntax (e.g. `assistantcommentary to=python`) \
in your response. Use standard markdown code blocks (` ```python `) for any code.
- Never emit channel markers or pseudo-tool calls such as `assistantcommentary`, \
`assistantanalysis`, `commentary`, `analysis to=python`, or `assistantcommentary to=python`. \
Those are internal control tokens, not valid solution text.

{patch_slot}
"""

# Placeholder for injecting learned rules from local analysis
PATCH_SLOT_DEFAULT = """\
## Domain-Specific Patches
(No patches loaded — this is the baseline prompt)
"""


# =============================================================================
# TOPIC-SPECIFIC PATCHES — Inject strategy hints based on problem type
# =============================================================================

TOPIC_PATCHES = {
    "algebra": """\
## Algebra-Specific Strategies
- Try substitution first for systems of equations
- For polynomials, consider Vieta's formulas and factor theorem
- For inequalities, try AM-GM, Cauchy-Schwarz, or Jensen's inequality
- For functional equations, test f(x)=ax+b but PROVE uniqueness
- Check if the problem has symmetry you can exploit""",

    "combinatorics": """\
## Combinatorics-Specific Strategies
- Search for an INVARIANT or MONOVARIANT first
- Consider bijections to simpler counting problems
- Try small cases (n=1,2,3) first, then generalize with induction
- Apply pigeonhole principle when items > containers
- For coloring/tiling: look for parity arguments""",

    "geometry": """\
## Geometry-Specific Strategies
- Try coordinate geometry if the problem has specific labeled points
- Use trigonometric identities for angle-based problems
- Apply Stewart's theorem, power of a point, or radical axes
- For optimization, look at reflection principles
- Use the law of cosines / law of sines as computational tools""",

    "number_theory": """\
## Number Theory-Specific Strategies
- Check modular arithmetic for divisibility constraints
- Factor the expression and analyze prime factor structure
- Apply Fermat's little theorem, Euler's theorem as appropriate
- For Diophantine equations, bound the solutions then check
- Use Legendre's formula for prime factorizations of factorials""",
}

# Keywords used for automatic topic classification
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
    """Classify a math problem into a topic via keyword matching.

    Args:
        problem_text (str): The text of the math problem to classify.

    Returns:
        str | None: The topic key (e.g., "algebra") if classified with at least
                    2 matching keywords, or None if uncertain.

    Note:
        Blindspot: Simple keyword matching is highly brittle. Words like 'variable'
        might appear in geometry or combinatorics problems, leading to misclassification.
    """
    text_lower = problem_text.lower()
    scores = {}
    for topic, keywords in _TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[topic] = score

    if not scores:
        return None

    # Return topic with highest keyword match count
    best_topic = max(scores, key=scores.get)
    # Only classify if we have at least 2 matching keywords (avoid false positives)
    if scores[best_topic] >= 2:
        return best_topic
    return None


# =============================================================================
# GENERATE PROMPT — Initial solution generation (v2)
# =============================================================================

GENERATE_PROMPT = """\
Solve the following competition math problem. Think step-by-step, show all \
your work, and write Python code to verify your computations.

## Problem
{problem_text}

## Instructions
1. Analyze the problem carefully. Identify all constraints and what is asked.
2. Consider at least two possible approaches. Briefly outline why you chose one.
3. Execute the solution with full mathematical rigor.
4. Write Python code blocks to verify intermediate results and your final answer.
5. Before stating your answer, briefly attempt to disprove it (edge cases, \
boundary values, or alternative reasoning).
6. State your final answer as: **ANSWER: [value]**

Important: Your Python code will be executed and the output returned to you. \
Use this to check your work.
"""


# =============================================================================
# VERIFY PROMPT — Ask model to write verification code
# =============================================================================

VERIFY_PROMPT = """\
You previously proposed this solution to a math problem:

## Problem
{problem_text}

## Your Previous Solution
{solution}

## Task
Write a Python program that independently verifies whether the answer is \
correct. The program should:
1. Solve the problem from scratch using a DIFFERENT method if possible
2. Compare its result with your proposed answer
3. Print "VERIFIED: True" if correct, "VERIFIED: False" if not
4. If the answer is wrong, print what the correct answer should be

Wrap your code in a ```python ... ``` block.
"""


# =============================================================================
# NATURAL LANGUAGE VERIFIER — Catch logic errors code can't detect
# =============================================================================

NL_VERIFY_PROMPT = """\
You are a rigorous mathematical reviewer. Carefully review the following \
solution for logical errors, unstated assumptions, and mathematical mistakes.

## Problem
{problem_text}

## Solution Under Review
{solution}

## Your Task
1. Check each logical step for validity
2. Identify any unstated assumptions
3. Look for common mistakes (sign errors, off-by-one, incorrect formula usage)
4. Verify the final answer is consistent with ALL problem constraints

If the solution is correct, respond with: **VERDICT: CORRECT**
If you find errors, respond with: **VERDICT: ERROR** followed by a \
description of the specific flaw.
"""


# =============================================================================
# SELF-CORRECT PROMPT — Fix errors based on verification feedback (v2)
# =============================================================================

CORRECT_PROMPT = """\
Your previous solution to the following problem had errors during verification.

## Problem
{problem_text}

## Your Previous Solution
{previous_solution}

## Verification Error
{error_message}

## Task
1. Carefully analyze what went wrong
2. Identify the specific mathematical or logical error
3. Consider whether your entire approach was wrong, or just a calculation error
4. Produce a corrected solution with full reasoning
5. Write NEW Python verification code to confirm the corrected answer
6. Before accepting, try to disprove your new answer
7. State your corrected final answer as: **ANSWER: [value]**

Do NOT repeat the same approach if it fundamentally failed. Try a different \
strategy if needed.
"""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_system_prompt(patch_text: str | None = None) -> str:
    """Build the full system prompt with optional patches.

    Args:
        patch_text (str | None, optional): Custom instructions to inject into the system prompt.
                                           Defaults to None.

    Returns:
        str: The complete system prompt text.
    """
    patch = patch_text if patch_text else PATCH_SLOT_DEFAULT
    return SYSTEM_PROMPT.format(patch_slot=patch)


def build_generate_prompt(problem_text: str) -> str:
    """Build the generation prompt for a problem.

    Args:
        problem_text (str): The math problem to be solved.

    Returns:
        str: The generation prompt asking the model to solve the problem.
    """
    return GENERATE_PROMPT.format(problem_text=problem_text)


def build_verify_prompt(problem_text: str, solution: str) -> str:
    """Build the verification prompt.

    Args:
        problem_text (str): The math problem.
        solution (str): The proposed solution text.

    Returns:
        str: The prompt asking the model to verify the proposed solution.
    """
    return VERIFY_PROMPT.format(problem_text=problem_text, solution=solution)


def build_nl_verify_prompt(problem_text: str, solution: str) -> str:
    """Build the natural language verifier prompt.

    Args:
        problem_text (str): The math problem.
        solution (str): The proposed solution text.

    Returns:
        str: The prompt asking the model to perform a rigorous NL review of the solution.
    """
    return NL_VERIFY_PROMPT.format(problem_text=problem_text, solution=solution)


def build_correct_prompt(
    problem_text: str, previous_solution: str, error_message: str
) -> str:
    """Build the self-correction prompt.

    Args:
        problem_text (str): The math problem.
        previous_solution (str): The incorrect solution that needs correction.
        error_message (str): The error details from sandbox execution or NL verifier.

    Returns:
        str: The self-correction prompt guiding the model to fix the mistakes.
    """
    return CORRECT_PROMPT.format(
        problem_text=problem_text,
        previous_solution=previous_solution,
        error_message=error_message,
    )


# =============================================================================
# APPROACH-DIVERSE GENERATION — Semantic diversity for hard IMO problems
# =============================================================================

# Four mathematically distinct frameworks. Each forces the model into a
# genuinely different reasoning path, unlike temperature-only diversity which
# produces correlated errors from the same underlying approach.
APPROACH_FRAMEWORKS: dict[str, dict[str, str]] = {
    "algebraic": {
        "name": "Algebraic",
        "directive": (
            "Approach this problem ALGEBRAICALLY. "
            "Introduce variables, set up equations or inequalities, and manipulate symbolically. "
            "Use Vieta's formulas for polynomial roots, substitution for systems of equations, "
            "AM-GM or Cauchy-Schwarz for inequalities, and generating functions where appropriate. "
            "For functional equations, you MUST prove uniqueness — showing one solution works is not enough."
        ),
    },
    "computational": {
        "name": "Computational",
        "directive": (
            "Approach this problem COMPUTATIONALLY. "
            "Write Python code to exhaustively explore the problem space. "
            "Enumerate small cases first to discover the pattern, then verify the pattern holds. "
            "Use sympy for symbolic computation, itertools for enumeration, "
            "and numpy for numerical verification. "
            "Your code output IS the primary evidence — make the answer unambiguous from the output."
        ),
    },
    "case_analysis": {
        "name": "Case Analysis / Structural",
        "directive": (
            "Approach this problem via CASE ANALYSIS and STRUCTURAL REASONING. "
            "Identify ALL distinct cases and handle each completely — prove no cases are missed. "
            "Search for an INVARIANT or MONOVARIANT first (a quantity preserved or monotone under allowed operations). "
            "Apply the pigeonhole principle, parity arguments, or extremal principle. "
            "For combinatorics: look for bijections to simpler counting problems."
        ),
    },
    "number_theoretic": {
        "name": "Number-Theoretic",
        "directive": (
            "Approach this problem NUMBER-THEORETICALLY. "
            "Apply modular arithmetic to derive constraints (try mod 2, 4, 8, p, p²). "
            "Analyze prime factorization structure. Use Fermat's little theorem, "
            "Euler's theorem, or the Lifting the Exponent (LTE) lemma where relevant. "
            "For Diophantine equations: bound solutions analytically, then check all candidates. "
            "For counting: use generating functions, inclusion-exclusion, or Legendre's formula."
        ),
    },
}

# List of approach keys in canonical order (matches index in attempt lists)
APPROACH_KEYS: list[str] = list(APPROACH_FRAMEWORKS.keys())

# COGNITIVE_STANCES — Universal fallbacks for problems outside framework scope.
# These are domain-agnostic reasoning stances that work across all mathematical
# areas (functional equations, projective geometry, analytic NT, game theory, etc.).
# Each stance is paired with the framework slot it replaces when routing triggers.
COGNITIVE_STANCES: dict[str, dict[str, str]] = {
    "algebraic": {
        "name": "Structure-First",
        "directive": (
            "Approach this problem by IDENTIFYING ITS CORE MATHEMATICAL STRUCTURE first. "
            "Before computing anything: name what kind of object this problem is fundamentally about "
            "(fixed-point problem? extremal problem? functional equation? coloring? game?). "
            "Let the structure dictate the approach — the right tool emerges naturally once the "
            "structure is named. Search for symmetry, invariants, or self-similarity before calculating. "
            "Then apply whichever mathematical subfield owns that structure."
        ),
    },
    "computational": {
        # Computational is universal — it's kept as-is for all problem types.
        # This entry exists only for completeness; routing never replaces it.
        "name": "Computation-First",
        "directive": APPROACH_FRAMEWORKS["computational"]["directive"],
    },
    "case_analysis": {
        "name": "Backward / Key-Lemma",
        "directive": (
            "Approach this problem by WORKING BACKWARDS FROM THE KEY CLAIM. "
            "State precisely what needs to be proved or found. Then ask: what single lemma, "
            "if true, would make the answer immediate? Prove that lemma first. "
            "If the direct proof seems hard, try the contrapositive or a dual formulation. "
            "For existence problems: construct explicitly, or apply a non-constructive principle "
            "(pigeonhole, probabilistic method, extremal principle) — state which you use and why. "
            "Break the problem into the minimum number of non-overlapping cases."
        ),
    },
    "number_theoretic": {
        "name": "Representation Shift",
        "directive": (
            "Approach this problem by FINDING A BETTER REPRESENTATION. "
            "The problem in its current form resists direct attack — look for a change of variables, "
            "a bijection, a generating function, a matrix encoding, or a geometric/analytic interpretation "
            "that makes the structure transparent. "
            "For geometry: try coordinates, complex numbers, or projective duality. "
            "For number theory outside standard divisibility: try p-adic valuations, "
            "quadratic reciprocity, or analytic bounds. "
            "For combinatorics: try a polynomial or algebraic encoding. "
            "Translate into the domain where the right tools already exist."
        ),
    },
}

# Which classify_topic() results indicate a problem is within each framework's domain.
# "computational" covers all topics (it is universal — never triggers routing).
_FRAMEWORK_TOPICS: dict[str, frozenset[str]] = {
    "algebraic":       frozenset({"algebra"}),
    "computational":   frozenset({"algebra", "combinatorics", "geometry", "number_theory"}),
    "case_analysis":   frozenset({"combinatorics"}),
    "number_theoretic": frozenset({"number_theory"}),
}


def _is_within_framework_scope(topic: str | None, approach_key: str) -> bool:
    """Return True if the classified topic is within the framework's natural domain.

    Args:
        topic: Output of classify_topic(), or None if classification was uncertain.
        approach_key: One of the APPROACH_FRAMEWORKS keys.

    Returns:
        True  → use the hardcoded framework as-is.
        False → route to the cognitive stance fallback for this slot.
    """
    # Computational is universal — always in scope.
    if approach_key == "computational":
        return True
    # If topic is unknown, cognitive stances are safer (they're designed to be domain-agnostic).
    if topic is None:
        return False
    return topic in _FRAMEWORK_TOPICS.get(approach_key, frozenset())


def build_approach_prompt(problem_text: str, approach_key: str) -> str:
    """Build a generation prompt for one slot of the approach-diverse ensemble.

    Routing logic: classifies the problem's topic, then checks whether it falls
    within the hardcoded framework's natural domain. If yes, the framework is used
    unchanged. If no (problem is outside scope, e.g. a geometry problem sent to the
    number-theoretic slot), the prompt transparently routes to the corresponding
    cognitive stance — a lightweight, universal reasoning angle that works across
    all mathematical domains.

    This keeps the 4-slot diversity ensemble intact while eliminating the
    pigeonholing problem where out-of-scope frameworks actively harm performance.

    Args:
        problem_text (str): The math problem to solve.
        approach_key (str): One of "algebraic", "computational", "case_analysis",
                            "number_theoretic".

    Returns:
        str: A prompt directing the model toward the best-fit approach for this
             specific problem — either the hardcoded framework or a cognitive stance.
    """
    topic = classify_topic(problem_text)
    use_framework = _is_within_framework_scope(topic, approach_key)

    if use_framework:
        fw = APPROACH_FRAMEWORKS[approach_key]
        directive = fw["directive"]
        approach_name = fw["name"]
        mandate = "You MUST follow this approach. Do not switch to a different method mid-solution."
    else:
        stance = COGNITIVE_STANCES[approach_key]
        directive = stance["directive"]
        approach_name = stance["name"]
        mandate = (
            "This approach was selected because the problem appears to lie outside the domain of "
            f"the standard {APPROACH_FRAMEWORKS[approach_key]['name']} framework. "
            "Follow this reasoning stance. If it leads you to a natural method from any subfield, use it."
        )

    return (
        f"Solve the following competition math problem.\n\n"
        f"## Approach for This Problem: {approach_name}\n"
        f"{directive}\n\n"
        f"{mandate}\n\n"
        f"## Problem\n"
        f"{problem_text}\n\n"
        f"## Instructions\n"
        f"1. State in one sentence which mathematical approach you are using and why it fits this problem.\n"
        f"2. Execute the approach completely and rigorously, showing all steps.\n"
        f"3. Write Python code blocks to verify intermediate results.\n"
        f"4. Before stating your answer, try one counterexample or edge case to challenge it.\n"
        f"5. State your final answer as: **ANSWER: [value]**"
    )


# GVR REVISE PROMPT — Aletheia-inspired targeted revision
REVISE_PROMPT = """\
Your previous solution to this problem was reviewed by an adversarial checker \
who found a specific error. Your task: produce a corrected solution that \
addresses EXACTLY the critique below.

## Problem
{problem_text}

## Your Previous Solution
{previous_solution}

## Specific Critique
{critique}
{approach_note}
## Instructions
1. Understand the critique precisely — what specific step failed?
2. Decide: is this a local calculation error (fix that step) or a \
fundamental approach error (the whole method was wrong)?
3. If the approach was fundamentally flawed: explain why, then solve \
using a DIFFERENT method entirely.
4. If it was a local error: fix the specific step and re-verify all \
surrounding steps that depended on it.
5. Write NEW Python verification code to confirm the corrected answer.
6. Challenge your new answer: attempt to construct a counterexample.
7. State your corrected final answer as: **ANSWER: [value]**
"""


def build_revise_prompt(
    problem_text: str,
    previous_solution: str,
    critique: str,
    approach_key: str | None = None,
) -> str:
    """Build the GVR Reviser prompt: previous solution + specific critique → targeted revision.

    This is the 'R' in the Generator→Verifier→Reviser loop from Aletheia (2602.10177).
    The critique from the adversarial verifier provides targeted error context,
    enabling a much more focused revision than generic self-correction.

    Args:
        problem_text (str): The math problem.
        previous_solution (str): The solution that had an error.
        critique (str): The specific error description from the adversarial verifier.
        approach_key (str | None): If provided, adds a directive to maintain the
                                   framework that was originally used (so the model
                                   doesn't just abandon the approach after one error).

    Returns:
        str: The revision prompt.
    """
    approach_note = ""
    if approach_key and approach_key in APPROACH_FRAMEWORKS:
        fw = APPROACH_FRAMEWORKS[approach_key]
        approach_note = (
            f"\n## Approach Context\n"
            f"Your previous solution used the {fw['name']} approach. "
            f"If the critique shows this approach is fundamentally wrong for this problem, "
            f"switch freely. Otherwise, fix within the same framework.\n"
        )
    return REVISE_PROMPT.format(
        problem_text=problem_text,
        previous_solution=previous_solution[:3500],  # Cap to stay within context
        critique=critique,
        approach_note=approach_note,
    )


# =============================================================================
# ITERATIVE REFINEMENT — Build upon the current best reasoning chain
# =============================================================================

ITERATIVE_REFINE_PROMPT = """\
You previously worked on the following competition math problem and produced a solution.
Your task is to BUILD UPON that solution — extend the reasoning, fill any gaps,
add independent verification, and produce a strictly more rigorous version.

Do NOT start from scratch. Work from what you already established.

## Problem
{problem_text}

## Your Previous Reasoning (Iteration {iteration})
{previous_solution}

## Your Current Best Answer: {previous_answer}

## Build-Upon Instructions
1. **Preserve**: Identify the solid, correct core of your previous reasoning.
2. **Gap-fill**: Which steps were asserted but not fully proved? Prove them now.
3. **Independent check**: Verify **{previous_answer}** via a DIFFERENT computational \
or algebraic path than you used before. Write new Python code for this.
4. **Stress test**: Find the single most plausible way your answer could be wrong, \
then either disprove it or revise if you find an actual error.
5. **Extend**: Is there additional insight (a cleaner proof, a tighter bound, a \
symmetry argument) that deepens confidence without changing the answer?
6. State your refined final answer as: **ANSWER: [value]**

Your goal is a strictly more rigorous and complete chain of reasoning, not \
a repetition of the same argument.
"""


def build_iterative_refine_prompt(
    problem_text: str,
    previous_solution: str,
    previous_answer: str | None = None,
    iteration: int = 1,
) -> str:
    """Build the iterative-refinement prompt: extend the current best reasoning chain.

    Unlike revision (which fixes a specific error flagged by critique), refinement
    builds upon a promising or correct solution — filling gaps, adding independent
    verification, and stress-testing the answer. Each iteration produces a strictly
    more rigorous reasoning chain.

    Args:
        problem_text (str): The math problem.
        previous_solution (str): The current best solution to build upon.
        previous_answer (str | None): The answer extracted from previous_solution.
        iteration (int): Which refinement pass this is (shown in the prompt for
                         context — helps the model know how much has been done).

    Returns:
        str: The refinement prompt.
    """
    answer_str = str(previous_answer) if previous_answer is not None else "[not yet extracted]"
    return ITERATIVE_REFINE_PROMPT.format(
        problem_text=problem_text,
        previous_solution=previous_solution[:4000],  # Cap to stay within context
        previous_answer=answer_str,
        iteration=iteration,
    )


# ---------------------------------------------------------------------------
# Harmony channel extraction — gpt-oss multi-channel output
# ---------------------------------------------------------------------------
# gpt-oss emits three channels: analysis (thinking), final (answer),
# commentary/assistantcommentary (tool calls). On Kaggle the openai_harmony
# Rust library can parse token IDs directly. Locally we fall back to a
# text-based splitter that handles the decoded special-token text.

# Try importing the Rust-backed openai_harmony library (available on Kaggle
# when installed from the wheel in supply_chain/).
try:
    from openai_harmony import (
        HarmonyEncoding as _HarmonyEncoding,
        load_harmony_encoding as _load_harmony_encoding,
        Role as _HarmonyRole,
        HarmonyEncodingName as _HarmonyEncodingName,
    )
    _harmony_encoding: _HarmonyEncoding | None = None

    def _get_harmony_encoding() -> _HarmonyEncoding:
        global _harmony_encoding
        if _harmony_encoding is None:
            _harmony_encoding = _load_harmony_encoding(
                str(_HarmonyEncodingName.HARMONY_GPT_OSS)
            )
        return _harmony_encoding

    _HAS_HARMONY = True
except Exception:  # pragma: no cover
    _HAS_HARMONY = False


def _extract_harmony_final_via_tokens(token_ids: list[int]) -> str:
    """Parse Harmony channels from raw token IDs using the Rust library.

    Returns the 'final' channel text, or empty string if parsing fails.
    Only callable when openai_harmony is installed.
    """
    if not _HAS_HARMONY:
        return ""
    try:
        enc = _get_harmony_encoding()
        messages = enc.parse_messages_from_completion_tokens(
            token_ids, _HarmonyRole.ASSISTANT, strict=False
        )
        # Collect text from messages on the 'final' channel
        final_parts = []
        for msg in messages:
            channel = getattr(msg, 'channel', None)
            if channel == 'final' or channel is None:
                # None-channel text also goes to final (it's the default)
                content = msg.content
                if hasattr(content, 'text'):
                    final_parts.append(content.text)
                elif isinstance(content, str):
                    final_parts.append(content)
        return "\n".join(final_parts).strip()
    except Exception:
        return ""


# Regex fallback: more robust than the original single-regex approach.
# Splits on channel boundary markers that appear when vLLM decodes Harmony
# special tokens into text.  The channel markers appear as bare words on
# their own line (e.g. "analysis\n", "final\n", "commentary\n").
_HARMONY_CHANNEL_BOUNDARY = re.compile(
    r"^(analysis|final|commentary|assistantcommentary|assistantanalysis)"
    r"(?:\s+to=\w+)?\s*$",
    re.MULTILINE | re.IGNORECASE,
)


def _extract_harmony_final(text: str, token_ids: list[int] | None = None) -> str:
    """Return the 'final' channel text from a Harmony-formatted gpt-oss response.

    Strategy:
      1. If openai_harmony is installed AND token_ids provided → Rust parser (exact).
      2. Otherwise → text-based channel splitting (robust fallback).
      3. Returns empty string if no channel markers found (non-Harmony output).

    Args:
        text: The decoded text output from vLLM.
        token_ids: Raw token IDs from vLLM CompletionOutput (optional but preferred).
    """
    # Strategy 1: Rust library with token IDs
    if _HAS_HARMONY and token_ids:
        result = _extract_harmony_final_via_tokens(token_ids)
        if result:
            return result

    # Strategy 2: Text-based channel splitting
    # Find all channel boundary positions
    boundaries = list(_HARMONY_CHANNEL_BOUNDARY.finditer(text))
    if not boundaries:
        return ""  # Not Harmony format

    # Build channel→text mapping from boundary positions
    channels: dict[str, list[str]] = {}
    for i, match in enumerate(boundaries):
        channel_name = match.group(1).lower()
        # Normalize variants
        if channel_name in ("assistantcommentary", "assistantanalysis"):
            channel_name = "commentary"
        content_start = match.end()
        content_end = boundaries[i + 1].start() if i + 1 < len(boundaries) else len(text)
        chunk = text[content_start:content_end].strip()
        if chunk:
            channels.setdefault(channel_name, []).append(chunk)

    # Return final channel content; strip any remaining channel markers
    final_text = "\n\n".join(channels.get("final", []))
    if final_text:
        return final_text

    # If no explicit 'final' channel but we found channel markers,
    # the model may have put everything under 'analysis'. Return empty
    # rather than returning analysis content (which has intermediate numbers).
    return ""


def extract_answer(
    solution_text: str,
    token_ids: list[int] | None = None,
) -> str | None:
    """Extract the final integer answer from a solution text.

    AIMO answers are non-negative integers in the range [0, 99999].
    Only extracts clean integer tokens — rejects prose-polluted answers
    that would fracture the majority-vote counter.

    Patterns tried in order:
      1. ``**ANSWER: 42**``  (bold, with closing markers)
      2. ``**ANSWER: 42``    (bold, model truncated before closing **)
      3. ``ANSWER: 42``      (no bold markers)
      4. ``\\boxed{42}``     (LaTeX boxed format)

    Args:
        solution_text: The full text of the model's generated solution.
        token_ids: Raw vLLM token IDs for Harmony channel parsing (optional).

    Returns:
        str | None: The integer string (e.g. ``"42"``), or None if no valid
        integer in [0, 99999] can be extracted.
    """
    # Pre-step: for gpt-oss Harmony output, isolate the 'final' channel.
    # The analysis (thinking) channel often contains intermediate numbers
    # that would produce false matches if we searched the full text.
    search_text = _extract_harmony_final(solution_text, token_ids=token_ids) or solution_text

    if _extract_canonical_answer is not None:
        extracted = _extract_canonical_answer(search_text)
        if extracted is not None:
            return extracted

    # Fallback for environments where src/ is unavailable.
    match = re.search(
        r"\*\*ANSWER:\s*(\d{1,6})(?:\*\*|\s*$|\s*\n)",
        search_text, re.IGNORECASE | re.MULTILINE
    )
    if match:
        val = int(match.group(1))
        return str(val) if 0 <= val <= 99999 else None

    match = re.search(r"ANSWER:\s*(\d{1,6})(?:\s|$|\n)", search_text, re.IGNORECASE)
    if match:
        val = int(match.group(1))
        return str(val) if 0 <= val <= 99999 else None

    match = re.search(r"\\boxed\{(\d{1,6})\}", search_text)
    if match:
        val = int(match.group(1))
        return str(val) if 0 <= val <= 99999 else None

    return None


def extract_nl_verdict(verifier_output: str) -> tuple[bool, str]:
    """Extract the verdict from the natural language verifier.

    Fails safe: if the verifier model does not produce a recognisable
    ``VERDICT:`` tag, the function returns ``False`` (reject). A verifier
    that cannot communicate its decision should never silently approve.

    Args:
        verifier_output (str): The output generated by the NL verifier prompt.

    Returns:
        tuple[bool, str]: A tuple where the first element is True only when
        ``VERDICT: CORRECT`` was explicitly found, and the second element is
        an explanation or error message.
    """
    if "VERDICT: CORRECT" in verifier_output.upper():
        return True, "NL Verifier: Solution is correct"

    match = re.search(
        r"VERDICT:\s*ERROR\s*(.*)", verifier_output, re.IGNORECASE | re.DOTALL
    )
    if match:
        return False, f"NL Verifier found error: {match.group(1).strip()[:500]}"

    # Fail-safe: unclear or hallucinated format → reject, never silently approve.
    return False, "NL Verifier: Unclear output format — treated as UNVERIFIED (fail-safe)"


def build_harmony_messages(
    system_prompt: str,
    user_prompt: str,
) -> list[dict]:
    """Build Harmony-formatted message list for gpt-oss models.

    gpt-oss requires the 'developer' role (not 'system') and uses
    tokenizer.apply_chat_template with reasoning_effort="high".

    Usage:
        messages = build_harmony_messages(system_prompt, user_prompt)
        prompt = tokenizer.apply_chat_template(
            messages,
            reasoning_effort="high",
            tokenize=False,
            add_generation_prompt=True,
        )
    """
    return [
        {"role": "developer", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
