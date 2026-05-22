#!/usr/bin/env python3
"""Install me plugin into Claude Code.

Uses `claude plugin marketplace add/remove` CLI commands for proper registration.

After installation, restart Claude Code and enable the plugin via /plugins.

This creates slash commands:
  /me          — from skills/me/SKILL.md (name: me) — Hub
  /me:init     — from commands/init.md
  /me:record   — from commands/record.md
  /me:dream    — from commands/dream.md
  /me:reflect  — from commands/reflect.md
  /me:decide   — from commands/decide.md
  /me:recall   — from commands/recall.md
  /me:update   — from commands/update.md
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "me"


def install(dry_run=False):
    print(f"Installing plugin '{PLUGIN_NAME}' from: {PLUGIN_ROOT}")

    if dry_run:
        print(f"  Would run: claude plugin marketplace add {PLUGIN_ROOT}")
        print(f"\nAvailable commands after enabling:")
        print_commands()
        return

    result = subprocess.run(
        ["claude", "plugin", "marketplace", "add", str(PLUGIN_ROOT)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}")
        sys.exit(1)

    print(result.stdout.strip())
    print(f"\nAvailable commands after enabling:")
    print_commands()
    print(f"\nRestart Claude Code, then enable the plugin via /plugins or run:")
    print(f"  claude plugin install {PLUGIN_NAME}@{PLUGIN_NAME}")


def uninstall():
    print(f"Uninstalling plugin '{PLUGIN_NAME}'...")

    result = subprocess.run(
        ["claude", "plugin", "marketplace", "remove", PLUGIN_NAME],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"Warning: {result.stderr.strip()}")
    else:
        print(result.stdout.strip())

    print("\nUninstallation complete.")
    print("Restart Claude Code to apply changes.")


def print_commands():
    print(f"  /me          — Hub (all capabilities)")
    print(f"  /me:init     — Initialize data files")
    print(f"  /me:record   — Record work/life logs")
    print(f"  /me:dream    — Dream & connect memories")
    print(f"  /me:reflect  — Reflect & improve")
    print(f"  /me:decide   — Decision support")
    print(f"  /me:recall   — Recall & summarize")
    print(f"  /me:update   — Update memory archive")


def main():
    parser = argparse.ArgumentParser(description="Install me plugin for Claude Code")
    parser.add_argument("--action", default="install", choices=["install", "uninstall"])
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.action == "install":
        install(args.dry_run)
    elif args.action == "uninstall":
        uninstall()


if __name__ == "__main__":
    main()
