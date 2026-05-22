---
description: "初始化数据文件 — 首次使用 /me 前必须执行一次。"
allowed-tools: "Read Write Edit Bash AskUserQuestion"
---

Initialize all data files for the me plugin. This must be run once before using any other /me commands.

## Step 1: Determine data directory

Read the config file `~/.claude/me-config.json`. If it exists and contains a `data_dir` field, use that path and skip the prompt.

If the config file does NOT exist or has no `data_dir`:

**Ask the user this question (using AskUserQuestion):**

> 数据文件存储在哪里？

Options:
1. **插件内（默认）** — `${CLAUDE_PLUGIN_ROOT}/skills/me/data/`
   - Warning: 插件重新安装时数据会被清除，建议先 `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/version_manager.py --action backup` 备份
2. **独立目录** — `~/.me-data/`
   - 安全：不受插件更新影响

If user chooses option 2 (or provides a custom path), use that path.

**After the user chooses, save the config:**

```bash
echo '{"data_dir": "<chosen_path>"}' > ~/.claude/me-config.json
```

Set `DATA_DIR` to the chosen path for all subsequent steps.

## Step 2: Check existing data

If `work_log.csv`, `life_log.csv`, and `memory.md` all exist under `DATA_DIR`, tell the user:

```
数据文件已存在，无需重复初始化。
数据目录: DATA_DIR
如需重置，先手动删除该目录。
```

## Step 3: Initialize data files

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action init --file work_log --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action init --file life_log --data-dir DATA_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action init --data-dir DATA_DIR
```

## Step 4: Success message

```
初始化完成！数据目录: DATA_DIR

  📝 /me:record work  — 记录工作日志
  📝 /me:record life  — 记录生活日志

先记录几天，积累数据后就能做梦、反思、做决策了。
```
