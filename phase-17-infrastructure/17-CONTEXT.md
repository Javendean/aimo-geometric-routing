# Phase 17: Geometric Intelligence - Context

**Gathered:** 2026-03-26
**Status:** Ready for planning
**Mode:** Auto-generated (autonomous pipeline)

<domain>
## Phase Boundary

Build the geometric intelligence system — pairwise feature ablation, interference detection, prompt lane separation, diminishing returns detection, and feature grouping for orthogonal exploration. Applies at TWO levels: (1) notebook feature interference (the 10+ v26 features) and (2) system-level interference (the agent's own infrastructure components competing for shared resources like context, input routing, and execution time).

</domain>

<decisions>
## Implementation Decisions

### Geometric Intelligence Module
- **D-01:** New module `src/agent/geometric_intelligence.py`
- **D-02:** `GeometricIntelligence` class composing KnowledgeBase, ResearchSurfacer (for interaction map)

### Pairwise Feature Ablation Matrix (GEO-01)
- **D-03:** `AblationMatrix` dataclass tracking: feature_pair, accuracy_with_both, accuracy_a_only, accuracy_b_only, accuracy_neither, synergy_score (positive = synergistic, negative = interference)
- **D-04:** `build_ablation_matrix(features, results)` — computes the N×N matrix from submission results stored in KB. Each cell = accuracy(A+B) - accuracy(A) - accuracy(B) + baseline
- **D-05:** Matrix populated incrementally as submission results accumulate — not all pairs needed upfront

### Interference Detection (GEO-02)
- **D-06:** `detect_interference(matrix, threshold=-0.02)` — flags pairs where synergy_score < threshold
- **D-07:** For each interference pair, recommends disabling the feature with lower individual accuracy contribution
- **D-08:** Interference findings stored with tag `interference` and Grade A evidence (backed by measured accuracy deltas)

### Prompt Lane Separation (GEO-03)
- **D-09:** `generate_lane_separated_prompt(problem, features)` — structures the system prompt with explicitly separated sections: [ANALYSIS], [STRATEGY], [CODE], [EXTRACTION]
- **D-10:** Each lane has its own instruction block — no cross-lane instruction mixing
- **D-11:** Lane separation effectiveness measured by comparing accuracy before/after on the same problem set

### Diminishing Returns Detection (GEO-04)
- **D-12:** `detect_diminishing_returns(recent_results, window=10)` — tracks accuracy_gain/additional_samples as a declining curve
- **D-13:** When marginal gain drops below configurable threshold (default 0.01), returns a `DiminishingReturns` signal recommending orthogonal exploration instead of more scaling
- **D-14:** Uses linear regression on the last `window` data points — slope < threshold triggers the signal

### Feature Grouping (GEO-05)
- **D-15:** `classify_features(features)` — assigns each feature to a function group: reasoning_modifier, selection_modifier, verification_modifier, sampling_modifier
- **D-16:** `suggest_exploration_order(groups, matrix)` — returns cross-group combinations first (likely synergistic), within-group combinations last (likely conflicting)
- **D-17:** Exploration order feeds into controller's task selection (Phase 16) via CandidateTask generation

### System-Level Interference (NEW — per user feedback)
- **D-18:** `detect_system_interference(iteration_logs)` — analyzes the agent's own iteration logs for infrastructure interference patterns: (a) routing overhead (commands intercepted that should have been direct), (b) context budget waste (large context consumed by low-value components), (c) tool contention (multiple components competing for same resource)
- **D-19:** System interference findings stored with tag `system_interference` — these inform the agent's self-optimization, not just notebook optimization
- **D-20:** The `/gsd:do` interception example is the canonical case: a conversation input routed through a command dispatcher when direct response was correct

### Claude's Discretion
- Exact synergy_score computation for partial data
- Linear regression implementation (numpy vs manual)
- Feature group taxonomy refinement
- System interference detection heuristics beyond the canonical examples

</decisions>

<canonical_refs>
## Canonical References

### Built Infrastructure
- `src/agent/research_surfacer.py` — InteractionMatrix, InteractionType (Phase 15)
- `src/agent/controller.py` — AgentController for wiring geometric intelligence into the loop (Phase 16)
- `src/agent/knowledge_base.py` — KnowledgeBase for storing ablation results
- `src/agent/submission_pipeline.py` — SubmissionResult, GateResult for accuracy data

### Research
- `Transcript_GeometricStructure-vs-Pure Scaling.md` — Richard Aragon's geometric structure thesis
- `.planning/research/FEATURES.md` — Feature grouping and anti-feature analysis
- `.planning/research/PITFALLS.md` — Internal interference as #1 risk

### Requirements
- `.planning/REQUIREMENTS.md` §Geometric Intelligence — GEO-01 through GEO-05

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- ResearchSurfacer.map_interactions() — existing interaction matrix, extend with ablation data
- ResearchSurfacer.InteractionType.INTERFERENCE — already classifies interference
- SubmissionResult.gates — gate results for computing accuracy deltas
- KnowledgeBase.query(tags=["..."]) — retrieve tagged findings

### Integration Points
- `src/agent/geometric_intelligence.py` — new module consumed by controller
- Ablation matrix feeds into controller's task selection
- Lane-separated prompts used by builder subagent
- Diminishing returns signal changes controller's exploration strategy

</code_context>

<deferred>
## Deferred Ideas

- Full MCTS tree search — evidence-weighted priority queue suffices
- Real-time interference monitoring during inference — requires weight access we don't have
- Automated prompt A/B testing framework — manual comparison for now

</deferred>

---

*Phase: 17-geometric-intelligence*
*Context gathered: 2026-03-26 via autonomous pipeline*
