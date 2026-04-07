---
phase: 17-geometric-intelligence
plan: 01
subsystem: agent
tags: [ablation, synergy, bliss-independence, interference-detection, frozen-dataclass]

# Dependency graph
requires:
  - phase: 13-evidence-discipline
    provides: EvidenceTracker with register_claim for KB persistence
  - phase: 15-research-surfacing
    provides: InteractionMatrix, InteractionType, KNOWN_COMPONENTS for integration
provides:
  - AblationCell, AblationMatrix, InterferencePair, DiminishingReturns, FeatureExplorationOrder frozen dataclasses
  - compute_synergy function (Bliss independence formula)
  - build_ablation_matrix with partial data support and pair normalization
  - detect_interference with threshold-based flagging and weaker feature identification
  - store_interference_finding for Grade A KB persistence
affects: [17-02-PLAN, controller, research-loop]

# Tech tracking
tech-stack:
  added: []
  patterns: [bliss-independence-synergy, sorted-pair-normalization, partial-data-ablation]

key-files:
  created:
    - src/agent/geometric_intelligence.py
    - tests/test_geometric_intelligence.py
  modified: []

key-decisions:
  - "Bliss independence formula for synergy: acc_both - acc_a - acc_b + baseline (standard drug interaction model)"
  - "Sorted pair normalization prevents A-B vs B-A duplicates (consistent with Phase 15 InteractionMatrix)"
  - "Synergy score None when any measurement missing -- partial data never produces false signals"
  - "Weaker feature = lower individual accuracy (acc_a_only vs acc_b_only) for interference pair recommendation"

patterns-established:
  - "Bliss independence synergy: positive=synergistic, zero=independent, negative=interference"
  - "TYPE_CHECKING guards for cross-module imports to prevent circular dependencies"
  - "Frozen dataclass type contracts defined in Plan 01, consumed by Plan 02"

requirements-completed: [GEO-01, GEO-02]

# Metrics
duration: 3min
completed: 2026-03-26
---

# Phase 17 Plan 01: Type Contracts + Ablation Matrix Summary

**Bliss independence synergy computation with pairwise ablation matrix, interference detection flagging pairs below -0.02 threshold, and Grade A KB persistence**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-26T21:11:05Z
- **Completed:** 2026-03-26T21:14:00Z
- **Tasks:** 1 (TDD: RED + GREEN)
- **Files created:** 2

## Accomplishments
- 5 frozen dataclasses establishing complete type system for Phase 17 geometric intelligence
- Bliss independence synergy formula correctly computes independent (0.0), synergistic (positive), and interference (negative) scores
- Ablation matrix handles partial measurement data gracefully -- None synergy when any of 4 values missing
- Interference detection flags pairs below configurable threshold with weaker feature identified by lower individual accuracy
- Grade A interference findings persisted to KB with "interference" tag for downstream consumption

## Task Commits

Each task was committed atomically (TDD):

1. **Task 1 RED: Failing tests** - `e82f067` (test)
2. **Task 1 GREEN: Implementation** - `341f4bc` (feat)

## Files Created/Modified
- `src/agent/geometric_intelligence.py` - Core module: 5 frozen dataclasses + 4 functions (compute_synergy, build_ablation_matrix, detect_interference, store_interference_finding)
- `tests/test_geometric_intelligence.py` - 15 tests: type contracts (5), synergy computation (3), ablation matrix (3), interference detection (3), KB persistence (1)

## Decisions Made
- Bliss independence formula (standard drug interaction model) chosen for synergy computation -- well-established, interpretable, matches D-04 spec
- Sorted pair normalization via `tuple(sorted(pair))` -- consistent with Phase 15 InteractionMatrix convention
- None synergy score for incomplete measurements rather than imputing -- avoids false positives per D-05
- Weaker feature identified by lower `accuracy_a_only` vs `accuracy_b_only` -- simple, interpretable per D-07
- TYPE_CHECKING guards for EvidenceTracker and ResearchSurfacer imports -- prevents circular dependency at runtime per Pitfall 6

## Deviations from Plan

None -- plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None -- no external service configuration required.

## Known Stubs

None -- all functions are fully implemented with no placeholder logic.

## Next Phase Readiness
- All 5 type contracts ready for Plan 02 (diminishing returns detection, exploration ordering, MCTS integration)
- InterferencePair and AblationMatrix ready for controller integration
- store_interference_finding tested with in-memory KB -- production KB path unchanged

## Self-Check: PASSED

- [x] src/agent/geometric_intelligence.py exists
- [x] tests/test_geometric_intelligence.py exists
- [x] 17-01-SUMMARY.md exists
- [x] Commit e82f067 (RED) verified
- [x] Commit 341f4bc (GREEN) verified

---
*Phase: 17-geometric-intelligence*
*Completed: 2026-03-26*
