---
description: "初始化数据文件 — 首次使用 /me 前必须执行一次。"
allowed-tools: "Read Write Edit Bash"
---

Initialize all data files for the me plugin. This must be run once before using any other /me commands.

1. Check if data directory already has files. If `work_log.csv`, `life_log.csv`, and `memory.md` all exist under `${CLAUDE_PLUGIN_ROOT}/skills/me/data/`, tell the user:

```
数据文件已存在，无需重复初始化。如需重置，先手动删除 ${CLAUDE_PLUGIN_ROOT}/skills/me/data/ 目录。
```

2. If not initialized, run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action init --file work_log --data-dir ${CLAUDE_PLUGIN_ROOT}/skills/me/data
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action init --file life_log --data-dir ${CLAUDE_PLUGIN_ROOT}/skills/me/data
python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action init --data-dir ${CLAUDE_PLUGIN_ROOT}/skills/me/data
```

3. After successful initialization, tell the user:

```
初始化完成！现在可以开始使用了：

  📝 /me:record work  — 记录工作日志
  📝 /me:record life  — 记录生活日志

先记录几天，积累数据后就能做梦、反思、做决策了。
```