---
name: novelai
description: Generate images via the NovelAI image API. Use when the user asks to generate an anime/illustration image with NovelAI, mentions a NovelAI prompt, references a model like nai-diffusion-4-5-full / nai-diffusion-3, or wants to render a Danbooru-tag-style image prompt.
---

Generate images via NovelAI's image API. Output is one or more PNG files written to a local directory.

## Auth setup
Read the API key (NovelAI persistent token) from, in order:
1. `$NOVELAI_API_KEY`
2. `~/.config/novelai/key`

If neither is set, tell the user once how to configure it — never ask them to paste the key into chat:

```
echo 'YOUR_KEY' > ~/.config/novelai/key && chmod 600 ~/.config/novelai/key
```

The key starts with `pst-...` and is obtained from `https://novelai.net` → User Settings → Account → Get Persistent API Token.

## How to invoke

```bash
~/.claude/skills/novelai/generate.py "PROMPT" --out ./out
```

The script prints generated file paths to stdout, one per line: `nai-<timestamp>-<seed>-<i>.png`.

### Common flags
- `--model` — `nai-diffusion-4-5-full` (default), `nai-diffusion-4-5-curated`, `nai-diffusion-3`
- `--negative "..."` — replaces the default negative prompt
- `--width / --height` — must be multiples of 64. Common: `832x1216` portrait, `1216x832` landscape, `1024x1024` square
- `--steps` — default 28; 28 is the free-tier ceiling on Opus subs
- `--scale` — CFG scale, default 6
- `--sampler` — default `k_euler_ancestral`; alternatives: `k_dpmpp_2s_ancestral`, `k_euler`
- `--seed N` — omit or 0 for random
- `--n N` — samples per call (each costs Anlas)

### Prompt tips
- Use comma-separated Danbooru-style tags: `1girl, blue hair, looking at viewer, school uniform, classroom`.
- For v4.5, lead with quality tags: `masterpiece, best quality, very aesthetic, absurdres, ...`.
- The default negative already covers common quality issues. To add to it instead of replacing, pass the full string yourself.

## Error handling
- `401` — bad/expired key. Tell the user to refresh the persistent token.
- `402` — no Anlas / inactive subscription. Image generation requires an Opus tier or sufficient Anlas.
- `429` — rate limited. Back off ~10s and retry once.
- `400` — usually invalid model name or non-multiple-of-64 dimensions. Verify and retry.

## Safety
- Never echo the API key in chat or commit it to a repo.
- Don't auto-install anything on the user's behalf — the script uses only Python stdlib.
