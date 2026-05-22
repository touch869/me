---
description: "在记忆里做个梦 — 把碎片连接成故事，发现隐藏的线索。"
allowed-tools: "Read Write Edit Bash AskUserQuestion"
---

Dream in your memories — connect fragments into a narrative and discover hidden threads.

0. Resolve data directory — read `~/.claude/me-config.json` to get `data_dir`. If not found, tell user to run `/me:init` first. Set `DATA_DIR` from config value.

1. Check data initialization. If not initialized, tell user to run `/me:init` first.

2. Collect素材 — read memory + extract from CSV:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file {log} --from {recent_date} --format summary --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file {log} --format patterns --data-dir DATA_DIR
```

3. Read the dream prompt: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/dream.md`

4. Follow the dream prompt strictly — this is narrative, not summary. Three acts: 入梦 → 漫游 → 醒来.

5. After dream, offer to write discovered threads to memory:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action append-section --section 关注清单 --content '{线索}' --data-dir DATA_DIR
```
