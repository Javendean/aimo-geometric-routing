---
phase: 17-geometric-intelligence
plan: 02
subsystem: agent
tags: [lane-separation, diminishing-returns, feature-grouping, exploration-ordering, system-interference, facade]

# Dependency graph
requires:
  - phase: 17-geometric-intelligence/01
    provides: AblationCell, AblationMatrix, InterferencePair, DiminishingReturns, FeatureExplorationOrder frozen dataclasses; compute_synergy, build_ablation_matrix, detect_interference, store_interference_finding functions
  - phase: 15-research-surfacing
    provides: ResearchSurfacer, KNOWN_COMPONENTS, InteractionType for facade integration
  - phase: 13-evidence-discipline
    provides: EvidenceTracker with register_claim for KB persistence
provides:
  - LANE_TEMPLATE with 4 isolated prompt sections (ANALYSIS, STRATEGY, CODE, EXTRACTION)
  - generate_lane_separated_prompt function for instruction-isolated prompts
  - detect_diminishing_returns using np.polyfit linear regression on sliding window
  - FEATURE_GROUPS taxonomy mapping all 15 KNOWN_COMPONENTS to 4 functional groups
  - classify_features function with reasoning_modifier default for unknowns
  - suggest_exploration_order with cross-group-first prioritization and measured pair filtering
  - detect_system_interference via 2x median duration threshold
  - GeometricIntelligence facade composing KB + ResearchSurfacer with analyze_iteration and get_interference_pairs
affects: [controller, research-loop, agent-loop]

# Tech tracking
tech-stack:
  added: []
  patterns: [lane-separated-prompting, linear-regression-diminishing-returns, cross-group-exploration-priority, duration-anomaly-detection]

key-files:
  created: []
  modified:
    - src/agent/geometric_intelligence.py
    - tests/test_geometric_intelligence.py

key-decisions:
  - "Lane template uses format placeholders with 4 strictly isolated sections -- no cross-lane instruction mixing"
  - "np.polyfit degree-1 regression for diminishing returns slope detection with configurable window and threshold"
  - "FEATURE_GROUPS maps all 15 KNOWN_COMPONENTS: 3 reasoning, 5 selection, 2 verification, 5 sampling"
  - "Cross-group pairs prioritized over within-group for maximum information gain in exploration"
  - "System interference uses 2x median duration threshold with reward floor guard to avoid false positives on hard problems"
  - "GeometricIntelligence facade uses composition (KB + ResearchSurfacer) consistent with Phase 15 pattern"

patterns-established:
  - "Lane-separated prompting: each section has isolated instructions to reduce cross-lane interference"
  - "Feature group taxonomy: reasoning/selection/verification/sampling modifier classification"
  - "Cross-group exploration priority: different-group pairs before same-group pairs"
  - "Duration anomaly detection: 2x median with reward floor guard"

requirements-completed: [GEO-03, GEO-04, GEO-05]

# Metrics
duration: 4min
completed: 2026-03-26
---

# Phase 17 Plan 02: Lane Separation + Feature Grouping + GeometricIntelligence Facade Summary

**Lane-separated 4-section prompting, np.polyfit diminishing returns detection, 15-component feature taxonomy with cross-group exploration priority, and GeometricIntelligence facade composing all signals**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-26T21:16:07Z
- **Completed:** 2026-03-26T21:20:57Z
- **Tasks:** 2 (both TDD: RED + GREEN)
- **Files modified:** 2

## Accomplishments
- Lane-separated prompt generator with 4 isolated sections (ANALYSIS, STRATEGY, CODE, EXTRACTION) preventing cross-lane instruction interference
- Diminishing returns detector using degree-1 polynomial regression on configurable sliding window with negative slope threshold
- Feature taxonomy classifying all 15 KNOWN_COMPONENTS into 4 functional groups (reasoning, selection, verification, sampling)
- Exploration ordering that prioritizes cross-group pairs for maximum information gain and filters already-measured pairs
- System interference detection flagging routing overhead via 2x median duration with reward floor guard
- GeometricIntelligence facade composing KB + ResearchSurfacer and orchestrating all analysis signals
- All 5 GEO requirements (GEO-01 through GEO-05) now implemented across Plans 01 and 02

## Task Commits

Each task was committed atomically (TDD):

1. **Task 1 RED: Lane separation + diminishing returns tests** - `07a435c` (test)
2. **Task 1 GREEN: Lane separation + diminishing returns implementation** - `f0d394c` (feat)
3. **Task 2 RED: Feature grouping + exploration + interference + facade tests** - `1803edf` (test)
4. **Task 2 GREEN: Feature grouping + exploration + interference + facade implementation** - `cd0caba` (feat)

## Files Created/Modified
- `src/agent/geometric_intelligence.py` - Extended with LANE_TEMPLATE, generate_lane_separated_prompt, detect_diminishing_returns, FEATURE_GROUPS, classify_features, suggest_exploration_order, detect_system_interference, GeometricIntelligence class
- `tests/test_geometric_intelligence.py` - Extended from 15 to 29 tests: lane separation (3), diminishing returns (4), feature grouping (2), exploration ordering (2), system interference (1), facade (2)

## Decisions Made
- Lane template uses Python string format placeholders with 4 strictly isolated sections -- validated by test_lane_isolation asserting no cross-lane markers
- np.polyfit degree-1 polynomial fit chosen for diminishing returns (simple, interpretable, matches D-12 spec from RESEARCH.md)
- FEATURE_GROUPS taxonomy follows RESEARCH.md lines 328-348 exactly: 3 reasoning, 5 selection, 2 verification, 5 sampling modifiers
- Unknown features default to reasoning_modifier (safe default -- reasoning is the broadest category)
- System interference threshold at 2x median duration with reward floor guard prevents false positives from genuinely hard problems
- GeometricIntelligence facade uses TYPE_CHECKING imports for KB and ResearchSurfacer (consistent with Pitfall 6 from RESEARCH.md)
- Best-effort measured pair extraction from KB interference findings in analyze_iteration (graceful degradation if KB has no data)

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None -- no external service configuration required.

## Known Stubs

None -- all functions are fully implemented with no placeholder logic.

## Next Phase Readiness
- Phase 17 complete -- all 5 GEO requirements implemented across Plans 01 and 02
- GeometricIntelligence facade ready for controller integration (Phase 16 controller can import and call analyze_iteration)
- All 29 module tests pass; full suite 1035 passed with only 3 pre-existing failures
- This is the FINAL plan of the FINAL phase -- v2.0 milestone complete

## Self-Check: PASSED

- [x] src/agent/geometric_intelligence.py exists
- [x] tests/test_geometric_intelligence.py exists
- [x] 17-02-SUMMARY.md exists
- [x] Commit 07a435c (Task 1 RED) verified
- [x] Commit f0d394c (Task 1 GREEN) verified
- [x] Commit 1803edf (Task 2 RED) verified
- [x] Commit cd0caba (Task 2 GREEN) verified

---
*Phase: 17-geometric-intelligence*
*Completed: 2026-03-26*
