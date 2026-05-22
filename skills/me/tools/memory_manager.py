#!/usr/bin/env python3
"""Memory manager for me plugin.

Actions: init, read, update-section, append-section, extract-from-csv, version-info.
Manages the memory.md file — the accumulated understanding layer built from CSV data.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

_PLUGIN_ROOT_ENV = os.environ.get("CLAUDE_PLUGIN_ROOT")
if _PLUGIN_ROOT_ENV:
    PLUGIN_ROOT = Path(_PLUGIN_ROOT_ENV)
    SKILL_ROOT = PLUGIN_ROOT / "skills" / "me"
else:
    SKILL_ROOT = Path(__file__).resolve().parent.parent
    PLUGIN_ROOT = SKILL_ROOT.parent.parent
DEFAULT_DATA_DIR = SKILL_ROOT / "data"

MEMORY_FILE = "memory.md"
META_FILE = "meta.json"

MEMORY_TEMPLATE = """# 记忆档案

> 这是你的累积记忆，由日志数据定期提炼而成。不是日志的复制，而是对规律、模式和因果的理解。

## 核心轨迹

### 工作时间线
<!-- impact≥3 的重要节点，按时间排列 -->

### 生活时间线
<!-- 有 high_point 或 low_point 的节点 -->

## 模式识别

### 工作模式
<!-- 高产出触发条件、常见卡点、项目切换节奏、高效时段... -->

### 生活模式
<!-- 情绪周期、社交偏好、作息规律、消费习惯... -->

### 思维模式
<!-- 决策倾向：理性vs感性？果断vs犹豫？风险态度？压力反应？ -->

## 决策档案
<!-- 重大决策记录：情境 → 选择 → 原因 → 当前结果 -->

## 反思档案
<!-- 阶段性反思：发现的问题 → 改进方向 → 执行计划 -->

## 关注清单
<!-- 用户明确说过想追踪的事 -->
"""


def resolve_data_dir(data_dir=None):
    if data_dir:
        return Path(data_dir)
    return DEFAULT_DATA_DIR


def init_memory(data_dir=None):
    dd = resolve_data_dir(data_dir)
    dd.mkdir(parents=True, exist_ok=True)

    mem_path = dd / MEMORY_FILE
    if mem_path.exists():
        print(f"Memory file already exists: {mem_path}")
        return

    with open(mem_path, "w", encoding="utf-8") as f:
        f.write(MEMORY_TEMPLATE)

    # Update meta.json with memory version info
    meta_path = dd / META_FILE
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    else:
        meta = {"version": "1.0.0", "created_at": datetime.now().isoformat()}
    meta["memory_version"] = "v0"
    meta["memory_updated_at"] = datetime.now().isoformat()
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"Created: {mem_path}")


def _find_heading_level(lines, section):
    """Find the heading level (number of #) for a given section name."""
    for line in lines:
        stripped = line.strip()
        # Match "## Section" or "### Section" etc.
        if stripped.endswith(f" {section}"):
            hashes = stripped.split(" ")[0]
            if hashes.startswith("#") and hashes.replace("#", "") == "":
                return len(hashes)
    return 2  # default to ## level


def _section_heading_match(line, section, level):
    """Check if a line matches the section heading at the given level."""
    prefix = "#" * level
    return line.strip() == f"{prefix} {section}"


def read_memory(data_dir=None, section=None):
    dd = resolve_data_dir(data_dir)
    mem_path = dd / MEMORY_FILE

    if not mem_path.exists():
        print("Error: memory.md not found. Run 'init' first.")
        sys.exit(1)

    with open(mem_path, "r", encoding="utf-8") as f:
        content = f.read()

    if section:
        lines = content.split("\n")
        level = _find_heading_level(lines, section)
        in_section = False
        section_lines = []
        for line in lines:
            if _section_heading_match(line, section, level):
                in_section = True
                section_lines.append(line)
                continue
            if in_section and line.strip().startswith("#") and not _section_heading_match(line, section, level):
                hashes = line.strip().split(" ")[0]
                if hashes.startswith("#") and hashes.replace("#", "") == "":
                    if len(hashes) <= level:
                        break
            if in_section:
                section_lines.append(line)
        if section_lines:
            print("\n".join(section_lines))
        else:
            print(f"Section '{section}' not found in memory.md.")
    else:
        print(content)


def update_section(section_name, new_content, data_dir=None):
    dd = resolve_data_dir(data_dir)
    mem_path = dd / MEMORY_FILE

    if not mem_path.exists():
        print("Error: memory.md not found. Run 'init' first.")
        sys.exit(1)

    with open(mem_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    level = _find_heading_level(lines, section_name)

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if _section_heading_match(line, section_name, level):
            start_idx = i
        elif start_idx is not None and line.strip().startswith("#"):
            hashes = line.strip().split(" ")[0]
            if hashes.startswith("#") and hashes.replace("#", "") == "":
                line_level = len(hashes)
                if line_level <= level:
                    end_idx = i
                    break

    if start_idx is None:
        print(f"Section '{section_name}' not found. Available headings:")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("## ") or stripped.startswith("### "):
                print(f"  {stripped}")
        sys.exit(1)

    replacement = [lines[start_idx], "", new_content.strip(), ""]
    if end_idx:
        new_lines = lines[:start_idx] + replacement + lines[end_idx:]
    else:
        new_lines = lines[:start_idx] + replacement

    with open(mem_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    # Update meta
    meta_path = dd / META_FILE
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        meta["memory_updated_at"] = datetime.now().isoformat()
        # Increment version
        v = meta.get("memory_version", "v0")
        num = int(v.replace("v", "")) + 1
        meta["memory_version"] = f"v{num}"
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

    print(f"Updated section '{section_name}' in memory.md (version: v{num})")


def append_section(section_name, append_content, data_dir=None):
    dd = resolve_data_dir(data_dir)
    mem_path = dd / MEMORY_FILE

    if not mem_path.exists():
        print("Error: memory.md not found. Run 'init' first.")
        sys.exit(1)

    with open(mem_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    level = _find_heading_level(lines, section_name)

    start_idx = None
    end_idx = None
    for i, line in enumerate(lines):
        if _section_heading_match(line, section_name, level):
            start_idx = i
        elif start_idx is not None and line.strip().startswith("#"):
            hashes = line.strip().split(" ")[0]
            if hashes.startswith("#") and hashes.replace("#", "") == "":
                line_level = len(hashes)
                if line_level <= level:
                    end_idx = i
                    break

    if start_idx is None:
        print(f"Section '{section_name}' not found.")
        sys.exit(1)

    # Find insertion point: just before the next ## heading or end of section content
    # Insert after the last non-empty, non-comment line in the section
    if end_idx:
        # Insert before the next section heading
        insertion = [f"<!-- [追加于 {datetime.now().strftime('%Y-%m-%d')}] -->", append_content.strip(), ""]
        new_lines = lines[:end_idx] + insertion + lines[end_idx:]
    else:
        # Append at end of file
        insertion = [f"<!-- [追加于 {datetime.now().strftime('%Y-%m-%d')}] -->", append_content.strip()]
        new_lines = lines + [""] + insertion

    with open(mem_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print(f"Appended to section '{section_name}' in memory.md")


def extract_from_csv(log_name, from_date=None, to_date=None, data_dir=None,
                     impact_threshold=None, format_type="summary"):
    """Extract structured data from CSV for memory update."""
    dd = resolve_data_dir(data_dir)
    csv_path = dd / f"{log_name}.csv"

    if not csv_path.exists():
        print(f"Error: {log_name}.csv not found.")
        sys.exit(1)

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if from_date:
        rows = [r for r in rows if r.get("date", "") >= from_date]
    if to_date:
        rows = [r for r in rows if r.get("date", "") <= to_date]

    if impact_threshold:
        rows = [r for r in rows if r.get("impact", "") and int(r.get("impact", "0")) >= impact_threshold]

    if format_type == "summary":
        # Output a concise summary suitable for memory.md timeline sections
        for row in rows:
            d = row.get("date", "")
            s = row.get("summary", "")
            extra = []
            if row.get("impact"):
                extra.append(f"impact={row['impact']}")
            if row.get("project"):
                extra.append(row["project"])
            if row.get("mood"):
                extra.append(row["mood"])
            if row.get("category"):
                extra.append(row["category"])
            if row.get("high_point"):
                extra.append(f"亮点: {row['high_point']}")
            if row.get("low_point"):
                extra.append(f"低谷: {row['low_point']}")
            if row.get("tags"):
                extra.append(f"[{row['tags']}]")
            suffix = " | " + ", ".join(extra) if extra else ""
            print(f"- **{d}** — {s}{suffix}")

    elif format_type == "patterns":
        # Output pattern analysis hints
        if not rows:
            print("No data to analyze.")
            return
        # Collect tag frequencies
        tags = []
        for r in rows:
            t = r.get("tags", "")
            if t:
                tags.extend(t.split(","))
        from collections import Counter
        if tags:
            tag_counts = Counter(tags)
            print("### 标签频率")
            for tag, cnt in tag_counts.most_common(20):
                print(f"- {tag}: {cnt}")

        # Mood patterns
        moods = [r.get("mood", "") for r in rows if r.get("mood")]
        if moods:
            mood_counts = Counter(moods)
            print("\n### 心情分布")
            for mood, cnt in mood_counts.most_common(10):
                print(f"- {mood}: {cnt}")

        # Category patterns (work)
        cats = [r.get("category", "") for r in rows if r.get("category")]
        if cats:
            cat_counts = Counter(cats)
            print("\n### 工作类型分布")
            for cat, cnt in cat_counts.most_common(10):
                print(f"- {cat}: {cnt}")

        # Impact distribution
        impacts = [r.get("impact", "") for r in rows if r.get("impact")]
        if impacts:
            print(f"\n### 重要度统计")
            avg = sum(int(i) for i in impacts) / len(impacts)
            print(f"- 平均重要度: {avg:.1f}/5")
            high_impact = [r for r in rows if r.get("impact") and int(r["impact"]) >= 4]
            print(f"- 高重要度天数 (impact≥4): {len(high_impact)}/{len(rows)}")

    elif format_type == "json":
        print(json.dumps(rows, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="me plugin memory manager")
    parser.add_argument("--action", required=True,
                        choices=["init", "read", "update-section", "append-section",
                                 "extract-from-csv", "version-info"])
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--section", default=None, help="Section name for read/update/append")
    parser.add_argument("--content", default=None, help="New content for update/append")
    parser.add_argument("--file", default=None, choices=["work_log", "life_log"],
                        help="CSV file for extract-from-csv")
    parser.add_argument("--from", dest="from_date", default=None)
    parser.add_argument("--to", dest="to_date", default=None)
    parser.add_argument("--impact-threshold", dest="impact_threshold", default=None, type=int,
                        help="Minimum impact score for extract (1-5)")
    parser.add_argument("--format", dest="format_type", default="summary",
                        choices=["summary", "patterns", "json"])

    args = parser.parse_args()

    if args.action == "init":
        init_memory(args.data_dir)

    elif args.action == "read":
        read_memory(args.data_dir, args.section)

    elif args.action == "update-section":
        if not args.section or not args.content:
            print("Error: --section and --content are required for update-section.")
            sys.exit(1)
        update_section(args.section, args.content, args.data_dir)

    elif args.action == "append-section":
        if not args.section or not args.content:
            print("Error: --section and --content are required for append-section.")
            sys.exit(1)
        append_section(args.section, args.content, args.data_dir)

    elif args.action == "extract-from-csv":
        if not args.file:
            print("Error: --file is required for extract-from-csv.")
            sys.exit(1)
        extract_from_csv(args.file, args.from_date, args.to_date, args.data_dir,
                         args.impact_threshold, args.format_type)

    elif args.action == "version-info":
        dd = resolve_data_dir(args.data_dir)
        meta_path = dd / META_FILE
        if meta_path.exists():
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            print(f"Memory version: {meta.get('memory_version', 'unknown')}")
            print(f"Last updated: {meta.get('memory_updated_at', 'unknown')}")
            print(f"CSV work_log rows: {meta.get('stats', {}).get('work_log_rows', 0)}")
            print(f"CSV life_log rows: {meta.get('stats', {}).get('life_log_rows', 0)}")
        else:
            print("No meta.json found. Run init first.")


if __name__ == "__main__":
    main()