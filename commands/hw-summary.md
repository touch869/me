---
description: "华为阶段性总结 — 自评四段式：个人贡献、对他人的贡献、借助的帮助、待改进。给领导看的述职文档。"
allowed-tools: "Read Write Edit Bash AskUserQuestion"
---

华为阶段性总结 — 生成可直接提交给领导的四段式自评文档。

0. Resolve data directory — read `~/.claude/me-config.json` to get `data_dir`. If not found, tell user to run `/me:init` first. Set `DATA_DIR` from config value.

1. Check data initialization. If not initialized, tell user to run `/me:init` first.

2. Determine time range from user request:
   - "上半年" → Jan 1 ~ Jun 30
   - "下半年" → Jul 1 ~ Dec 31
   - "上个月" → last month 1st ~ last day
   - "季度" / "Q1~Q4" → 该季度起止
   - Explicit date → use directly
   - No date mentioned → 当前半年（到今天）

3. Query log data:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action query --file work_log --from {from_date} --to {to_date} --format json --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --section 核心轨迹 --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file work_log --from {from_date} --to {to_date} --impact-threshold 3 --format summary --data-dir DATA_DIR
```

4. Read the summary prompt: `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/hw-summary.md`

5. Follow the prompt strictly — output the official 四段式华为阶段性总结。**第一部分（个人贡献）是重点、篇幅最长**；第二~四部分精炼。每条改进点遵循"把优点写成缺点"的包装原则。

6. 生成后询问用户是否需要调整（如某条措辞、增删条目、调整重点），迭代到满意为止。
