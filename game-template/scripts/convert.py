#!/usr/bin/env python3
"""
game-template 格式转换工具

用法:
  python convert.py toml2json <dir>   — 将目录内的 TOML 转换为 JSON（in-place）
  python convert.py json2toml <dir>   — 将目录内的 JSON 转换为 TOML（in-place）

<dir> 同时包含 TOML 和 JSON 文件，转换结果直接覆盖同目录内的对应文件。

文件对应关系:
  template.toml        ↔  template.json
  response_format.toml ↔  response_format.json
  trigger.toml         ↔  trigger.json
  global_variables.toml ↔  global_variables.json  （可选，游戏根目录）
"""

import sys
import json
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from pathlib import Path


# ─────────────────────────────────────────────
# JSON → TOML
# ─────────────────────────────────────────────

def _toml_str(value: str) -> str:
    if "'''" in value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    if "\n" in value:
        return f"'''\n{value}'''"
    return f"'{value}'"


def _build_nested_layer(layer: dict, table_path: str) -> list[str]:
    lines = []
    lines.append(f"[{table_path}]")
    lines.append(f"regex = {_toml_str(layer['regex'])}")
    occ = layer["occurrence"]
    lines.append("occurrence = 1" if occ == 1 else "occurrence = 'multiple'")
    lines.append("")
    for key, sublayer in layer.get("nested_layers", {}).items():
        lines.extend(_build_nested_layer(sublayer, f"{table_path}.nested_layers.{key}"))
    return lines


def _build_template_toml(data: dict) -> str:
    lines = ["# HTML 模板"]
    lines.append(f"html_template = {_toml_str(data['html_template'])}")
    lines.append("")
    lines.append("# 变量替换规则")
    for rule in data.get("variable_replacement_rules", []):
        lines.append("[[variable_replacement_rules]]")
        lines.append(f'target_selector = "{rule["target_selector"]}"')
        lines.append(f'replacement_type = "{rule["replacement_type"]}"')
        lines.append(f"template = {_toml_str(rule['template'])}")
        lines.append("")
    return "\n".join(lines)


def _build_response_format_toml(data: dict) -> str:
    lines = ["# 响应格式", "[response_format]"]
    lines.append(f"example = {_toml_str(data['example'])}")
    if "format_note" in data:
        lines.append(f"format_note = {_toml_str(data['format_note'])}")
    lines.append("")
    lines.extend(_build_nested_layer(data["nested_extraction"], "response_format.nested_extraction"))
    return "\n".join(lines)


def _build_global_variables_toml(data: list) -> str:
    lines = ["# 全局变量声明", "# 游戏级别的全局变量，跨模板共享", "# 用 apply-globals 命令将此文件同步到数据库", ""]
    for v in data:
        lines.append("[[global_variables]]")
        lines.append(f'name = "{v["name"]}"')
        lines.append(f'type = "{v["type"]}"')
        dv = v["defaultValue"]
        if isinstance(dv, bool):
            lines.append(f'default_value = {"true" if dv else "false"}')
        elif isinstance(dv, (int, float)):
            lines.append(f'default_value = {dv}')
        elif isinstance(dv, list):
            lines.append(f'default_value = []')
        else:
            lines.append(f'default_value = {_toml_str(str(dv))}')
        lines.append(f'description = {_toml_str(v.get("description", ""))}')
        lines.append("")
    return "\n".join(lines)


def _build_trigger_toml(triggers: list) -> str:
    lines = ["# 触发器配置", ""]
    for t in triggers:
        lines.append(f"# 触发器: {t['trigger_name']}")
        lines.append("[[triggers]]")
        lines.append(f'trigger_name = "{t["trigger_name"]}"')
        lines.append("")

        tc = t["trigger_condition"]
        lines.append("[triggers.trigger_condition]")
        for k, v in tc.items():
            lines.append(f'{k} = "{v}"')
        lines.append("")

        for action in t["action_sequence"]:
            lines.append("[[triggers.action_sequence]]")
            lines.append(f'action_type = "{action["action_type"]}"')
            lines.append(f'action_order = {action["action_order"]}')
            lines.append("")

            params = action.get("action_params", {})
            updates = params.get("variable_updates", [])
            exec_cond = params.get("__execution_condition")
            target_tid = params.get("target_template_id")

            if target_tid is not None:
                lines.append("[triggers.action_sequence.action_params]")
                lines.append(f'target_template_id = "{target_tid}"')
                lines.append("")

            for u in updates:
                lines.append("[[triggers.action_sequence.action_params.variable_updates]]")
                if "mode" in u:
                    lines.append(f'mode = "{u["mode"]}"')
                lines.append(f'variable_name = "{u["variable_name"]}"')
                lines.append(f"variable_value = {_toml_str(u['variable_value'])}")
                lines.append("")

            if exec_cond:
                cp = "triggers.action_sequence.action_params.__execution_condition"
                lines.append(f"[{cp}]")
                lines.append(f'logic = "{exec_cond["logic"]}"')
                lines.append("")
                for c in exec_cond["conditions"]:
                    lines.append(f"[[{cp}.conditions]]")
                    for k, v in c.items():
                        lines.append(f'{k} = "{v}"')
                    lines.append("")

            # 透传其他 action_params 字段（如 userInputTemplate）
            known_keys = {"target_template_id", "variable_updates", "__execution_condition"}
            for k, v in params.items():
                if k not in known_keys:
                    # 简单序列化为 TOML inline table
                    lines.append(f"[triggers.action_sequence.action_params.{k}]")
                    for fk, fv in (v.items() if isinstance(v, dict) else {}.items()):
                        if isinstance(fv, bool):
                            lines.append(f'{fk} = {"true" if fv else "false"}')
                        elif isinstance(fv, str):
                            lines.append(f"{fk} = {_toml_str(fv)}")
                        else:
                            lines.append(f'{fk} = {json.dumps(fv, ensure_ascii=False)}')
                    lines.append("")

        lines.append("")
    return "\n".join(lines)


def json2toml(directory: Path):
    src = directory / "template.json"
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        (directory / "template.toml").write_text(_build_template_toml(data), encoding="utf-8")
        print(f"  template.json → template.toml")

    src = directory / "response_format.json"
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        (directory / "response_format.toml").write_text(_build_response_format_toml(data), encoding="utf-8")
        print(f"  response_format.json → response_format.toml")

    src = directory / "trigger.json"
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        (directory / "trigger.toml").write_text(_build_trigger_toml(data), encoding="utf-8")
        print(f"  trigger.json → trigger.toml")

    src = directory / "global_variables.json"
    if src.exists():
        data = json.loads(src.read_text(encoding="utf-8"))
        (directory / "global_variables.toml").write_text(_build_global_variables_toml(data), encoding="utf-8")
        print(f"  global_variables.json → global_variables.toml")


# ─────────────────────────────────────────────
# TOML → JSON
# ─────────────────────────────────────────────

def _strip_multiline(s: str) -> str:
    if s.startswith("\n"):
        s = s[1:]
    if s.endswith("\n"):
        s = s[:-1]
    return s


def _parse_nested_layer(layer_data: dict) -> dict:
    result: dict = {
        "regex": _strip_multiline(layer_data["regex"]),
        "occurrence": layer_data["occurrence"],
    }
    nested = layer_data.get("nested_layers", {})
    if nested:
        result["nested_layers"] = {
            key: _parse_nested_layer(sub) for key, sub in nested.items()
        }
    return result


def _parse_template_toml(data: dict) -> dict:
    result = {
        "html_template": _strip_multiline(data["html_template"]),
        "variable_replacement_rules": [],
    }
    for rule in data.get("variable_replacement_rules", []):
        result["variable_replacement_rules"].append({
            "target_selector": rule["target_selector"],
            "replacement_type": rule["replacement_type"],
            "template": _strip_multiline(rule["template"]),
        })
    return result


def _parse_response_format_toml(data: dict) -> dict:
    rf = data["response_format"]
    result: dict = {
        "example": _strip_multiline(rf["example"]),
        "nested_extraction": _parse_nested_layer(rf["nested_extraction"]),
    }
    if "format_note" in rf:
        result["format_note"] = rf["format_note"]
    return result


def _parse_global_variables_toml(data: dict) -> list:
    result = []
    for v in data.get("global_variables", []):
        result.append({
            "name": v["name"],
            "type": v["type"],
            "scope": "global",
            "description": v.get("description", ""),
            "defaultValue": v["default_value"],
        })
    return result


def _parse_trigger_toml(data: dict) -> list:
    triggers = []
    for t in data.get("triggers", []):
        trigger: dict = {
            "trigger_name": t["trigger_name"],
            "trigger_condition": dict(t["trigger_condition"]),
            "action_sequence": [],
        }
        for action in t.get("action_sequence", []):
            a: dict = {
                "action_type": action["action_type"],
                "action_order": action["action_order"],
                "action_params": {},
            }
            params = action.get("action_params", {})

            if "target_template_id" in params:
                a["action_params"]["target_template_id"] = params["target_template_id"]

            updates = params.get("variable_updates", [])
            if updates:
                a["action_params"]["variable_updates"] = [
                    {k: _strip_multiline(v) if k == "variable_value" else v
                     for k, v in u.items()}
                    for u in updates
                ]

            exec_cond = params.get("__execution_condition")
            if exec_cond:
                a["action_params"]["__execution_condition"] = {
                    "logic": exec_cond["logic"],
                    "conditions": [dict(c) for c in exec_cond.get("conditions", [])],
                }

            known_keys = {"target_template_id", "variable_updates", "__execution_condition"}
            for k, v in params.items():
                if k not in known_keys:
                    a["action_params"][k] = v

            trigger["action_sequence"].append(a)
        triggers.append(trigger)
    return triggers


def toml2json(directory: Path):
    src = directory / "template.toml"
    if src.exists():
        data = tomllib.loads(src.read_text(encoding="utf-8"))
        (directory / "template.json").write_text(
            json.dumps(_parse_template_toml(data), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  template.toml → template.json")

    src = directory / "response_format.toml"
    if src.exists():
        data = tomllib.loads(src.read_text(encoding="utf-8"))
        (directory / "response_format.json").write_text(
            json.dumps(_parse_response_format_toml(data), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  response_format.toml → response_format.json")

    src = directory / "trigger.toml"
    if src.exists():
        data = tomllib.loads(src.read_text(encoding="utf-8"))
        (directory / "trigger.json").write_text(
            json.dumps(_parse_trigger_toml(data), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  trigger.toml → trigger.json")

    src = directory / "global_variables.toml"
    if src.exists():
        data = tomllib.loads(src.read_text(encoding="utf-8"))
        (directory / "global_variables.json").write_text(
            json.dumps(_parse_global_variables_toml(data), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"  global_variables.toml → global_variables.json")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────

def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("json2toml", "toml2json"):
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    directory = Path(sys.argv[2])

    if not directory.exists():
        print(f"错误: 目录不存在: {directory}")
        sys.exit(1)

    print(f"{mode}: {directory}")
    if mode == "json2toml":
        json2toml(directory)
    else:
        toml2json(directory)
    print("完成。")


if __name__ == "__main__":
    main()
