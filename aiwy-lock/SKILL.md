---
name: aiwy-lock
description: Slash entry point for checkpointing the current phase of an AI 文游 design project. Use when the user types `/aiwy-lock <phase>`, says "锁定立项 / 角色 / 世界观 / 玩法 / 界面 / 资产", "把当前阶段定了", "checkpoint 一下", or wants to make a phase's artifacts authoritative. Must hand off to `aiwy-design` workflow. The phase argument is one of: concept, characters, world, gameplay, interfaces, assets.
---

# /aiwy-lock <phase> — checkpoint a phase

Thin entry point. Full semantics in `aiwy-design`.

## What to do

1. **Parse args**: phase ∈ `concept | characters | world | gameplay | interfaces | assets`. If missing, ask which phase.
2. **Skim the phase's artifacts** and ask the user to confirm "ready to lock?" — flag obvious gaps (empty sections, placeholder text) but don't enforce a strict schema.
3. **Run the lock**: `python ~/.claude/skills/aiwy-design/scripts/lock.py <phase> [--note "..."] [--key-decisions "..."]`.
4. The script appends a dated entry to `decisions.md` and updates `manifest.json`'s `locked_phases`.
5. **Brief the user** on what got locked and the next phase to work on.

## Lock semantics

A locked phase becomes authoritative. Downstream work must be consistent with it. If the user later wants to modify locked content, require explicit `/aiwy-unlock <phase>` and warn about which downstream artifacts may need re-validation.
