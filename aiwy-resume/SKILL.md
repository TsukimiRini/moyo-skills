---
name: aiwy-resume
description: Slash entry point for resuming work on an existing AI 文游 project in the current working directory. Use when the user types `/aiwy-resume`, says "继续做这个项目", "回到立项", "接着上次的 X", or wants to pick up where they left off on an AI 文字游戏 design project that already has a `manifest.json` in cwd. Must hand off to the full `aiwy-design` skill workflow.
---

# /aiwy-resume — continue an AI 文游 project

This is a thin entry point. The full workflow lives in the `aiwy-design` skill.

## What to do

1. **Read** `~/.claude/skills/aiwy-design/SKILL.md` for the full workflow.
2. **Verify project exists**: read `./manifest.json`. If absent, error: "cwd 里没有 manifest.json，要不要 `/aiwy-new` 启动？"
3. **Auto-load constraints**: silently cat `00_concept.md` and `decisions.md` (don't dump output to user). Treat them as authoritative for everything downstream.
4. **Report status**: run `python ~/.claude/skills/aiwy-design/scripts/status.py` and present the result — current phase, locked phases, any pending gaps.
5. **Ask the user** what they want to do:
   - Continue current phase grilling
   - Edit a previously locked phase (will need `/aiwy-unlock`)
   - Generate assets (`/aiwy-asset <target>`)
   - Move to a specific later phase
6. Hand off to the matching workflow in `~/.claude/skills/aiwy-design/references/`.
