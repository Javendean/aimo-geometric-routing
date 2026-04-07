# KB Findings on Prompting, Routing, and Answer Selection

Total findings matching prompt/routing/topic keywords: 30

## F2595 (iter None, Grade B)
**[regression_risk] Without the diff, it is unknown whether the VerificationPipeline integration respects the ConfidenceLevel hierarchy (LEVEL_0_EXACT > LEVEL_1_SYMBOLIC > ENUMERATED > NL_JUDGMENT > UNVERIFIED) mandated by CLAUDE.md. Incorrect confidence level assignment by the ModularVerifier could corrupt answer selection logic.**

[regression_risk] Without the diff, it is unknown whether the VerificationPipeline integration respects the ConfidenceLevel hierarchy (LEVEL_0_EXACT > LEVEL_1_SYMBOLIC > ENUMERATED > NL_JUDGMENT > UNVERIFIED) mandated by CLAUDE.md. Incorrect confidence level assignment by the ModularVerifier could corrupt answer selection logic.

---

## F2584 (iter None, Grade B)
**[unfounded_assumption] Test test_no_two_consecutive_attempts_identical (line 263-275) assumes the interleaving algorithm in TopicAwareSamplingPlan always produces non-identical consecutive pairs for N=8. This is an emergent property of the scheduling algorithm, not a contractual guarantee. If the scheduling logic changes, this test becomes fragile.**

[unfounded_assumption] Test test_no_two_consecutive_attempts_identical (line 263-275) assumes the interleaving algorithm in TopicAwareSamplingPlan always produces non-identical consecutive pairs for N=8. This is an emergent property of the scheduling algorithm, not a contractual guarantee. If the scheduling logic changes, this test becomes fragile.

---

## F2583 (iter None, Grade B)
**[regression_risk] The non-TIR batch path (deep_researcher.py line 2052-2069) uses _generate_batch() with a single temperature for N samples. DiverseCandidateGenerator produces per-attempt temperatures, requiring N separate generation calls instead of one batched call. This could degrade inference throughput significantly on H100 (batch inference is far more efficient than sequential calls in vLLM). This performance regression is not analyzed anywhere.**

[regression_risk] The non-TIR batch path (deep_researcher.py line 2052-2069) uses _generate_batch() with a single temperature for N samples. DiverseCandidateGenerator produces per-attempt temperatures, requiring N separate generation calls instead of one batched call. This could degrade inference throughput significantly on H100 (batch inference is far more efficient than sequential calls in vLLM). This performance regression is not analyzed anywhere.

---

## F2582 (iter None, Grade B)
**[evidence_gap] No evidence chain provided (explicitly stated: 'no evidence chain available'). The arXiv:2502.11027 and 'NVIDIA GenSelect' citations are mentioned inline but have no Grade A/B evidence backing. The claimed '+3-5 point improvement from diverse prompting' cannot be verified. Additionally, since user-prompt perturbation is ALREADY active in deep_researcher.py, the cited improvement likely applies to the FROM-ZERO baseline, not the current partially-diverse state.**

[evidence_gap] No evidence chain provided (explicitly stated: 'no evidence chain available'). The arXiv:2502.11027 and 'NVIDIA GenSelect' citations are mentioned inline but have no Grade A/B evidence backing. The claimed '+3-5 point improvement from diverse prompting' cannot be verified. Additionally, since user-prompt perturbation is ALREADY active in deep_researcher.py, the cited improvement likely applies to the FROM-ZERO baseline, not the current partially-diverse state.

---

## F2581 (iter None, Grade B)
**[unfounded_assumption] The DiverseCandidateGenerator duplicates perturbation scheduling logic that TopicAwareSamplingPlan.perturbation_schedule() already handles, AND duplicates the prompt construction that deep_researcher.py already does with apply_user_perturbation(). When this IS eventually wired in, it will conflict with deep_researcher.py's existing perturbation application (lines 2035-2049). The integration path is not documented — will deep_researcher stop calling apply_user_perturbation directly, or will perturbations be applied twice?**

[unfounded_assumption] The DiverseCandidateGenerator duplicates perturbation scheduling logic that TopicAwareSamplingPlan.perturbation_schedule() already handles, AND duplicates the prompt construction that deep_researcher.py already does with apply_user_perturbation(). When this IS eventually wired in, it will conflict with deep_researcher.py's existing perturbation application (lines 2035-2049). The integration path is not documented — will deep_researcher stop calling apply_user_perturbatio

---

## F2579 (iter None, Grade B)
**[logical_inconsistency] Evidence chain claim #1 is FALSE: 'prompt_perturbation.py — 6 orthogonal prompt variants defined, zero callers outside self.' In reality, deep_researcher.py already imports and actively calls apply_user_perturbation() and get_perturbation() at lines 2035-2049. User prompts ARE already being perturbed per-attempt via round-robin. The actual gap is narrower than claimed: only temperature diversity and system-prompt perturbation are missing. This means the stated +3-5 point improvement from 'diverse prompting' is partially already captured, and the incremental gain from this change is overstated.**

[logical_inconsistency] Evidence chain claim #1 is FALSE: 'prompt_perturbation.py — 6 orthogonal prompt variants defined, zero callers outside self.' In reality, deep_researcher.py already imports and actively calls apply_user_perturbation() and get_perturbation() at lines 2035-2049. User prompts ARE already being perturbed per-attempt via round-robin. The actual gap is narrower than claimed: only temperature diversity and system-prompt perturbation are missing. This means the stated +3-5 poin

---

## F2577 (iter None, Grade B)
**[unfounded_assumption] answer_diversity() (lines 287-306) is dead code — nothing in the codebase calls it. The claim that it's 'useful for adaptive stopping decisions by BayesianController' is aspirational; BayesianController does not import or reference this method. Adding untested integration paths is speculative complexity.**

[unfounded_assumption] answer_diversity() (lines 287-306) is dead code — nothing in the codebase calls it. The claim that it's 'useful for adaptive stopping decisions by BayesianController' is aspirational; BayesianController does not import or reference this method. Adding untested integration paths is speculative complexity.

---

## F2573 (iter None, Grade B)
**[unfounded_assumption] The change assumes unanimous agreement implies correctness ('Correctly signaling certainty'). No evidence supports this. Math competition models are known to converge on systematic errors (e.g., off-by-one in combinatorics, wrong modular arithmetic). The CLAUDE.md itself cites a paper showing 'none beat T=1.0, N=8, majority vote (39.7/50)' — meaning even the best config gets 10+ problems wrong. If the model consistently fails a problem the same way across all 8 samples, the unanimous path returns confidence=1.0 for the wrong answer.**

[unfounded_assumption] The change assumes unanimous agreement implies correctness ('Correctly signaling certainty'). No evidence supports this. Math competition models are known to converge on systematic errors (e.g., off-by-one in combinatorics, wrong modular arithmetic). The CLAUDE.md itself cites a paper showing 'none beat T=1.0, N=8, majority vote (39.7/50)' — meaning even the best config gets 10+ problems wrong. If the model consistently fails a problem the same way across all 8 samples, 

---

## F2572 (iter None, Grade B)
**[logical_inconsistency] Unanimous fast-path (lines 186-189 of answer_selector.py) bypasses ALL quality signals: flaw_penalty, tir_factor, deepconf_weight, and extraction_confidence. If 8 attempts all extract the same wrong answer but all have UNVERIFIED confidence, critical flaws (NON_EXECUTABLE_CODE), and deepconf_weight=0.1, the existing weighted system would correctly assign near-zero aggregate weight. The unanimous path returns confidence=1.0 instead. This is the exact failure mode the weighted voting system was designed to prevent — LLMs converging on a confidently wrong answer. Test test_unanimous_mixed_confidence_levels (line 100-110) explicitly validates this broken behavior: UNVERIFIED traces return confidence=1.0.**

[logical_inconsistency] Unanimous fast-path (lines 186-189 of answer_selector.py) bypasses ALL quality signals: flaw_penalty, tir_factor, deepconf_weight, and extraction_confidence. If 8 attempts all extract the same wrong answer but all have UNVERIFIED confidence, critical flaws (NON_EXECUTABLE_CODE), and deepconf_weight=0.1, the existing weighted system would correctly assign near-zero aggregate weight. The unanimous path returns confidence=1.0 instead. This is the exact failure mode the weigh

---

## F2570 (iter None, Grade B)
**[unfounded_assumption] The _MIN_TOPIC_CONFIDENCE threshold of 0.3 (line 73) and the perturbation biasing threshold of 0.5 (line 161) are magic numbers with no empirical basis. The test for low-confidence fallback (test_ambiguous_problem_uses_defaults, line 185) depends on 'Solve the problem.' producing confidence < 0.3, which is an implementation detail of the regex classifier — if the classifier is ever improved, this test becomes fragile.**

[unfounded_assumption] The _MIN_TOPIC_CONFIDENCE threshold of 0.3 (line 73) and the perturbation biasing threshold of 0.5 (line 161) are magic numbers with no empirical basis. The test for low-confidence fallback (test_ambiguous_problem_uses_defaults, line 185) depends on 'Solve the problem.' producing confidence < 0.3, which is an implementation detail of the regex classifier — if the classifier is ever improved, this test becomes fragile.

---

## F2569 (iter None, Grade B)
**[logical_inconsistency] The docstring (line 27) claims 'plan.temperature_schedule(8)' returns '[0.6, 0.8, 0.6, 1.0, 0.6, ...]' for number theory. But the actual algorithm (lines 107-138) for baseline=0.6 with diverse=[0.8, 1.0] and n=8 produces [0.6, 0.6, 0.8, 0.6, 1.0, 0.6, 0.6, 0.6] — the interleave pattern doesn't match the docstring example. Minor, but indicates the schedule logic wasn't carefully traced.**

[logical_inconsistency] The docstring (line 27) claims 'plan.temperature_schedule(8)' returns '[0.6, 0.8, 0.6, 1.0, 0.6, ...]' for number theory. But the actual algorithm (lines 107-138) for baseline=0.6 with diverse=[0.8, 1.0] and n=8 produces [0.6, 0.6, 0.8, 0.6, 1.0, 0.6, 0.6, 0.6] — the interleave pattern doesn't match the docstring example. Minor, but indicates the schedule logic wasn't carefully traced.

---

## F2568 (iter None, Grade B)
**[regression_risk] The TopicAwareSampler is currently disconnected (zero call sites outside its own file + tests), so it cannot cause regressions today. However, the stated 'next step' is to wire it into the notebook's sampling loop. When that happens, it will OVERRIDE the existing SamplingStrategy schedule with potentially untested temperatures. Since there's no measurement gate validating the temperature choices, wiring it in could silently degrade accuracy on the 50-problem competition set.**

[regression_risk] The TopicAwareSampler is currently disconnected (zero call sites outside its own file + tests), so it cannot cause regressions today. However, the stated 'next step' is to wire it into the notebook's sampling loop. When that happens, it will OVERRIDE the existing SamplingStrategy schedule with potentially untested temperatures. Since there's no measurement gate validating the temperature choices, wiring it in could silently degrade accuracy on the 50-problem competition set.

---

## F2567 (iter None, Grade B)
**[logical_inconsistency] The module is described as 'bridging' TopicClassifier → SamplingStrategy, but it does NOT actually integrate with SamplingStrategy or SamplingConfig. It produces its own TopicAwareSamplingPlan with its own temperature_schedule() and perturbation_schedule() methods that are completely independent of, and potentially conflicting with, the existing SamplingStrategy._build_schedule(). The 'bridge' creates a THIRD scheduling system rather than modifying or extending the existing one.**

[logical_inconsistency] The module is described as 'bridging' TopicClassifier → SamplingStrategy, but it does NOT actually integrate with SamplingStrategy or SamplingConfig. It produces its own TopicAwareSamplingPlan with its own temperature_schedule() and perturbation_schedule() methods that are completely independent of, and potentially conflicting with, the existing SamplingStrategy._build_schedule(). The 'bridge' creates a THIRD scheduling system rather than modifying or extending the exis

---

## F2566 (iter None, Grade B)
**[unfounded_assumption] The _TOPIC_LEAD_PERTURBATION mapping (lines 54-59) assumes 'adversarial_framing' is optimal for combinatorics, 'tool_emphasis' for geometry, etc. These are identical to the pre-existing _TOPIC_PERTURBATION in topic_classifier.py (lines 44-49). No evidence supports these pairings — they are hunches copied from a module that was itself never validated in production.**

[unfounded_assumption] The _TOPIC_LEAD_PERTURBATION mapping (lines 54-59) assumes 'adversarial_framing' is optimal for combinatorics, 'tool_emphasis' for geometry, etc. These are identical to the pre-existing _TOPIC_PERTURBATION in topic_classifier.py (lines 44-49). No evidence supports these pairings — they are hunches copied from a module that was itself never validated in production.

---

## F2565 (iter None, Grade B)
**[unfounded_assumption] The module assumes topic-specific temperature tuning (T=0.6 for number theory, T=0.8 for algebra, T=1.0 for combinatorics) is beneficial. No A/B test, ablation, or external citation supports these specific values. The _TOPIC_BASELINE_TEMP mapping in topic_aware_sampler.py lines 61-66 duplicates _TOPIC_TEMPERATURE from topic_classifier.py lines 55-59 — these values were already present but never validated, and the new module just copies them without independent justification.**

[unfounded_assumption] The module assumes topic-specific temperature tuning (T=0.6 for number theory, T=0.8 for algebra, T=1.0 for combinatorics) is beneficial. No A/B test, ablation, or external citation supports these specific values. The _TOPIC_BASELINE_TEMP mapping in topic_aware_sampler.py lines 61-66 duplicates _TOPIC_TEMPERATURE from topic_classifier.py lines 55-59 — these values were already present but never validated, and the new module just copies them without independent justificat

---

## F2564 (iter None, Grade B)
**[evidence_gap] The entire evidence chain is marked '(no evidence chain available)'. The core claim — that topic-aware temperature selection improves accuracy — has zero Grade A or B evidence. The CLAUDE.md itself cites a March 2026 paper showing 23+ prompt strategies on gpt-oss-120B FAILED to beat T=1.0, N=8, majority vote (39.7/50). This module's per-topic temperatures (0.6, 0.8) are LOWER than the empirically-validated T=1.0 baseline, directly contradicting the project's own recorded evidence.**

[evidence_gap] The entire evidence chain is marked '(no evidence chain available)'. The core claim — that topic-aware temperature selection improves accuracy — has zero Grade A or B evidence. The CLAUDE.md itself cites a March 2026 paper showing 23+ prompt strategies on gpt-oss-120B FAILED to beat T=1.0, N=8, majority vote (39.7/50). This module's per-topic temperatures (0.6, 0.8) are LOWER than the empirically-validated T=1.0 baseline, directly contradicting the project's own recorded evide

---

## F2557 (iter None, Grade B)
**[unfounded_assumption] The TIR factor in _tir_factor() uses PASS_FACTOR=2.0 and FAIL_FACTOR=0.25. A 2x boost for TIR-passing solutions is aggressive and uncalibrated. No evidence shows this multiplier improves answer selection accuracy. If TIR verification has false positives (e.g., code block output matches by coincidence), this doubles the weight of potentially wrong answers. The 0.25 penalty is similarly arbitrary — a single spurious FAIL from a timeout-prone sandbox could quarter the weight of a correct solution.**

[unfounded_assumption] The TIR factor in _tir_factor() uses PASS_FACTOR=2.0 and FAIL_FACTOR=0.25. A 2x boost for TIR-passing solutions is aggressive and uncalibrated. No evidence shows this multiplier improves answer selection accuracy. If TIR verification has false positives (e.g., code block output matches by coincidence), this doubles the weight of potentially wrong answers. The 0.25 penalty is similarly arbitrary — a single spurious FAIL from a timeout-prone sandbox could quarter the weigh

---

## F2523 (iter None, Grade B)
**[logical_inconsistency] Lines 1611-1612 compute `_header` via `_task_match.group(0)[:_task_match.start(1) - _task_match.start(0)]` which is an indirect way to extract the header portion. But then lines 1613-1614 reconstruct the prompt using `prompt[_task_match.start():_task_match.start(1)]` for the same purpose — making _header a dead variable. The string slicing in lines 1613-1616 is correct but the dead `_header` variable suggests incomplete refactoring.**

[logical_inconsistency] Lines 1611-1612 compute `_header` via `_task_match.group(0)[:_task_match.start(1) - _task_match.start(0)]` which is an indirect way to extract the header portion. But then lines 1613-1614 reconstruct the prompt using `prompt[_task_match.start():_task_match.start(1)]` for the same purpose — making _header a dead variable. The string slicing in lines 1613-1616 is correct but the dead `_header` variable suggests incomplete refactoring.

---

## F2522 (iter None, Grade B)
**[regression_risk] The post-assembly sanitize_prompt_task_section regex (line 205 of infra_task_gate.py) uses `(?=\n\n|\n##|\Z)` as the task body terminator. If the task description contains a double newline (e.g., a multi-paragraph task), the regex will only capture text up to the first `\n\n`, potentially missing the infra keywords that appear after the first paragraph break. This is a silent false-negative path.**

[regression_risk] The post-assembly sanitize_prompt_task_section regex (line 205 of infra_task_gate.py) uses `(?=\n\n|\n##|\Z)` as the task body terminator. If the task description contains a double newline (e.g., a multi-paragraph task), the regex will only capture text up to the first `\n\n`, potentially missing the infra keywords that appear after the first paragraph break. This is a silent false-negative path.

---

## F2518 (iter None, Grade B)
**[evidence_gap] No evidence chain provided at all. The build result claims the bare import at line 1489 was 'the root cause of 200+ wasted iterations' and 'the probable root cause of infra tasks reaching the builder despite 8+ defense layers all being individually correct.' This is an extraordinary causal claim with zero Grade A or B evidence. There are no stack traces, no reproduction logs, no iteration records showing the import actually failed. The claim could be true, but it could equally be that infra tasks leak through a completely different mechanism (e.g., task selection upstream, KB context re-injection, a different code path that bypasses _build_builder_prompt entirely). Without evidence of the import actually throwing an exception in production, this entire change is a guess.**

[evidence_gap] No evidence chain provided at all. The build result claims the bare import at line 1489 was 'the root cause of 200+ wasted iterations' and 'the probable root cause of infra tasks reaching the builder despite 8+ defense layers all being individually correct.' This is an extraordinary causal claim with zero Grade A or B evidence. There are no stack traces, no reproduction logs, no iteration records showing the import actually failed. The claim could be true, but it could equally be 

---

## F2492 (iter None, Grade B)
**[unfounded_assumption] `gate_or_replace()` is defined in infra_task_gate.py and tested in test_infra_task_gate.py but is NEVER imported or called from any production code (controller.py or otherwise). It is dead code. This suggests either (a) the builder forgot to wire it into the prompt-level safety net mentioned at line 1464-1470, or (b) the change is incomplete.**

[unfounded_assumption] `gate_or_replace()` is defined in infra_task_gate.py and tested in test_infra_task_gate.py but is NEVER imported or called from any production code (controller.py or otherwise). It is dead code. This suggests either (a) the builder forgot to wire it into the prompt-level safety net mentioned at line 1464-1470, or (b) the change is incomplete.

---

## F2307 (iter None, Grade B)
**[regression_risk] Circular import risk during bootstrap: `agent/__init__.py` line 190 calls `_bootstrap_validate()` which invokes `preflight_check()` → `_check_src_modules()` → `importlib.import_module('agent.harmony_layer')` (and 4 other agent submodules) WHILE `agent/__init__.py` is still executing. Python will see `agent` as a partially-initialized module in `sys.modules`. If any agent submodule (harmony_layer, sandbox, prompts, blueprint_generator, geometry_prompts) has top-level code that accesses attributes set later in `agent/__init__` or triggers re-import of the agent package in a way that expects it to be fully initialized, this will produce opaque `AttributeError` or `ImportError` at import time — the exact class of bug this change claims to fix. No evidence that all 5 agent submodules were audited for compatibility with a partially-initialized parent package.**

[regression_risk] Circular import risk during bootstrap: `agent/__init__.py` line 190 calls `_bootstrap_validate()` which invokes `preflight_check()` → `_check_src_modules()` → `importlib.import_module('agent.harmony_layer')` (and 4 other agent submodules) WHILE `agent/__init__.py` is still executing. Python will see `agent` as a partially-initialized module in `sys.modules`. If any agent submodule (harmony_layer, sandbox, prompts, blueprint_generator, geometry_prompts) has top-level code th

---

## F2222 (iter None, Grade B)
**[logical_inconsistency] import_guard._SRC_MODULES only checks the 7 `from src.*` imports (lines 47-53 of deep_researcher.py) but does NOT check the 4 `from agent.*` imports (lines 33-45: agent.harmony_layer, agent.sandbox, agent.geometry_prompts, agent.blueprint_generator). If any of these agent/ modules fail to import (e.g., missing dependency or path issue), preflight will report all_ok=True but the actual DeepResearcher import will still crash with ModuleNotFoundError. The stated goal — 'structured diagnostics instead of opaque ModuleNotFoundError' — is only partially achieved.**

[logical_inconsistency] import_guard._SRC_MODULES only checks the 7 `from src.*` imports (lines 47-53 of deep_researcher.py) but does NOT check the 4 `from agent.*` imports (lines 33-45: agent.harmony_layer, agent.sandbox, agent.geometry_prompts, agent.blueprint_generator). If any of these agent/ modules fail to import (e.g., missing dependency or path issue), preflight will report all_ok=True but the actual DeepResearcher import will still crash with ModuleNotFoundError. The stated goal — 'st

---

## F2078 (iter None, Grade B)
**[regression_risk] _filter_suppressed_candidates (controller.py:1106-1176) imports from task_sanitizer with NO try/except fallback, unlike the parallel guards in parse_iteration.py (lines 127-143) and build_mega_prompt.py (lines 55-74) which both have fail-closed inline fallbacks. If task_sanitizer import fails (e.g., circular import, missing dependency in Kaggle environment), every iteration will throw an exception inside _gather_candidates(), consuming consecutive_failures budget (5 failures = halt). The other two guards survive this scenario; the controller guard does not.**

[regression_risk] _filter_suppressed_candidates (controller.py:1106-1176) imports from task_sanitizer with NO try/except fallback, unlike the parallel guards in parse_iteration.py (lines 127-143) and build_mega_prompt.py (lines 55-74) which both have fail-closed inline fallbacks. If task_sanitizer import fails (e.g., circular import, missing dependency in Kaggle environment), every iteration will throw an exception inside _gather_candidates(), consuming consecutive_failures budget (5 failures = 

---

## F2036 (iter None, Grade B)
**[unfounded_assumption] The change assumes REPO_ROOT / 'data' / 'agent_state.json' is always the correct state file path when called from build_mega_prompt.py (line 55). REPO_ROOT is derived from __file__.parent.parent, which depends on the script's filesystem location. In the Kaggle Docker environment, the script may be at a different path than during development, causing the circuit breaker marker and cumulative counter to be written to the wrong directory or a non-existent path.**

[unfounded_assumption] The change assumes REPO_ROOT / 'data' / 'agent_state.json' is always the correct state file path when called from build_mega_prompt.py (line 55). REPO_ROOT is derived from __file__.parent.parent, which depends on the script's filesystem location. In the Kaggle Docker environment, the script may be at a different path than during development, causing the circuit breaker marker and cumulative counter to be written to the wrong directory or a non-existent path.

---

## F2035 (iter None, Grade B)
**[regression_risk] build_mega_prompt.py::load_task() only catches ImportError (line 57), not other exceptions from sanitize_task_text(). While _load_approach_history internally handles json.JSONDecodeError/OSError, the _increment_cumulative_count() call (line 416) writes to disk and could raise OSError (e.g., permissions, disk full). An unhandled OSError in the read path would crash prompt generation entirely — a regression from the previous behavior where load_task() always returned a string.**

[regression_risk] build_mega_prompt.py::load_task() only catches ImportError (line 57), not other exceptions from sanitize_task_text(). While _load_approach_history internally handles json.JSONDecodeError/OSError, the _increment_cumulative_count() call (line 416) writes to disk and could raise OSError (e.g., permissions, disk full). An unhandled OSError in the read path would crash prompt generation entirely — a regression from the previous behavior where load_task() always returned a string.

---

## F2015 (iter None, Grade B)
**[logical_inconsistency] finding_id=-1 sentinel is truthy in Python, causing bogus upstream linkage. In research_surfacer.py line 485: `upstream_ids = [flaw_finding_id] if flaw_finding_id else None` — when a deduped flaw with finding_id=-1 is passed to `build_research_prompt()` (line 406 extracts it), -1 is truthy, so `[-1]` is passed as upstream_ids to `register_claim()`. This creates KB findings linked to a nonexistent finding ID -1, corrupting the evidence chain. The sentinel should be None or the downstream truthiness checks need updating.**

[logical_inconsistency] finding_id=-1 sentinel is truthy in Python, causing bogus upstream linkage. In research_surfacer.py line 485: `upstream_ids = [flaw_finding_id] if flaw_finding_id else None` — when a deduped flaw with finding_id=-1 is passed to `build_research_prompt()` (line 406 extracts it), -1 is truthy, so `[-1]` is passed as upstream_ids to `register_claim()`. This creates KB findings linked to a nonexistent finding ID -1, corrupting the evidence chain. The sentinel should be None 

---

## F1978 (iter None, Grade B)
**[regression_risk] Duplicate purge paths create double-purge risk. Both sanitize_task_text() (line 340-341 in task_sanitizer.py) and save_next_task() (line 107-108 in parse_iteration.py) independently trigger purge_stagnant_history() on the same state file for the same task. If both code paths execute in the same iteration (write-side guard in parse_iteration then read-side in build_mega_prompt), the second purge is a no-op but performs an unnecessary full file read-write cycle. More critically, if the ordering changes or a third caller is added, the keep_last=2 guarantee could be violated across multiple purge calls.**

[regression_risk] Duplicate purge paths create double-purge risk. Both sanitize_task_text() (line 340-341 in task_sanitizer.py) and save_next_task() (line 107-108 in parse_iteration.py) independently trigger purge_stagnant_history() on the same state file for the same task. If both code paths execute in the same iteration (write-side guard in parse_iteration then read-side in build_mega_prompt), the second purge is a no-op but performs an unnecessary full file read-write cycle. More critically, 

---

## F1906 (iter None, Grade B)
**[logical_inconsistency] The change claims to fix the '0% clean trace rate' by downgrading MALFORMED_TOOL_CALL and PSEUDO_VERIFICATION to severity 2 (below the is_clean threshold of 3). However, answer_selector.py _flaw_penalty() at line 138 checks flaw CODES by set membership, not severity. MALFORMED_TOOL_CALL is in _MAJOR_FLAW_CODES (line 123-130), so ANY Harmony trace with this code still receives a 0.25x penalty regardless of the severity downgrade. The downgrade changes is_clean reporting but does NOT change the answer selection weight penalty. The stated fix may be cosmetic rather than functional for the critical path (answer aggregation).**

[logical_inconsistency] The change claims to fix the '0% clean trace rate' by downgrading MALFORMED_TOOL_CALL and PSEUDO_VERIFICATION to severity 2 (below the is_clean threshold of 3). However, answer_selector.py _flaw_penalty() at line 138 checks flaw CODES by set membership, not severity. MALFORMED_TOOL_CALL is in _MAJOR_FLAW_CODES (line 123-130), so ANY Harmony trace with this code still receives a 0.25x penalty regardless of the severity downgrade. The downgrade changes is_clean reporting bu

---

## F1901 (iter None, Grade B)
**[regression_risk] SamplingConfig.from_bayesian_params() (line 121-139) does NOT handle FileNotFoundError — it will raise if the path doesn't exist. This is inconsistent with TemperatureScheduler.from_bayesian_params() which gracefully falls back. If any caller passes a bad path to SamplingConfig.from_bayesian_params(), it will crash rather than degrade gracefully — a potential runtime failure on Kaggle if the configs directory structure differs.**

[regression_risk] SamplingConfig.from_bayesian_params() (line 121-139) does NOT handle FileNotFoundError — it will raise if the path doesn't exist. This is inconsistent with TemperatureScheduler.from_bayesian_params() which gracefully falls back. If any caller passes a bad path to SamplingConfig.from_bayesian_params(), it will crash rather than degrade gracefully — a potential runtime failure on Kaggle if the configs directory structure differs.

---

