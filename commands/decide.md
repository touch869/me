---
description: "根据记忆辅助决策 — 查找过去类似情境，分析结果，给出建议。"
allowed-tools: "Read Write Edit Bash"
---

Decision support — find past similar situations, analyze outcomes, provide reference advice.

0. Resolve data directory — read `~/.claude/me-config.json` to get `data_dir`. If not found, tell user to run `/me:init` first. Set `DATA_DIR` from config value.

1. Check data initialization. If not initialized, tell user to run `/me:init` first.

2. If user didn't specify the decision question, ask: "你在考虑什么决定？说说情境和纠结点。"

3. Search memory for past decisions + thinking patterns:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --section 决策档案 --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --section 模式识别 --data-dir DATA_DIR
```

4. Query relevant log entries:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action query --file {log} --format json --data-dir DATA_DIR
```

5. Read the decide prompt: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/decide.md`

6. Follow decide prompt strictly — **don't make decisions for the user**, only provide references.

7. Offer to record the decision:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action append-section --section 决策档案 --content '{决策记录}' --data-dir DATA_DIR
```
