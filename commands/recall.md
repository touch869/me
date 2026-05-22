---
description: "回忆与总结 — 提取最有价值的内容，帮你述职写颁奖词。"
allowed-tools: "Read Write Edit Bash"
---

Recall and summarize — extract the most valuable content from your logs and memory.

0. Resolve data directory — read `~/.claude/me-config.json` to get `data_dir`. If not found, tell user to run `/me:init` first. Set `DATA_DIR` from config value.

1. Check data initialization. If not initialized, tell user to run `/me:init` first.

2. Determine time range and output type from user request:
   - "最近" → 7 days
   - "上半年" → Jan ~ Jun
   - "下半年" → Jul ~ Dec
   - "上个月" → last month 1st ~ last day
   - Explicit date → use directly

   Output types:
   - "最有价值的N条" / "最重要的" → 精选: sort by impact, top N
   - "总结上半年" / "述职" → 总结: organize by project/time
   - "颁奖词" → 叙事: narrative achievement text
   - "看看最近" / "查看记录" → 展示: direct table display

3. Query log data:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action query --file {log} --from {from_date} --to {to_date} --format json --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --section 核心轨迹 --data-dir DATA_DIR
```

For "最有价值" queries, also extract high-impact entries:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file work_log --from {from_date} --to {to_date} --impact-threshold 3 --format summary --data-dir DATA_DIR
```

4. Read the recall prompt: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/recall.md`

5. Follow recall prompt — organize output by type (精选/述职/颁奖词/展示).
