# Intake protocol — ingesting user input at project start

Use this when starting a new project (`/aiwy-new`). The user typically arrives with one of three states; ask them which, then follow the matching protocol.

## The intake question

> "你有多少前置材料？(a) 已有草稿文档（给我路径） (b) 口述 idea，我直接听 (c) 完全空白，从头来"

## (a) Draft document

User points you at a file (markdown, doc, plain text — could be in cwd `drafts/` or anywhere).

1. **Read the entire draft**.
2. **Save a copy** to `drafts/original_<timestamp>.md` if not already there. This is for archival; don't edit it.
3. **Map the draft onto the concept schema** (`schemas/concept.yaml`). For each required field, classify what you found:

   ```
   ✓ 已确认  — 草稿明确写了，可以直接填进 concept
   ⚠ 模糊需细化 — 草稿提到但模棱两可
   ✗ 缺失必填 — 草稿没提
   ⚡ 矛盾需选边 — 不同地方说法不一致
   ```

4. **Present the 4-zone summary to the user** before any grilling. Format:

   ```
   ✓ 已从草稿提取:
     - 题材: <从草稿提取的关键词>
     - 玩家锁定: <如有锁定项, 写在这里>
     - R18: explicit (从sexual_experience段推断)

   ⚡ 矛盾需选边:
     - 第3段说"4个攻略对象"，第7段又只列了3个名字 — 哪个对？

   ✗ 缺失必填:
     - 视觉风格关键词
     - 写作示范段
     - 红线 (你哪些事绝不写?)

   ⚠ 模糊需细化:
     - 主玩法说"分支选择"，但没说有几条主线 / 真结局机制
   ```

5. **Grill in this order**: ✗ 缺失（阻塞） → ⚡ 矛盾（选边） → ⚠ 模糊（细化）。Each question come with a recommended answer based on context.

6. After 立项 schema 填齐，写入 `00_concept.md`，提示用户检查并 `/aiwy-lock concept`.

## (b) Verbal idea — user describes now

1. **Listen** to the user's full description without interrupting (let them dump). Don't grill mid-stream.
2. **Echo back your understanding** in 80-150 字, structured: "我理解你想做的是 X，主要钩子是 Y，玩家代入 Z 的位置，对吗？"
3. **User confirms or corrects**. Iterate until echo matches.
4. **Ask for any draft-like artifacts** they've written — even half-baked notes, world maps, character sketches. If yes, proceed as (a).
5. **Otherwise**, treat the verbal description as a draft transcript and run the same 4-zone analysis as (a).

## (c) Blank slate

Rare for this user (per memory: they typically come with concrete ideas), but for completeness:

1. **Start with the 钩子 question**: "用一句话说清你想做的核心体验是什么？" Don't accept generic answers like "好玩" or "沉浸感" — push for specifics that name the unique emotional hook + setting.
2. Then **题材标签** (拿钩子里的关键词扩展)
3. Then **参考作品** (锚定方向)
4. Then **目标玩家 / 嗑点** (验证钩子有市场)
5. Then **R18 等级 / 红线** (锁约束)
6. Then **玩家锁定维度 / 主玩法骨架**
7. Finally **写作示范段 / 视觉风格关键词** (style 锚)

Each question one at a time, with recommended answer. If user struggles on any, propose 2-3 options for them to pick from.

## Don'ts

- **Don't write a draft for them** during intake. Only collect existing input + structure it. Generation happens in subsequent phase grilling.
- **Don't skip the echo step in (b)** — verbal ideas are easy to misinterpret; the echo catches it before you bake it into files.
- **Don't ignore drafts/** — if there's anything in `drafts/`, surface it and ask if it's relevant.
