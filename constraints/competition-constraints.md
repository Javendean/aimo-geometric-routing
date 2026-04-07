# Competition Constraints (AIMO 3)

| Constraint | Value | Source |
|-----------|-------|--------|
| Model | gpt-oss-120B, MoE (5.1B active of 117B), MXFP4 quantization | Kaggle model card |
| GPU | Single H100 80GB | kernel-metadata.json: NvidiaH100 |
| Context window | 32,768 tokens | vLLM --max-model-len 32768 |
| Exemplar budget | ~13,784 tokens (after system prompt + generation reserve) | Measured |
| Time budget | 5 hours total for ~110 problems (~2.7 min/problem average) | Competition rules |
| Environment | Air-gapped Kaggle, no internet, no fine-tuning | Competition rules |
| Scoring | Two attempts per problem (primary + secondary answer) | Competition rules |
| Problem taxonomy | algebra, combinatorics, geometry, number_theory | IMO standard |
| Cross-topic fraction | ~25-30% of problems span multiple categories | Estimated from past IMO |
| Current score | ~39.7/50 baseline (T=1.0, N=8, majority vote) | Measured |
| Ceiling observed | ~44/50 (reference notebook) | Kaggle public leaderboard |
| Answer format | Integer in [0, 99999] | Competition rules |
| Submission format | inference_server + submission.parquet | Competition portal |
