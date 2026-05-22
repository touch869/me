---
name: me
description: "你的数字自我。记录、回忆、做梦、反思、决策 — 聊着聊着就活过来了。"
argument-hint: "[work|life]"
version: "2.0.0"
user-invocable: true
allowed-tools: "Read Write Edit Bash Glob Grep"
---

# me — 你的数字自我

记录每天的工作和生活，聊着聊着就记下来了。然后在记忆中做梦、反思、决策。

---

## 命令一览

所有能力通过冒号子命令触发：

| 命令 | 用途 | 说明 |
|------|------|------|
| `/me` | 能力总览 | 无参数时显示所有能力 |
| `/me:init` | 初始化数据 | 首次使用前必须执行，创建 CSV + memory.md |
| `/me:record` | 记录日志 | 工作或生活，聊天式采录 |
| `/me:dream` | 整理记忆 | 从日志提炼记忆，整理已有记忆 |
| `/me:reflect` | 反思改进 | 发现行为模式，提出可执行建议 |
| `/me:decide` | 辅助决策 | 查找过去类似决策，给出参考 |
| `/me:recall` | 回忆总结 | 精选、述职、颁奖词、展示 |
| `/me:update` | 更新记忆 | 从日志提炼，写入记忆档案 |

---

## 能力一览

当用户输入 `/me` 无参数时：

```
你的数字自我，能做什么？

  🛠️ /me:init     — 初始化数据文件（首次使用必执行）
  📝 /me:record   — 记录今天的工作或生活
  💭 /me:dream    — 整理记忆，提炼日志，清理重复
  🔍 /me:reflect  — 反思行为模式，提出改进建议
  🎯 /me:decide   — 根据记忆辅助决策
  📊 /me:recall   — 回忆与总结，提取最有价值的内容
  🔄 /me:update   — 从日志提炼，更新记忆档案

选一个，或者直接说你想做什么。
```

---

## 路径约定

`CLAUDE_PLUGIN_ROOT` 指向插件根目录（如 `~/.claude/plugins/marketplaces/me/`）。所有 skill 内资源通过 `${CLAUDE_PLUGIN_ROOT}/skills/me/` 定位。

**数据目录** 通过 `~/.claude/me-config.json` 的 `data_dir` 字段配置（`/me:init` 时设置）。所有命令的 Step 0 均读取此配置获得 `DATA_DIR`。

| 资源 | 路径 |
|------|------|
| Python 工具 | `${CLAUDE_PLUGIN_ROOT}/skills/me/tools/` |
| 提示词模板 | `${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/` |
| 用户数据 | `DATA_DIR`（从 `~/.claude/me-config.json` 读取） |

---

## 工具映射

所有 Bash 命令使用 `${CLAUDE_PLUGIN_ROOT}` 定位工具，`DATA_DIR` 定位数据（从 `~/.claude/me-config.json` 读取）：

| 任务 | 命令 |
|------|------|
| 初始化 CSV | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action init --file {work_log|life_log} --data-dir DATA_DIR` |
| 插入记录 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action insert --file {log} --date {YYYY-MM-DD} --data '{json}' --data-dir DATA_DIR` |
| 覆盖记录 | 同上 + `--overwrite` |
| 查询记录 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action query --file {log} --from {date} --to {date} --format {table|json} --data-dir DATA_DIR` |
| 按impact排序 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action query --file work_log --sort-by impact --limit {N} --format json --data-dir DATA_DIR` |
| 导出 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action export --file {log} --from {date} --to {date} --format {markdown|json|csv} --output {path} --data-dir DATA_DIR` |
| 统计 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action stats --file {log} --from {date} --to {date} --data-dir DATA_DIR` |
| 添加新列 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/csv_manager.py --action add-column --file {log} --column {name} --default {val} --data-dir DATA_DIR` |
| 初始化记忆 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action init --data-dir DATA_DIR` |
| 读取记忆 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --data-dir DATA_DIR` |
| 读取某节 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action read --section {name} --data-dir DATA_DIR` |
| 更新某节 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action update-section --section {name} --content '{text}' --data-dir DATA_DIR` |
| 追加某节 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action append-section --section {name} --content '{text}' --data-dir DATA_DIR` |
| 提取摘要 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file {log} --format summary --data-dir DATA_DIR` |
| 提取模式 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file {log} --format patterns --data-dir DATA_DIR` |
| 高价值节点 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/memory_manager.py --action extract-from-csv --file {log} --impact-threshold 3 --format summary --data-dir DATA_DIR` |
| 版本备份 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/version_manager.py --action backup --data-dir DATA_DIR` |
| 版本回滚 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/version_manager.py --action rollback --version {v} --data-dir DATA_DIR` |
| 版本列表 | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/me/tools/version_manager.py --action list --data-dir DATA_DIR` |

---

## 数据存储

数据目录由 `~/.claude/me-config.json` 的 `data_dir` 字段决定（`/me:init` 时设置）。默认为插件内路径，推荐使用独立目录（如 `~/.me-data/`）。

数据目录下包含：

- `work_log.csv` — 工作日志
- `life_log.csv` — 生活日志
- `memory.md` — 记忆档案（双层架构的第二层）
- `meta.json` — Schema 定义与统计
- `versions/` — 版本备份

### CSV 列定义

**work_log.csv**：date(必填), summary(必填), project, category(开发/会议/调研/评审/规划/运维/沟通/文档), impact(1-5), key_result, mood, tags(逗号分隔)

**life_log.csv**：date(必填), summary(必填), mood, high_point, low_point, people, location, tags(逗号分隔)

列可通过 `add-column` 动态扩展。

### 记忆档案结构

memory.md 包含 6 个节：

- 核心轨迹（工作时间线、生活时间线）
- 模式识别（工作模式、生活模式、思维模式）
- 决策档案
- 反思档案
- 关注清单

---

## 运行规则

1. 所有脚本路径使用 `${CLAUDE_PLUGIN_ROOT}/skills/me/`，不用绝对路径或猜测路径。
2. 数据目录从 `~/.claude/me-config.json` 的 `data_dir` 字段读取，存入 `DATA_DIR` 变量。
3. 提示词模板用 `Read ${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/{name}.md` 读取。
4. **所有用户交互使用 AskUserQuestion 工具**，不输出纯文本问题。用户通过选项或 Other 输入自由文本。
5. category/impact/tags 由 agent 自动推断，不问用户。
6. 追问有节制：工作最多2轮，生活最多1轮。
7. 记忆数据不足时诚实告知，不强推结论。