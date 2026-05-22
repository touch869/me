---
description: "整理记忆 — 从日志提炼记忆，整理已有记忆。像大脑在睡眠中整理记忆一样。"
allowed-tools: "Read Write Edit Bash AskUserQuestion"
---

Organize memories — distill from logs, tidy up what's already there.

0. Resolve data directory — read `~/.claude/me-config.json` to get `data_dir`. If not found, tell user to run `/me:init` first. Set `DATA_DIR` from config value.

1. Check data initialization. If not initialized, tell user to run `/me:init` first.

2. Collect素材 — read memory + extract from CSV (last 30 days):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file work_log --from {30_days_ago} --format summary --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file life_log --from {30_days_ago} --format summary --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file work_log --format patterns --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file life_log --format patterns --data-dir DATA_DIR
```

3. Read the dream prompt: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/dream.md`

4. Follow the dream prompt strictly — two phases:

   **Phase A — Extract from logs**: Compare log data against existing memory.md. Identify important events, patterns, and insights that are NOT yet recorded. For each, determine which section it belongs to.

   **Phase B — Organize existing memory**: Review current memory.md for duplicates, stale info, misplaced entries, and opportunities to merge similar items.

5. Write results back using update-section (for reorganized sections) and append-section (for new additions):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action update-section --section '{section_name}' --content '{reorganized_content}' --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action append-section --section '{section_name}' --content '{new_content}' --data-dir DATA_DIR
```

6. Show a brief changelog: what was added, modified, or removed.
