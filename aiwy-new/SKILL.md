---
name: aiwy-new
description: Slash entry point for starting a new AI 文游 (AI text adventure) project in the current working directory. Use when the user types `/aiwy-new`, says "新建 文游 项目", "做个新文游", "开个新策划", or otherwise initiates a fresh AI 文字游戏 design project. Must hand off to the full `aiwy-design` skill workflow — this skill is just the trigger.
---

# /aiwy-new — start a new AI 文游 project in cwd

This is a thin entry point. The full workflow lives in the `aiwy-design` skill.

## What to do

1. **Read** `~/.claude/skills/aiwy-design/SKILL.md` and `~/.claude/skills/aiwy-design/references/intake.md` — these contain the full workflow.
2. **Verify cwd is project-ready**:
   - Run `ls -A` in cwd. If non-empty (and not just `drafts/`), warn the user and offer to create `./aiwy_<name>/` subdirectory instead.
   - If empty or only contains `drafts/`, proceed.
3. **Run intake**: ask the user "你有多少前置材料？(a) 已有草稿文档，给我路径 (b) 口述 idea，我直接听 (c) 完全空白，从头来"
4. **Initialize**: run `python ~/.claude/skills/aiwy-design/scripts/init.py <project_name>` from cwd. This creates `manifest.json`, `00_concept.md`, `decisions.md`, and the directory skeleton.
5. **Enter Phase 1 (Concept) grilling** following `references/workflow_concept.md`.

The user's args (after `/aiwy-new`) are typically the project name. If absent, ask in the first turn.
