---
name: game-template
description: 在 starworld 项目中创建和修改游戏模板（InterfaceTemplate）。当用户想要创建新游戏界面、修改现有模板、设计聊天界面、配置AI响应格式、设置触发器或变量替换规则时，必须使用此 skill。触发词包括：创建游戏模板、新建界面、修改界面、修改游戏、修改页面、修改html、html页面、页面模板、HTML模板、嵌套提取规则、变量替换规则、触发器配置、修改触发器、触发器、游戏界面设计、InterfaceTemplate、这个页面、这个模板、这个界面、这个html。
---

# Game Template Skill

帮助在 starworld 项目中创建和修改游戏模板（`InterfaceTemplate`）。

## 项目背景

starworld 是一个 AI 驱动的互动游戏平台。每个游戏界面由 `InterfaceTemplate` 定义，包含五个核心部分：

1. **HTML Template** — 界面的视觉框架（HTML + CSS）
2. **嵌套提取规则** — 从 AI 响应中提取结构化变量的正则规则
3. **变量替换规则** — 将提取的变量渲染到 HTML 中的规则
4. **触发器** — 用户交互事件与 AI 调用的绑定
5. **上下文结构** — 定义如何为 AI 组装对话上下文

类型定义见 `/src/types/game-structure.ts`，示例见 `/src/examples/test_game_template/`。

## 文件结构

每个游戏模板是一个目录，同时包含 TOML（编辑源）和 JSON（转换产物）：

```
my_template/
├── template.toml        — HTML + 变量替换规则（编辑源）
├── template.json        — 转换产物
├── response_format.toml — AI 响应格式 + 嵌套提取规则（编辑源）
├── response_format.json — 转换产物
├── trigger.toml         — 触发器数组（编辑源）
└── trigger.json         — 转换产物
```

全局变量放在游戏根目录（包含所有模板的父目录）：

```
my_game/
├── global_variables.toml
├── global_variables.json
├── my_template_1/
└── my_template_2/
```

## 格式转换工具

`.claude/skills/game-template/scripts/convert.py` 提供 JSON ↔ TOML 双向转换，需要 Python 3.11+。

```bash
# TOML → JSON（编辑完 TOML 后执行）
python .claude/skills/game-template/scripts/convert.py toml2json <dir>

# JSON → TOML（从已有 JSON 生成 TOML 编辑源）
python .claude/skills/game-template/scripts/convert.py json2toml <dir>
```

input 和 output 是同一目录，转换结果直接覆盖同目录内的对应文件。

**AI 编辑工作流**：编辑 TOML → `toml2json` 转换 → 存回数据库。如需从数据库导出编辑，先 `json2toml` 转换再编辑。

---

## 工作流程

**新建模板**：
1. 在 `src/examples/test_game_template/` 下新建目录
2. 创建三个 TOML 文件（语法参考各组件章节）
3. 执行转换：`python .claude/skills/game-template/scripts/convert.py toml2json src/examples/test_game_template/my_template`

**修改已有模板**：
1. 直接编辑目录下的 TOML 文件
2. 执行转换覆盖 JSON（同上命令）

**从 JSON 反向导出 TOML**（如果只有 JSON）：
```bash
python .claude/skills/game-template/scripts/convert.py json2toml src/examples/test_game_template/my_template
```

**新增或修改全局变量**：
1. 编辑游戏根目录下的 `global_variables.toml`（格式见 `references/global-variables.md`）
2. 执行转换：`python .claude/skills/game-template/scripts/convert.py toml2json src/examples/test_game_template`

> 始终以 TOML 为编辑源，JSON 是转换产物。每次修改 TOML 后必须重新执行转换脚本。

### 设计顺序

按以下顺序设计，因为后三个都依赖 HTML 结构：

```
HTML Template → 嵌套提取规则 → 变量替换规则 → 触发器 → 上下文结构
```

---

## 组件一：HTML Template

```toml
html_template = '''
<!DOCTYPE html>
...
'''

[[variable_replacement_rules]]
target_selector = "#target-id"
replacement_type = "append"   # 或 "replace"
template = '<div>{{variable}}</div>'
```

设计要点：
- 需要动态填充内容的区域给唯一 `id`（如 `id="messages-container"`）
- 交互元素给唯一 `id`（如 `id="send-button"`、`id="message-input"`）
- CSS 写在 `<style>` 标签内，不依赖外部文件
- 移动端：用 `100vw`/`100dvh` 而非固定像素，触控目标最小高度 44px
- `dvh` 能正确处理移动端浏览器地址栏：`height: 100vh; height: 100dvh`
- 箭头等 Unicode 字符在 iOS 上可能渲染为 emoji，加 `&#xFE0E;` 强制文本渲染
- 纯 UI 逻辑（翻页、滚动、模态框开关）可直接写在 `<script>` 标签里

**多帧视觉小说界面**（每帧含多个媒体变量、多角色立绘、帧级副作用）的高级模式见 `references/advanced-html-patterns.md`，包含：`#script-data` 隐藏容器、跨帧状态继承、帧级副作用触发、多角色立绘。

---

## 组件二：嵌套提取规则（ResponseFormat）

```toml
[response_format]
example = """
AI 响应示例文本
"""
format_note = "给 AI 的格式说明（可选，会注入到 prompt 中）"

[response_format.nested_extraction]
regex = '正则表达式（包含命名捕获组）'
occurrence = 1   # 或 'multiple'

[response_format.nested_extraction.nested_layers.capture_group_name]
regex = '子层正则'
occurrence = 'multiple'
```

**核心原则**：用正则的嵌套层级分解 AI 响应。第一层提取宏观结构，第二层对第一层的某个捕获组再次匹配，支持三层及以上嵌套。

### 变量引用规则

- 第一层捕获组：`{{捕获组名}}`，如 `{{grand_prix}}`
- 第二层（`occurrence: 'multiple'`）：`{{父层key.子捕获组名}}`，如 `{{dialogue_list.speaker}}`
- 第三层：`{{祖父层key.父层key.子捕获组名}}`，如 `{{battle_data.round_actions.actor}}`
- 内置变量：`{{TIMESTAMP}}`、`{{DATE}}`、`{{TIME}}`

> 常见模式（单条消息、多条消息、书名号对话、结构化多字段、三层嵌套）见 `references/nested-extraction-patterns.md`。

---

## 组件三：变量替换规则（VariableReplacementRule[]）

```json
[
  {
    "target_selector": "#story-list",
    "replacement_type": "append",
    "template": "<div class=\"story-line\"><div class=\"speaker\">{{dialogue_list.speaker}}</div><div class=\"content\">{{dialogue_list.content}}</div></div>"
  },
  {
    "target_selector": "#grand-prix",
    "replacement_type": "replace",
    "template": "<span id=\"grand-prix\">{{grand_prix}}</span>"
  }
]
```

- **`append`**：向目标元素内部追加内容（适合消息列表、日志等）
- **`replace`**：完全替换目标元素的内容（适合状态显示、单值更新）
- `occurrence: 'multiple'` 的变量，每条匹配结果触发一次 `append`
- `target_selector` 中的 id 必须在 HTML template 中存在
- `template` 中属性值里的双引号需转义为 `\"`

> `replace` 会销毁旧节点，导致绑定在其上的事件监听器和 MutationObserver 失效。与内嵌 JS 混用时的陷阱和解法见 `references/advanced-triggers.md`。

---

## 媒体变量（Media Variables）

媒体变量将一个普通变量与素材库中的图片/音频/视频绑定，引擎渲染时自动把变量值解析为素材 URL 注入 HTML。

**命名规范**：所有媒体变量**必须以 `_asset` 结尾**，没有例外。

```
portrait_asset   ✅      portrait        ❌
gp_track_asset   ✅      gp_track_image  ❌
bgm_asset        ✅      bgm_track       ❌
```

嵌套捕获组同样适用，捕获组名本身要以 `_asset` 结尾：

```toml
[response_format.nested_extraction.nested_layers.dialogue_list]
regex = '【(?<speaker>[^|】]+)\|(?<portrait_asset>[^】]*)】\s*(?<content>[\s\S]*?)(?=【|$)'
occurrence = 'multiple'
```

### 在 HTML 中声明媒体占位符

引擎支持三种注入方式：

**方式一：直接作为 src**（最常见）
```html
<img id="bg-image" src="{{gp_track_asset}}" class="bg-layer" />
<audio id="bgm" src="{{bgm_asset}}" autoplay loop></audio>
```

**方式二：CSS background-image**
```html
<div style="background-image: url({{card_bg_asset}})"></div>
```

**方式三：data 属性 + JS 读取**（适合需要 JS 动态切换的场景，如翻页立绘）
```html
<div class="story-line" data-portrait-asset="{{dialogue_list.portrait_asset}}">...</div>
```
```javascript
const url = currentLine.dataset.portraitAsset || '';  // data-portrait-asset → dataset.portraitAsset
portraitImg.src = url;
```

### 配置媒体联动

在 UGC 编辑器的变量管理器中，找到该变量，点击"联动素材库"，配置素材选项：

- **默认素材**（`is_default: true`）：变量值为空或无匹配时使用
- **条件素材**：当某个变量满足条件时使用，支持 `==`、`!=`、`contains`、`in`

引擎渲染优先级：变量值已是 URL → 精确匹配 asset_id → 满足条件的素材 → 默认素材 → 空 URL。

典型用法：根据全局变量（如当前大奖赛）自动切换背景图，在变量管理器里为 `gp_bg_asset` 配置多个条件素材即可。

---

## 全局变量（Global Variables）

全局变量在整个游戏会话中持续存在，跨模板共享。典型用途：玩家阵营、进度标记、跨页面传递的状态。

声明格式、读写方式、常见模式（按全局变量初始化页面、状态门控、注入上下文）见 `references/global-variables.md`。

---

## 组件四：触发器（TemplateTrigger[]）

```toml
[[triggers]]
trigger_name = "触发器名称"

[triggers.trigger_condition]
type = "html_event"          # html_event | variable_condition | on_load | always
event_type = "click"         # click | keypress | change | submit
element_selector = "#btn-id"

[[triggers.action_sequence]]
action_type = "update_variable"   # update_variable | trigger_ai_response | jump_interface
action_order = 1

[[triggers.action_sequence.action_params.variable_updates]]
variable_name = "user_input"
variable_value = '{{input:#input-id::value}}'

[[triggers.action_sequence]]
action_type = "trigger_ai_response"
action_order = 2
```

### 常见触发器模式

**发送消息**（最常见）：
```json
{
  "trigger_name": "发送消息",
  "trigger_condition": { "type": "html_event", "event_type": "click", "element_selector": "#send-btn" },
  "action_sequence": [
    {
      "action_type": "update_variable",
      "action_params": { "variable_updates": [{ "variable_name": "user_input", "variable_value": "{{input:#user-input::value}}" }] },
      "action_order": 1
    },
    { "action_type": "trigger_ai_response", "action_params": {}, "action_order": 2 }
  ]
}
```

**回车键发送**：同上，`event_type: "keypress"`，`element_selector: "#user-input"`。

**页面加载**：`trigger_condition: { "type": "on_load" }`，action 为 `trigger_ai_response`。

**跳转界面**：`action_type: "jump_interface"`，`action_params: { "target_template_id": "目标模板id" }`。

> 条件执行（`__execution_condition`）、expression 模式变量更新、变量条件触发器、`replace` 与 JS 兼容性等高级用法见 `references/advanced-triggers.md`。

---

## 组件五：上下文结构（ContextStructure）

`context_structure` 定义每次 AI 调用时如何组装 prompt 上下文，按 `context_items` 数组顺序注入。

```json
{
  "context_structure": {
    "context_items": [
      { "type": "worldsetting", "router": "character/夏以昼" },
      { "type": "worldsetting", "router": "rule/线上聊天" },
      { "type": "description", "content": "你是夏以昼，用简短的线上聊天风格回复。" },
      { "type": "history", "filter": { "interface_template_id": "chat-template", "limit": 8 } },
      { "type": "variable", "variable_name": "player_name", "variable_scope": "global" }
    ]
  }
}
```

可用的 `type` 值：
- `worldsetting` — 注入世界设定（按 `router` 查找）
- `description` — 注入静态描述文本
- `history` — 注入对话历史，可选 `filter`（`interface_template_id`、`limit`、`role`）
- `user_action` — 注入用户操作
- `variable` — 注入变量值，`variable_scope` 为 `global` | `interface` | `temporary`

---

## 输出规范

1. **新建模板**：输出完整的 `InterfaceTemplate` JSON，并说明每个部分的设计决策
2. **修改单个组件**：只输出被修改的组件，并解释改动原因
3. **验证一致性**：确保 HTML 中的 `id` 与变量替换规则的 `target_selector` 和触发器的 `element_selector` 一致
4. **正则测试**：提供嵌套提取规则的测试示例，展示如何从 `example` 中提取变量

如果用户只提供了部分信息，先输出可以确定的部分，并明确标注需要用户补充的内容。
