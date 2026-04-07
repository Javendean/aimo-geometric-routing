# Two-Attempt Strategy Analysis

AIMO 3 allows two answer attempts per problem: primary and secondary.

## Current Implementation

The hybrid notebook submits:
- Primary: majority vote across N samples
- Secondary: second-most-common answer (if different from primary)

## Open Questions

### 1. Routing diversity vs answer hedging

**Option A (routing diversity):**
- Attempt 1: topic-routed prompt (specialized strategy per problem type)
- Attempt 2: generic baseline prompt (T=1.0, N=8, no routing)
- Rationale: if routing helps, attempt 1 wins. If routing hurts, attempt 2 is the baseline.

**Option B (answer hedging):**
- Attempt 1: majority answer from all N samples
- Attempt 2: second-most-common answer
- Rationale: if the majority is wrong, the second-most-common might be right

**Option C (confidence-based):**
- Attempt 1: highest-confidence answer (weighted by verification strength)
- Attempt 2: highest-confidence answer from a DIFFERENT reasoning strategy
- Rationale: diversify reasoning approaches, not just vote counts

### 2. Information theory perspective

Two attempts = 1 bit of additional information capacity per problem.
- Hedging uses this bit for "in case majority is wrong"
- Routing diversity uses this bit for "in case routing is wrong"
- Confidence-based uses this bit for "in case the verification is wrong"

The optimal strategy depends on: where is the current system's error budget dominated? If most errors are from wrong majority votes, hedging helps most. If most errors are from wrong strategy selection, routing diversity helps most.

### 3. GenSelect interaction

NemoSkills GenSelect (76.5% → 93.3% on AIME24) selects the best candidate from N solutions. If GenSelect is the primary selector:
- Attempt 1: GenSelect pick
- Attempt 2: majority vote (as safety net)
- This uses the two-attempt structure as GenSelect-vs-majority A/B test per problem
