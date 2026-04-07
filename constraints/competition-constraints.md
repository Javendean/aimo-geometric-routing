# Competition Constraints (AIMO 3)

| Constraint | Value | Source |
|-----------|-------|--------|
| **Problems** | **50 (NOT 110)** | Competition rules |
| Model | gpt-oss-120B, MoE (5.1B active of 117B), MXFP4 quantization | Kaggle model card |
| GPU | Single H100 80GB | kernel-metadata.json: NvidiaH100 |
| Context window | 32,768 tokens | vLLM --max-model-len 32768 |
| Exemplar budget | ~13,784 tokens (after system prompt + generation reserve) | Measured |
| Time budget | 5 hours for 50 problems (~6 min/problem average) | Competition rules |
| Environment | Air-gapped Kaggle, no internet, no fine-tuning | Competition rules |
| Answer format | Integer in [0, 99999] (5 digits, up from 3 in AIMO2) | Competition rules |
| Submission format | kaggle_evaluation.aimo_3_inference_server + submission.parquet | Competition portal |
| Problem taxonomy | algebra, combinatorics, geometry, number_theory | IMO standard |
| Cross-topic fraction | ~25-30% of problems span multiple categories | Estimated from past IMO |
| Current score | ~39.7/50 baseline (T=1.0, N=8, majority vote) | Measured |
| Ceiling observed | ~44/50 (reference notebook) | Kaggle public leaderboard |

## Scoring System (Critical for Strategy)

### Public Test (during submission period)
- Unnormalized accuracy = number of correct answers
- Single notebook run

### Private Test (determines winner)
- Notebook runs **TWICE** over private test set
- Predictions concatenated into single submission file
- Penalized accuracy scoring:

| Both runs correct | 1.0 per problem |
|---|---|
| One run correct, one wrong | 0.5 per problem |
| Neither run correct | 0.0 per problem |

**Overall score = sum of per-problem scores. Max = 50.**

### Strategic Implications

1. **Expectation-neutral scoring.** E[score] = p (per-problem accuracy) regardless of whether runs are identical or independent. Diversity between runs is NOT penalized in expectation. The only strategic question is whether a change increases p.

2. **High temperature hurts on easy problems.** T=1.0 with majority vote may produce different majority answers between runs. For problems the model CAN solve, lower variance → both runs agree → full points.

3. **The two runs are NOT "two attempts" within one run.** They are two complete, independent notebook executions. The notebook itself can use multiple samples per problem within each run, but the scoring is across runs.

4. **Optimal strategy: maximize expected accuracy with minimum variance.** A solver that gets 40/50 consistently beats one that gets 42/50 half the time and 38/50 the other half.

## Evaluation API

- Template: `kaggle kernels pull ryanholbrook/aimo-3-submission-demo`
- Problems served one-by-one in random order (public) or fixed random order (private)
- Must use `AIMO3InferenceServer(predict)` pattern
- `predict(id_, question)` receives polars DataFrame, returns answer
