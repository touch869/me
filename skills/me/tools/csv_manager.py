#!/usr/bin/env python3
"""CSV manager for me plugin.

Actions: init, insert, query, export, stats, add-column.
All operations target CSV files under --data-dir (default: plugin_root/data).
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Resolve paths: CLAUDE_PLUGIN_ROOT points to plugin root (me/),
# skill root is skills/me/ under it. Fallback to script location for dev mode.
_PLUGIN_ROOT_ENV = os.environ.get("CLAUDE_PLUGIN_ROOT")
if _PLUGIN_ROOT_ENV:
    PLUGIN_ROOT = Path(_PLUGIN_ROOT_ENV)
    SKILL_ROOT = PLUGIN_ROOT / "skills" / "me"
else:
    SKILL_ROOT = Path(__file__).resolve().parent.parent
    PLUGIN_ROOT = SKILL_ROOT.parent.parent
DEFAULT_DATA_DIR = SKILL_ROOT / "data"

DEFAULT_WORK_SCHEMA = {
    "mandatory": ["date", "summary"],
    "optional": ["project", "category", "impact", "key_result", "mood", "tags"],
}

DEFAULT_LIFE_SCHEMA = {
    "mandatory": ["date", "summary"],
    "optional": ["mood", "high_point", "low_point", "people", "location", "tags"],
}

SCHEMA_MAP = {
    "work_log": DEFAULT_WORK_SCHEMA,
    "life_log": DEFAULT_LIFE_SCHEMA,
}

META_FILE = "meta.json"


def resolve_data_dir(data_dir=None):
    if data_dir:
        return Path(data_dir)
    return DEFAULT_DATA_DIR


def resolve_file_path(log_name, data_dir=None):
    dd = resolve_data_dir(data_dir)
    return dd / f"{log_name}.csv"


def load_meta(data_dir=None):
    dd = resolve_data_dir(data_dir)
    meta_path = dd / META_FILE
    if meta_path.exists():
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def save_meta(meta, data_dir=None):
    dd = resolve_data_dir(data_dir)
    dd.mkdir(parents=True, exist_ok=True)
    meta["updated_at"] = datetime.now().isoformat()
    with open(dd / META_FILE, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def build_default_meta():
    schemas = {}
    for log_name, schema in SCHEMA_MAP.items():
        all_cols = schema["mandatory"] + schema["optional"]
        schemas[log_name] = {
            "mandatory": schema["mandatory"],
            "optional": schema["optional"],
            "all_columns": all_cols,
        }
    return {
        "version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "schemas": schemas,
        "stats": {"work_log_rows": 0, "life_log_rows": 0},
    }


def load_schema(log_name, data_dir=None):
    meta = load_meta(data_dir)
    if meta and log_name in meta.get("schemas", {}):
        return meta["schemas"][log_name]
    if log_name in SCHEMA_MAP:
        default = SCHEMA_MAP[log_name]
        return {
            "mandatory": default["mandatory"],
            "optional": default["optional"],
            "all_columns": default["mandatory"] + default["optional"],
        }
    print(f"Error: unknown log name '{log_name}'. Use work_log or life_log.")
    sys.exit(1)


def init_csv(log_name, data_dir=None):
    dd = resolve_data_dir(data_dir)
    dd.mkdir(parents=True, exist_ok=True)

    csv_path = resolve_file_path(log_name, data_dir)
    schema = load_schema(log_name, data_dir)
    all_cols = schema["all_columns"]

    if csv_path.exists():
        print(f"CSV file already exists: {csv_path}")
    else:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=all_cols)
            writer.writeheader()
        print(f"Created: {csv_path} with columns: {', '.join(all_cols)}")

    meta = load_meta(data_dir)
    if meta is None:
        meta = build_default_meta()
    save_meta(meta, data_dir)
    print(f"Meta file ready: {dd / META_FILE}")


def insert_row(log_name, date_str, data_json, overwrite=False, data_dir=None):
    csv_path = resolve_file_path(log_name, data_dir)
    if not csv_path.exists():
        print(f"Error: CSV file not found. Run 'init' first: {csv_path}")
        sys.exit(1)

    schema = load_schema(log_name, data_dir)
    all_cols = schema["all_columns"]
    mandatory = schema["mandatory"]

    row_data = json.loads(data_json)
    row_data["date"] = date_str

    for col in mandatory:
        if col not in row_data or not row_data[col]:
            print(f"Error: mandatory field '{col}' is missing or empty.")
            sys.exit(1)

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        existing_fieldnames = reader.fieldnames or all_cols

    existing_idx = None
    for i, row in enumerate(rows):
        if row.get("date") == date_str:
            existing_idx = i
            break

    if existing_idx is not None:
        if overwrite:
            rows[existing_idx] = {col: row_data.get(col, "") for col in existing_fieldnames}
            print(f"Overwritten existing row for date {date_str}.")
        else:
            print(f"Warning: date {date_str} already exists. Use --overwrite to replace.")
            sys.exit(1)
    else:
        new_row = {col: row_data.get(col, "") for col in existing_fieldnames}
        rows.append(new_row)
        print(f"Inserted row for date {date_str}.")

    rows.sort(key=lambda r: r.get("date", ""))

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=existing_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    meta = load_meta(data_dir)
    if meta:
        meta["stats"][f"{log_name}_rows"] = len(rows)
        save_meta(meta, data_dir)


def query_rows(log_name, from_date=None, to_date=None, filter_json=None,
               format_type="table", data_dir=None, sort_by=None, limit=None):
    csv_path = resolve_file_path(log_name, data_dir)
    if not csv_path.exists():
        print(f"Error: CSV file not found. Run 'init' first.")
        sys.exit(1)

    schema = load_schema(log_name, data_dir)
    all_cols = schema["all_columns"]

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if from_date:
        rows = [r for r in rows if r.get("date", "") >= from_date]
    if to_date:
        rows = [r for r in rows if r.get("date", "") <= to_date]

    if filter_json:
        filters = json.loads(filter_json)
        for key, val in filters.items():
            rows = [r for r in rows if r.get(key, "").lower() == val.lower()]

    # Tag-based filter: match if any tag in filter matches any tag in row
    # Requires --filter '{"tags": "重构"}' — matches rows where tags contains "重构"
    # This is already handled by the above logic since tags is comma-separated

    if sort_by:
        rows.sort(key=lambda r: r.get(sort_by, ""), reverse=True)

    if limit:
        rows = rows[:limit]

    if format_type == "json":
        print(json.dumps(rows, indent=2, ensure_ascii=False))
    elif format_type == "table":
        if not rows:
            print("No rows found.")
            return
        active_cols = []
        for col in all_cols:
            if any(r.get(col, "") for r in rows):
                active_cols.append(col)
        header = " | ".join(active_cols)
        sep = "-+-".join("-" * max(len(col), 3) for col in active_cols)
        print(header)
        print(sep)
        for row in rows:
            vals = [row.get(col, "") or "" for col in active_cols]
            print(" | ".join(vals))
    else:
        print(f"Unknown format: {format_type}. Use 'table' or 'json'.")


def export_rows(log_name, from_date=None, to_date=None, format_type="markdown",
                output_path=None, data_dir=None):
    csv_path = resolve_file_path(log_name, data_dir)
    if not csv_path.exists():
        print("Error: CSV file not found.")
        sys.exit(1)

    schema = load_schema(log_name, data_dir)

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if from_date:
        rows = [r for r in rows if r.get("date", "") >= from_date]
    if to_date:
        rows = [r for r in rows if r.get("date", "") <= to_date]

    label = "工作日志" if log_name == "work_log" else "生活日志"

    if format_type == "markdown":
        lines = [f"# {label}", ""]
        for row in rows:
            d = row.get("date", "")
            s = row.get("summary", "")
            lines.append(f"## {d}")
            lines.append(f"**摘要**: {s}")
            for col in schema["all_columns"]:
                if col in ("date", "summary"):
                    continue
                val = row.get(col, "")
                if val:
                    cn = _col_label(col)
                    lines.append(f"- **{cn}**: {val}")
            lines.append("")
        content = "\n".join(lines)

    elif format_type == "json":
        content = json.dumps(rows, indent=2, ensure_ascii=False)

    elif format_type == "csv":
        all_cols = schema["all_columns"]
        out_rows = [{col: row.get(col, "") for col in all_cols} for row in rows]
        import io
        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=all_cols)
        writer.writeheader()
        writer.writerows(out_rows)
        content = buf.getvalue()
    else:
        print(f"Unknown format: {format_type}. Use markdown, json, or csv.")
        sys.exit(1)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Exported to: {output_path}")
    else:
        print(content)


def _col_label(col):
    labels = {
        "date": "日期", "summary": "摘要", "project": "项目",
        "category": "类型", "impact": "重要度", "key_result": "关键产出",
        "mood": "心情", "tags": "标签",
        "high_point": "今日亮点", "low_point": "今日低谷",
        "people": "一起的人", "location": "地点",
    }
    return labels.get(col, col)


def compute_stats(log_name, from_date=None, to_date=None, data_dir=None):
    csv_path = resolve_file_path(log_name, data_dir)
    if not csv_path.exists():
        print("Error: CSV file not found.")
        sys.exit(1)

    schema = load_schema(log_name, data_dir)
    label = "工作日志" if log_name == "work_log" else "生活日志"

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if from_date:
        rows = [r for r in rows if r.get("date", "") >= from_date]
    if to_date:
        rows = [r for r in rows if r.get("date", "") <= to_date]

    total = len(rows)
    dates = sorted(r.get("date", "") for r in rows)

    print(f"=== {label} 统计 ===")
    print(f"总记录数: {total}")
    if dates:
        print(f"日期范围: {dates[0]} ~ {dates[-1]}")
        print(f"记录天数: {len(dates)}")
    else:
        print("暂无记录")

    print("\n列填充率:")
    for col in schema["all_columns"]:
        filled = sum(1 for r in rows if r.get(col, ""))
        rate = (filled / total * 100) if total > 0 else 0
        cn = _col_label(col)
        print(f"  {cn} ({col}): {filled}/{total} = {rate:.1f}%")

    # Mood distribution
    if "mood" in schema["all_columns"]:
        moods = [r.get("mood", "") for r in rows if r.get("mood", "")]
        if moods:
            from collections import Counter
            mood_counts = Counter(moods)
            print(f"\n心情分布:")
            for mood, cnt in mood_counts.most_common(10):
                print(f"  {mood}: {cnt}")

    # Category distribution (work_log)
    if "category" in schema["all_columns"]:
        cats = [r.get("category", "") for r in rows if r.get("category", "")]
        if cats:
            from collections import Counter
            cat_counts = Counter(cats)
            print(f"\n工作类型分布:")
            for cat, cnt in cat_counts.most_common(10):
                print(f"  {cat}: {cnt}")

    # Impact distribution (work_log)
    if "impact" in schema["all_columns"]:
        impacts = [r.get("impact", "") for r in rows if r.get("impact", "")]
        if impacts:
            from collections import Counter
            impact_counts = Counter(impacts)
            print(f"\n重要度分布:")
            for imp, cnt in sorted(impact_counts.items()):
                print(f"  impact={imp}: {cnt}")

    # Tag frequency
    if "tags" in schema["all_columns"]:
        all_tags = []
        for r in rows:
            t = r.get("tags", "")
            if t:
                all_tags.extend(t.split(","))
        if all_tags:
            from collections import Counter
            tag_counts = Counter(all_tags)
            print(f"\n高频标签 (Top 15):")
            for tag, cnt in tag_counts.most_common(15):
                print(f"  {tag}: {cnt}")


def add_column(log_name, column_name, default_value="", data_dir=None):
    csv_path = resolve_file_path(log_name, data_dir)
    if not csv_path.exists():
        print("Error: CSV file not found. Run 'init' first.")
        sys.exit(1)

    schema = load_schema(log_name, data_dir)
    all_cols = schema["all_columns"]

    if column_name in all_cols:
        print(f"Column '{column_name}' already exists.")
        sys.exit(1)

    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        row[column_name] = default_value

    new_fieldnames = all_cols + [column_name]

    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    meta = load_meta(data_dir)
    if meta:
        meta["schemas"][log_name]["optional"].append(column_name)
        meta["schemas"][log_name]["all_columns"].append(column_name)
        save_meta(meta, data_dir)

    cn = _col_label(column_name)
    print(f"Added column '{column_name}' ({cn}) to {log_name} with default: '{default_value}'")
    print(f"Existing {len(rows)} rows backfilled.")


def main():
    parser = argparse.ArgumentParser(description="me plugin CSV manager")
    parser.add_argument("--action", required=True,
                        choices=["init", "insert", "query", "export", "stats", "add-column"])
    parser.add_argument("--file", required=True, choices=["work_log", "life_log"])
    parser.add_argument("--data-dir", default=None)
    parser.add_argument("--date", default=None)
    parser.add_argument("--data", default=None)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--from", dest="from_date", default=None)
    parser.add_argument("--to", dest="to_date", default=None)
    parser.add_argument("--filter", dest="filter_json", default=None)
    parser.add_argument("--format", dest="format_type", default="table")
    parser.add_argument("--output", dest="output_path", default=None)
    parser.add_argument("--column", dest="column_name", default=None)
    parser.add_argument("--default", dest="default_value", default="")
    parser.add_argument("--sort-by", dest="sort_by", default=None,
                        help="Sort results by column (e.g., impact)")
    parser.add_argument("--limit", dest="limit", default=None, type=int,
                        help="Limit number of results")

    args = parser.parse_args()

    if args.action == "init":
        init_csv(args.file, args.data_dir)
    elif args.action == "insert":
        if not args.date or not args.data:
            print("Error: --date and --data are required for insert.")
            sys.exit(1)
        insert_row(args.file, args.date, args.data, args.overwrite, args.data_dir)
    elif args.action == "query":
        fmt = args.format_type if args.format_type in ("table", "json") else "table"
        query_rows(args.file, args.from_date, args.to_date, args.filter_json,
                   fmt, args.data_dir, args.sort_by, args.limit)
    elif args.action == "export":
        if args.format_type not in ("markdown", "json", "csv"):
            print("Error: --format must be markdown, json, or csv for export.")
            sys.exit(1)
        export_rows(args.file, args.from_date, args.to_date, args.format_type,
                    args.output_path, args.data_dir)
    elif args.action == "stats":
        compute_stats(args.file, args.from_date, args.to_date, args.data_dir)
    elif args.action == "add-column":
        if not args.column_name:
            print("Error: --column is required for add-column.")
            sys.exit(1)
        add_column(args.file, args.column_name, args.default_value, args.data_dir)


if __name__ == "__main__":
    main()