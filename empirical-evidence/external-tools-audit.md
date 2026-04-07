# External Tools Audit: AgentAIMO Competition Ecosystem

**Domain:** AIMO 3 Math Olympiad Competition Solver
**Researched:** 2026-04-03
**Overall confidence:** MEDIUM-HIGH (multiple sources corroborate key findings; some Kaggle-specific details inaccessible via web scraping)

---

## Executive Summary

This audit surveys the external ecosystem of tools, MCP servers, GitHub repositories, HuggingFace models, and competitive intelligence relevant to winning the AIMO 3 competition. The single most important finding comes from a March 2026 paper ([arxiv:2603.27844](https://arxiv.org/abs/2603.27844)) that tested 23+ inference-time optimizations on AIMO 3 and concluded **model capability dominates by an order of magnitude** -- prompt diversity, temperature tuning, and fancy prompt engineering all failed to beat the baseline of gpt-oss-120B at T=1.0 with 8 samples. This fundamentally shapes the optimization strategy: maximize model utilization (more samples, better answer selection) rather than chasing prompt tricks.

The competitive landscape is defined by: (1) NVIDIA's AIMO-2 winning NemoSkills approach (TIR + GenSelect), (2) the available OpenMathReasoning dataset (540K problems, 5.5M solutions), (3) several usable MCP servers for Kaggle API and math computation, and (4) emerging process reward models (ThinkPRM) for solution verification. The top public notebooks score 39-44/50 using gpt-oss-120B with straightforward majority voting.

---

## 1. MCP Servers for Math/Competition Solving

### 1.1 Kaggle API MCP Servers

**Recommendation: Install `54yyyu/kaggle-mcp` for Claude Code integration.**

| Server | Stars | Features | Confidence |
|--------|-------|----------|------------|
| [54yyyu/kaggle-mcp](https://github.com/54yyyu/kaggle-mcp) | Most complete | Browse competitions, datasets, kernels, models; auth via kaggle.json | MEDIUM |
| [Dishant27/kaggle-MCP](https://github.com/Dishant27/kaggle-MCP) | Basic | Competition interaction | LOW |
| [arrismo/kaggle-mcp](https://github.com/arrismo/kaggle-mcp) | Basic | Dataset search/download; uses fastmcp | LOW |
| [KrishnaPramodParupudi/kaggle-mcp-server](https://github.com/KrishnaPramodParupudi/kaggle-mcp-server) | Basic | Competition list, basic operations | LOW |
| [dexhunter/kaggle-mcp](https://github.com/dexhunter/kaggle-mcp) | Basic | Kaggle API wrapper | LOW |

**Assessment:** The Kaggle MCP servers are lightweight wrappers around the Kaggle API. They could help with automated notebook pushing and log retrieval -- operations that have historically been pain points for this project. However, for the 5-day sprint remaining, the existing `kaggle` CLI workflow in the submission pipeline (Phase 12) is already functional. Adding an MCP server would introduce a new dependency with marginal benefit. **Skip unless the existing CLI workflow hits a blocker.**

Kaggle also now provides an official MCP server documented at [kaggle.com/docs/mcp](https://www.kaggle.com/docs/mcp) -- worth checking if it provides better coverage than the community implementations.

### 1.2 Math Computation MCP Servers

**Recommendation: Install `sdiehl/sympy-mcp` for symbolic verification.**

| Server | Purpose | Why It Matters | Confidence |
|--------|---------|----------------|------------|
| [sdiehl/sympy-mcp](https://github.com/sdiehl/sympy-mcp) | Symbolic algebra via SymPy | Equations, derivatives, integrals, simplification. LLMs are "absolutely abysmal at symbolic manipulation" -- offloading to a CAS is the correct architecture. | HIGH |
| [codeprimate/math-mcp](https://github.com/codeprimate/math-mcp) | SymPy + SciPy math | Equations, derivatives, integrals, visualization | MEDIUM |
| [SHSharkar/MCP-Mathematics](https://github.com/SHSharkar/MCP-Mathematics) | 21 tools, 52 functions | Arithmetic through scientific computation | MEDIUM |
| [EthanHenrickson/math-mcp](https://github.com/EthanHenrickson/math-mcp) | Basic math/statistics | Simple numerical calculations | LOW |

**Assessment:** `sdiehl/sympy-mcp` is the most valuable here. It provides symbolic manipulation that Claude Code agents can use to verify algebraic steps in solution traces. This directly addresses the PSEUDO_VERIFICATION flaw pattern seen in baseline metrics (100% of problems). However, this is for the *development* workflow (verifying solutions during iteration), not for the Kaggle notebook itself (which runs air-gapped). **Install for local research loop use; do not add to notebook.**

### 1.3 Theorem Proving MCP Servers

| Server | Purpose | Assessment |
|--------|---------|------------|
| [lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp) | Lean 4 theorem prover via LSP | Exposes diagnostics, goal states, hover info |
| [lean4-skills](https://github.com/cameronfreer/lean4-skills) | Lean 4 workflow pack for AI agents | Works with lean-lsp-mcp for sub-second feedback |
| [Aristotle Lean Theorem Prover](https://mcpmarket.com/tools/skills/aristotle-lean-theorem-prover) | Claude Code skill for Lean | Structured proof verification |

**Assessment:** Formal verification is theoretically powerful for math competition solving (DeepSeek-Prover-V2 achieved gold-level IMO scores using Lean 4). However, integrating a formal theorem prover into the 5-day sprint is infeasible -- the overhead of Lean setup, formalization, and proof search would consume more time than it saves. **Skip for AIMO 3. Consider for post-competition work.**

### 1.4 Code Execution MCP Servers

| Server | Purpose | Assessment |
|--------|---------|------------|
| mcp_code_executor | Python in Conda env | Useful for safe code execution during development |
| mcp-code-sandbox | Isolated sandboxed execution | Docker-based, more secure |
| python_sandbox_mcp_server | Docker containers with SSE | Real-time communication |

**Assessment:** The AgentAIMO codebase already has `PythonExecutor` (src/solver/python_executor.py) for code execution. These MCP servers add Docker isolation but no functional benefit for the competition workflow. **Skip.**

---

## 2. GitHub Repos for AIMO/Math Competition Solving

### 2.1 Directly Relevant Repositories

#### project-numina/aimo-progress-prize (AIMO 1 Winner)
- **URL:** [github.com/project-numina/aimo-progress-prize](https://github.com/project-numina/aimo-progress-prize)
- **What:** SC-TIR (Self-Consistency + Tool-Integrated Reasoning) inference pipeline
- **Score:** 29/50 on AIMO 1 private test
- **Key technique:** Generate diverse reasoning traces with code execution, prune via self-consistency
- **Model:** NuminaMath-7B-TIR (fine-tuned deepseek-math-7b-base)
- **Training:** Two-stage SFT: (1) CoT on diverse math, (2) TIR on synthetic code-interleaved solutions
- **Relevance to AgentAIMO:** The SC-TIR pattern (generate N solutions, execute embedded code, vote on answers) is the proven baseline. AgentAIMO already implements a version of this. The data generation pipeline (GPT-4 producing TORA-style reasoning paths) is worth studying for prompt engineering.
- **Confidence:** HIGH (official winner writeup, code available)

#### NVIDIA-NeMo/Skills (AIMO 2 Winner Framework)
- **URL:** [github.com/NVIDIA-NeMo/Skills](https://github.com/NVIDIA-NeMo/Skills)
- **What:** Full training/evaluation/inference pipeline for math reasoning
- **Score:** 34/50 on AIMO 2 private test
- **Key techniques:** TIR, GenSelect, large-scale data generation
- **Models:** OpenMath-Nemotron-14B-Kaggle (competition), OpenMath-Nemotron-32B (research)
- **Datasets:** OpenMathReasoning (540K problems, 5.5M solutions)
- **Relevance to AgentAIMO:** GenSelect is the single most impactful technique to study. Instead of majority voting, train a model to *select the best solution from candidates*. This achieved 93.3% on AIME24 vs lower scores with standard voting. However, implementing GenSelect requires a fine-tuned selector model, which is beyond the 5-day sprint.
- **Confidence:** HIGH (official winner, paper published, code open)

#### abonvalle/AIMO3-Kaggle
- **URL:** [github.com/abonvalle/AIMO3-Kaggle](https://github.com/abonvalle/AIMO3-Kaggle)
- **What:** Community AIMO 3 solution with problem classification, TIR, weighted voting
- **Key features:**
  - Problem type classification (number theory, algebra, combinatorics, geometry, sequence, probability)
  - Multi-attempt generation (3+ attempts with varying sampling)
  - Code execution weight bonus (+0.5 for successful execution)
  - Boxed answer extraction with fallback chain
  - Iterative refinement when agreement < 50%
- **Answer selection weights:** Code execution (+0.5), code-text agreement (+0.3), greedy first attempt (+0.2), boxed notation (+0.2)
- **Relevance to AgentAIMO:** The weighted answer selection strategy is directly applicable. The project already has AnswerSelector -- compare its weighting with this approach.
- **Confidence:** MEDIUM (community project, unverified scores)

#### trotsky1997/MathBlackBox (MCTSr)
- **URL:** [github.com/trotsky1997/MathBlackBox](https://github.com/trotsky1997/MathBlackBox)
- **What:** Monte Carlo Tree Self-Refine for math olympiad
- **Key technique:** MCTS over solution refinement steps with UCB, self-evaluation, backpropagation
- **Results:** AIME improved from 2.36% (zero-shot CoT) to 11.79% (8 rollouts) with LLaMA-3 8B
- **Relevance to AgentAIMO:** The algorithm design (selection, self-refine, self-evaluate, backprop) is relevant to the MCTS controller in Phase 9/17. However, MCTSr operates at the *per-problem solution refinement* level, not the *iteration configuration* level that AgentAIMO needs. The UCB1 formula and self-refine loop concepts transfer, but the implementation does not.
- **Confidence:** HIGH (published paper, benchmarks verified)

#### aorwall/moatless-tree-search (SWE-Search)
- **URL:** [github.com/aorwall/moatless-tree-search](https://github.com/aorwall/moatless-tree-search)
- **What:** MCTS for software engineering agents (ICLR 2025)
- **Key technique:** Hybrid value function combining numerical + qualitative LLM evaluation, iterative refinement
- **Results:** 23% relative improvement on SWE-bench over standard agents
- **Relevance to AgentAIMO:** The "hybrid value function" concept (combining scalar scores with LLM qualitative assessment) maps directly to the GeometricIntelligence facade. Could inform the MCTS controller design.
- **Confidence:** HIGH (ICLR 2025 paper)

#### WecoAI/aideml (AIDE)
- **URL:** [github.com/WecoAI/aideml](https://github.com/WecoAI/aideml)
- **What:** AI-Driven Exploration in code space; ML engineering agent with tree search
- **Key technique:** Frames ML engineering as code optimization, uses tree search over potential solutions
- **Results:** 4x more medals than best linear agent on MLE-Bench
- **Relevance to AgentAIMO:** The AIDE architecture (tree search over code configurations) is conceptually similar to AgentAIMO's approach tree. The key insight -- tree search outperforms linear exploration by 4x -- validates the Phase 17 geometric intelligence direction.
- **Confidence:** HIGH (published benchmarks, active project)

### 2.2 Reference Notebooks (Kaggle)

| Notebook | Author | Score | Key Approach | URL |
|----------|--------|-------|--------------|-----|
| TIR+DynamicTime+Pooling | zaynyu | 39/50 | TIR, dynamic time allocation, answer pooling | [Link](https://www.kaggle.com/code/zaynyu/39-50-gpt-oss-120b-tir-dynamictime-out-pooling) |
| With tools | andreasbis | Unknown | Tool-integrated reasoning, reference kernel | [Link](https://www.kaggle.com/code/andreasbis/aimo-3-gpt-oss-120b-with-tools) |
| Agentic Solver | seshurajup | Unknown | Agentic pipeline with code execution | [Link](https://www.kaggle.com/code/seshurajup/aimo-3-gpt-oss-120b-agentic-solver) |
| ~3hours H100 | seshurajup | Unknown | Time-optimized H100 execution | [Link](https://www.kaggle.com/code/seshurajup/aimo-3-gpt-oss-120b-3hours-wow-h100) |
| Baseline | takuji | Unknown | Basic baseline implementation | [Link](https://www.kaggle.com/code/takuji/aimo-3-baseline-gpt-oss-120b) |
| Submission Demo | ryanholbrook | N/A | Official demo showing API contract | [Link](https://www.kaggle.com/code/ryanholbrook/aimo-3-submission-demo) |
| Winner | bhargavaabhi | Unknown | Possibly top solution | [Link](https://www.kaggle.com/code/bhargavaabhi/aimo-3-winner/input) |

**Key finding from zaynyu's notebook title:** "TIR+DynamicTime(&out)+Pooling" achieving 39/50 suggests the core competitive approach is:
1. Tool-Integrated Reasoning (code execution within solutions)
2. Dynamic time allocation per problem (spend more time on harder problems)
3. Output pooling (aggregate multiple solution attempts)

This aligns exactly with AgentAIMO's architecture. The 39/50 score matches the paper's reported mean of 39.7 for gpt-oss-120B.

---

## 3. HuggingFace Models and Datasets

### 3.1 Math-Specialized Models

#### gpt-oss-120B (Primary Model)
- **URL:** [huggingface.co/openai/gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b)
- **Architecture:** 117B parameters, 5.1B active (MoE), MXFP4 quantized
- **Context:** Configurable, fits on single H100 80GB
- **Key features:** Configurable reasoning effort (low/medium/high), full chain-of-thought access, native function calling, harmony response format
- **License:** Apache 2.0
- **Critical note:** Must use harmony response format -- model will not work correctly without it
- **Confidence:** HIGH

#### OpenMath-Nemotron-32B (Verification/GenSelect Reference)
- **URL:** [huggingface.co/nvidia/OpenMath-Nemotron-32B](https://huggingface.co/nvidia/OpenMath-Nemotron-32B)
- **Inference modes:** CoT, TIR, GenSelect
- **GenSelect results:** 93.3% on AIME24 (vs 76.5% CoT-only)
- **Relevance:** Cannot run alongside gpt-oss-120B on H100 (insufficient VRAM). But the GenSelect prompting pattern -- give the model multiple solutions and ask it to select the best -- could be adapted as a *prompt technique* for gpt-oss-120B itself.
- **Confidence:** HIGH

#### DeepSeekMath-V2 (Self-Verification Reference)
- **URL:** [huggingface.co/deepseek-ai/DeepSeek-Math-V2](https://huggingface.co/deepseek-ai/DeepSeek-Math-V2)
- **Architecture:** Built on DeepSeek-V3.2-Exp-Base
- **Results:** Gold-level IMO 2025, 118/120 Putnam 2024
- **Key innovation:** Trains verifier as reward model, then trains generator against verifier; self-verification loop
- **Relevance:** Too large to run on Kaggle H100 alongside gpt-oss-120B. The self-verification concept is relevant to solution quality assessment.
- **License:** Apache 2.0
- **Confidence:** HIGH

#### ThinkPRM (Process Reward Model)
- **URL:** [github.com/mukhal/ThinkPRM](https://github.com/mukhal/ThinkPRM)
- **What:** Generative PRM that verifies each step via verification chain-of-thought
- **Results:** Beats discriminative PRMs using only 1% of PRM800K labels; +7.2% over LLM-as-Judge on ProcessBench
- **Relevance:** If a small ThinkPRM could fit alongside gpt-oss-120B, it could score solution quality for best-of-N selection. This would replace majority voting with quality-weighted selection. However, running two models on one H100 is extremely tight.
- **Confidence:** MEDIUM (would need to verify VRAM requirements)

### 3.2 Datasets for Few-Shot Examples and Training

#### nvidia/OpenMathReasoning (Primary Dataset)
- **URL:** [huggingface.co/datasets/nvidia/OpenMathReasoning](https://huggingface.co/datasets/nvidia/OpenMathReasoning)
- **Scale:** 306K unique problems, 540K total with additional; 5.5M solutions
- **Sources:** Art of Problem Solving forums, MATH training set
- **Solution types:** 3.2M CoT, 1.7M TIR, 566K GenSelect
- **Format:** Parquet, ~114GB total
- **Key fields:** problem, generated_solution, expected_answer, pass_rate_72b_tir, inference_mode, used_in_kaggle
- **License:** CC-BY-4.0
- **Actionable use cases:**
  1. **Few-shot prompting:** Extract high-quality TIR solutions (filter by pass_rate_72b_tir > 0.5) as in-context examples for gpt-oss-120B prompts
  2. **Problem-type-specific examples:** Filter by problem_source (e.g., "aops_c6_high_school_olympiads") for olympiad-level examples
  3. **Answer format templates:** Study how solutions are structured for the boxed-answer extraction pattern
- **Confidence:** HIGH

#### openai/prm800k (Process Reward Labels)
- **URL:** [github.com/openai/prm800k](https://github.com/openai/prm800k)
- **What:** 800K step-level correctness labels on math solutions
- **Relevance:** Reference data for understanding process reward model training; each problem has up to 1860 scored samples
- **Confidence:** HIGH

#### RLHFlow/MATH Process Reward Model
- **URL:** [huggingface.co/collections/RLHFlow/rlhflow-math-process-reward-model](https://huggingface.co/collections/RLHFlow/rlhflow-math-process-reward-model-6725a42fc8808e12aa1cb144)
- **What:** Collection of math PRMs
- **Relevance:** Pre-trained verifiers for solution quality scoring
- **Confidence:** MEDIUM

---

## 4. Kaggle-Specific Intelligence

### 4.1 Competition Structure (AIMO 3)
- **Problems:** 110 problems spanning algebra, combinatorics, geometry, number theory
- **Difficulty:** National Olympiad to IMO standard, significantly harder than AIMO 2
- **Scoring:** Penalized accuracy (exact formula not accessible via web scraping, must check Kaggle directly)
- **Compute:** H100 GPU, 5-hour time limit
- **API:** Must use `kaggle_evaluation.aimo_3_inference_server.AIMO3InferenceServer`
- **Deadline:** April 8, 2026 (entry), April 15, 2026 (final submission)
- **Confidence:** MEDIUM (some details inferred from multiple sources; scoring formula not verified)

### 4.2 The "Model Capability Dominates" Paper

**This is the single most important external finding.** [arxiv:2603.27844](https://arxiv.org/abs/2603.27844)

Key findings from 23+ experiments on AIMO 3 with gpt-oss-120B on H100:

| Strategy | Score | vs Baseline |
|----------|-------|-------------|
| **Baseline (original prompt, T=1.0, N=8)** | **39.7 mean** | -- |
| Best single run (lucky) | 44/50 | +4.3 (noise) |
| Code-First strategy | 41/50 initial, 37.7 mean | -2.0 (worse) |
| Conservative mixing | 40/50 | +0.3 (noise) |
| Aggressive mixing | 40/50 | +0.3 (noise) |
| 8x Small Cases prompt | 37/50 | -2.7 |
| 8x Classify prompt | 36/50 | -3.7 |
| 8x Work Backwards | 39/50 | -0.7 |
| Temperature 0.5 | 38/50 | -1.7 |
| Temperature 1.2 | 37/50 | -2.7 |
| Nemotron-Super-120B (alt model) | 23/50 | -16.7 |
| Smaller 20B variant (alt model) | 26/50 | -13.7 |

**Why diversity failed:**
- Temperature T=1.0 already decorrelates errors (pairwise correlation approx -0.113, near zero)
- Every alternative prompt *lowered per-attempt accuracy* more than it reduced correlation
- Net effect: diversity strategies hurt more than they help

**The paper's recommendation:** "Use the largest model that fits, keep temperature high, and spend submission budget on lottery tickets, not on prompt engineering."

**Implications for AgentAIMO:**
1. Stop investing in prompt diversity engineering
2. Maximize the number of high-quality samples per problem (N=8 is the baseline; can we do more within time budget?)
3. Focus on answer selection quality, not prompt quality
4. The 39.7 mean is the floor -- beating it requires either (a) better answer selection than majority voting, or (b) fine-tuning gpt-oss-120B
5. The 44/50 "lucky run" shows the ceiling is reachable -- the question is how to make it reliable

### 4.3 gpt-oss-120B on vLLM Configuration

From official docs and community notebooks:

```python
# Model runs MXFP4 quantized out of the box
# Fits on single H100 80GB
# Must use harmony response format

# vLLM launch: vllm serve openai/gpt-oss-120b

# Key parameters (from vLLM recipes):
# --gpu-memory-utilization 0.95
# --max-num-batched-tokens 1024  (for single H100)
# Tensor parallelism: tp=1 for single H100

# CRITICAL: The model uses harmony response format via chat template
# Transformers library auto-applies it; manual prompting must include it
```

The model arrives MXFP4 quantized (more compressed than FP8). FP8 is the only quantization format worth using on H100 (native Tensor Core support). Key: do not attempt FP16 -- it will not fit on a single H100.

### 4.4 Common Failure Modes

From baseline metrics and community notebooks:
1. **CHANNEL_LEAKAGE** (100% of problems) -- model leaks intermediate state into answer
2. **MALFORMED_TOOL_CALL** (100%) -- code blocks not properly formatted for execution
3. **PSEUDO_VERIFICATION** (70-100%) -- model claims to verify but does not actually check
4. **MISSING_FINAL_COMMIT** -- correct answer derived but not output in extractable format
5. **CONTEXT_CONFABULATION** -- model requests prior context on self-contained problems
6. **Answer extraction failure** -- correct answer in prose, not in extractable format

---

## 5. Prompt Engineering for Math Competition

### 5.1 What Actually Works (Evidence-Based)

Based on the "Model Capability Dominates" paper and AIMO 1/2 winning solutions:

**Works:**
- **High temperature (T=1.0)** for diversity in sampling -- confirmed by paper
- **Tool-Integrated Reasoning (TIR):** Interleaving code execution with reasoning -- confirmed by AIMO 1 (Numina) and AIMO 2 (NemoSkills) winners
- **Self-Consistency voting:** Generate N solutions, extract answers, majority vote -- baseline approach
- **Dynamic time allocation:** Spend more time on harder problems -- used in 39/50 notebook
- **Boxed answer format:** `\boxed{answer}` as extraction target -- standard in math competitions

**Does NOT work (or marginal):**
- Prompt diversity (different system prompts per attempt) -- confirmed negative by paper
- Temperature tuning below 1.0 or above 1.2 -- confirmed neutral/negative
- "Classify then solve" prompting -- confirmed negative (-3.7 points)
- "Work backwards" prompting -- confirmed neutral (-0.7 points)

### 5.2 GenSelect as a Prompt Pattern

The NemoSkills GenSelect approach can be adapted as a gpt-oss-120B prompt pattern without a separate model:

1. Generate N=8 solutions with high temperature
2. Extract all answers
3. If no clear majority, present the top 2-3 distinct solutions to gpt-oss-120B and ask it to select the best one
4. This uses one additional inference call but avoids the tie-breaking failure mode

**Status:** Untested on gpt-oss-120B specifically, but the concept is sound (MEDIUM confidence)

### 5.3 TIR Implementation Pattern

From NuminaMath and NemoSkills:

```
Problem: [problem statement]

Think step by step. When you need to compute something, write Python code
in ```python blocks. Execute the code mentally and use the result in your
reasoning. At the end, put your final answer inside \boxed{}.
```

The key insight from NemoSkills: TIR solutions must be *trained* (via SFT), not just prompted. Direct few-shot prompting of reasoning models to produce TIR was "unsuccessful." However, gpt-oss-120B has native code execution support (harmony format includes tool calling), so it may respond better to TIR prompting than the models NemoSkills tested.

### 5.4 PRIME (Process Reinforcement through Implicit Rewards)

[huggingface.co/blog/ganqu/prime](https://huggingface.co/blog/ganqu/prime) -- 16.7% average improvement, 20%+ on AMC/AIME. Enables PRM updates using only outcome labels (no step-level annotation needed). This is a training-time technique, not applicable to the 5-day sprint, but represents the state of the art in PRM training.

---

## 6. Strategic Assessment

### 6.1 What Can Actually Be Done in 5 Days

| Action | Impact | Effort | Recommendation |
|--------|--------|--------|----------------|
| Maximize samples per problem (N>8) | HIGH | LOW | **DO THIS** -- time budget analysis needed |
| Implement dynamic time allocation | HIGH | MEDIUM | **DO THIS** -- harder problems get more attempts |
| Add TIR code execution to solutions | HIGH | MEDIUM | **DO THIS** -- if not already active |
| Improve answer extraction/selection | MEDIUM | MEDIUM | **DO THIS** -- weighted voting from abonvalle repo |
| Install sympy-mcp for development | LOW | LOW | Optional -- helps during iteration |
| Study OpenMathReasoning for few-shot | MEDIUM | LOW | Extract 5-10 high-quality examples |
| Implement GenSelect as prompt pattern | MEDIUM | MEDIUM | Worth testing |
| Install Kaggle MCP server | LOW | LOW | Skip -- existing CLI works |
| Fine-tune gpt-oss-120B | HIGH | VERY HIGH | **NOT FEASIBLE** in 5 days |
| Run separate verifier model | HIGH | VERY HIGH | **NOT FEASIBLE** -- VRAM constraint |
| Integrate formal theorem proving | LOW | VERY HIGH | **SKIP ENTIRELY** |

### 6.2 The Winning Formula (Evidence-Based)

Based on all research:

```
Score = f(model_capability) * g(num_samples, time_allocation) * h(answer_selection)
```

Where:
- `f(model_capability)` = gpt-oss-120B (cannot improve in 5 days)
- `g(num_samples, time_allocation)` = maximize by dynamic time budgeting
- `h(answer_selection)` = improve beyond majority voting with weighted selection

The ceiling is ~44/50 (observed lucky run). The floor is ~36/50 (worst prompt engineering). The reliable target is 40-42/50 with optimized sampling and selection.

### 6.3 Key Differences from Current AgentAIMO

| Area | Current AgentAIMO | Competitive Best Practice |
|------|-------------------|--------------------------|
| Temperature | Unknown (check) | T=1.0 (confirmed optimal) |
| Samples per problem | Unknown (check) | N=8 minimum, more is better |
| Time allocation | Per-problem budget exists | Dynamic based on difficulty estimation |
| Answer selection | confidence_weighted_vote | Weighted by code execution, agreement, boxed notation |
| TIR | Unknown status | Should be active -- interleave code execution |
| Prompt format | Check harmony compliance | Must use harmony format -- model fails without it |
| Answer format | Check current format | Industry standard is `\boxed{N}` |

---

## 7. Confidence Assessment

| Area | Confidence | Rationale |
|------|------------|-----------|
| Model capability dominance | HIGH | Published paper with 23+ experiments on exact competition |
| MCP server landscape | HIGH | Multiple verified GitHub repos with documentation |
| NemoSkills winning approach | HIGH | Published paper, official Kaggle writeup, open code |
| OpenMathReasoning dataset | HIGH | Official NVIDIA release, CC-BY-4.0, verified on HuggingFace |
| Top notebook scores (39-44/50) | MEDIUM | Paper reports mean 39.7; 44 was single lucky run |
| AIMO 3 scoring formula | LOW | Could not scrape exact formula from Kaggle |
| GenSelect as prompt pattern | MEDIUM | Concept proven in NemoSkills; untested on gpt-oss-120B |
| ThinkPRM VRAM fit alongside 120B | LOW | Not verified; likely does not fit |

---

## 8. Gaps and Open Questions

1. **Exact AIMO 3 scoring formula** -- need to check Kaggle directly. Is it penalized accuracy with wrong-answer deduction? How many answer attempts per problem?
2. **gpt-oss-120B harmony format details** -- need to verify the exact prompt template being used in the current notebook matches the required format
3. **Current N (samples per problem)** -- need to check what the notebook currently uses and whether increasing it fits in the 5-hour time budget
4. **TIR activation status** -- is tool-integrated reasoning (code execution within solution traces) currently active in the notebook?
5. **How far are we from the 39.7 baseline?** -- current baseline shows 38% (3/8) to 75% (6/8) on local test set, but these are different problems than the Kaggle test set

---

## Sources

### Papers
- [Model Capability Dominates: AIMO 3 Lessons (2603.27844)](https://arxiv.org/abs/2603.27844) -- March 2026
- [AIMO-2 Winning Solution: OpenMathReasoning (2504.16891)](https://arxiv.org/abs/2504.16891) -- April 2025
- [MCTSr: Monte Carlo Tree Self-Refine (2406.07394)](https://arxiv.org/abs/2406.07394) -- June 2024
- [SWE-Search: MCTS for Software Agents (2410.20285)](https://arxiv.org/abs/2410.20285) -- ICLR 2025
- [AIDE: AI-Driven Exploration (2502.13138)](https://arxiv.org/abs/2502.13138) -- February 2025
- [ThinkPRM: Process Reward Models That Think (2504.16828)](https://arxiv.org/abs/2504.16828) -- April 2025
- [Let's Verify Step by Step (2305.20050)](https://arxiv.org/abs/2305.20050) -- OpenAI PRM800K
- [PRIME: Process Reinforcement through Implicit Rewards](https://huggingface.co/blog/ganqu/prime)
- [DeepSeekMath-V2: Self-Verifiable Reasoning (2511.22570)](https://arxiv.org/abs/2511.22570) -- November 2025
- [Proof or Bluff? Evaluating LLMs on 2025 USAMO](https://arxiv.org/abs/2503.21934) -- March 2025

### Repositories
- [project-numina/aimo-progress-prize](https://github.com/project-numina/aimo-progress-prize) -- AIMO 1 winner
- [NVIDIA-NeMo/Skills](https://github.com/NVIDIA-NeMo/Skills) -- AIMO 2 winner framework
- [abonvalle/AIMO3-Kaggle](https://github.com/abonvalle/AIMO3-Kaggle) -- Community AIMO 3 solution
- [trotsky1997/MathBlackBox](https://github.com/trotsky1997/MathBlackBox) -- MCTSr implementation
- [aorwall/moatless-tree-search](https://github.com/aorwall/moatless-tree-search) -- SWE-Search
- [WecoAI/aideml](https://github.com/WecoAI/aideml) -- AIDE agent
- [openai/gpt-oss](https://github.com/openai/gpt-oss) -- Official model repo
- [openai/prm800k](https://github.com/openai/prm800k) -- Process reward labels
- [mukhal/ThinkPRM](https://github.com/mukhal/ThinkPRM) -- Generative PRM

### MCP Servers
- [54yyyu/kaggle-mcp](https://github.com/54yyyu/kaggle-mcp) -- Kaggle API MCP
- [sdiehl/sympy-mcp](https://github.com/sdiehl/sympy-mcp) -- Symbolic algebra MCP
- [codeprimate/math-mcp](https://github.com/codeprimate/math-mcp) -- Math MCP
- [SHSharkar/MCP-Mathematics](https://github.com/SHSharkar/MCP-Mathematics) -- Mathematics MCP
- [lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp) -- Lean 4 MCP

### HuggingFace
- [nvidia/OpenMathReasoning](https://huggingface.co/datasets/nvidia/OpenMathReasoning) -- 540K problems, 5.5M solutions
- [nvidia/OpenMath-Nemotron-32B](https://huggingface.co/nvidia/OpenMath-Nemotron-32B) -- GenSelect model
- [nvidia/OpenMath-Nemotron-14B-Kaggle](https://huggingface.co/nvidia/OpenMath-Nemotron-14B-Kaggle) -- AIMO 2 competition model
- [openai/gpt-oss-120b](https://huggingface.co/openai/gpt-oss-120b) -- Primary competition model
- [deepseek-ai/DeepSeek-Math-V2](https://huggingface.co/deepseek-ai/DeepSeek-Math-V2) -- Self-verifiable math
- [RLHFlow/math-process-reward-model](https://huggingface.co/collections/RLHFlow/rlhflow-math-process-reward-model-6725a42fc8808e12aa1cb144) -- PRM collection

### Kaggle Notebooks
- [zaynyu: 39/50 TIR+DynamicTime+Pooling](https://www.kaggle.com/code/zaynyu/39-50-gpt-oss-120b-tir-dynamictime-out-pooling)
- [andreasbis: With tools](https://www.kaggle.com/code/andreasbis/aimo-3-gpt-oss-120b-with-tools)
- [seshurajup: Agentic Solver](https://www.kaggle.com/code/seshurajup/aimo-3-gpt-oss-120b-agentic-solver)
- [ryanholbrook: Submission Demo](https://www.kaggle.com/code/ryanholbrook/aimo-3-submission-demo)
- [NemoSkills: 1st Place AIMO 2](https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-2/writeups/nemoskills-1st-place-solution-nemoskills)

### Competition
- [AIMO 3 Competition Page](https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-3)
- [AIMO Prize Official](https://aimoprize.com/updates/)
- [How NuminaMath Won AIMO 1](https://huggingface.co/blog/winning-aimo-progress-prize)
