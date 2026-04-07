"""Geometric intelligence for pairwise feature ablation and interference detection.

Provides frozen dataclasses (type contracts) for ablation analysis and functions
to compute synergy scores via the Bliss independence formula, build ablation
matrices from partial measurement data, detect destructive interference between
feature pairs, and persist interference findings to the knowledge base.

This module is the foundation for Phase 17 -- all other geometric intelligence
capabilities (diminishing returns detection, exploration ordering, MCTS
integration) build on these types and functions.

Usage:
    from src.agent.geometric_intelligence import (
        AblationCell, AblationMatrix, InterferencePair,
        compute_synergy, build_ablation_matrix, detect_interference,
        store_interference_finding,
    )

    synergy = compute_synergy(acc_both=0.8, acc_a=0.6, acc_b=0.5, acc_baseline=0.3)
    matrix = build_ablation_matrix(feature_results, baseline_accuracy=0.3)
    pairs = detect_interference(matrix.cells, threshold=-0.02)
"""

from __future__ import annotations

import statistics
from itertools import combinations

import numpy as np
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agent.evidence_tracker import EvidenceTracker
    from src.agent.knowledge_base import KnowledgeBase
    from src.agent.research_surfacer import (
        InteractionMatrix,
        InteractionType,
        ResearchSurfacer,
    )


# ---------------------------------------------------------------------------
# Frozen dataclasses -- type contracts for Phase 17
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AblationCell:
    """Single pairwise ablation measurement between two features.

    Stores the four accuracy values needed for Bliss independence synergy
    computation, plus the computed synergy score (None if any measurement
    is missing).

    Attributes:
        feature_a: First feature name (sorted order).
        feature_b: Second feature name (sorted order).
        accuracy_with_both: Accuracy when both features are active.
        accuracy_a_only: Accuracy when only feature A is active.
        accuracy_b_only: Accuracy when only feature B is active.
        accuracy_neither: Accuracy when neither feature is active (baseline).
        synergy_score: Bliss independence score (None if incomplete data).
        sample_count: Number of samples used for this measurement.
    """

    feature_a: str
    feature_b: str
    accuracy_with_both: float | None
    accuracy_a_only: float | None
    accuracy_b_only: float | None
    accuracy_neither: float | None
    synergy_score: float | None
    sample_count: int


@dataclass(frozen=True)
class AblationMatrix:
    """Collection of pairwise ablation measurements.

    Only measured pairs are populated -- no exhaustive N*(N-1)/2 generation.

    Attributes:
        cells: Tuple of measured ablation cells.
        baseline_accuracy: Overall baseline accuracy (neither feature active).
        last_updated: ISO timestamp of last matrix update.
        finding_id: KB finding ID where this matrix is stored (None if unsaved).
    """

    cells: tuple[AblationCell, ...]
    baseline_accuracy: float | None
    last_updated: str
    finding_id: int | None


@dataclass(frozen=True)
class InterferencePair:
    """A detected destructive interference between two features.

    Attributes:
        feature_a: First feature name.
        feature_b: Second feature name.
        synergy_score: Negative synergy score indicating interference.
        weaker_feature: The feature with lower individual accuracy.
        individual_accuracy_a: Accuracy of feature A alone.
        individual_accuracy_b: Accuracy of feature B alone.
    """

    feature_a: str
    feature_b: str
    synergy_score: float
    weaker_feature: str
    individual_accuracy_a: float
    individual_accuracy_b: float


@dataclass(frozen=True)
class DiminishingReturns:
    """Detection result for diminishing returns in iteration progress.

    Attributes:
        detected: Whether diminishing returns were detected.
        slope: Linear regression slope of recent accuracy changes.
        window_size: Number of recent iterations analyzed.
        recommendation: Actionable recommendation based on detection.
    """

    detected: bool
    slope: float
    window_size: int
    recommendation: str


@dataclass(frozen=True)
class FeatureExplorationOrder:
    """Prioritized ordering for feature pair exploration.

    Cross-group pairs (features from different functional groups) are
    prioritized over within-group pairs for maximum information gain.

    Attributes:
        cross_group_pairs: Tuples of (feature_a, feature_b) across groups.
        within_group_pairs: Tuples of (feature_a, feature_b) within groups.
    """

    cross_group_pairs: tuple[tuple[str, str], ...]
    within_group_pairs: tuple[tuple[str, str], ...]


# ---------------------------------------------------------------------------
# Synergy computation -- Bliss independence formula
# ---------------------------------------------------------------------------


def compute_synergy(
    acc_both: float,
    acc_a_only: float,
    acc_b_only: float,
    acc_baseline: float,
) -> float:
    """Compute synergy score using the Bliss independence formula.

    Formula: acc_both - acc_a_only - acc_b_only + acc_baseline

    Returns:
        Positive = synergistic (features enhance each other).
        Zero = independent (no interaction).
        Negative = interference (features degrade each other).
    """
    return acc_both - acc_a_only - acc_b_only + acc_baseline


# ---------------------------------------------------------------------------
# Ablation matrix construction
# ---------------------------------------------------------------------------


def build_ablation_matrix(
    feature_results: dict[tuple[str, str], dict[str, float | None]],
    baseline_accuracy: float | None,
) -> AblationMatrix:
    """Build an ablation matrix from partial measurement results.

    Args:
        feature_results: Dict keyed by (feature_a, feature_b) tuples. Each
            value is a dict with keys "both", "a_only", "b_only", "neither"
            mapping to accuracy floats (or None if unmeasured). Pairs are
            normalized via sorted() so (b, a) and (a, b) are equivalent.
        baseline_accuracy: Overall baseline accuracy when no features active.

    Returns:
        AblationMatrix with cells for each provided pair. Synergy scores
        are computed only when all 4 accuracy values are present (D-05).
    """
    cells: list[AblationCell] = []

    for pair, measurements in feature_results.items():
        # Normalize pair ordering via sorted()
        sorted_pair = tuple(sorted(pair))
        fa, fb = sorted_pair[0], sorted_pair[1]

        acc_both = measurements.get("both")
        acc_a = measurements.get("a_only")
        acc_b = measurements.get("b_only")
        acc_neither = measurements.get("neither")

        # Compute synergy only when all 4 values are present (D-05)
        synergy: float | None = None
        if all(v is not None for v in (acc_both, acc_a, acc_b, acc_neither)):
            synergy = compute_synergy(
                acc_both,  # type: ignore[arg-type]
                acc_a,  # type: ignore[arg-type]
                acc_b,  # type: ignore[arg-type]
                acc_neither,  # type: ignore[arg-type]
            )

        cells.append(
            AblationCell(
                feature_a=fa,
                feature_b=fb,
                accuracy_with_both=acc_both,
                accuracy_a_only=acc_a,
                accuracy_b_only=acc_b,
                accuracy_neither=acc_neither,
                synergy_score=synergy,
                sample_count=0,
            )
        )

    return AblationMatrix(
        cells=tuple(cells),
        baseline_accuracy=baseline_accuracy,
        last_updated=datetime.now(timezone.utc).isoformat(),
        finding_id=None,
    )


# ---------------------------------------------------------------------------
# Interference detection
# ---------------------------------------------------------------------------


def detect_interference(
    cells: tuple[AblationCell, ...],
    threshold: float = -0.02,
) -> list[InterferencePair]:
    """Detect feature pairs with destructive interference (D-06, D-07).

    Filters cells where synergy_score is not None and below the threshold.
    The weaker feature is identified as the one with lower individual accuracy
    (accuracy_a_only vs accuracy_b_only).

    Args:
        cells: Tuple of AblationCell measurements.
        threshold: Synergy score below which interference is flagged.
            Default -0.02.

    Returns:
        List of InterferencePair objects for each detected interference.
    """
    pairs: list[InterferencePair] = []

    for cell in cells:
        if cell.synergy_score is None:
            continue
        if cell.synergy_score >= threshold:
            continue

        # Identify weaker feature by lower individual accuracy (D-07)
        acc_a = cell.accuracy_a_only if cell.accuracy_a_only is not None else 0.0
        acc_b = cell.accuracy_b_only if cell.accuracy_b_only is not None else 0.0
        weaker = cell.feature_b if acc_b <= acc_a else cell.feature_a

        pairs.append(
            InterferencePair(
                feature_a=cell.feature_a,
                feature_b=cell.feature_b,
                synergy_score=cell.synergy_score,
                weaker_feature=weaker,
                individual_accuracy_a=acc_a,
                individual_accuracy_b=acc_b,
            )
        )

    return pairs


# ---------------------------------------------------------------------------
# KB persistence
# ---------------------------------------------------------------------------


def store_interference_finding(
    et: EvidenceTracker,
    pair: InterferencePair,
) -> int:
    """Persist an interference finding to the knowledge base (D-08).

    Calls register_claim with evidence_grade="A" (measured from ablation data),
    risk_level=MEDIUM, and tag="interference".

    Args:
        et: EvidenceTracker instance for claim registration.
        pair: The detected interference pair to store.

    Returns:
        The integer ID of the newly created finding.
    """
    from src.agent.evidence_tracker import RiskLevel

    claim = (
        f"Interference detected between {pair.feature_a} and {pair.feature_b}: "
        f"synergy_score={pair.synergy_score:.4f}. "
        f"Weaker feature: {pair.weaker_feature} "
        f"(acc_a={pair.individual_accuracy_a:.4f}, "
        f"acc_b={pair.individual_accuracy_b:.4f})"
    )

    finding_id = et.register_claim(
        claim=claim,
        evidence_grade="A",
        sources=["ablation_matrix"],
        risk_level=RiskLevel.MEDIUM,
        tags=["interference"],
    )

    return finding_id


# ---------------------------------------------------------------------------
# Prompt lane separation (D-09, D-10)
# ---------------------------------------------------------------------------


LANE_TEMPLATE = """\
[ANALYSIS]
Analyze the following competition math problem. Identify the problem type, \
key constraints, and mathematical domain. Do NOT attempt a solution yet.

Problem: {problem}

{analysis_instructions}

[STRATEGY]
Based on your analysis above, select a solution strategy. Consider: \
{strategy_features}. Output your chosen approach.

{strategy_instructions}

[CODE]
Write Python code implementing your chosen strategy. The code must be \
self-contained, use only standard libraries and sympy.

{code_instructions}

[EXTRACTION]
From the code output above, extract the final numerical answer. \
Apply answer validation rules: {extraction_rules}

{extraction_instructions}
"""


def generate_lane_separated_prompt(
    problem: str,
    features: list[str],
) -> str:
    """Generate a lane-separated prompt with 4 isolated instruction sections (D-09).

    Each lane has its own instruction block with no cross-lane instruction mixing
    (D-10). The problem text is included in the analysis lane.

    Args:
        problem: The math problem statement to solve.
        features: List of enabled feature names (used to populate strategy lane).

    Returns:
        A formatted prompt string with [ANALYSIS], [STRATEGY], [CODE], and
        [EXTRACTION] lane markers.
    """
    feature_list = ", ".join(features) if features else "general mathematical reasoning"

    return LANE_TEMPLATE.format(
        problem=problem,
        analysis_instructions=(
            "Identify: (1) problem type (algebra, geometry, number theory, "
            "combinatorics), (2) key constraints, (3) relevant theorems or formulas."
        ),
        strategy_features=feature_list,
        strategy_instructions=(
            "Select the most promising approach based on your analysis. "
            "Explain why this strategy fits the problem structure."
        ),
        code_instructions=(
            "Implement your chosen strategy as a self-contained Python script. "
            "Use sympy for symbolic computation. Print only the final numerical answer."
        ),
        extraction_rules="integer output, strip whitespace, verify numeric",
        extraction_instructions=(
            "Extract the final numerical answer from the code output. "
            "If multiple values appear, select the one matching the problem constraints."
        ),
    )


# ---------------------------------------------------------------------------
# Diminishing returns detection (D-12, D-13, D-14)
# ---------------------------------------------------------------------------


def detect_diminishing_returns(
    accuracy_gains: list[float],
    window: int = 10,
    threshold: float = 0.01,
) -> DiminishingReturns:
    """Detect diminishing returns via linear regression on marginal gains (D-12).

    Fits a degree-1 polynomial to the last ``window`` accuracy gain values.
    If the slope is negative and its magnitude exceeds ``threshold``, returns
    detected=True with a recommendation to switch to orthogonal exploration.

    Args:
        accuracy_gains: Marginal accuracy gain per iteration/submission.
        window: Number of recent values to analyze.
        threshold: Minimum magnitude of negative slope to trigger detection.

    Returns:
        DiminishingReturns with detection result, slope, window size, and
        actionable recommendation.
    """
    if len(accuracy_gains) < window:
        return DiminishingReturns(
            detected=False,
            slope=0.0,
            window_size=window,
            recommendation="insufficient data",
        )

    recent = accuracy_gains[-window:]
    x = np.arange(len(recent), dtype=float)
    coeffs = np.polyfit(x, recent, 1)  # [slope, intercept]
    slope = float(coeffs[0])

    detected = slope < -threshold
    if detected:
        recommendation = (
            "Diminishing returns detected -- switch to orthogonal exploration "
            "of untested feature combinations"
        )
    else:
        recommendation = "No diminishing returns detected -- continue current strategy"

    return DiminishingReturns(
        detected=detected,
        slope=slope,
        window_size=window,
        recommendation=recommendation,
    )


# ---------------------------------------------------------------------------
# Feature grouping (D-15)
# ---------------------------------------------------------------------------


FEATURE_GROUPS: dict[str, str] = {
    # reasoning_modifier: changes how the model reasons
    "prompt_perturbation": "reasoning_modifier",
    "blueprint_generator": "reasoning_modifier",
    "deep_researcher": "reasoning_modifier",
    # selection_modifier: changes which answer is selected
    "few_shot_selection": "selection_modifier",
    "confidence_scoring": "selection_modifier",
    "answer_extraction": "selection_modifier",
    "consensus_voting": "selection_modifier",
    "code_quality_voting": "selection_modifier",
    # verification_modifier: changes answer verification
    "tir_verification": "verification_modifier",
    "self_verification": "verification_modifier",
    # sampling_modifier: changes how many/which samples are generated
    "multi_temperature": "sampling_modifier",
    "bayesian_controller": "sampling_modifier",
    "adaptive_compute": "sampling_modifier",
    "early_pruning": "sampling_modifier",
    "python_executor": "sampling_modifier",
}


def classify_features(features: list[str]) -> dict[str, str]:
    """Classify features into functional groups (D-15).

    Maps each feature name to one of 4 groups: reasoning_modifier,
    selection_modifier, verification_modifier, sampling_modifier.
    Unknown features default to reasoning_modifier.

    Args:
        features: List of feature name strings.

    Returns:
        Dict mapping each feature name to its group string.
    """
    return {f: FEATURE_GROUPS.get(f, "reasoning_modifier") for f in features}


# ---------------------------------------------------------------------------
# Exploration ordering (D-16)
# ---------------------------------------------------------------------------


def suggest_exploration_order(
    groups: dict[str, str],
    measured_pairs: set[tuple[str, str]],
) -> FeatureExplorationOrder:
    """Return prioritized exploration order: cross-group pairs first (D-16).

    Uses itertools.combinations to enumerate all feature pairs. Normalizes
    via sorted() to prevent A-B vs B-A duplicates. Separates into cross-group
    (groups differ) and within-group (groups same). Filters out already-measured
    pairs.

    Args:
        groups: Dict mapping feature names to their group strings.
        measured_pairs: Set of already-measured (feature_a, feature_b) tuples
            (normalized via sorted()).

    Returns:
        FeatureExplorationOrder with cross_group_pairs before within_group_pairs.
    """
    features = list(groups.keys())
    cross_group: list[tuple[str, str]] = []
    within_group: list[tuple[str, str]] = []

    for a, b in combinations(features, 2):
        pair = tuple(sorted((a, b)))
        if pair in measured_pairs:
            continue
        if groups[a] != groups[b]:
            cross_group.append(pair)
        else:
            within_group.append(pair)

    return FeatureExplorationOrder(
        cross_group_pairs=tuple(cross_group),
        within_group_pairs=tuple(within_group),
    )


# ---------------------------------------------------------------------------
# System interference detection (D-18, D-19, D-20)
# ---------------------------------------------------------------------------


def detect_system_interference(
    iteration_results: list[dict],
) -> list[dict]:
    """Detect routing overhead via duration anomaly detection (D-18, D-19, D-20).

    Flags iterations where duration_seconds > 2 * median(all durations) AND
    submission_reward is not the lowest (meaning slowness is not from a
    hard problem but from system overhead).

    Args:
        iteration_results: List of dicts with keys: "iteration_number" (int),
            "duration_seconds" (float), "task_selected" (str),
            "submission_reward" (float).

    Returns:
        List of dicts with keys: "iteration_number", "type" ("routing_overhead"),
        "evidence" (str), "severity" ("warning").
    """
    if len(iteration_results) < 2:
        return []

    durations = [r["duration_seconds"] for r in iteration_results]
    median_duration = statistics.median(durations)
    min_reward = min(r["submission_reward"] for r in iteration_results)

    findings: list[dict] = []
    for r in iteration_results:
        if (
            r["duration_seconds"] > 2 * median_duration
            and r["submission_reward"] > min_reward
        ):
            findings.append({
                "iteration_number": r["iteration_number"],
                "type": "routing_overhead",
                "evidence": (
                    f"Duration {r['duration_seconds']:.1f}s exceeds "
                    f"2x median ({median_duration:.1f}s) while reward "
                    f"{r['submission_reward']:.3f} is not the lowest"
                ),
                "severity": "warning",
            })

    return findings


# ---------------------------------------------------------------------------
# GeometricIntelligence facade (D-01, D-02)
# ---------------------------------------------------------------------------


class GeometricIntelligence:
    """Facade composing KnowledgeBase and ResearchSurfacer for geometric analysis.

    Orchestrates ablation analysis, interference detection, diminishing returns,
    feature grouping, and exploration ordering into a unified analysis API.

    Args:
        kb: An initialized KnowledgeBase instance.
        surfacer: An initialized ResearchSurfacer instance.
    """

    def __init__(self, kb: KnowledgeBase, surfacer: ResearchSurfacer) -> None:
        self._kb = kb
        self._surfacer = surfacer

    def analyze_iteration(
        self,
        iteration_result: dict,
        feature_config: list[str],
        accuracy_gains: list[float],
    ) -> dict:
        """Orchestrate geometric analysis for a single iteration.

        Classifies features, checks for diminishing returns, and suggests
        exploration order with measured pairs filtered from KB.

        Args:
            iteration_result: Dict with iteration metadata (iteration_number,
                duration_seconds, etc.).
            feature_config: List of currently enabled feature names.
            accuracy_gains: Historical accuracy gain values for diminishing
                returns detection.

        Returns:
            Dict with keys:
                - "diminishing_returns": DiminishingReturns result
                - "exploration_order": FeatureExplorationOrder result
                - "feature_groups": dict mapping features to groups
        """
        # Classify features into functional groups
        groups = classify_features(feature_config)

        # Check for diminishing returns
        dr = detect_diminishing_returns(accuracy_gains)

        # Get measured pairs from KB (best-effort: empty set if no data)
        measured_pairs: set[tuple[str, str]] = set()
        try:
            findings = self._kb.query("interference", limit=50)
            for f in findings:
                # Extract pair names from interference findings
                content = f.content
                for comp_a in feature_config:
                    for comp_b in feature_config:
                        if comp_a != comp_b and comp_a in content and comp_b in content:
                            measured_pairs.add(tuple(sorted((comp_a, comp_b))))
        except Exception:
            pass  # Best-effort: proceed with empty measured set

        # Suggest exploration order
        exploration = suggest_exploration_order(groups, measured_pairs)

        return {
            "diminishing_returns": dr,
            "exploration_order": exploration,
            "feature_groups": groups,
        }

    def get_interference_pairs(
        self,
        ablation_matrix: AblationMatrix,
        threshold: float = -0.02,
    ) -> list[InterferencePair]:
        """Detect interference and store findings to KB.

        Delegates detection to detect_interference(), then persists each
        found pair via store_interference_finding().

        Args:
            ablation_matrix: Matrix of pairwise ablation measurements.
            threshold: Synergy score below which interference is flagged.

        Returns:
            List of detected InterferencePair objects.
        """
        from src.agent.evidence_tracker import EvidenceTracker

        pairs = detect_interference(ablation_matrix.cells, threshold)

        # Persist each pair -- need EvidenceTracker for KB storage
        # Access via surfacer's internal tracker
        et = getattr(self._surfacer, "_et", None)
        if et is not None:
            for pair in pairs:
                store_interference_finding(et, pair)

        return pairs
