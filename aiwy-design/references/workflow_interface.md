# Phase 5 workflow — Interfaces (界面)

> **重要**: AI 文游里**没有 scene** (剧情场景). 实际剧情由 runtime LLM 在玩家进入某个界面时, 基于 `gameplay/03_runtime_injection.md` 里给该界面定的 injection 配方 + 玩家上下文 + 当前 state 自由生成. 所以本阶段不写任何剧情脚本.
>
> **本阶段产出 = 玩家可见的所有界面的 UI/UX 设计**. 纯 UI/UX, 不掺杂逻辑 / state / 注入配方 (那些都在 gameplay/ 里). 这一阶段产出指导用户在他自己的平台上写界面前端.
>
> **这是个 3-step flow**, 不要跳:
> 1. **UI style guide** (`ui/style_guide.md`) — 全局视觉规范, 锁定调子
> 2. **Interface sitemap** (`interfaces/_sitemap.md`) — 自顶向下列所有界面 + 跳转关系图
> 3. **Per-interface specs** (`interfaces/<id>.md`) — 一个一个写每个界面的 UI/UX 详情

跳过 step 1 直接画 interface, 容易每个界面风格各搞一套; 跳过 step 2 直接挑一个 interface 写, 容易漏界面 / 跳转回路对不上.

---

## Step 1 — UI style guide (`ui/style_guide.md`)

**先于任何 interface 文档存在**. 它是后续所有 interface 文档的视觉参考标准.

`ui/style_guide.md` 是给作者(以及未来在平台上写前端实现的自己 / 美工)看的设计文档, **不被 runtime 注入**. 用 free-form md 写, 可读性优先.

骨架建议:

```markdown
# UI style guide

## 风格定调
- 整体氛围 (一两句话). 例: "深夜手机屏的冷白光底, 极简, 像 iOS 短信但更黑更窄"
- 参考 (列 1-3 个具体的 app / 游戏 / 视觉作品 — 越具体越好)

## 色板
- Primary: #xxxxxx — 用于 ...
- Background: #xxxxxx — 用于 ...
- Accent / 警示: #xxxxxx
- 文字主色 / 次色 / 禁用色

## 字体
- 标题字体 / 正文字体 / 等宽字体 (如有)
- 玩家输入区字体 (如有特殊)

## 控件视觉
- 按钮 (圆角 / 颜色 / hover 状态)
- 输入框
- 弹窗 / Toast
- 列表项

## 排版基调
- 行距 / 字号档位 / padding 习惯

## 跟 NovelAI visual_style_tags 的关系

`00_concept.visual_style_tags` 是 **NovelAI 出图 (角色立绘 / 场景背景图) 用的标签**, 跟这里的 **UI 控件视觉规范是两层**:
- visual_style_tags → 影响 NovelAI 生成的 .png 内容 (画风 / 灯光 / 人物造型基调)
- 本文档 → 影响平台 UI 控件的 CSS / 字体 / 色板

两者**调性应该一致** (都偏冷调 / 都偏暖调) 但不直接互相引用. 风格不一致时容易出现"立绘是赛博朋克但 UI 是日系小清新"的 mismatch.
```

跟用户**不要走完整问答**, 让他贴一张参考图 / 描述一段就好, 你帮他结构化. 这是相对快的一步, 避免陷入色板细抠.

**Lock**: `ui/style_guide.md` **没有独立的 lock**, 它跟 sitemap + 各 interface 一起进 `interfaces` lock. 但**它要先稳定再写 interface** — 先 lock 它的"风格定调"段, 控件细节可以边写 interface 边补.

---

## Step 2 — Interface sitemap (`interfaces/_sitemap.md`)

自顶向下列出**所有界面 + 跳转关系**. 这一步产出之前**不要碰任何具体 interface 文档**. Sitemap 锁住的是"项目一共有多少个交互面 / 它们怎么串"的拓扑.

`_sitemap.md` 不被 runtime 注入. 给作者用. 骨架:

```markdown
# Interface sitemap

## 入口
游戏开始后玩家落到哪个界面? (例: `home_screen` 主菜单)

## 全部界面清单

| ID | display_name | category | 一句话功能 |
|---|---|---|---|
| home_screen | 主屏 | system | 游戏入口, 选择存档 / 开始 |
| daily_hub | 每日决策 | custom | 每天选时段动作的中枢界面 |
| phone_chat | 短信 | chat | 跟单个 NPC 文字聊天 |
| irl_dialogue | 面对面对话 | dialogue | 在地点跟 NPC 当面聊 (带立绘) |
| status | 状态 | status | 看好感度 / 资源 / 日历 |
| inventory | 物品 | inventory | 看收藏 / 道具 |
| settings | 设置 | system | 音量 / 存档 / 退出 |
| ending | 结局展示 | system | 30 天后展示结局 |

## 跳转关系

用 mermaid / ascii 画一张图. mermaid 比较容易维护:

\`\`\`mermaid
graph TD
  home_screen --> daily_hub
  daily_hub --> phone_chat
  daily_hub --> irl_dialogue
  daily_hub --> status
  daily_hub --> inventory
  daily_hub -.30天到.-> ending
  phone_chat --> daily_hub
  irl_dialogue --> daily_hub
  status --> daily_hub
  inventory --> daily_hub
  any --> settings
\`\`\`

## 跳转触发说明 (跳转图里说不清楚的)
- daily_hub → phone_chat: 玩家点"看手机"图标进入. 选具体聊谁后进入对应 NPC 的会话.
- daily_hub → ending: 不是手动触发, 是 `current_day == 30` 时段结束自动跳转.
```

**Grilling 关键问题**:
- **每个界面都能从某处进得来吗** — 没有入口的界面 = 死代码.
- **每个界面都有出口吗** — 进去就出不来 = 困住玩家 (settings / ending 除外).
- **有没有界面跟 daily_hub 之外的界面互连?** — 比如 phone_chat 里能不能直接打电话进 phone_call. 这种 cross-jump 容易漏掉.
- **跟 `gameplay/00_loop.md` 的循环对得上吗** — 循环里说"每个时段玩家可去地点 / 看手机 / 自习", 那 sitemap 里就该有对应的"去地点(=irl_dialogue)" / "看手机(=phone_chat)" / "自习" 三种入口.

**Lock**: sitemap 跟 ui style guide 一起进 `interfaces` 总 lock. 但**sitemap 没稳定就不要往下写 interface** — 否则后面要回来改 ID 改连接关系会牵动每个 interface 文档.

---

## Step 3 — Per-interface specs (`interfaces/<id>.md`)

为 sitemap 里每个 interface 写一份独立的 UI/UX 设计文档. 一个 interface 一个 md 文件.

Interface 文件**不被 runtime 注入**, 是给作者(以及在平台上写实现的自己 / 美工)看的 UI/UX 设计文档. 用 md 写, 可读性优先.

### 设计边界 (重要)

**这份文档纯 UI/UX**, 不写:
- ❌ injection_recipe / 注入配方 — 在 `gameplay/03_runtime_injection.md`
- ❌ state reads / writes / 公式 — 在 `gameplay/01_state.md` / `02_progression.md`
- ❌ 解锁条件 / 路线分岔 — 在 `gameplay/02_progression.md`
- ❌ 剧情 / 选项树 — 不存在(由 runtime LLM 生成)

它写:
- ✅ 这个界面长什么样 (背景 / 布局 / 控件)
- ✅ 玩家在这个界面能做什么 (输入 mode / 约束)
- ✅ 跟其他界面的进 / 出关系 (引用 sitemap)
- ✅ 需要的视觉资产 (背景图 / 立绘 / sticker)
- ✅ 动效 / 特殊交互细节 (如有)

### 骨架

```markdown
# Interface: <interface_id>

**Category**: chat / dialogue / phone_call / status / inventory / system / custom
**One-liner**: 这个界面的功能是什么 (一句话, 同 sitemap)

## Layout
界面整体布局描述. 可贴 ascii 框图 / 描述区域划分:
- 顶栏: ...
- 主区域: ...
- 底栏 / 输入区: ...
配合 ui/style_guide.md 的色板和控件风格.

## Player input
- Mode: free_text / choice_list / mixed / none
- Constraints: 例 ≤ 50 字 / 不允许 OOC
- Example inputs: 玩家典型会输入什么

## Visual needs
- Background: <bg 文件名, 后续 assets 阶段生成. 一句话气质描述>
- UI elements: 按钮 / 图标 / 框架元素 (引用 ui/style_guide.md 的控件规范)
- Character portraits: 这个界面会显示哪些角色立绘 / 在哪个位置
- Stickers / 表情包: 拉哪些角色的 sticker 包 (如有)

## 跳转
- 进入来源: <从哪些界面来> (跟 _sitemap.md 一致)
- 出口: <跳到哪些界面 / 通过什么操作>

## Interaction notes (可选)
特殊交互 / 动效 / 反馈 (如: "玩家发完消息后输入框 disable 1.5s, 期间显示对方'正在输入...'")
```

### Grill 关键问题 (per interface)

- 输入 mode 是什么? free_text 的话有没有字数 / 内容约束? choice_list 的话选项是 runtime LLM 生成还是预设?
- 在场角色多少? 同时显示几个立绘?
- 跟 sitemap 描述的进入 / 退出关系一致吗?
- 跨平台 / 跨设备布局有没有特殊要求?

**不要 grill** 跟数据 / 注入 / state 相关的 — 那些已经在 gameplay phase 处理过. 这里发现 gameplay 那边遗漏了, **要么去补 gameplay 文件, 要么 unlock gameplay phase**, 不要在 interface 文档里偷偷塞.

---

## Cross-interface 一致性检查

完成所有 interface 后:

1. **Sitemap 完整性**: `_sitemap.md` 列的每个 interface 都有对应 `<id>.md` 文件 (`/aiwy-lock interfaces` 前会查)
2. **跳转闭环**: 各 `<id>.md` 的"跳转"段跟 sitemap 互相对得上, 没人是孤岛
3. **角色覆盖**: 每个出场角色都至少在一个 interface 被引用过 (Visual needs / Character portraits 段)
4. **跟 gameplay 对齐**: `gameplay/03_runtime_injection.md` 里出现的 interface_id 跟 `_sitemap.md` 列表一致 — 一对一. 不一致时优先以 sitemap 为准, 回去补 gameplay (如果 gameplay 已 lock 则 unlock).

## /aiwy-lock interfaces

锁定后, assets 阶段会按各 interface 的 `Visual needs > Background` 描述生成界面背景图.

## Don'ts

- **不要在 interface 里写 injection_recipe / state / 解锁条件**. 那些属于 gameplay phase. 在 interface 文档里发现要写, 说明 gameplay 漏了, 回去补.
- **不要在 interface 里写剧情 / 选项树**. 由 runtime LLM 生成.
- **不要先写 interface 再补 sitemap**. 顺序反了, sitemap 失去自顶向下的意义, 容易漏界面.
- **不要每个 interface 各自定义视觉风格**. 全局风格在 `ui/style_guide.md`, 这里只引用 / 标注差异.
- **不要把 platform UI 实现细节(具体 CSS / 蓝图 node)写进 interface md**. 那是用户在他平台上写代码 / 拖蓝图. 这里只到"设计层面" — 长什么样、玩家怎么操作、跟谁连.
