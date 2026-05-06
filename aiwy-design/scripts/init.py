#!/usr/bin/env python3
"""
Initialize a new AI 文游 project in cwd.

Usage:
    init.py <project_name>

Creates:
    manifest.json
    00_concept.md (from template)
    decisions.md (from template)
    characters/, world/, gameplay/, ui/, interfaces/, assets/, drafts/
"""
import argparse
import json
import os
import pathlib
import re
import shutil
import sys
import time

SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_ROOT / "templates"
SUBDIRS = ["characters", "world", "gameplay", "ui", "interfaces", "assets", "drafts"]


def render_template(template_path: pathlib.Path, vars: dict) -> str:
    text = template_path.read_text(encoding="utf-8")
    for key, value in vars.items():
        text = text.replace("{{" + key + "}}", str(value))
    # Strip any unfilled {{var}} markers so the file looks clean.
    text = re.sub(r"\{\{[a-z_]+\}\}", "", text)
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_name", help="项目代号 (英文 / 拼音, no spaces)")
    ap.add_argument(
        "--force",
        action="store_true",
        help="overwrite existing manifest.json",
    )
    args = ap.parse_args()

    name = args.project_name.strip()
    if not re.match(r"^[a-zA-Z0-9_\-]+$", name):
        sys.exit(
            f"error: project name '{name}' must match [a-zA-Z0-9_-]+ "
            "(no spaces or unicode — keep it filesystem-friendly)"
        )

    cwd = pathlib.Path.cwd()
    manifest_path = cwd / "manifest.json"
    if manifest_path.exists() and not args.force:
        sys.exit(
            f"error: {manifest_path} already exists. "
            "Use --force to overwrite, or run /aiwy-resume instead."
        )

    # Verify cwd is reasonably empty
    existing = [p.name for p in cwd.iterdir() if not p.name.startswith(".")]
    allowed = {"manifest.json", "drafts"}  # tolerated leftovers
    foreign = [n for n in existing if n not in allowed]
    if foreign and not args.force:
        print(
            "warning: cwd is not empty. Found:",
            ", ".join(foreign[:8]),
            "..." if len(foreign) > 8 else "",
            file=sys.stderr,
        )
        print(
            "Continue anyway? Re-run with --force, or cd to an empty dir.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Create subdirs
    for sub in SUBDIRS:
        (cwd / sub).mkdir(exist_ok=True)

    # Render templates
    now = time.strftime("%Y-%m-%d %H:%M")
    today = time.strftime("%Y-%m-%d")
    vars = {
        "project_name": name,
        "created_at": now,
        "date": today,
        "one_line_pitch": "",
        "ref_title_1": "",
        "ref_title_2": "",
    }
    (cwd / "00_concept.md").write_text(
        render_template(TEMPLATES / "00_concept.md.tpl", vars),
        encoding="utf-8",
    )
    (cwd / "decisions.md").write_text(
        render_template(TEMPLATES / "decisions.md.tpl", vars),
        encoding="utf-8",
    )

    # Manifest
    manifest = {
        "schema_version": 1,
        "project_name": name,
        "created_at": now,
        "current_phase": "concept",
        "locked_phases": [],
        "phase_order": ["concept", "characters", "world", "gameplay", "interfaces", "assets"],
        "skill_version": "0.1.0",
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"✓ initialized project '{name}' in {cwd}")
    print("  → 00_concept.md and decisions.md created from templates")
    print(f"  → subdirs: {', '.join(SUBDIRS)}")
    print("  → next: enter Phase 1 (Concept) grilling")


if __name__ == "__main__":
    main()
