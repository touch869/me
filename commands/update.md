---
description: "从日志提炼记忆 — 把CSV记录转化为可推理的记忆档案。"
allowed-tools: "Read Write Edit Bash AskUserQuestion"
---

Update memory archive — distill patterns from CSV logs into the memory.md understanding layer.

0. Resolve data directory — read `~/.claude/me-config.json` to get `data_dir`. If not found, tell user to run `/me:init` first. Set `DATA_DIR` from config value.

1. Check data initialization. If not initialized, tell user to run `/me:init` first.

2. Ensure memory file exists:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action init --data-dir DATA_DIR
```

3. Extract data from CSV:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file work_log --format summary --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file work_log --impact-threshold 3 --format summary --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file work_log --format patterns --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file life_log --format summary --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file life_log --format patterns --data-dir DATA_DIR
```

4. Read the memory update prompt: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/memory_update.md`

5. Follow memory_update prompt strictly — extract patterns, not copy logs. Incremental update, preserve valid old conclusions.

6. Write updated sections to memory.md:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action update-section --section {name} --content '{content}' --data-dir DATA_DIR
```

7. Backup after update:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/version_manager.py --action backup --data-dir DATA_DIR
```
