---
description: "反思行为模式 — 发现自己的问题，提出具体可执行的改进建议。"
allowed-tools: "Read Write Edit Bash"
---

Reflect on behavioral patterns — find problems and propose actionable improvements.

1. Check data initialization. If not initialized, tell user to run `/me:init` first.

2. If memory's 模式识别 section is empty, suggest `/me:update` first.

3. Read patterns from memory + CSV:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --section 模式识别 --data-dir ${CLAUDE_PLUGIN_ROOT}/skills/me/data
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file {log} --format patterns --data-dir ${CLAUDE_PLUGIN_ROOT}/skills/me/data
```

4. Read the reflect prompt: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/reflect.md`

5. Follow reflect prompt strictly — every conclusion must cite specific log entries as evidence.

6. After analysis, offer to write findings to memory:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action update-section --section 反思档案 --content '{反思内容}' --data-dir ${CLAUDE_PLUGIN_ROOT}/skills/me/data
```