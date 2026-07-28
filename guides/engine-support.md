# Engine Support

llm-d supports **vLLM**, **SGLang**, and **TensorRT-LLM** as inference backends. This page shows what is validated with each engine.

**Legend:** ✅ validated, guide exists · 🚧 partial or guide missing · ❌ not started · — not applicable

## Feature Support

| Feature | vLLM | SGLang | TRT-LLM | Guide |
|---|:---:|:---:|:---:|---|
| Optimized Baseline | ✅ | ✅ | ✅ | [→](./optimized-baseline/README.md) |
| Approx Prefix Routing | ✅ | ✅ | — | [→](./optimized-baseline/README.md) |
| Precise Prefix Routing | ✅ | ✅ | — | [→](./precise-prefix-cache-routing/README.md) |
| Predicted Latency Routing | ✅ | 🚧 ¹ | — | [→](./predicted-latency-routing/README.md) |
| Tiered Cache L1/L2 (CPU offload) | ✅ | ✅ | — | [→](./tiered-prefix-cache/README.md) |
| Tiered Cache L3/L4 (remote store) | ✅ | 🚧 | — | [→](./tiered-prefix-cache/README.md) |
| P/D Disaggregation | ✅ | 🚧 ² | — | [→](./pd-disaggregation/README.md) |
| Wide Expert Parallelism | ✅ | 🚧 | — | [→](./wide-ep-lws/README.md) |
| Agentic Serving | ✅ | 🚧 | — | [→](./agentic-serving/README.md) |
| Multimodal Serving | ✅ | ❌ | — | [→](./multimodal-serving/README.md) |
| Flow Control | ✅ | ✅ | ✅ | [→](./flow-control/README.md) |
| Workload Autoscaling | ✅ | 🚧 | — | [→](./workload-autoscaling/README.md) |

¹ Feature works; no SGLang guide yet  
² NVIDIA-only; RDMA recipes in progress

## Hardware Support

| Accelerator | vLLM | SGLang |
|---|:---:|:---:|
| NVIDIA GPU | ✅ | ✅ |
| AMD ROCm | ✅ | ✅ |
| Google TPU | ✅ | 🚧 |
| Intel XPU / Gaudi | ✅ | — |
| CPU | ✅ | — |

## Prefill Throughput Benchmarks

Measured `peakPrefillThroughput` (tokens/sec) at `--max-num-batched-tokens=8192` unless noted. SGLang achieves ~1.9× vLLM prefill throughput on identical NVIDIA hardware.

| Accelerator | Engine | Model | TP | tok/s |
|---|---|---|:---:|---:|
| H100 80 GB | vLLM v0.22.0 | gpt-oss-120B (MoE, MXFP4) | 1 | 39,065 |
| H100 80 GB | SGLang v0.5.13 | Qwen3-32B | 2 | **30,720** |
| TPU v7x | vLLM tpu v0.22.0 | Qwen3-32B | 8 | 27,336 |
| TPU v6e | vLLM tpu v0.22.0 | Qwen3-32B | 8 | 26,290 |
| H100 80 GB | vLLM v0.23.0 | Qwen3-32B | 2 | 15,928 |
| CPU (AMX) | vLLM cpu v0.6.0 | Llama-3.2-3B | 1 | 1,970 ³ |

³ Calibrated at `CHUNK_SIZE=2048` (CPU vLLM default), not 8192

To add a row, run the calibration script against your stack — see [`recipes/router/calibration/`](./recipes/router/calibration/README.md).
