#!/usr/bin/env python3
"""NovelAI image generator. Uses only stdlib."""
import argparse
import io
import json
import os
import pathlib
import random
import sys
import time
import urllib.error
import urllib.request
import zipfile

API_URL = "https://image.novelai.net/ai/generate-image"


def load_key() -> str:
    k = os.environ.get("NOVELAI_API_KEY")
    if k:
        return k.strip()
    p = pathlib.Path.home() / ".config" / "novelai" / "key"
    if p.exists():
        return p.read_text().strip()
    sys.exit(
        "error: no NovelAI key. Set $NOVELAI_API_KEY or write the persistent "
        "token to ~/.config/novelai/key (chmod 600)."
    )


def build_body(args: argparse.Namespace) -> dict:
    is_v4 = args.model.startswith("nai-diffusion-4")
    params: dict = {
        "params_version": 3,
        "width": args.width,
        "height": args.height,
        "scale": args.scale,
        "sampler": args.sampler,
        "steps": args.steps,
        "n_samples": args.n,
        "seed": args.seed,
        "ucPreset": 0,
        "qualityToggle": True,
        "negative_prompt": args.negative,
        "sm": False,
        "sm_dyn": False,
        "dynamic_thresholding": False,
        "cfg_rescale": 0,
        "noise_schedule": "karras",
        "legacy": False,
        "legacy_v3_extend": False,
        "controlnet_strength": 1,
        "add_original_image": True,
    }
    if is_v4:
        params["use_coords"] = False
        params["characterPrompts"] = []
        params["v4_prompt"] = {
            "caption": {"base_caption": args.prompt, "char_captions": []},
            "use_coords": False,
            "use_order": True,
        }
        params["v4_negative_prompt"] = {
            "caption": {"base_caption": args.negative, "char_captions": []},
            "legacy_uc": False,
        }
    return {
        "input": args.prompt,
        "model": args.model,
        "action": "generate",
        "parameters": params,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate images via NovelAI.")
    ap.add_argument("prompt", help="comma-separated tag prompt")
    ap.add_argument("--out", default=".", help="output directory")
    ap.add_argument("--model", default="nai-diffusion-4-5-full")
    ap.add_argument("--negative", default="", help="negative prompt; default empty")
    ap.add_argument("--width", type=int, default=832)
    ap.add_argument("--height", type=int, default=1216)
    ap.add_argument("--steps", type=int, default=28)
    ap.add_argument("--scale", type=float, default=6.0)
    ap.add_argument("--seed", type=int, default=0, help="0 = random")
    ap.add_argument("--n", type=int, default=1, help="samples per request")
    ap.add_argument("--sampler", default="k_euler_ancestral")
    args = ap.parse_args()

    if args.width % 64 or args.height % 64:
        sys.exit("error: width and height must be multiples of 64")

    if args.seed == 0:
        args.seed = random.randint(1, 2**32 - 1)

    body = json.dumps(build_body(args)).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {load_key()}",
            "Content-Type": "application/json",
            "Accept": "application/x-zip-compressed",
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Origin": "https://novelai.net",
            "Referer": "https://novelai.net/",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            zip_bytes = resp.read()
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        sys.exit(f"HTTP {e.code}: {body_text}")
    except urllib.error.URLError as e:
        sys.exit(f"network error: {e.reason}")

    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    output_pngs: list[pathlib.Path] = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        for i, name in enumerate(z.namelist()):
            data = z.read(name)
            out = out_dir / f"nai-{ts}-{args.seed}-{i}.png"
            out.write_bytes(data)
            output_pngs.append(out)
            print(out)

    log_path = out_dir / f"nai-{ts}-{args.seed}.txt"
    log_path.write_text(
        f"timestamp: {ts}\n"
        f"model: {args.model}\n"
        f"seed: {args.seed}\n"
        f"sampler: {args.sampler}\n"
        f"steps: {args.steps}\n"
        f"scale: {args.scale}\n"
        f"size: {args.width}x{args.height}\n"
        f"n_samples: {args.n}\n"
        "\nprompt:\n"
        f"{args.prompt}\n"
        "\nnegative_prompt:\n"
        f"{args.negative}\n"
        "\noutputs:\n"
        + "".join(f"- {p.name}\n" for p in output_pngs),
        encoding="utf-8",
    )
    print(log_path)


if __name__ == "__main__":
    main()
