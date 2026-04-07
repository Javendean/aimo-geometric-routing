# Critical Tension: "Prompt Diversity Hurts" ≠ "Routing Hurts"

## The Apparent Contradiction

The March 2026 paper tested 23+ prompt engineering strategies on gpt-oss-120B for AIMO 3. None beat T=1.0, N=8, majority vote. Some REDUCED accuracy.

Conclusion often drawn: "Don't change prompts. Just sample more."

But Zhu et al. (2024) show 67% accuracy improvement from topic-based strategy routing. And Aragon shows routing + orthogonality beats 4x scale.

## Why These Don't Actually Contradict

The 23-strategy paper tested **intra-problem diversity** — different prompt styles for the SAME problem. This adds noise to individual attempts without adding information.

Topic routing is **inter-problem specialization** — different strategies for DIFFERENT problem types. This doesn't add noise; it removes irrelevant strategy from each problem.

The distinction:
- **Intra-problem diversity**: "Try persona A on problem 1, persona B on problem 1" → noise
- **Inter-problem routing**: "Use algebra strategy on algebra problems, geometry strategy on geometry problems" → signal

## The Unresolved Question

Where is the boundary between intra-problem noise and inter-problem signal?

A topic-specific exemplar bank (2-3 worked examples per topic) is inter-problem routing. But a topic-specific system prompt that changes the reasoning style could be either — it might help if the style matches the problem type, or hurt if the model's internal MoE already handles this.

## Evidence from Our Agent's KB

- Prompt perturbation (intra-problem diversity) has NO Grade A evidence supporting it
- Topic patches (inter-problem routing) have Grade B evidence but no accuracy measurement
- The keyword topic classifier is ~60-70% accurate — below Zhu et al.'s phase transition threshold
- Temperature diversity was reduced from 4/8 to 5/8 with no validation

## What Would Settle This

A controlled experiment:
1. Baseline: T=1.0, N=8, no routing (current: ~39.7/50)
2. Treatment: T=1.0, N=8, topic-routed exemplars (2-3 per topic, ~100 tokens each)
3. Same problems, same seeds, same hardware
4. Measure: per-topic accuracy delta

If the treatment gains >1 point, routing is net positive despite the noisy classifier.
If the treatment loses, the classifier noise dominates and we should abandon routing.
