# KB Findings on Prompt Perturbation

Total findings: 15

Key question: does prompt perturbation improve accuracy on gpt-oss-120B?

## F2582 (iter None, Grade B)
**[evidence_gap] No evidence chain provided (explicitly stated: 'no evidence chain available'). The arXiv:2502.11027 and 'NVIDIA GenSelect' citations are mentioned inline but have no Grade A/B evidence backing. The claimed '+3-5 point improvement from diverse prompting' cannot be verified. Additionally, since user-prompt perturbation is ALREADY active in deep_researcher.py, the cited improvement likely applies to the FROM-ZERO baseline, not the current partially-diverse state.**

[evidence_gap] No evidence chain provided (explicitly stated: 'no evidence chain available'). The arXiv:2502.11027 and 'NVIDIA GenSelect' citations are mentioned inline but have no Grade A/B evidence backing. The claimed '+3-5 point improvement from diverse prompting' cannot be verified. Additionally, since user-prompt perturbation is ALREADY active in deep_researcher.py, the cited improvement lik

---

## F2581 (iter None, Grade B)
**[unfounded_assumption] The DiverseCandidateGenerator duplicates perturbation scheduling logic that TopicAwareSamplingPlan.perturbation_schedule() already handles, AND duplicates the prompt construction that deep_researcher.py already does with apply_user_perturbation(). When this IS eventually wired in, it will conflict with deep_researcher.py's existing perturbation application (lines 2035-2049). The integration path is not documented — will deep_researcher stop calling apply_user_perturbation directly, or will perturbations be applied twice?**

[unfounded_assumption] The DiverseCandidateGenerator duplicates perturbation scheduling logic that TopicAwareSamplingPlan.perturbation_schedule() already handles, AND duplicates the prompt construction that deep_researcher.py already does with apply_user_perturbation(). When this IS eventually wired in, it will conflict with deep_researcher.py's existing perturbation application (lines 2035-2049).

---

## F2579 (iter None, Grade B)
**[logical_inconsistency] Evidence chain claim #1 is FALSE: 'prompt_perturbation.py — 6 orthogonal prompt variants defined, zero callers outside self.' In reality, deep_researcher.py already imports and actively calls apply_user_perturbation() and get_perturbation() at lines 2035-2049. User prompts ARE already being perturbed per-attempt via round-robin. The actual gap is narrower than claimed: only temperature diversity and system-prompt perturbation are missing. This means the stated +3-5 point improvement from 'diverse prompting' is partially already captured, and the incremental gain from this change is overstated.**

[logical_inconsistency] Evidence chain claim #1 is FALSE: 'prompt_perturbation.py — 6 orthogonal prompt variants defined, zero callers outside self.' In reality, deep_researcher.py already imports and actively calls apply_user_perturbation() and get_perturbation() at lines 2035-2049. User prompts ARE already being perturbed per-attempt via round-robin. The actual gap is narrower than claimed: on

---

## F2570 (iter None, Grade B)
**[unfounded_assumption] The _MIN_TOPIC_CONFIDENCE threshold of 0.3 (line 73) and the perturbation biasing threshold of 0.5 (line 161) are magic numbers with no empirical basis. The test for low-confidence fallback (test_ambiguous_problem_uses_defaults, line 185) depends on 'Solve the problem.' producing confidence < 0.3, which is an implementation detail of the regex classifier — if the classifier is ever improved, this test becomes fragile.**

[unfounded_assumption] The _MIN_TOPIC_CONFIDENCE threshold of 0.3 (line 73) and the perturbation biasing threshold of 0.5 (line 161) are magic numbers with no empirical basis. The test for low-confidence fallback (test_ambiguous_problem_uses_defaults, line 185) depends on 'Solve the problem.' producing confidence < 0.3, which is an implementation detail of the regex classifier — if the classifie

---

## F2567 (iter None, Grade B)
**[logical_inconsistency] The module is described as 'bridging' TopicClassifier → SamplingStrategy, but it does NOT actually integrate with SamplingStrategy or SamplingConfig. It produces its own TopicAwareSamplingPlan with its own temperature_schedule() and perturbation_schedule() methods that are completely independent of, and potentially conflicting with, the existing SamplingStrategy._build_schedule(). The 'bridge' creates a THIRD scheduling system rather than modifying or extending the existing one.**

[logical_inconsistency] The module is described as 'bridging' TopicClassifier → SamplingStrategy, but it does NOT actually integrate with SamplingStrategy or SamplingConfig. It produces its own TopicAwareSamplingPlan with its own temperature_schedule() and perturbation_schedule() methods that are completely independent of, and potentially conflicting with, the existing SamplingStrategy._build_sc

---

## F2566 (iter None, Grade B)
**[unfounded_assumption] The _TOPIC_LEAD_PERTURBATION mapping (lines 54-59) assumes 'adversarial_framing' is optimal for combinatorics, 'tool_emphasis' for geometry, etc. These are identical to the pre-existing _TOPIC_PERTURBATION in topic_classifier.py (lines 44-49). No evidence supports these pairings — they are hunches copied from a module that was itself never validated in production.**

[unfounded_assumption] The _TOPIC_LEAD_PERTURBATION mapping (lines 54-59) assumes 'adversarial_framing' is optimal for combinatorics, 'tool_emphasis' for geometry, etc. These are identical to the pre-existing _TOPIC_PERTURBATION in topic_classifier.py (lines 44-49). No evidence supports these pairings — they are hunches copied from a module that was itself never validated in production.

---

## F1894 (iter None, Grade B)
**[regression_risk] The tests (test_prompt_perturbation_wiring.py) verify wiring via source code string matching (e.g., 'apply_user_perturbation(generate_prompt' in source_code). These are fragile tests that will break on any variable rename or formatting change. This is a maintenance risk, not a correctness risk.**

[regression_risk] The tests (test_prompt_perturbation_wiring.py) verify wiring via source code string matching (e.g., 'apply_user_perturbation(generate_prompt' in source_code). These are fragile tests that will break on any variable rename or formatting change. This is a maintenance risk, not a correctness risk.

---

## F1893 (iter None, Grade B)
**[unfounded_assumption] The perturbation engine assumes orthogonality between variants improves diversity. However, some variants may actively harm performance on specific problem types. For example, 'tool_emphasis' forces code verification on every step — for pure combinatorics/number theory problems where code enumeration is infeasible, this could waste the model's token budget on failed code attempts. No per-variant accuracy analysis was conducted.**

[unfounded_assumption] The perturbation engine assumes orthogonality between variants improves diversity. However, some variants may actively harm performance on specific problem types. For example, 'tool_emphasis' forces code verification on every step — for pure combinatorics/number theory problems where code enumeration is infeasible, this could waste the model's token budget on failed code a

---

## F1891 (iter None, Grade B)
**[regression_risk] In batch mode (non-TIR), all N samples in a wave share the same perturbation. With wave_size=4 and num_samples=16, only 4 distinct perturbations are used across 16 samples (indices 0,1,2,3). This means 2 of the 6 variants are never used, reducing the diversity benefit the feature is designed to provide. The claimed 'different waves get different variants' is true but incomplete — not all variants are exercised.**

[regression_risk] In batch mode (non-TIR), all N samples in a wave share the same perturbation. With wave_size=4 and num_samples=16, only 4 distinct perturbations are used across 16 samples (indices 0,1,2,3). This means 2 of the 6 variants are never used, reducing the diversity benefit the feature is designed to provide. The claimed 'different waves get different variants' is true but incomplete �

---

## F1890 (iter None, Grade B)
**[unfounded_assumption] The perturbation is applied to the user prompt, not the system prompt, per the design decision 'to minimize changes to the Harmony conversation builder.' But the module docstring (line 8-9) says variants are 'orthogonal system-prompt overlays.' The system_overlay field exists on every PromptPerturbation but is never used — only user_prefix is applied. If the system_overlay was designed as the primary mechanism, using only user_prefix may produce weaker diversity than intended.**

[unfounded_assumption] The perturbation is applied to the user prompt, not the system prompt, per the design decision 'to minimize changes to the Harmony conversation builder.' But the module docstring (line 8-9) says variants are 'orthogonal system-prompt overlays.' The system_overlay field exists on every PromptPerturbation but is never used — only user_prefix is applied. If the system_overlay

---

## F1889 (iter None, Grade B)
**[regression_risk] Perturbation prefixes add 15-80 tokens to every user prompt (e.g., '[Expert Mode] As an experienced olympiad problem setter...'). On a 32K context window with max_generate_tokens already set high, this prefix consumes reasoning budget. For hard problems near the token limit, this could truncate the model's actual solution trace. No evidence that token budget impact was measured.**

[regression_risk] Perturbation prefixes add 15-80 tokens to every user prompt (e.g., '[Expert Mode] As an experienced olympiad problem setter...'). On a 32K context window with max_generate_tokens already set high, this prefix consumes reasoning budget. For hard problems near the token limit, this could truncate the model's actual solution trace. No evidence that token budget impact was measured.

---

## F1888 (iter None, Grade B)
**[evidence_gap] No evidence chain was provided. The build result cites arXiv:2502.11027 and 'NVIDIA AIMO2 GenSelect' for the +3-5 point claim, but no Grade A/B evidence links were supplied for review. The entire change is motivated by an unverifiable performance claim. Without measurement gate results showing this perturbation actually improves pass@k on the AIMO3 problem distribution with gpt-oss-120B, the change could be net-negative.**

[evidence_gap] No evidence chain was provided. The build result cites arXiv:2502.11027 and 'NVIDIA AIMO2 GenSelect' for the +3-5 point claim, but no Grade A/B evidence links were supplied for review. The entire change is motivated by an unverifiable performance claim. Without measurement gate results showing this perturbation actually improves pass@k on the AIMO3 problem distribution with gpt-oss-

---

## F777 (iter None, Grade B)
**[unfounded_assumption] The claim 'All 3 provably live — no_selector produces distinct behavior vs baseline' is not enforced by a hard-fail assertion in notebook_validation.py. The _assert_dead_effect() function (lines 446-448) explicitly excludes NO_SELECTOR — it only checks NO_PERTURBATION and NO_MULTI_TEMP. Selector liveness is deferred to compare_modes() in forensic_closeout.py, which is a separate code path. The weight schedule makes it *likely* the selector lever is live, but the validation module itself does not hard-fail on selector collapse — only on weight uniformity (line 376). Weight variance ≠ different final answer.**

[unfounded_assumption] The claim 'All 3 provably live — no_selector produces distinct behavior vs baseline' is not enforced by a hard-fail assertion in notebook_validation.py. The _assert_dead_effect() function (lines 446-448) explicitly excludes NO_SELECTOR — it only checks NO_PERTURBATION and NO_MULTI_TEMP. Selector liveness is deferred to compare_modes() in forensic_closeout.py, which is a 

---

## F759 (iter None, Grade B)
**[logical_inconsistency] The validation gate (notebook_validation.py) does NOT test the actual solver pipeline. simulate_mode_for_problem() (lines 215-324) calls a mock answer_fn — it never invokes InferenceEngine, the real prompt perturbation application, the real answer selector, or any real solver code path. The module docstring (lines 1-7) claims it 'executes the solver pipeline under four ablation modes' but it simulates a synthetic pipeline. This means the validation gate can pass with flying colors while the real notebook has dead-effect wiring bugs. The stated intent ('proving solver levers are live end-to-end') contradicts the implementation (pure mock simulation).**

[logical_inconsistency] The validation gate (notebook_validation.py) does NOT test the actual solver pipeline. simulate_mode_for_problem() (lines 215-324) calls a mock answer_fn — it never invokes InferenceEngine, the real prompt perturbation application, the real answer selector, or any real solver code path. The module docstring (lines 1-7) claims it 'executes the solver pipeline under four ab

---

## F752 (iter None, Grade B)
**[unfounded_assumption] The module assumes get_perturbation(i) for i in range(num_samples) will produce >= 2 distinct .key values when num_samples >= 2. If prompt_perturbation.py has N_VARIANTS=1 or all variants have the same key, the ALL_LEVERS assertion would fail at runtime for reasons outside this module's control. N_VARIANTS is imported but never checked against min_distinct_variants.**

[unfounded_assumption] The module assumes get_perturbation(i) for i in range(num_samples) will produce >= 2 distinct .key values when num_samples >= 2. If prompt_perturbation.py has N_VARIANTS=1 or all variants have the same key, the ALL_LEVERS assertion would fail at runtime for reasons outside this module's control. N_VARIANTS is imported but never checked against min_distinct_variants.

---

