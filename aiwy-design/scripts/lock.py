#!/usr/bin/env python3
"""
Checkpoint a phase: append dated entry to decisions.md, update manifest.

Usage:
    lock.py <phase> [--note "rationale"] [--key-decisions "..."]

Caller (Claude) decides when artifacts are ready — this script just records the lock.
"""
import argparse
import json
import pathlib
import sys
import time

PHASES = ("concept", "characters", "world", "gameplay", "interfaces", "assets")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=PHASES)
    ap.add_argument("--note", default="", help="optional rationale to record")
    ap.add_argument(
        "--key-decisions",
        default="",
        help="optional bulleted summary of key decisions, one per line "
             "(passed by Claude after grilling)",
    )
    args = ap.parse_args()

    cwd = pathlib.Path.cwd()
    manifest_path = cwd / "manifest.json"
    decisions_path = cwd / "decisions.md"
    if not manifest_path.exists():
        sys.exit("error: no manifest.json in cwd")
    if not decisions_path.exists():
        sys.exit("error: no decisions.md in cwd")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if args.phase in manifest.get("locked_phases", []):
        print(f"warning: phase '{args.phase}' is already locked. "
              f"Run unlock.py first if you want to re-lock.", file=sys.stderr)
        sys.exit(2)

    # Append checkpoint
    today = time.strftime("%Y-%m-%d")
    timestamp = time.strftime("%Y-%m-%d %H:%M")
    entry = [f"\n### {today} — locked: {args.phase}\n"]
    if args.note:
        entry.append(f"\n**Note**: {args.note}\n")
    if args.key_decisions:
        entry.append("\n**关键决策**:\n")
        for line in args.key_decisions.strip().splitlines():
            line = line.strip().lstrip("-").strip()
            if line:
                entry.append(f"- {line}\n")
    entry.append(f"\n**Locked at**: {timestamp}\n")
    entry.append("\n---\n")

    with decisions_path.open("a", encoding="utf-8") as f:
        f.writelines(entry)

    # Update manifest
    locked = manifest.setdefault("locked_phases", [])
    if args.phase not in locked:
        locked.append(args.phase)
    # Move current_phase forward if locking the current one
    if manifest.get("current_phase") == args.phase:
        order = manifest.get("phase_order", list(PHASES))
        try:
            idx = order.index(args.phase)
            if idx + 1 < len(order):
                manifest["current_phase"] = order[idx + 1]
        except ValueError:
            pass

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"✓ locked phase '{args.phase}'")
    print(f"  → decisions.md updated")
    print(f"  → current_phase now: {manifest['current_phase']}")


if __name__ == "__main__":
    main()
