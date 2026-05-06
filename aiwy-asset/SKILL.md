---
name: aiwy-asset
description: Slash entry point for generating visual assets (角色立绘, 界面背景图, 关键 CG, 封面 / 立项关键画) within an AI 文游 design project. Use when the user types `/aiwy-asset <target>`, says "出 X 的立绘", "生成界面背景", "画一下封面", or otherwise wants to produce visual artwork for an AI 文字游戏 project. Routes to the asset pipeline in `aiwy-design`. The target arg is a character name, interface_id (for interface backgrounds), or `concept` (for cover / key art).
---

# /aiwy-asset <target> — generate assets for the project

Thin entry point. Full pipeline in `aiwy-design/references/asset_pipeline.md`.

## What to do

1. **Verify project**: read `./manifest.json`. If absent, error.
2. **Read** `~/.claude/skills/aiwy-design/references/asset_pipeline.md` and follow it. Briefly:
   - Resolve `<target>` to a design file:
     - character → `characters/<target>/04_visual.yaml` (and `00_core.yaml` for vibe context)
     - interface_id → `interfaces/<target>.md` (for background art only — chat/dialogue/phone bg)
     - `concept` → `00_concept.md` (key art / cover)
   - **Step A — 气质中介层**: produce a 50-100 字 prose block describing first-impression vibe + composition + lighting. User confirms or adjusts.
   - **Step B — Tag conversion**: convert to Danbooru-style tags. **Always prepend `00_concept.md`'s `visual_style_tags`** to the front of the prompt.
   - **Step C — NovelAI generation**: invoke `~/.claude/skills/novelai/generate.py` with the assembled prompt. Save under `<target_dir>/portrait/concept_v<N>.png` or `interfaces/<target>_bg_v<N>.png`. Default `--n 1` while iterating prompt; bump to `--n 4` once prompt is stable and only seed-shopping. Default no `--negative`; only add a negative tag if a specific recurring problem warrants it. (Full rationale in `asset_pipeline.md` Step C.)
   - **Step D — Canonicalize**: user picks the best one → `cp` to `concept_canonical.png` so downstream立绘 generation has a stable reference.
   - **Step E — (optional)立绘 variations**: if user wants expression / pose variations and an i2i skill is installed (e.g. `liclick`), hand off to it using `concept_canonical.png` as reference image. Save outputs to `portrait/expressions/`.
3. After generation, briefly recap what was produced and where, and ask if user wants more iterations.

## Hard rules

- **NEVER call NovelAI without prepending the project's `visual_style_tags`** — it's the #1 cause of cross-character style drift.
- **气质中介层 is mandatory** before tag generation, even for repeat runs — it's the human-in-the-loop checkpoint that prevents you from confidently producing the wrong-vibe image.
- If the project is in concept phase and `visual_style_tags` is empty, refuse and ask the user to define it first (it's a Phase 1 必产出).
