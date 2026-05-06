# Phase 2 workflow — Characters (角色)

For each character in `00_concept.protagonists`, build out their folder one at a time. Don't batch-process unless the user is explicit about it.

**Field reference**: `schemas/character.yaml` 是字段说明 + 起手骨架, 创建新角色文件时直接 cp 它的相关段落 (e.g. `cat schemas/character.yaml` 找到 `00_core.yaml:` 那段, 把 example structure 抠出来当起点) 到 `characters/<name>/00_core.yaml`, 再基于跟用户的对话填.

## Character folder layout

```
characters/<name>/
  00_core.yaml         # required, runtime-injected 核心人设
  04_visual.yaml       # required for /aiwy-asset (NOT runtime-injected)
  _discussion.md       # 设计意图 / 决策依据 (NOT injected)
  portrait/            # 立绘 + 表情变体 (assets 阶段才出)
```

**仅当项目 UX 真的需要时**, 加额外文件. 这些是项目特有的, 不要默认创建:

- `01_chat_style.yaml` — 仅当游戏有"聊天界面" + AI 演这个角色聊天时
- `02_affection.yaml` — 仅当游戏有显式好感度机制 + 不同等级触发不同行为
- `03_stickers.yaml` — 仅当聊天界面真的让玩家 / NPC 发表情包 (不是默认!)
- 项目专属段落塞在 `00_core.yaml` 末尾, 命名按 `*_tactics / *_protocol / *_mechanism / *_scenarios` 约定

判断原则: **仅当这份 YAML 会被 runtime 真的注入到某个界面 prompt 里**, 才创建它. 不要凭空预设玩法.

## Order of operations per character

Don't try to fill the whole folder in one pass. Drill in this order:

### Step 0 — 起手 mindset (CoT 一遍再下笔)

**写人设的文字质量决定角色立不立得住**. 后续 Step A-G 是结构填空, 但**填什么字进去**取决于这一步. 跳过这步直接 schema-driven 填 yaml = 出又装又空又没记忆点的 AI 烂大街人设, 玩家不会爱, runtime LLM 拿到也演不出灵气.

每写一段 (personality 块 / language_style 块 / 项目专属段 / sexual 段) 之前, **强制自己在脑子里过这三关**. 不写在 yaml 里, 但每一段文字都要扛住这三关的审视.

#### A. 文字定调: 大白话, 接地气, 不要装

要的: **平实白话**. 用普通人心里想事情、朋友间互相描述的语气写. 行为细节如果是角色真实模式可以写, 没想到具体例子就直接叙述心理 / 性格模式 — 两种都行. **不要为了"有画面感"刻意造场景** — 造出来的场景往往比直接说更装.

不要的: **AI (尤其 Claude / Opus) 默认会写的"文艺装 B 风"**. 高发翻车词: "内心深处" / "灵魂" / "命运" / "如同..." / "般" 句式 / 四字成语堆叠 / "悄然" / "无声" / "炽热" / "脆弱" / 散文化心理独白. 这种文字塞进 yaml, runtime LLM 拿到也只能跟着装下去演空气.

❌ "她内心深处隐藏着不为人知的脆弱"
❌ "他用冷峻的外表掩盖着炽热的灵魂"
❌ "她的笑容如午后阳光般温暖明媚"

✓ "喜欢用嘲讽掩饰自己的真心，但又在私底下为此感到痛苦"
✓ "对玩家有保护欲，但嘴上说出来的都是嫌弃"
✓ "知道自己不讨人喜欢，也不打算改，但怕玩家真的走"

每段写完**逐句扫一遍**, 看见"内心" / "灵魂" / "命运" / "如同" / 四字成语 / 散文比喻 → **立刻删, 重写平实白话**. 你 (Claude) 写文字的默认惯性就是装, 警觉点. 这一步没有例外.

#### B. 萌点和深度: 都从"具体画面 + 矛盾"来, 不从"苦难"来

**戳人的点 = 一个具体的特质 / 矛盾 / 反常反应**, 不是标签. 不写"傲娇 / 毒舌 / 病娇" — 写"嘴上嫌弃，私下一直盯着对方的动态".

**深度不来自苦难 / 创伤 / 童年阴影** — 这是 AI 默认 fallback, 烂大街. 深度来自**矛盾性 + 反差 + 惯性怪癖**: 这个角色在哪些地方的反应跟普通人不一样? 那一下就是深度.

**萌点和深度可以是同一个特质**: 同一个怪癖, 轻松场景是萌点, 沉重场景是深度. 例: "他做事认真但永远忘记关冰箱门" — 平时是萌点, 等他出了大事这个细节消失了, 就是让人难受的点.

**下笔前回答得出来才能写**: "这角色'戳'人的点是什么? 说一个具体特质, 让玩家看了心里会冒出'好喜欢'". 答不上来 → 回去想, 不要急着填 schema.

#### C. 切换视角: 用"同人女七七"的脑子写

写每一段之前, 切到一个虚构的"同人女七七"视角. 七七是这种人:

- 微博 mutual 几千, 每天嗑 CP, 自己写过 N 个 OC, 不嗑 BG 嗑 BL 嗑 GL 嗑姐弟嗑骨科, 眼光毒
- 写 OC 不写"完美攻 / 完美受", 要写"让我和我姐妹**很想**为他熬夜写 30k 字同人 / 嗑生嗑死"的那种
- 内心 OS 而不是 schema: 思考路径不是 "这个角色应该有 X 属性", 是 **"这个角色干啥能让我和我姐妹尖叫"**
- 嗑点词汇: "卧槽我懂了" / "啊啊啊这个画面" / "我可以" / "好戳" / "他要是这样我就死了" / "这个细节封神了"
- 极度反感"AI 文艺装 b 风" — 看见"她内心深处..." 立刻拍桌, "什么 b 玩意"

每写完一段, 先用七七的脑子过一遍, 内心 OS 默念三个问题:
1. 嗑得动吗?
2. 有具体特质 / 反应可以描述吗?
3. 室友看到这段会不会想给这个角色写同人?

任何一个答 "不行 / 凑合 / 还可以" → **删了重写**. 不要拿"差不多"的产物给用户交差, 七七会哭, 玩家更哭.

写完七七的视角下的内容, 再切回 schema-driven 视角把它**结构化**进 yaml — 按 personality / language_style / *_tactics 分段. **但结构化时不要把语言再装回去** — 七七的"他生气的时候很客气地叫您"放进 yaml 里也是这个原汁原味, 不要给它加上"用敬语作为冷暴力武器"这种解释性翻译.

---

走完 Step 0 再进 Step A.

### Step A — `_discussion.md` first (lightweight)

Get the user to dump in a few sentences:
- 这个角色在故事里的功能 (love interest? rival? mentor?)
- 跟玩家的关系动力学 (the emotional through-line — "暗恋哥哥的弟弟" / "想救赎玩家的破碎神")
- 一句话 hook — 最戳玩家的点

Save to `_discussion.md`. This frames everything that follows.

### Step B — `00_core.yaml` base_info + appearance + personality first pass

Schema-driven grill, in order:

1. **base_info** — name / title / identity / age / extra
2. **appearance** — physique / hair / eyes / face / outfit_default
3. **personality** — external / internal / 3-5 traits / weaknesses / habits

For each, recommend an initial fill based on the user's `_discussion.md` notes + concept's reference works. User accepts / corrects.

### Step C — `00_core.yaml` language_style

This is high-leverage and often skipped. Push back if user is vague.

- **tone** — 整体说话风格 (毒舌 / 闷骚 / 阳光 / 老成 / 装傻)
- **verbal_quirks** — 口癖 / 句式偏好 (特定句尾词 / 反问句 / 长 vs 短句)
- **forbidden** — 这个角色绝不会说的话 (例: "他绝不会说'我爱你'，会说'你想多了'")

If user struggles, dig out their reference works' character dialog and ask "类似 X 的说话方式吗？"

### Step D — Project-specific dynamics (the deep cut)

This is where most depth comes from. Ask:
- "这角色跟玩家有什么独特的互动模式？"
- "他/她有没有什么"无法自控"的行为机制？"
- "在某种特定情境下他/她会失控吗？"

Map answers to verb-anchored named sections in `00_core.yaml`:
- `<feature>_tactics` — 行为策略集
- `<situation>_behavior` — 在某场景下的行为
- `*_protocol` — 行为协议
- `*_mechanism` — 心理机制

### Step E — Sexual sections (if R18 ≥ medium)

Required by schema. Start with **psychology**, then experience, then quirks. Ask:
- "他/她跟性的关系是什么样的？"（动机 / 模式 / 与玩家的关系）
- "经验密度？" (处男 → 老练 → 玩家)
- "床上行为偏好？支配 / 服从 / 情感依赖型 / 工具型?"

Don't lift wholesale from references; this is character-specific.

### Step F — `04_visual.yaml`

- **vibe_prose** (50-100 字气质中介) — 见 `asset_pipeline.md` Step A
- **danbooru_tags** — 角色专属标签 (visual_style_tags 在调用时由 prompt assembler 自动 prepend)
- **portrait_meta** — composition / lighting / mood
- **expressions_needed** — 仅当游戏需要多个表情变体时填 (会传给 i2i skill, 例 liclick). 不需要可省.

### Step G — 项目可选文件 (仅当对应 UX 真的存在)

不要默认创建. 看 `00_concept.md` 列的"主玩法骨架"+"已知机制"判断有没有相关 UX:

- **`01_chat_style.yaml`** — 仅当游戏有"聊天界面" + AI 演这个角色发消息时
  - avatar_description / private_chat_with_player (tone / reply_speed / openings / language_features / emotional_concealment) / public_chat_behavior / digital_footprint
- **`02_affection.yaml`** — 仅当游戏有显式好感度机制 + 不同等级触发不同行为
  - levels (各级 behavior_changes / unlocked_topics / body_language) / transition_triggers / key_events
- **`03_stickers.yaml`** — 仅当聊天界面里 NPC 真的会发表情包. 大多数文游不需要.
- 项目专属段落塞在 `00_core.yaml` 末尾, 不开新文件 (除非段落特别大)

## Cross-character pass

完成所有角色后:

1. **走查每个角色 folder**, 修明显遗漏 (例 base_info / language_style 必填字段空着, 或者声明用了某玩法 UX 但对应 yaml 不存在)
2. **Read all `_discussion.md`** 一遍, 检查角色之间动力学是否合理 / 有趣 / 没冲突
3. **如果出现复杂关系** (例 多个攻略对象互相是情敌), 创建 `characters/_relations.yaml` 抽出共享关系网
4. **/aiwy-lock characters**

## Don'ts

- **不要主动给角色安插 backstory 而不问用户**. Backstory 应该跟玩家关系强相关; 你不知道用户的设计意图.
- **不要把 trait 写成形容词列表**. "毒舌 / 傲娇 / 高冷" → 这是标签, 不是 trait. Trait 是行为锚定的: "在被夸时会先否认再小声接受".
- **不要默认创建 01/02/03 这些 yaml**. 它们是项目特化的 — 没有对应 UX 就不开. 写人设的时候只需要 00_core + 04_visual + _discussion 就够了.
- **不要在角色 yaml 里写文件引用** ("见 04_visual.yaml" / "见 personality_*.yaml" / "由 archetype 决定" / "详见 _discussion"). Runtime 把一组 yaml 拼成一坨纯文本喂给 LLM, LLM 眼里没有"文件"这个概念 — 这种引用对它就是一串没用的字符. 文件是给作者用的组织单位, 不是 runtime 单位. 内容该 inline 就 inline (即便要在两份文件里都写一遍), 不该写就删掉; 段间引用 ("见 personality.weaknesses") 也别写, 重写或删除.
- **不要把用户给的立绘 prompt 整段塞进角色设定**. 拆开看: 里面"角色形象事实"的部分(发型 / 体型 / 服饰 / 五官)翻成日常叙述放到 `00_core.yaml` 的 appearance/attire; "画面风格 / 标签 / 镜头 / 光影"的部分(artist tag, masterpiece, cinematic lighting, dynamic angle 之类)只落到 `04_visual.yaml` 的 danbooru_tags / portrait_meta. 同一份内容不要在两个文件里都存. 草稿里跟人设无关的杂项(平台备忘 / 参考链接 / 用户给自己的笔记)归档到 `drafts/` 不要往 yaml 里塞.
