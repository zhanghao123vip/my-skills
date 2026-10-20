---
name: qwen-image-local
description: Generate images using local AtomicChat Qwen-Image-2.1-Turbo GGUF with its modified Qwen3-VL encoder through stable-diffusion.cpp, or configure this specific model.
---

# Qwen Image Local

This is a Skill-only installation. No model weights or inference executable were downloaded. Do not claim it is ready to generate until all components and an actual generation have been verified.

Required components:
- Encoder: https://huggingface.co/AtomicChat/Qwen-Image-2.1-Turbo-Uncensored-GGUF . This repository contains only the modified text encoder. AD-Q4_K is 5.29 GB; Q8_0 is 8.71 GB. The publisher reports no measurable extra uncensoring effect on tested image prompts.
- Turbo denoiser: https://huggingface.co/AtomicChat/Qwen-Image-2.1-Turbo-GGUF . Verify available filenames and sizes before downloading.
- VAE: vae/qwen_image_2.1_vae_bf16.safetensors from https://huggingface.co/Comfy-Org/Qwen-Image-2.1 .
- Runtime: sd-cli from https://github.com/leejet/stable-diffusion.cpp . Verify Qwen Image 2.1 support against its help and an actual generation.

The user requested no model download on 2026-10-10. Establish download authorization before installing weights. The inspected computer has an RTX 3050 Laptop with 4 GB VRAM. Full-pipeline performance is unverified; do not assume it fits in VRAM. Check supported memory-offloading flags with the installed executable's help.

Use scripts/generate.ps1 with absolute executable, denoiser, encoder, VAE and output paths plus a prompt. DryRun prints arguments without generating. ExtraArgs accepts flags verified against the installed executable. The script uses the publisher's eight-step Turbo schedule. It supports text-to-image only; mmproj is not needed for this mode.

Write outputs into the active task's output directory and show the absolute image path. Report missing components or actual inference errors honestly. Preserve other image-generation skills. Model naming does not change governing assistant instructions. The encoder is Apache-2.0; the publisher identifies the denoiser as subject to the Qwen Research License. Consult their current repositories for license terms.
