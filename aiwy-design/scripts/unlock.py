#!/usr/bin/env python3
"""
Unlock a previously-locked phase. Records the unlock and warns about downstream impact.

Usage:
    unlock.py <phase> [--reason "rationale"]
"""
import argparse
import json
import pathlib
import sys
import time

PHASES = ("concept", "characters", "world", "gameplay", "interfaces", "assets")

# Which phases are downstream of which (i.e. depend on it)
DOWNSTREAM = {
    "concept": ["characters", "world", "gameplay", "interfaces", "assets"],
    "characters": ["world", "gameplay", "interfaces", "assets"],
    "world": ["gameplay", "interfaces", "assets"],
    "gameplay": ["interfaces", "assets"],
    "interfaces": ["assets"],
    "assets": [],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=PHASES)
    ap.add_argument("--reason", default="", help="why are we unlocking?")
    args = ap.parse_args()

    cwd = pathlib.Path.cwd()
    manifest_path = cwd / "manifest.json"
    decisions_path = cwd / "decisions.md"
    if not manifest_path.exists():
        sys.exit("error: no manifest.json in cwd")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    locked = manifest.get("locked_phases", [])
    if args.phase not in locked:
        sys.exit(f"phase '{args.phase}' is not currently locked")

    locked.remove(args.phase)
    # current_phase rolls back to this phase
    manifest["current_phase"] = args.phase

    # Append unlock record
    today = time.strftime("%Y-%m-%d")
    timestamp = time.strftime("%Y-%m-%d %H:%M")
    affected = [p for p in DOWNSTREAM.get(args.phase, []) if p in locked]
    entry = [
        f"\n### {today} — UNLOCKED: {args.phase}\n",
    ]
    if args.reason:
        entry.append(f"\n**Reason**: {args.reason}\n")
    entry.append(f"\n**Unlocked at**: {timestamp}\n")
    if affected:
        entry.append(
            f"\n**⚠ Downstream phases potentially invalidated**: {', '.join(affected)}\n"
            f"  Re-validate these after re-locking '{args.phase}'.\n"
        )
    entry.append("\n---\n")
    if decisions_path.exists():
        with decisions_path.open("a", encoding="utf-8") as f:
            f.writelines(entry)

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"✓ unlocked '{args.phase}'")
    print(f"  → current_phase rolled back to: {args.phase}")
    if affected:
        print(f"  ⚠ check these downstream phases after re-lock: {', '.join(affected)}")


if __name__ == "__main__":
    main()
