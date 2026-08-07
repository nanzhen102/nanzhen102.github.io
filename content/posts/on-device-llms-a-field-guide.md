---
title: On-device LLMs, a field guide
date: 2026-08-06
---

On-device LLMs have picked up real momentum in fields where patient or client data legally can't leave the building, favoring locally-run models over the general-purpose cloud APIs most people reach for by default, e.g., Claude, GPT-5.1, Gemini 3.1 Pro, none of which you can download and run yourself.

It can be categorized by:

| Tier | Defined by | Param range | Typical footprint | Example hardware | Quantization |
|---|---|---|---|---|---|
| 1: Embedded | Parameter count | <500M | <1GB | Wearables, IoT, microcontroller-class CPUs | Standard (FP16/INT8) |
| 1b: 1-bit / extreme quantization | Weight representation (a technique, not a size class) | ~2B raw params → ~0.4GB footprint | <0.5GB despite 2B params | Any CPU (tested on Apple M2) | Native ternary, 1.58-bit, not post-hoc quantized |
| 2: Mobile / phone | Parameter count, phone-SoC latency | 1B–4B | 1–4GB | Snapdragon / Tensor / A-series NPU | 4-bit (INT4) typical |
| 3: Laptop / single consumer GPU | Parameter count, consumer GPU VRAM | 7B–14B | 4–10GB (4-bit) | RTX 3060 12GB, Apple Silicon unified memory | 4-bit (GGUF/AWQ) |
| 4: Workstation / prosumer GPU | Parameter count, high-VRAM card | 20B–35B | 12–24GB+ | RTX 4090 24GB, prosumer workstation cards | 4-bit, or native BF16 on high-VRAM cards |
| 5: Single high-end GPU / local server | Parameter count, single top-tier GPU | 70B+ (up to ~120B total, MoE) | up to 80GB | Single A100/H100 80GB | BF16/FP8 native; MoE keeps active params low |

For each tier, below are the specific model, release date, size, etc.

## Tier 1: Embedded, under 500M parameters

The smallest useful models, built for wearables and IoT hardware rather than anything resembling a chat assistant.

| Model | Org | Size | Date | Ref |
|---|---|---|---|---|
| SmolLM2-135M | Hugging Face (HuggingFaceTB) | 135M | Feb 2025 | [model card](https://huggingface.co/HuggingFaceTB/SmolLM2-135M) |
| SmolLM2-360M | Hugging Face (HuggingFaceTB) | 360M | Feb 2025 | [model card](https://huggingface.co/HuggingFaceTB/SmolLM2-360M-Instruct) |

## Tier 1b: 1-bit models, a different trick entirely

Not a size class, a different way of storing weights. BitNet represents every weight as one of just three values (-1, 0, 1) instead of the usual 16 or 32 bits, so a 2B-parameter model, normally phone-class by size, ends up small enough to run on a plain CPU with room to spare.

| Model | Org | Size | Date | Ref |
|---|---|---|---|---|
| BitNet b1.58 2B4T | Microsoft Research | 2B params, native 1.58-bit ternary weights, ~0.4GB footprint, trained on 4T tokens, runs on CPU (tested on Apple M2) | Apr 16, 2025 (technical report) | [model card](https://huggingface.co/microsoft/bitnet-b1.58-2B-4T) · [technical report](https://arxiv.org/pdf/2410.16144) |

## Tier 2: Phone-class, 1 to 4B parameters

*This is the tier most people mean by "on-device LLM"*: small enough to run at usable speed on a phone's NPU. It's also the most crowded tier, every major lab has an entry here.

| Model | Org | Size | Date | Ref |
|---|---|---|---|---|
| Gemma 3n E2B | Google | ~5B raw / ~2B effective footprint, runs in 2GB RAM | June 2025 | [model card](https://huggingface.co/google/gemma-3n-E2B) · [dev guide](https://developers.googleblog.com/en/introducing-gemma-3n-developer-guide/) |
| Gemma 3n E4B | Google | ~8B raw / ~4B effective footprint, runs in 3GB RAM | June 2025 | [model card](https://huggingface.co/google/gemma-3n-E4B) |
| Gemini Nano 4 (Fast/Full) | Google | distilled from Gemma 4 E2B/E4B (4.2GB / 5.9GB) | previewing 2026, Android AICore | [9to5google](https://9to5google.com/2026/04/02/gemini-nano-4-android/) · [Android Authority benchmarks](https://www.androidauthority.com/gemini-nano-4-benchmarks-3655763/) |
| Phi-4-mini-instruct | Microsoft | 3.8B | early 2025 | [model card](https://huggingface.co/microsoft/Phi-4-mini-instruct) |
| Llama 3.2 1B | Meta | 1B (pruned/distilled from Llama 3.1 8B) | Sep 25, 2024 | [model card](https://huggingface.co/meta-llama/Llama-3.2-1B) · [Meta announcement](https://ai.meta.com/blog/llama-3-2-connect-2024-vision-edge-mobile-devices/) |
| Llama 3.2 3B | Meta | 3B | Sep 25, 2024 | [model card](https://huggingface.co/meta-llama/Llama-3.2-3B) |
| Qwen3-0.6B | Alibaba | 0.6B | Apr 28, 2025 | [model card](https://huggingface.co/Qwen/Qwen3-0.6B) |
| Qwen3-1.7B | Alibaba | 1.7B | Apr 28, 2025 | [model card](https://huggingface.co/Qwen/Qwen3-1.7B) |
| Qwen3-4B | Alibaba | 4B | Apr 28, 2025 | [model card](https://huggingface.co/Qwen/Qwen3-4B) |
| SmolLM2-1.7B | Hugging Face | 1.7B | Feb 2025 | [model card](https://huggingface.co/HuggingFaceTB/SmolLM2-1.7B) |
| SmolLM3-3B | Hugging Face | 3B | mid-2025 | [blog](https://huggingface.co/blog/smollm3) · [model card](https://huggingface.co/HuggingFaceTB/SmolLM3-3B) |
| Apple on-device foundation model | Apple | ~3B, compressed to 2 bits/weight via QAT | introduced WWDC 2024; opened to developers WWDC 2025 | [Apple ML research](https://machinelearning.apple.com/research/apple-intelligence-foundation-language-models) |
| MiniCPM5-1B | OpenBMB | 1B dense, built for on-device/local deployment | May 2026 | [model card](https://huggingface.co/openbmb/MiniCPM5-1B) |
| Ministral-3-3B | Mistral AI | 3B, fits in 16GB VRAM BF16 / <8GB quantized | Dec 2025 | [model card](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512) · [Mistral 3 announcement](https://mistral.ai/news/mistral-3/) |

## Tier 3: Laptop-class, 7 to 14B parameters

Needs a real GPU, but a consumer one, not a datacenter one. A 12GB card or an Apple Silicon laptop with enough unified memory is plenty.

| Model | Org | Size | Date | Ref |
|---|---|---|---|---|
| Mistral 7B | Mistral AI | 7B | Sep 2023 | [model card](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3) |
| Llama 3.1 8B | Meta | 8B | Jul 2024 | [model card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) |
| Ministral-3-8B | Mistral AI | 8B, fits in 24GB VRAM BF16 / <12GB quantized | Dec 2025 | [model card](https://huggingface.co/mistralai/Ministral-3-8B-Instruct-2512) |
| Qwen3-8B | Alibaba | 8B | Apr 28, 2025 | [model card](https://huggingface.co/Qwen/Qwen3-8B) |
| Qwen3-14B | Alibaba | 14B | Apr 28, 2025 | [model card](https://huggingface.co/Qwen/Qwen3-14B) |
| Phi-4 (full) | Microsoft | 14B | Dec 2024 | [model card](https://huggingface.co/microsoft/phi-4) |

## Tier 4: Workstation-class, 20 to 35B parameters

This is where it gets interesting: models at this size, run locally on a single high-VRAM card, are now beating some proprietary cloud models on real tasks.

| Model | Org | Size | Date | Ref |
|---|---|---|---|---|
| gpt-oss-20b | OpenAI | 21B total, 3.6B active (MoE) | Aug 5, 2025 | [model card](https://huggingface.co/openai/gpt-oss-20b) · [announcement](https://openai.com/index/introducing-gpt-oss/) |
| Gemma 4 31B | Google DeepMind | 30.7B dense, 256K context, multimodal (text/image/video/audio) | Apr 2, 2026 | [model card](https://huggingface.co/google/gemma-4-31B-it) |
| Qwen3.5-9B | Alibaba | 9B | ~Mar 2, 2026 | [model card](https://huggingface.co/Qwen/Qwen3.5-9B) |
| Qwen3.5-27B | Alibaba | 27B | Feb 24, 2026 | [model card](https://huggingface.co/Qwen/Qwen3.5-27B) |
| Qwen3.5-35B-A3B | Alibaba | 35B total (MoE) | Feb 24, 2026 | [model card](https://huggingface.co/Qwen/Qwen3.5-35B-A3B) |

## Tier 5: The upper limit, 70B and up

The last tier that still counts as one machine. gpt-oss-120b is the only entry here, purpose-built to fit a single 80GB GPU. Past this point, think 405B-parameter dense models or DeepSeek-R1's 671B, that's multi-GPU serving territory, a genuinely different engineering problem than "on-device," and where this guide stops.

| Model | Org | Size | Date | Ref |
|---|---|---|---|---|
| gpt-oss-120b | OpenAI | 117B total, 5.1B active (MoE), fits a single 80GB GPU | Aug 5, 2025 | [model card](https://huggingface.co/openai/gpt-oss-120b) |

This should serve as a starting point for benchmarking models, working with private data, or fine-tuning one from scratch. ✨
