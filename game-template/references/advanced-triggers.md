# 触发器高级用法

## variable_updates 的两种模式

**standard 模式**（默认，直接赋值）：
```json
{
  "variable_name": "user_input",
  "variable_value": "{{input:#user-input::value}}"
}
```

**expression 模式**（执行 JavaScript 表达式，可操作数组/对象）：
```json
{
  "mode": "expression",
  "variable_name": "schedule_array",
  "variable_value": "schedule_array.filter((_, i) => i !== Number(delete_idx))"
}
```

常用 expression 模式示例：
```js
// 追加元素到数组
"[...my_array, { time: tmp_time, event: tmp_event }]"

// 删除指定索引
"my_array.filter((_, i) => i !== Number(delete_idx))"

// 读取数组长度
"my_array.length"

// 映射转换
"raw_list.map(item => ({ time: item.time, event: item.event }))"
```

## 特殊变量语法

| 语法 | 说明 |
|------|------|
| `{{input:#selector::value}}` | 读取输入框的值（注意 `::value` 后缀） |
| `{{input:.class:first-child::text}}` | 读取元素的文本内容 |
| `{{increment:var_name}}` | 将变量值加 1 |
| `{{decrement:var_name}}` | 将变量值减 1 |

## `__execution_condition`：单个 action 的条件执行

在 `action_params` 中加入 `__execution_condition`，可以让该 action 只在满足条件时执行：

```json
{
  "action_id": "update-drivers-mclaren",
  "action_type": "update_variable",
  "action_order": 1,
  "action_params": {
    "variable_updates": [
      { "variable_name": "driver_name_1", "variable_value": "Lando Norris" }
    ],
    "__execution_condition": {
      "logic": "AND",
      "conditions": [
        { "kind": "variable", "scope": "global", "value": "McLaren", "operator": "==", "var_name": "team" }
      ]
    }
  }
}
```

`__execution_condition` 结构：
```typescript
{
  logic: 'AND' | 'OR'
  conditions: Array<{
    kind: 'variable'
    scope: 'global' | 'interface' | 'temporary'
    var_name: string
    operator: '==' | '!=' | '>' | '<' | '>=' | '<=' | 'contains'
    value: any
  }>
}
```

`trigger_ai_response` 同样支持 `__execution_condition`：
```json
{
  "action_id": "conditional-ai-call",
  "action_type": "trigger_ai_response",
  "action_order": 3,
  "action_params": {
    "__execution_condition": {
      "logic": "AND",
      "conditions": [
        { "kind": "variable", "scope": "global", "value": "true", "operator": "==", "var_name": "should_call_ai" }
      ]
    }
  }
}
```

## jump_interface 的正确写法

`target_template_id` 放在 `action_params` 里（不是顶层字段）：

```json
{
  "action_id": "go-to-event-page",
  "action_type": "jump_interface",
  "action_order": 2,
  "action_params": { "target_template_id": "event-template-id" }
}
```

## append_context：注入上下文消息

把一条消息定格为对话历史的一部分，以玩家侧（user）角色注入后续所有 AI 调用的上下文，**本身不发起 AI 请求**。消息会持久化在触发它的 state 上，之后的清屏、变量清空都不影响它。

```json
{
  "action_id": "inject-rent-event",
  "action_type": "append_context",
  "action_order": 1,
  "action_params": {
    "context_message": {
      "content": "【事件】三天过去了，房租账单已寄到。当前好感度：{{affection}}"
    }
  }
}
```

**规则**：
- `content` 与 `update_variable` 的 `variable_value` 同规则求值（宏 / `{{变量}}`），变量在**上下文组装时**解析为当时的值
- 同一个 action sequence 可以放多条 `append_context`，按 `action_order` 顺序进入历史
- 消息在历史中排在同一 state 的用户输入（`user_input`）**之前**
- 与 `trigger_ai_response` 同序列使用时，把 `append_context` 排在前面，本次 AI 调用即可看到该消息
- 可用于 `html_event`、`variable_condition`、`on_load` 触发器；**preload 中被引擎忽略并告警**（preload 每次渲染都执行，放行会导致每回合重复注入）
- 注入的消息同样参与长期记忆总结，不会在历史被总结后丢失

**典型场景**：on_load 注入"进入新章节/时间流逝"事件、点击道具后注入"（玩家使用了 X）"、变量条件达成时注入剧情转折旁白。

**不要再用旧 workaround**（给 `user_input` 赋值但不触发 AI）：`user_input` 是每次渲染边界都会被清空的工作寄存器，且重复的常量值会被残留检测丢弃，静态事件第二次注入会失败。

## `replace` 与内嵌 JavaScript 的兼容性

`replacement_type: "replace"` 会把目标元素**整个节点**替换成新节点，导致：

- 绑定在旧节点上的 `addEventListener` 失效
- 监听旧节点的 `MutationObserver` 断开，永远触发不到

**陷阱一**：用 MutationObserver 监听某个会被 `replace` 替换的节点——节点被替换后 observer 已绑定在旧节点上，新节点不在监听范围内。

**陷阱二（replace + append 混用时的时序问题）**：同一次 AI 响应中同时有 `replace` 和 `append` 规则时，引擎执行顺序不保证。如果在 `append` 的 MutationObserver 回调里读取 `replace` 写入的值，可能读到空。

**推荐解法：统一用 `setTimeout` 等待所有替换完成**

```javascript
setTimeout(() => {
    // 此时 replace 和 append 都已完成
    const value = document.getElementById('my-hidden-input')?.value || '';
    const items = document.querySelectorAll('.list-item');
    items.forEach(item => {
        if (item.dataset.name === value) item.classList.add('active');
    });
}, 300); // 300ms 是保守值，可根据实际情况调整
```

改用 `replacement_type: "append"` 往空容器里追加内容，节点本身不变，MutationObserver 可以正常工作（但仍需注意与其他 `replace` 规则的时序）：

```html
<!-- HTML 中保留空容器 -->
<div id="my-container"></div>
```
```javascript
const observer = new MutationObserver(() => { /* ... */ });
observer.observe(document.getElementById('my-container'), { childList: true });
```

## 变量条件触发器

当某个变量满足条件时自动触发（不需要用户操作）：

```json
{
  "trigger_id": "health-check",
  "template_id": "battle-template",
  "trigger_name": "生命值归零检查",
  "trigger_condition": {
    "type": "variable_condition",
    "variable_name": "player_health",
    "operator": "<=",
    "variable_value": 0
  },
  "action_sequence": [
    {
      "action_id": "go-to-game-over",
      "action_type": "jump_interface",
      "action_order": 1,
      "action_params": { "target_template_id": "game-over-template" }
    }
  ]
}
```
