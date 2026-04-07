# AIMO 3 Reference Bench Model Evaluation

Source: AIMO Progress Prize 3 Reference Problems (November 2025), page 2.

## Results

14 models evaluated on 10 problems. Uncontaminated (problems never seen by models before testing).

| Model | Problems Solved (/10) | Notes |
|---|---|---|
| GPT-5 Pro | 10 | Perfect |
| GPT-5.1 (high) | 10 | Perfect |
| GPT-5 (high) | 9 | Failed Problem 10 only |
| Grok-4 | 9 | Failed Problem 10 only |
| Gemini 2.5 Pro | 9 | Failed Problem 10 only |
| DeepSeek-v3.1-terminus (thinking) | 9 | 671B params, open-weight |
| **gpt-oss-120B** | **4** | **Solved only AIMO2-level (Problems 1-4). Failed ALL AIMO3-level (5-10).** |

## Key Implications for Routing

1. **gpt-oss-120B has a hard capability ceiling at AIMO2 difficulty.** Routing will not help the model solve Problem 10 (which only GPT-5 Pro and GPT-5.1 can solve). The question is whether routing can help solve Problems 5-9.

2. **The gap between gpt-oss-120B (4/10) and frontier models (9-10/10) is 5-6 problems.** This is the maximum improvement possible. Routing must target this gap.

3. **DeepSeek-v3.1-terminus at 671B matches second-tier commercial models.** This suggests model scale matters, but gpt-oss-120B's MoE architecture (5.1B active) may be capacity-limited in ways that routing can't overcome.

4. **The winning AIMO3 score will likely be in the high 40s** (per the document). Current baseline is 39.7/50 on the public set. The gap to win is ~5-8 points.
