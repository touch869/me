---
description: "记录今天的工作或生活。聊着聊着就记下来了。"
allowed-tools: "Read Write Edit Bash"
---

Record a work or life log entry through chat-based intake.

1. Determine mode from user argument:
   - `work` → work log
   - `life` → life log
   - No argument → ask the user

2. Determine date:
   - If user provides a date (YYYY-MM-DD), use it for catchup
   - No date → today's date
   - If user mentions multiple dates, switch to catchup mode

3. Check data initialization. If `${CLAUDE_PLUGIN_ROOT}/skills/me/data/work_log.csv` doesn't exist, tell the user to run `/me:init` first.

4. Read the corresponding intake prompt:
   - Work: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/work_intake.md`
   - Life: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/life_intake.md`
   - Catchup (multi-day): `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/catchup_intake.md`

5. Conduct chat-based intake following the prompt's flow.

6. Auto-infer category, impact, tags from conversation — **never ask user directly**:
   - **category**: from description → 开发/会议/调研/评审/规划/运维/沟通/文档
   - **impact**: from importance → 1-5 (routine=1-2, project push=3, milestone=4-5)
   - **tags**: extract keywords, comma-separated, 1-5 tags

7. Present structured confirmation (only show fields with content).

8. After user confirms, write to CSV:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action insert --file {work_log|life_log} --date {YYYY-MM-DD} --data '{json}' --data-dir ${CLAUDE_PLUGIN_ROOT}/skills/me/data
```

If data directory not initialized, tell user to run `/me:init` first.