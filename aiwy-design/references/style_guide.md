# Writing style for runtime-injected text

Every YAML in this skill is read by the runtime LLM, not the user. Style choices that read fine in a novel will get the AI confused, which produces character drift, OOC behavior, and "vibey" but unactionable output.

## Core principles

### 1. Behavior-anchored, not interpretive

❌ "她内心其实非常温柔。"  
✓ "她在被夸时会先否认再小声接受。"

❌ "他是一个充满矛盾的人。"  
✓ "他公开嘲讽对方时，私下会保留对话记录反复看。"

The AI needs to know what action to take. "Internal" qualities only matter if they manifest in observable behavior.

### 2. 现在时 + 陈述句

❌ "他曾经被父母严格管教，因此可能产生反叛心理。"  
✓ "他被父母严格管教，对权威表现出反叛。"

The runtime is operating in the eternal present. Past-tense / hedging confuses time anchoring.

### 3. 具体动作 / 具体语言

❌ "她说话很有风格。"  
✓ "她常用反问句反客为主：'你真的觉得这样合理？'"

❌ "他喜欢戏弄玩家。"  
✓ "他会突然问'你今天没想我吗？'然后看玩家反应；玩家害羞他不追，玩家回敬他会更进一步。"

### 4. 边界明确 (forbidden / 禁忌)

每个角色 `language_style.forbidden` 必填. 例:
> forbidden:
>   - 直接说"我爱你" — 会用"…还行" / "勉强算合格" 代替
>   - 主动联系玩家 — 永远是玩家先开口
>   - 在群聊 @ 玩家 — 不愿意在他人面前暴露关系

**反向锚定比正向锚定更省 token, 也更防 AI 漂移**. 与其写"他冷淡", 不如写"他绝不会主动".

### 5. Token 预算

不是越长越好. 长 prompt 不一定让 AI 更准, 反而稀释关键信息. 各文件软上限:
- `00_core.yaml`: ≤ 2500 tokens
- `01_chat_style.yaml`: ≤ 800 tokens
- `02_affection.yaml`: ≤ 1000 tokens
- `03_stickers.yaml`: ≤ 400 tokens
- `world/worldview.yaml`: ≤ 800 tokens

如果某条文件超了, 优先砍:
1. 重复信息 (在多处说同一件事)
2. 散文化的描述 (改成行为锚定)
3. 推论性 / 解释性内容 (例 "因为他童年被忽视, 所以…" → 直接写行为, 不写因果)

### 6. 占位符使用

`{{player_name}}` 等占位符是平台 runtime 替换的. 写人设时用占位符, 不要用具体名字 — 玩家可能改名.

## Anti-patterns (常见翻车)

### 装文艺 / 不接地气 (Claude / Opus 默认翻车区, 第 1 警觉)

写人设最高发的翻车点. Claude / Opus 写文字的默认惯性就是堆"文艺装 B 风", 这种语言塞给 runtime LLM, AI 拿到也只能跟着继续装下去演空气, 角色立不起来, 玩家也没记忆点.

❌
- "她内心深处隐藏着不为人知的脆弱"
- "他的眼神中流露出一丝难以察觉的疲惫"
- "笑容如午后阳光般温暖明媚"
- "命运的齿轮悄然转动 / 灵魂深处的炽热"
- 所有 "内心" / "灵魂" / "命运" / "深处" / "如同..." / "般..." / "悄然" / "无声地" / 散文比喻 / 四字成语堆叠

→ 没具体动作 / 没画面 / 没辨识度. AI 拿到也只能"嗯, 是个内心很复杂的角色", 然后瞎演.

✓
- "喜欢用嘲讽掩饰自己的真心，私底下为此感到痛苦"
- "对玩家有保护欲，但嘴上说出来的都是嫌弃"
- "知道自己不讨人喜欢，也不打算改，但怕玩家真的走"
- "生气不吵，改用很客气的语气对人"

→ 平实白话 + 没有文艺腔 + AI 拿到有具体方向可演.

**审稿动作**: 写完一段**逐句扫**, 见到上面❌列的高发翻车词 / 句式立刻**删了重写**, 用日常对话语言. 没有例外, 这一步比任何"行为锚定"原则都优先 — 因为装的文字哪怕"行为锚定"了也是死的.

### 散文心理描写
❌ 
> 她的心如那秋日的落叶，每一次飘落都带着不舍与期待。

→ AI 拿不到任何具体行动指令, 只能瞎演.

### 标签化人格
❌ 
> traits: [毒舌, 傲娇, 高冷, 闷骚, 病娇]

→ 5 个标签 + 0 个行为. AI 不知道在什么情境下展示哪种标签.

### 因果链推导
❌
> 因为父亲早逝，所以他早熟，所以他对年长女性有依恋，所以他会主动接近年长型的人。

→ AI 不需要知道因果, 它需要"他主动接近年长型". 因果留 `_discussion.md`.

### 跨段重复
❌ 同一个特征 ("她不擅长表达爱意") 在 personality / language_style / sexual_psychology 都写一遍

→ 浪费 token, 而且不同段写法不一致 AI 会困惑. 写一处即可, 其他段不再重复. 也不要靠 `# 见 personality.weaknesses` 这种段间引用 — runtime LLM 不会自动 follow 引用, 直接重写或者删除即可.

### 文件引用 / 跨文件指针
❌ 角色 yaml 里写 "见 04_visual.yaml 的 vibe_prose" / "见 _discussion.md 的设计意图" / "由 archetype 决定, 见 personality_*.yaml" / "(详见另一文件)"

→ Runtime LLM 眼里**没有文件这个概念** — 平台会把一组 yaml 拼成一坨纯文本扔进 prompt context, 所以 LLM 看到的只是 "见 04_visual.yaml 的 vibe_prose" 这串字符, 它没办法去打开任何文件. 文件是给作者用的组织单位, 不是 runtime 单位.

写文本的时候默认 LLM 就读到这一段, 不会去任何"别的地方"找补. 该 inline 就 inline (即便要在两份文件里都写一遍), 不该写就删掉, 但**不要写指针**.

## 项目专属段命名

要用动词锚定的命名约定:
- `<feature>_tactics` — "做这件事的策略集"
- `<situation>_behavior` — "在某情境下的行为"
- `*_protocol` — "处理某事的固定流程"
- `*_mechanism` — "心理 / 行为机制"
- `*_scenarios` — "可能发生的特定场景"

❌ 起名 `<character>_extra_info` (无意义) / `personality_deep_dive` (太泛)  
✓ 起名 `<feature>_tactics` / `crisis_exposure_scenarios` / `post_relationship_behavior`

理由: runtime 平台需要按段名挑选要不要注入. 命名要让"什么场合用"一目了然.
