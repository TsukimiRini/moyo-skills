# Tone calibration — operationalizing 基调

"基调" 是 vibey 词. 这个 skill 把它落到 5 个具体产出, 全在 `00_concept.md`, 全是下游 phase 强制兼容的约束.

## The 5 必产出

| 产出 | 字段 (in 00_concept.md) | 用途 (downstream) |
|---|---|---|
| 题材标签 | `genre_tags` | 全局 prompt prefix; 角色 / 世界 / 资产生成的总体氛围参考 |
| 参考作品 | `reference_works` | 写对白时锚定语气; 设计角色时找借鉴点; 防止用户和 AI 想象错位 |
| 红线 | `red_lines` | 每次出文 self-check; 拒绝违反红线的指令 |
| 写作示范段 | `writing_sample` | runtime 不直接注入, 但你 (Claude) 写任何对白前都要看一眼锚定语气 |
| 视觉风格关键词 | `visual_style_tags` | 所有 NovelAI 调用强制 prepend; 跨角色 / 跨界面风格一致性的根 |

## 怎么用

### 当用户给一个新指令时
你 (Claude) 应该:
1. 先 cat `00_concept.md` 看 5 项 (如果会话刚开始 / 没看过)
2. 接到指令后, 心里跑红线 self-check ("这指令是否违反某条红线？")
3. 如果是文本生成, 锚定 writing_sample 的语气
4. 如果是资产生成, 锚定 visual_style_tags + reference_works 的视觉风格

不要把 self-check 过程暴露给用户 — 他知道你在做就行.

### 当出现冲突时
用户的某次指令跟某个红线冲突. 怎么办?
- 直接照做 ❌ (违背了用户上次的设计承诺)
- 直接拒绝 ❌ (用户可能有正当理由想突破)
- ✓ 先指出冲突, 问用户是想 (a) 这次例外 (b) 调整红线 (需要 `/aiwy-unlock concept`) (c) 取消指令

例:
> 你刚才让我给某角色写一段跟人设相反的"突然温柔"内心戏。但红线写着"不允许角色 OOC 转向"。是想:
>   - (a) 这次破例, 不修红线
>   - (b) 把"OOC"的定义放宽 (revisit red lines)
>   - (c) 改成"表面冷淡, 内心剧烈波动" 的写法 (符合人设的"温柔暗涌")

## 5 项的常见短缺及应对

### 题材标签太宽
"奇幻" / "都市" — 不够锚定. 推回去要更具体的组合: 例如 `<情感模式> / <氛围> / <题材>` 这种三段式标签.

### 参考作品没说"借鉴什么 / 不借鉴什么"
单纯列名字 = 没用. 用户看了 3 遍 X 不代表你知道她为啥喜欢. 必须问"借鉴哪一面 / 不借鉴哪一面".

### 红线写得太抽象
"不写让人不爽的剧情" = 啥都不算红线. 推回去要具体: "不写 BE / 不允许多人同时正式交往 / 不写未成年角色性场面".

### 写作示范段太短或是 lorem
< 50 字或显然是占位符 → 推回去拿真东西.

### 视觉风格关键词只有 1-2 个
NovelAI 风格漂移 90% 来自这里. 至少 3 个, 最好 5-7 个 (画风 + 光感 + 调色 + 笔触).

例好的:
```
visual_style_tags:
  - anime style
  - soft watercolor lighting
  - muted palette
  - detailed line art
  - slight horror undertone
  - cinematic composition
```

## 审计 5 项是否健康

跟用户走查 `00_concept.md` 一遍即可. 概念上, 健康的 5 项满足:
- 一个不熟项目的人, 仅靠这 5 项 + concept 全部内容, 就能猜出后续 5 个角色大致是什么样的
- 5 项之间互相一致 (题材标签 ↔ 参考作品 ↔ visual style 不冲突)
- 写作示范段是用户的"实际写作", 不是范例 / 占位

如果不满足, 立项还没真锁好.
