#!/usr/bin/env python3
"""
Print current project state.

Usage:
    status.py
"""
import json
import pathlib
import sys


def main() -> None:
    cwd = pathlib.Path.cwd()
    manifest_path = cwd / "manifest.json"
    if not manifest_path.exists():
        sys.exit("error: no manifest.json in cwd. Run /aiwy-new to start a project.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    print(f"Project: {manifest.get('project_name', '?')}")
    print(f"Created: {manifest.get('created_at', '?')}")
    print(f"Current phase: {manifest.get('current_phase', '?')}")
    locked = manifest.get("locked_phases", [])
    print(f"Locked: {', '.join(locked) if locked else '(none yet)'}")
    print()

    # File inventory
    print("Files:")
    for f in ("00_concept.md", "decisions.md"):
        p = cwd / f
        flag = "✓" if p.exists() and p.stat().st_size > 200 else "✗"
        size = f"({p.stat().st_size}B)" if p.exists() else "(missing)"
        print(f"  {flag} {f} {size}")

    # Characters
    chars_dir = cwd / "characters"
    if chars_dir.exists():
        chars = [p.name for p in chars_dir.iterdir() if p.is_dir()]
        print(f"  characters/: {len(chars)} entries — {', '.join(chars) if chars else '(empty)'}")

    # World
    world_dir = cwd / "world"
    if world_dir.exists():
        ww = world_dir / "worldview.yaml"
        flag = "✓" if ww.exists() else "✗"
        print(f"  {flag} world/worldview.yaml")
        lores = sorted(p.name for p in world_dir.glob("lore_*.md"))
        if lores:
            print(f"  world/lore: {', '.join(lores)}")

    # Gameplay
    gp_dir = cwd / "gameplay"
    if gp_dir.exists():
        gps = sorted(p.name for p in gp_dir.glob("*.md") if not p.name.startswith("_"))
        print(f"  gameplay/: {len(gps)} files — {', '.join(gps[:5])}{'...' if len(gps) > 5 else ''}")

    # UI style guide
    ui_dir = cwd / "ui"
    if ui_dir.exists():
        sg = ui_dir / "style_guide.md"
        flag = "✓" if sg.exists() and sg.stat().st_size > 200 else "✗"
        print(f"  {flag} ui/style_guide.md")

    # Interfaces
    iface_dir = cwd / "interfaces"
    if iface_dir.exists():
        sitemap = iface_dir / "_sitemap.md"
        sm_flag = "✓" if sitemap.exists() and sitemap.stat().st_size > 100 else "✗"
        print(f"  {sm_flag} interfaces/_sitemap.md")
        ifaces = sorted(p.name for p in iface_dir.glob("*.md") if not p.name.startswith("_"))
        print(f"  interfaces/: {len(ifaces)} files — {', '.join(ifaces[:5])}{'...' if len(ifaces) > 5 else ''}")

    # Suggest next action
    print()
    phase = manifest.get("current_phase", "concept")
    if phase not in locked:
        print(f"Next: complete and /aiwy-lock {phase}")
    else:
        order = manifest.get("phase_order", [])
        try:
            idx = order.index(phase)
            if idx + 1 < len(order):
                print(f"Next: move to phase '{order[idx + 1]}'")
            else:
                print("All phases locked. Project complete?")
        except ValueError:
            pass


if __name__ == "__main__":
    main()
