---
description: "记录今天的工作或生活。聊着聊着就记下来了。"
allowed-tools: "Read Write Edit Bash AskUserQuestion"
---

Record a work or life log entry through chat-based intake.

0. Resolve data directory — read `~/.claude/me-config.json` to get `data_dir`. If not found, tell user to run `/me:init` first. Set `DATA_DIR` from config value.

1. Determine mode from user argument:
   - `work` → work log
   - `life` → life log
   - No argument → use AskUserQuestion to ask

2. Determine date:
   - If user provides a date (YYYY-MM-DD), use it for catchup
   - No date → today's date
   - If user mentions multiple dates, switch to catchup mode

3. Check data initialization. If `DATA_DIR/work_log.csv` doesn't exist, tell the user to run `/me:init` first.

4. **Read the intake prompt. This is mandatory — you MUST Read the file and follow it exactly:**
   - Work (single day): `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/work_intake.md`
   - Life (single day): `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/life_intake.md`
   - Catchup (multi-day): `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/catchup_intake.md`

5. **Follow the prompt strictly.** The prompt uses AskUserQuestion for interactive dialogue. You must call AskUserQuestion for every question — never output plain text questions.

6. Auto-infer category, impact, tags from conversation — **never ask user directly**:
   - **category**: from description → 开发/会议/调研/评审/规划/运维/沟通/文档
   - **impact**: from importance → 1-5 (routine=1-2, project push=3, milestone=4-5)
   - **tags**: extract keywords, comma-separated, 1-5 tags

7. After user confirms, write to CSV:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action insert --file {work_log|life_log} --date {YYYY-MM-DD} --data '{json}' --data-dir DATA_DIR
```
