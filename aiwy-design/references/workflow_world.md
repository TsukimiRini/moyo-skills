# Phase 3 workflow — World (世界观)

Output: `world/worldview.yaml` (always-injected) + optional `world/lore_<topic>.md` (loaded on demand).

In character-driven AI 文游, world is **shaped to fit the characters**, not the other way around. So this phase is shorter than for sandbox / lore-heavy games. Don't over-engineer.

## Grilling tree for `worldview.yaml`

1. **era_tone** — 一段话讲清"这个世界看起来 / 感觉起来怎么样". 200 字内.
   - 例: "近未来都市，灯红酒绿但精神空虚；阶级固化严重，普通人被算法支配；表面繁荣下是病态的人际关系。"

2. **core_rules** (≥ 3 条) — 这世界怎么运作的根本规则
   - 每条要写: `domain`(魔法/科技/社会/经济/阶级) + `rule`(怎么运作) + `implication`(对玩家什么影响)
   - 推荐挑：玩家最常碰到的 3 个领域。AI 会在 runtime 用这些规则填补剧情. 漏掉的领域会被 AI 自由编造，可能跟你设想冲突.

3. **player_position** — 玩家在世界里的定位
   - 一段话: 玩家身份 + 跟主流社会的关系 + 资源水平 + 能用的"路径" (合法 / 灰色 / 黑色)
   - 必须跟 `concept.player_locked_traits` 一致

4. **visual_keywords** (≥ 3) — 给资产生成用的世界观视觉关键词
   - 跟 `concept.visual_style_tags` 是叠加关系, 而不是替换. 这里写场景特化的, 例: `neon-lit alley, art deco interiors, 1980s shanghai vibe`

## 可选 (建议但不必填)

- **factions** — 主要阵营, 每个写 `name / stance / power / relation_to_player`
- **geography** — 玩家会去的关键地点, 每个写 `name / role / key_features`. 这跟 interfaces 阶段的 background art 直接相关.
- **timeline** — 重要历史事件 (相对玩家进入故事的时间点)
- **taboos** — in-world 禁忌 / 红线. 跟 concept.red_lines (玩法层面的) 不同, 这是世界内的.

## Extended lore — `world/lore_<topic>.md`

如果某个 lore 话题 (例: 某种神器的历史 / 某个组织的内部架构) 内容很多但**不需要每次注入 runtime**, 单独存一个 `lore_<topic>.md`. 在 `gameplay/03_runtime_injection.md` 里某个 interface 的 `conditional_includes` 中按需引用.

例:
```
world/
  worldview.yaml          # 总是注入
  lore_dark_pact.md       # 只在玩家解锁某剧情后注入
  lore_school_history.md  # 只在校园界面注入
```

## Don'ts

- **不要在 worldview 写故事**. 故事是 runtime AI 生成的. 这里只写"世界规则".
- **不要把 world 写成百科全书**. token 预算 ≤ 800 (worldview.yaml 部分). 想多写的话开 `lore_*.md`.
- **不要跟 concept 冲突**. visual_keywords 不能跟 concept.visual_style_tags 时代风格相左. 校验下.
