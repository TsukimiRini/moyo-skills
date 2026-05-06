# Asset pipeline — visual generation

Two stages: NovelAI for canonical concept art, then a 图生图 (image-to-image) skill for variations / preserving consistency. As of writing, `liclick` is the i2i skill installed on this user's setup; if a different i2i skill (or a future `nano-banana` skill) is the only one available, use that instead — the workflow is the same.

## Hard rules (read before doing anything)

1. **Never call NovelAI without prepending `00_concept.visual_style_tags`**. This is the #1 cause of cross-character style drift. The skill assembler must always do `<global_style> + <character_specific_tags>`.
2. **气质中介层 is mandatory** before tag generation. It's the human-in-the-loop checkpoint that catches "I'm about to confidently produce the wrong-vibe image."
3. **If `00_concept.visual_style_tags` is empty**, refuse the task and tell the user to lock concept first.

## Asset types and where they go

| Target | Source design file | Output path |
|---|---|---|
| Character concept art | `characters/<name>/04_visual.yaml` | `characters/<name>/portrait/concept_v<N>.png` |
| Character expression variants | `characters/<name>/portrait/concept_canonical.png` | `characters/<name>/portrait/expressions/<name>_<expr>.png` |
| Interface background | `interfaces/<id>.md` (Visual needs section) | `interfaces/<id>_bg_v<N>.png` |
| Cover / key art | `00_concept.md` | `assets/cover_v<N>.png` |

## Step A — 气质中介层 (vibe prose)

50-100 字散文, 包含**首印象气质 + 微表情 + 构图建议 + 光感**. 这是给用户看的, 不是给 AI 看的.

例:
> 清冷少年感，鼻梁高挺微抬，眼神带审视意味，嘴角微勾透出讽刺。半身侧脸构图，光从右上斜射，阴影落颈侧；整体冷调但唇色偏暖，留一点"伪装下的人情味"。

写完 → 给用户过目 → 用户点头 / 调整. **不通过不进 Step B**.

## Step B — Tag 转化

把 vibe prose + 04_visual.yaml 里的 appearance 字段 + concept.visual_style_tags 拼成 NovelAI prompt:

```
<concept.visual_style_tags>,
<appearance Danbooru tags from 04_visual.yaml>,
<vibe-derived modifiers (composition / lighting / mood)>,
<quality boosters: masterpiece, best quality, very aesthetic, absurdres>
```

把组装好的完整 prompt 给用户过目. 用户可以增删 tag, 但 visual_style_tags 不能删 (会破坏一致性).

## Step C — NovelAI 生成

调用 `~/.claude/skills/novelai/generate.py`:

```bash
~/.claude/skills/novelai/generate.py "<assembled_prompt>" \
  --out characters/<name>/portrait \
  --width 832 --height 1216 \
  --n 1
```

**节奏**: 调 prompt 是个反复来回的过程, 所以默认 `--n 1` —— 一次出一张, 用户看完决定 prompt 怎么调, 再发下一发. 等 prompt 稳定了 (用户对 vibe 满意, 只剩看不同 seed 哪张构图最佳), 切到 `--n 4` 一发拿 4 张挑.

**Negative prompt**: **默认不传** `--negative` (空串). NovelAI v4 没有 negative 也能出干净图, 强行加经典 boilerplate (`lowres, worst quality, ...`) 反而可能误伤. 只有当迭代过程里反复出现某种**具体**问题 (例 总是冒 watermark / 总是闭眼 / 某种构图毛病) 才针对性加对应 negative tag, 加完观察是否解决.

Parameters:
- 角色立绘默认 832×1216 (portrait)
- 界面背景默认 1216×832 (landscape) 或 1024×1024 (square)
- 关键 CG 默认 1216×832

**重命名输出**: `generate.py` 默认输出文件名是 `nai-<ts>-<seed>-<i>.png`. 把它 rename 成 `concept_v<N>.png` 方便管理.

**Prompt 存档**: 每次 `generate.py` 调用会同时在 `--out` 目录里写一个 sidecar `nai-<ts>-<seed>.txt`, 记录这次发出的 prompt / negative / sampler / steps / scale / seed / size, 以及对应的 PNG 输出文件名. 它跟 PNG 同名前缀, 一起留着 — rename PNG 时**别动 txt**, 这样将来想知道某张图当时是用哪条 prompt 出的、想复刻 / debug 风格漂移, 直接看 txt.

## Step D — Canonicalize

用户挑出最满意的那张 → `cp <chosen>.png concept_canonical.png`.

这张图变成下游所有 i2i 变体生成的参考图. **不能删**.

## Step E — 立绘变体 (i2i, 可选)

只有当存在某个图生图能力的 skill 时才能做. 检查 (按这个顺序优先):
```bash
ls ~/.claude/skills/ | grep -E 'liclick|nano-banana|i2i'
```

最常见就是 `liclick`. 读它的 SKILL.md 看调用方式. 把 `concept_canonical.png` 作为 reference image, 加 04_visual.yaml 里的 `expressions_needed` 每条的 `prompt_addon` 生成变体.

输出到 `characters/<name>/portrait/expressions/<name>_<expr>.png`.

如果**没有任何 i2i skill**, 告诉用户:
> "没找到图生图能力的 skill (例 liclick / nano-banana). 跳过表情变体生成. 角色 concept 立绘已生成在 portrait/. 装好 i2i skill 后再回来跑 /aiwy-asset 即可补全表情包."

## 界面背景图

跟角色立绘流程一样, 但:
- vibe prose 描述的是"这个界面应该给玩家什么场所感". 例 phone_chat 界面: "深夜的卧室, 床边台灯, 手机屏幕反光打在脸上. 静谧但有点孤独感."
- tag 转化时不要 1girl / 1boy 这类 character tag. 反而要加 `no humans, scenery, indoor` 等场景 tag.
- 一致性靠 `visual_style_tags` + 项目的 visual_keywords (在 world/worldview.yaml).

## 一致性 troubleshooting

如果两个角色的立绘看起来风格漂移:
1. 检查 NovelAI prompt 里 visual_style_tags 是不是真 prepend 了 (打日志看)
2. 同 sampler / scale / steps?
3. 角色 04_visual.yaml 的 portrait_meta.lighting 是不是各写各的? 应该全项目共享一套灯光风格 (在 visual_style_tags 里写明)
4. 画风差异是不是来自 Danbooru tag 里夹带了不一致的"画师 tag"? (例 一个用了 "by amazyrei", 另一个用了 "by toosaka asagi" — 立刻翻车)

## Don'ts

- 不要为节省时间跳过气质中介层. 它是结构性防错.
- 不要在用户没选 canonical 之前生成 i2i 变体. 没有 stable reference, 一致性归零.
- 不要把 concept_canonical.png 跟 v1/v2 放一起会被覆盖的位置. 它是 source of truth.
