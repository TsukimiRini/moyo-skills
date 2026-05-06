# Phase 4 workflow — Gameplay (玩法)

> **本阶段做什么**: 把项目的**核心玩法逻辑**(怎么玩 / 状态怎么变 / 推进与解锁规则 / runtime 注入配方)从 drafts / decisions / 脑子里集中整理到 `gameplay/` 文件夹. 这是一个**"决策汇总"**阶段, 不是"凭空设计"阶段 — 大部分内容应该早已散落在 `00_concept.md`, `decisions.md`, `drafts/` 各处, 这一步把它们提炼出来.
>
> **为什么单独一个 phase**: gameplay 是 interface 的上游约束. 想清楚"玩法循环 / 状态怎么定义 / 哪些事件触发什么" 之后, 再去设计 interface 才有边界. 把 gameplay 跟 interface 混在一起会让 interface 文档变成"半玩法半 UI"的烂摊子.
>
> **跟其它 phase 的边界**:
> - `00_concept.md` 里写的是**主玩法骨架** (一句话级别 / 题材级别). 这里写**机制级别** — 具体怎么算, 怎么变, 怎么触发.
> - Character / world phase 里写的是**实体设定** (角色是谁 / 世界长什么样). 这里写**这些实体之间发生什么交互** (好感度 / 状态变化 / 解锁条件).
> - Interface phase 里写的是**UI/UX** (玩家怎么看见、怎么操作). 这里写的是**逻辑层** — interface 里发生玩家输入后, 系统怎么响应.

## Output

`gameplay/` 文件夹. 内部用编号 md 文件组织, 顺序自顶向下:

```
gameplay/
├── 00_loop.md               # 核心玩法循环 — 一局怎么开始 / 中段怎么玩 / 怎么结束
├── 01_state.md              # 状态变量 schema — 哪些 state 存在 / 取值域 / 默认值
├── 02_progression.md        # 解锁 / 路线分岔 / 结局触发条件
├── 03_runtime_injection.md  # per-interface 注入配方 (runtime 在该界面下注入哪些 yaml 块)
└── _discussion.md           # 设计意图 / 为什么这么设计 (NOT injected)
```

编号是顺序建议, 不是硬约束. 如果项目玩法简单 (例 仅好感度 + 单结局) 可以合并 `00_loop` + `02_progression` 成一个 `00_loop_and_progression.md`. 编号的意义是**告诉读者从上到下读**.

文件**用 md 写**, 但 `01_state.md` 的状态变量定义和 `03_runtime_injection.md` 的 injection_recipe 内嵌 fenced ` ```yaml ` block 保结构.

`gameplay/` 文件**会被 runtime 注入** — 但具体注入哪几份, 由 `03_runtime_injection.md` 的 per-interface 配方决定. 所以这些文件每段都要顶住"runtime LLM 直接读到这段"的标准 (参考 `style_guide.md`).

## 入口问题

跟用户对一下:

**"打开 drafts / 当前的 00_concept.md / decisions.md, 我们来把已经做过的玩法决策捋出来. 你脑子里现在的核心玩法循环是什么样? — 玩家进游戏后干什么、怎么推进、什么时候算 ending?"**

默认从 drafts 已有内容**反向归纳**, 而不是开盲盒重新设计. Grilling tree 是用来**找漏洞**的, 不是**走流程**的.

## 自顶向下的整理顺序

### 1. 00_loop.md — 核心循环

最顶层抽象. 一两段话讲清楚**一个玩家一局是怎么过的**. 必含:

- **进入态**: 玩家初始处于什么状态 (起点是什么界面 / 初始 stat 是什么)
- **中段循环**: 一天 / 一回合 / 一关怎么过 — 玩家做什么 → 系统响应什么 → 推进到什么
- **结束触发**: 什么条件下到 ending — 时间到了 / 某 stat 满了 / 某条件满足

例 (一份 GLO 文游的 00_loop.md):
> 玩家是某宿舍楼的住客. 一局 = 30 天日历. 每天分早午晚三个时段, 每个时段玩家可选择**去某地点 (推进与某 NPC 的关系) / 看手机 (聊天 + 推剧情) / 自习 (回复体力)**. 30 天结束时根据"主线结局 flag + 各 NPC 好感梯度 + 关键选择 archive"判定 ending — 主线 4 路 × 角色线锁定 + 真结局共 5+1 个分支.

注意:
- 写到这层就够, **不要**展开成"30 天每天的剧情" — 剧情是 runtime LLM 跑时生成的.
- 这里出现的"地点"、"看手机"、"自习" 等都是 **interface 名字的来源**. interface phase 会基于这里的循环展开.
- 这里出现的"好感梯度"、"主线 flag"、"体力"等 **都是 state 变量** — 在 01_state.md 里定义.

### 2. 01_state.md — 状态变量

游戏运行期所有可变量的清单. 用 yaml block 保结构:

```yaml
state_schema:
  affection:
    type: map<character_id, int>
    range: [0, 5]
    default: 0
    描述: 跟每个 NPC 的好感度梯度. 升降规则见各 NPC 的 02_affection.yaml (如果项目用了)
  stamina:
    type: int
    range: [0, 100]
    default: 80
    描述: 体力. 推进任何"互动选项" -10, "自习" +30, 每天早晨 reset 到 80
  story_flags:
    type: set<string>
    描述: 不可逆的剧情 flag. 例 "noren_revealed_secret" / "found_diary"
  current_day:
    type: int
    range: [1, 30]
  current_period:
    type: enum
    values: [morning, afternoon, evening]
```

**Grill 关键问题**:
- 每个 state 变量, **谁会写它? 在哪个 interface 下被写? 写规则是什么?** (公式 / lookup table / runtime LLM 自由判定)
- 是否有不可逆 flag (例 进了真结局路线就回不了头)? 那它属于 story_flags 而非 affection.
- 时间 / 天数 / 资源**满了之后**会发生什么? — 这个问题如果没答, 推进闭环没接好.

**不要把字符级别的 RPG-style stat 表搬过来** (HP / MP / 攻击 / 防御之类除非项目真的有战斗系统). AI 文游的 state 通常很轻 — 好感度 + 几个 flag + 时间 + 资源就够.

### 3. 02_progression.md — 解锁与结局

什么状态下解锁什么, 什么状态下到什么结局. 用人话写, 不要写代码 — runtime 不读代码, 它读"这种情况下你应该往这个方向推剧情":

```markdown
## 解锁条件

- **真结局路线触发**: `story_flags` 里同时包含 `noren_revealed_secret` 和 `found_diary`. 触发后, NPC 在所有界面的对话基调切到"知情人"模式 — 在角色 yaml 里有对应的 `secret_revealed_addendum` 段, runtime 会在这种条件下追加注入.
- **Noren 角色线锁定**: `affection.noren >= 4` 且 `current_day <= 20`. 锁定后其他 NPC 好感不再升, 主线开始走 noren 专属 events.

## 结局判定 (current_day == 30 时执行)

按优先级匹配第一个命中的:

1. 真结局: `"true_end"` flag 在 story_flags
2. 角色锁定线 ending: `affection.<character>` >= 5
3. 平庸 ending: 没有任何 affection >= 4
```

**Grill**:
- 解锁条件**一定要落到 state 上**. "玩家用心和 noren 互动" 不是条件, "affection.noren >= 4" 才是.
- 路线之间是不是真互斥? 是不是同一局可以同时走两条路线? 如果可以, ending 优先级是什么?

### 4. 03_runtime_injection.md — 注入配方

**这是从原 interface yaml 剥过来的核心字段**. 每个 interface_id 对应一段配方, 描述"在这个界面 runtime 生成剧情时, 注入哪些 yaml 块":

```markdown
## interface: phone_chat

\`\`\`yaml
always_include:
  - 00_concept
  - world/worldview
  - gameplay/00_loop
  - gameplay/01_state
per_character_blocks:
  # 当前界面在场角色, 每人注入这些块
  - 00_core
  - 01_chat_style       # 仅当对应文件存在
  - 02_affection        # 仅当好感度机制存在
conditional_includes:
  - when: "story_flags has 'noren_revealed_secret'"
    include: ["characters/noren/secret_revealed_addendum"]
  - when: "affection.noren >= 4"
    include: ["world/lore_dark_secret"]
\`\`\`

## interface: phone_call
...
```

**为什么放在 gameplay 而不是各 interface 文件**: injection 是 runtime 配置, 跟 state / progression 同属于"逻辑层". 集中放一处方便 cross-interface 看 — 例 想知道"哪些界面会在 noren 解锁后注入 secret addendum", 一个文件里搜就行.

**Grill 关键问题** (per interface):
- 这个界面下 AI 应该知道关于角色的多少信息? (决定 `per_character_blocks` 选哪些)
- 有没有"解锁后才能聊"的话题 / 才会显示的内容? (决定 `conditional_includes`)
- 有需要的 lore 吗? 引用 `world/lore_*.md` 哪些?

`per_character_blocks` 的 "仅当对应文件存在" 措辞: 项目可能没有 `02_affection.yaml` (无好感度机制), 这时候这一行就别加. **不要为了凑结构往 yaml 里写不存在的文件名**.

### 5. _discussion.md — 设计意图

为什么这么设计的来由 / 跟用户讨论中拍板的取舍 / 还没拍板的悬而未决. 这是给作者自己的 / 给未来回看的, **不被 runtime 注入**.

Free-form md.

## 跟既有 phase 的衔接检查

完成 gameplay 后:

1. **state 跟 character 一致**: `01_state.md` 里所有 `affection.<character>` 引用的 character_id, 在 `characters/` 下都存在
2. **lore 引用真实**: `03_runtime_injection.md` 里所有 `world/lore_*.md` 引用都对应真实文件
3. **interface 名是占位**: 这一阶段 `03_runtime_injection.md` 里的 interface_id 列表跟 interface phase 还没完全确定的清单**应该会有出入** — 这正常, interface phase 会把它对齐.
4. **`00_loop.md` 出现的"地点 / 操作"** 都会在 interface phase 变成具体 interface. 这里只起占位作用.

## /aiwy-lock gameplay

锁定后, interface phase 会在它的 sitemap 步骤参考 `gameplay/00_loop.md` 的循环, 在 per-interface 步骤参考 `gameplay/03_runtime_injection.md` 把 injection 配方对齐到具体 interface.

## Don'ts

- **不要在 gameplay 里写 UI/UX**. "玩家点击 X 按钮后" / "界面右上角显示 Y" 都属于 interface, 不属于这里.
- **不要把每个 NPC 的好感升降公式都搬到 gameplay/**. 每个角色的具体反应规则属于角色自己的 `02_affection.yaml` (如果用). gameplay 只描述**机制框架** (有好感度, 0-5 梯度, 升降由 runtime LLM 根据角色 yaml 判定).
- **不要写完整剧本 / 选项树**. 剧情是 runtime LLM 现场生成的, gameplay 只规定**逻辑框架**.
- **不要把 drafts 里的杂项笔记原封不动搬过来**. drafts 是用户给自己的备忘, gameplay 是结构化产出, 必须经过提炼.
