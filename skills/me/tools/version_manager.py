#!/usr/bin/env python3
"""Version backup and rollback manager for life-logger CSV data.

Usage:
    python3 version_manager.py --action <backup|rollback|list> [--data-dir <path>] [--version <v>]
"""

import argparse
import os
import sys
import shutil
import json
from datetime import datetime
from pathlib import Path

_PLUGIN_ROOT_ENV = os.environ.get("CLAUDE_PLUGIN_ROOT")
if _PLUGIN_ROOT_ENV:
    PLUGIN_ROOT = Path(_PLUGIN_ROOT_ENV)
    SKILL_ROOT = PLUGIN_ROOT / "skills" / "me"
else:
    SKILL_ROOT = Path(__file__).resolve().parent.parent
    PLUGIN_ROOT = SKILL_ROOT.parent.parent
DEFAULT_DATA_DIR = SKILL_ROOT / "data"
MAX_VERSIONS = 20

BACKUP_FILES = ["work_log.csv", "life_log.csv", "memory.md", "meta.json"]


def resolve_data_dir(data_dir=None):
    if data_dir:
        return Path(data_dir)
    return Path(DEFAULT_DATA_DIR)


def load_meta(data_dir=None):
    dd = resolve_data_dir(data_dir)
    meta_path = dd / "meta.json"
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "v0"}


def save_meta(meta, data_dir=None):
    dd = resolve_data_dir(data_dir)
    dd.mkdir(parents=True, exist_ok=True)
    meta["updated_at"] = datetime.now().isoformat()
    with open(dd / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def backup(data_dir=None):
    dd = resolve_data_dir(data_dir)
    versions_dir = dd / "versions"

    meta = load_meta(data_dir)
    current_version = meta.get("version", "v0")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{current_version}_{timestamp}"
    backup_dir = versions_dir / backup_name

    backup_dir.mkdir(parents=True, exist_ok=True)

    for fname in BACKUP_FILES:
        src = dd / fname
        if src.exists():
            shutil.copy2(src, backup_dir / fname)

    print(f"Backup created: {backup_name} at {backup_dir}")
    cleanup_old_versions(data_dir)
    return backup_name


def rollback(version, data_dir=None):
    dd = resolve_data_dir(data_dir)
    versions_dir = dd / "versions"

    if not versions_dir.is_dir():
        print("No versions found.")
        sys.exit(1)

    # Find matching version
    target_dir = None
    for vname in sorted(versions_dir.iterdir()):
        if vname.name.startswith(version) or vname.name == version:
            target_dir = vname
            break

    if not target_dir or not target_dir.is_dir():
        print(f"Error: version '{version}' not found.")
        list_versions(data_dir)
        sys.exit(1)

    # Auto-backup current before rollback
    backup(data_dir)

    # Restore files
    for fname in BACKUP_FILES:
        src = target_dir / fname
        dst = dd / fname
        if src.exists():
            shutil.copy2(src, dst)

    # Update meta version
    meta = load_meta(data_dir)
    # Extract version prefix from target dir name
    restored_version = target_dir.name.split("_")[0]
    meta["version"] = restored_version
    save_meta(meta, data_dir)

    print(f"Rolled back to version {target_dir.name}")


def list_versions(data_dir=None):
    dd = resolve_data_dir(data_dir)
    versions_dir = dd / "versions"

    if not versions_dir.is_dir():
        print("No historical versions.")
        return

    versions = sorted(versions_dir.iterdir(), key=lambda p: p.name, reverse=True)
    active = [v for v in versions if v.is_dir()]

    if not active:
        print("No historical versions.")
        return

    print(f"Historical versions ({len(active)} total):\n")
    for v in active:
        print(f"  {v.name}")


def cleanup_old_versions(data_dir=None):
    dd = resolve_data_dir(data_dir)
    versions_dir = dd / "versions"

    if not versions_dir.is_dir():
        return

    versions = sorted(versions_dir.iterdir(), key=lambda p: p.name)
    active = [v for v in versions if v.is_dir()]

    if len(active) > MAX_VERSIONS:
        to_remove = active[: len(active) - MAX_VERSIONS]
        for v in to_remove:
            shutil.rmtree(v)
        print(f"Cleaned up {len(to_remove)} old version(s), keeping {MAX_VERSIONS}.")


def main():
    parser = argparse.ArgumentParser(description="Life-logger version manager")
    parser.add_argument("--action", required=True, choices=["backup", "rollback", "list"])
    parser.add_argument("--data-dir", default=None, help="Data directory path")
    parser.add_argument("--version", default=None, help="Target version for rollback")

    args = parser.parse_args()

    if args.action == "backup":
        backup(args.data_dir)

    elif args.action == "rollback":
        if not args.version:
            print("Error: --version is required for rollback.")
            sys.exit(1)
        rollback(args.version, args.data_dir)

    elif args.action == "list":
        list_versions(args.data_dir)


if __name__ == "__main__":
    main()