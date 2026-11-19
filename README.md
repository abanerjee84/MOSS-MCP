# MOSS Image local service

MOSS-Image-SFT UD-Q4_K_XL via stable-diffusion.cpp, a single local queued service, CLI and stdio MCP adapter. CUDA is restricted to the configured RTX 3060 UUID. The default UUID identifies the original machine; set `MOSS_GPU_UUID` to your card?s UUID on another system. The service requires 10500 MiB free before starting, samples total GPU usage every second, and terminates inference if it exceeds 11500 MiB. This is a safety monitor, not a hard allocator limit; brief peaks or shared-memory use can escape sampling. The Qwen3.5-9B Q4_K_M text encoder, MOSS UD-Q4_K_XL diffusion model, and VAE all run on the RTX 3060, with a 10.5 GiB engine budget and VAE tiling. The smaller Q4 encoder replaces the original Q8 encoder to leave room for generation buffers; its quantization can change prompt interpretation. The engine keeps all model weights resident in VRAM between jobs. Run `moss-image stop` to unload both and release the GPU. Cancelling a running job also unloads the engine.

## Installation (Windows)

Install Python 3.12, [uv](https://docs.astral.sh/uv/), and a current NVIDIA driver. In PowerShell from the project directory:

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
$env:MOSS_GPU_UUID = "GPU-your-3060-uuid" # find it with nvidia-smi -L
.venv\Scripts\python.exe download_assets.py
.\bin\moss-image.cmd setup-models
.\bin\moss-image.cmd doctor
```

Set `MOSS_GPU_UUID` in the environment of both the CLI and the MCP server. The downloader fetches the image model, Q4 text encoder, and pinned CUDA runtime; `setup-models` downloads any missing VAE and tokenizer. Downloads require several gigabytes of storage. The Windows launcher runs from this checkout; add its `bin` directory to PATH if desired. Adjust paths and the GPU environment variable in `mcp-config.example.json` for your machine.

## Status and setup

```
.\bin\moss-image.cmd doctor
.\bin\moss-image.cmd setup-models
```

Weights come from unsloth/MOSS-Image-SFT-GGUF, unsloth/Qwen3.5-9B-GGUF and unsloth/MOSS-Image-SFT-FP8. The stable-diffusion.cpp CUDA build must also be present under vendor/sd; version master-975 or later is required. `doctor` lists missing files. See https://huggingface.co/unsloth/MOSS-Image-SFT-GGUF and https://github.com/leejet/stable-diffusion.cpp/blob/master/docs/moss_image.md.

## Usage

Open a new terminal to use `moss-image` from PATH, or use the full launcher path above. Stop FLUX or other GPU workloads first if there is insufficient free memory.

```
moss-image generate --prompt "A red ceramic teapot on a white table" --width 1024 --height 1024 --steps 50 --seed 42 --wait --out teapot.png
moss-image generate --prompt "A mountain at sunrise"
moss-image status JOB_ID
moss-image wait JOB_ID
moss-image cancel JOB_ID
moss-image download JOB_ID --out image.png
moss-image stop
```

`generate` queues and returns immediately unless `--wait` is supplied. A request ID can be supplied with `--request-id` for safe retries. Jobs and images are stored in `data/outputs`. Jobs interrupted by a service restart are marked failed and must be resubmitted. The HTTP service binds only to localhost:8772 and requires the bearer token in `data/token.txt`; do not share that file. MCP runs a lightweight stdio adapter and starts the service if needed. The image engine also binds an unauthenticated, randomly chosen localhost port while running; it is intended only for trusted local users. The Codex `local-moss` registration takes effect in a new session.

With the Q4 text encoder, a 1024x1024, 4-step warm test succeeded in 16 seconds and peaked at 8691 MiB sampled GPU usage. The engine reported 7942 MiB of weights on VRAM and none on RAM. Peak use varies with resolution and prompt length. Cold-start time includes reading weights from the E: hard drive.

To resume all large downloads and install the pinned CUDA runtime, run `.venv\Scripts\python.exe download_assets.py` from this directory. The downloader uses partial files and retries; keep the terminal open until it finishes.
