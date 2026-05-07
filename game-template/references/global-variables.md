# 全局变量（Global Variables）

全局变量在整个游戏会话中持续存在，跨模板共享。典型用途：玩家选择的阵营、进度标记、跨页面传递的状态。

## 声明格式（global_variables.toml）

```toml
[[global_variables]]
name = "team"
type = "string"
default_value = ""
description = "玩家所在的车队名"

[[global_variables]]
name = "has_sent_msg"
type = "boolean"
default_value = false
description = "是否在打开通讯录后进行过线上聊天"

[[global_variables]]
name = "gp_round"
type = "number"
default_value = 1
description = "第x站大奖赛"

[[global_variables]]
name = "contacts"
type = "array"
default_value = []
description = "联系人列表"
```

支持的类型：`string` / `number` / `boolean` / `array` / `object`

`default_value` 使用 TOML 原生类型：布尔用 `true`/`false`，数字直接写，数组用 `[]`，字符串用引号。

## 在触发器中读写全局变量

**读取（条件判断）**：在 `__execution_condition` 的 `conditions` 里指定 `scope = "global"`：

```toml
[[triggers.action_sequence.action_params.__execution_condition.conditions]]
kind = "variable"
scope = "global"
var_name = "team"
operator = "=="
value = "Red Bull"
```

**写入**：`variable_updates` 直接写变量名，引擎按名称识别 scope，无需额外声明：

```toml
[[triggers.action_sequence.action_params.variable_updates]]
variable_name = "has_sent_msg"
variable_value = 'true'
```

## 常见模式

### 模式一：根据全局变量初始化页面内容

页面加载时读取全局变量，按条件分支设置界面数据（f1_chat 的联系人列表初始化）：

```toml
[[triggers]]
trigger_name = "页面加载-按车队渲染联系人"

[triggers.trigger_condition]
type = "on_load"

# action_order=1：Red Bull 分支
[[triggers.action_sequence]]
action_type = "update_variable"
action_order = 1

[[triggers.action_sequence.action_params.variable_updates]]
mode = "expression"
variable_name = "contacts"
variable_value = '[{ id: "max", name: "Max Verstappen" }, { id: "yuki", name: "Yuki Tsunoda" }]'

[triggers.action_sequence.action_params.__execution_condition]
logic = "AND"

[[triggers.action_sequence.action_params.__execution_condition.conditions]]
kind = "variable"
scope = "global"
var_name = "team"
operator = "=="
value = "Red Bull"

# action_order=2：Ferrari 分支（同结构，条件改为 Ferrari）
```

### 模式二：状态门控（布尔标志）

用布尔全局变量记录"某件事是否发生过"，控制后续动作是否执行（f1_chat 的 `has_sent_msg`）：

```toml
# 发生时：置为 true
[[triggers.action_sequence.action_params.variable_updates]]
variable_name = "has_sent_msg"
variable_value = 'true'

# 离开页面时：仅在 true 时触发 AI，然后重置
[[triggers.action_sequence.action_params.__execution_condition.conditions]]
kind = "variable"
scope = "global"
var_name = "has_sent_msg"
operator = "=="
value = "true"

# 重置
[[triggers.action_sequence.action_params.variable_updates]]
variable_name = "has_sent_msg"
variable_value = 'false'
```

### 模式三：在上下文结构中注入全局变量

让 AI 知道当前全局状态：

```toml
# context_structure 中（JSON 格式）
{ "type": "variable", "variable_name": "team", "variable_scope": "global" }
{ "type": "variable", "variable_name": "gp_round", "variable_scope": "global" }
```

## 工作流

1. 在游戏根目录编辑 `global_variables.toml`
2. 运行转换：`python3 .claude/skills/game-template/scripts/convert.py toml2json <游戏根目录>`

> 转换后的 `global_variables.json` 需由用户手动导入数据库（UGC 编辑器 → 变量管理器 → 导入全局变量）。导入会**完全替换**数据库中的全局变量列表，以 TOML 为 source of truth。
