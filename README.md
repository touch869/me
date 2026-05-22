# me — 你的数字自我

记录、回忆、做梦、反思、决策 — 聊着聊着就活过来了。

## 命令格式

所有能力通过 `/me:xxx` 冒号子命令触发：

```
/me          — 显示所有能力（Hub）
/me:init     — 初始化数据文件（首次使用必执行）
/me:record   — 记录工作或生活
/me:dream    — 在记忆里做梦，连接碎片
/me:reflect  — 反思行为模式，提出改进建议
/me:decide   — 根据记忆辅助决策
/me:recall   — 回忆与总结，提取最有价值的内容
/me:update   — 从日志提炼，更新记忆档案
```

更具体的使用：

```
/me:record work          — 记录今天的工作
/me:record life          — 记录今天的生活
/me:record work 2026-05-20 — 补录工作日志
/me:recall 上半年        — 回忆上半年工作
/me:reflect work         — 反思工作模式
```

## 架构

双层设计：

- **Layer 1 — CSV 日志层**：记录"发生了什么"
- **Layer 2 — memory.md 记忆层**：理解"为什么"和"规律是什么"

## 安装

方式一：从 GitHub 安装（推荐）

```bash
claude plugin marketplace add https://github.com/AssassinGQ/me.git
```

方式二：从本地目录安装

```bash
# 先 clone（如果还没有的话）
git clone git@github.com:AssassinGQ/me.git
cd me

# 使用安装脚本
python3 tools/install.py

# 或直接用 CLI
claude plugin marketplace add .
```

卸载：

```bash
claude plugin marketplace remove me
# 或
python3 tools/install.py --action uninstall
```

安装后，Claude Code 自动将 `commands/` 目录下的文件注册为 `/me:xxx` 冒号子命令。

## 首次使用

安装后执行 `/me:init` 初始化数据文件。

## 路径约定

`CLAUDE_PLUGIN_ROOT` 指向插件根目录。所有 skill 内资源通过 `${CLAUDE_PLUGIN_ROOT}/skills/me/` 定位。

- 脚本：`${CLAUDE_PLUGIN_ROOT}/skills/me/tools/`
- 提示词：`${CLAUDE_PLUGIN_ROOT}/skills/me/prompts/`
- 用户数据：由 `~/.claude/me-config.json` 的 `data_dir` 字段决定（`/me:init` 时设置，默认插件内，推荐 `~/.me-data/`）

## CSV 列定义

**work_log.csv**：date, summary, project, category(开发/会议/调研/评审/规划/运维/沟通/文档), impact(1-5), key_result, mood, tags

**life_log.csv**：date, summary, mood, high_point, low_point, people, location, tags

列可动态扩展。

## 依赖

仅使用 Python 标准库，无需额外安装。

## 目录结构

```
me/                               # 插件根目录 (CLAUDE_PLUGIN_ROOT 指向此处)
├── .claude-plugin/               # 插件元数据
│   ├── plugin.json
│   └── marketplace.json
├── commands/                     # 冒号子命令 (Claude Code 自动注册为 /me:xxx)
│   ├── init.md                   # /me:init
│   ├── record.md                 # /me:record
│   ├── dream.md                  # /me:dream
│   ├── reflect.md                # /me:reflect
│   ├── decide.md                 # /me:decide
│   ├── recall.md                 # /me:recall
│   └── update.md                 # /me:update
├── skills/me/                    # 主 skill
│   ├── SKILL.md                  # /me 入口 (Hub)
│   ├── prompts/                  # 提示词模板
│   │   ├── work_intake.md
│   │   ├── life_intake.md
│   │   ├── catchup_intake.md
│   │   ├── recall.md
│   │   ├── dream.md
│   │   ├── reflect.md
│   │   ├── decide.md
│   │   └── memory_update.md
│   ├── tools/                    # Python 工具脚本
│   │   ├── csv_manager.py        # CSV 6 actions
│   │   ├── memory_manager.py     # memory.md 6 actions
│   │   ├── version_manager.py    # 版本 3 actions
│   │   └── install.py            # 安装/卸载 (在插件根运行)
│   ├── requirements.txt          # (空，仅标准库)
│   └── data/                     # 用户数据 (首次 /me:init 时创建)
│       ├── work_log.csv
│       ├── life_log.csv
│       ├── memory.md
│       ├── meta.json
│       └── versions/
└── README.md
```