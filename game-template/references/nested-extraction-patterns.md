# 嵌套提取规则常见模式

## 单条消息

```json
{
  "example": "[角色名] 这是一条消息。",
  "nested_extraction": {
    "regex": "\\[角色名\\]\\s*(?<content>.+?)(?:\\n|$)",
    "occurrence": 1
  }
}
```

## 多条消息（`[角色名] 内容` 格式）

```json
{
  "example": "[角色名] 第一条。\n[角色名] 第二条。",
  "nested_extraction": {
    "regex": "(?<messages>(?:\\[角色名\\]\\s*.+?(?:\\n|$))+)",
    "occurrence": 1,
    "nested_layers": {
      "messages": {
        "regex": "\\[角色名\\]\\s*(?<content>.+?)(?:\\n|$)",
        "occurrence": "multiple"
      }
    }
  }
}
```

## 中文书名号格式（`【说话人】内容`，多角色对话）

```json
{
  "example": "【记者】你们有升级吗？【Lando】带来了一些小更新。",
  "nested_extraction": {
    "regex": "^(?<dialogue_list>[\\s\\S]*)$",
    "occurrence": 1,
    "nested_layers": {
      "dialogue_list": {
        "regex": "【(?<speaker>[^】]+)】\\s*(?<content>[\\s\\S]*?)(?=【|$)",
        "occurrence": "multiple"
      }
    }
  }
}
```

## 结构化多字段（如 `- 时间：X | 事件：Y | 详情：Z`）

```json
{
  "example": "【大奖赛】\n澳大利亚大奖赛\n\n【日程安排】\n- 时间：周五 10:00 | 事件：FP1 | 详情：测试硬胎衰减。",
  "format_note": "每项日程的字数控制在50到100字内",
  "nested_extraction": {
    "regex": "【大奖赛】\\s*(?<grand_prix>[^\\n]+)\\s*\\n【日程安排】\\s*(?<schedule_list>[\\s\\S]*)",
    "occurrence": 1,
    "nested_layers": {
      "schedule_list": {
        "regex": "-\\s*时间：\\s*(?<time>[^|]+?)\\s*\\|\\s*事件：\\s*(?<event>[^|]+?)\\s*\\|\\s*详情：\\s*(?<detail>[^\\n]+)",
        "occurrence": "multiple"
      }
    }
  }
}
```

## 三层嵌套（整体 → 回合 → 每回合的行动）

```json
{
  "example": "[战斗回合]\n第1回合战斗结果：\n艾莉使用【光剑斩击】攻击哥布林：造成25点伤害\n哥布林使用【利爪攻击】攻击艾莉：造成15点伤害",
  "nested_extraction": {
    "regex": "\\[战斗回合\\]\\s*(?<battle_data>[\\s\\S]*)",
    "occurrence": 1,
    "nested_layers": {
      "battle_data": {
        "regex": "第(?<round_num>\\d+)回合战斗结果：\\s*(?<round_actions>[^第]*?)(?=第|$)",
        "occurrence": "multiple",
        "nested_layers": {
          "round_actions": {
            "regex": "(?<actor>.+?)使用【(?<skill>.+?)】(?<target>攻击.+?|：.+?)：(?<effect>.+?)(?=\\n|$)",
            "occurrence": "multiple"
          }
        }
      }
    }
  }
}
```
