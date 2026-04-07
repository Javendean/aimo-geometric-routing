# TurboQuant: KV Cache Compression (ICLR 2026, Google Research)

Source: https://research.google/blog/turboquant-redefining-ai-efficiency-with-extreme-compression/
PyTorch implementation: https://github.com/tonbistudio/turboquant-pytorch

## What It Does

Compresses the Key-Value cache during LLM inference to 3-4 bits per value. Training-free, data-oblivious. Works on any transformer model without modification to weights.

## Key Results

- 3-bit KV cache with 99.5% attention fidelity (vs uncompressed)
- 4-bit achieves **8x performance increase** over 32-bit keys on H100
- 5x total compression at 3-bit
- No fine-tuning or training required
- Works as a drop-in replacement for the KV cache layer

## How It Works

1. **Random rotation** normalizes vector distributions (simplifies geometry)
2. **Lloyd-Max optimal scalar quantization** per coordinate
3. **Asymmetric bit allocation** — more precision for keys (determine attention focus) than values
4. **Optional QJL residual correction** — community found this HURTS for softmax attention; MSE-only variant is better

## Community Implementation (turboquant-pytorch)

The `tonbistudio/turboquant-pytorch` repo is a from-scratch PyTorch implementation:
- Pure PyTorch (no custom CUDA kernels required)
- V3 variant removes QJL, uses MSE-only quantization
- K6/V4 compression with 128-token residual window: ~2x compression, exact text output
- Validated across multiple community implementations

## Our Current KV Cache

```python
# From notebook/kaggle_hybrid_submission.py
kv_cache_dtype = "fp8_e4m3"  # 8-bit KV cache
```

gpt-oss-120B on H100 with 32K context and fp8 KV cache. TurboQuant could compress from 8-bit to 3-4 bit — a 2-2.6x reduction.

## What This Could Enable

### More samples per problem
Current: N=8 samples (limited by memory). With 2x KV cache compression:
- Free ~15-20GB of GPU memory during inference
- Potentially run N=16-24 samples per problem
- More lottery tickets = higher per-problem accuracy

### Longer context per sample
Current: 32K tokens. With compressed KV cache:
- Could extend to 48K-64K context
- More room for exemplars, chain-of-thought, verification steps

### Both simultaneously
Partial compression for both more samples AND longer context.

## Implementation Feasibility (OPEN QUESTION for GPT-5.4-pro)

1. **Can turboquant-pytorch be integrated into vLLM 0.11.2's KV cache layer?** The implementation is pure PyTorch; vLLM's cache is PyTorch-based. But vLLM has its own memory management (PagedAttention). Is there an integration path?

2. **Could we bypass vLLM entirely?** Run inference with a custom PyTorch loop that includes TurboQuant. This would lose vLLM's batching/scheduling but gain KV cache compression. Is the tradeoff worth it for N=16+ samples?

3. **Can we pre-build turboquant-pytorch as a wheel?** The Kaggle environment is air-gapped. We'd need to build the wheel on Azure and upload to the hopeinchrist dataset. Pure Python wheels are straightforward, but any compiled extensions would need to match the Kaggle Docker's Python/CUDA versions.

4. **What's the exact memory math?** For gpt-oss-120B (117B params, MoE, MXFP4 weights) on H100 80GB:
   - Current: model weights + fp8 KV cache (32K context, 16 concurrent seqs) = ~76GB
   - With TurboQuant 3-bit: model weights + 3-bit KV cache = ? GB freed
   - How many additional concurrent sequences does the freed memory support?

5. **Is the 99.5% attention fidelity sufficient for math reasoning?** AIMO3 problems require exact integer answers. Any attention degradation could cause wrong answers. The community validated "exact text output" at K6/V4 — but has anyone tested on math reasoning specifically?
