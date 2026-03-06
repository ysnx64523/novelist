#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

REQUIRED_COLUMNS = [
    "id",
    "主线",
    "伏笔内容",
    "首次埋设章节",
    "计划回收章节",
    "实际回收章节",
    "状态",
    "关联人物",
    "备注",
]

DONE_STATUSES = {"已回收"}
INACTIVE_STATUSES = {"弃用"}
DEFAULT_OUTFILE = "06-长线统计.md"


def normalize_status(value: str) -> str:
    text = (value or "").strip()
    return text if text else "未标注"


def extract_chapter_num(value: str) -> int | None:
    text = (value or "").strip()
    if not text:
        return None
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def safe_cell(value: str) -> str:
    return (value or "").replace("|", "\\|").strip()


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV 为空或缺少表头。")
        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV 缺少字段: {', '.join(missing)}")
        return [dict(row) for row in reader]


def build_markdown(rows: list[dict[str, str]], current_chapter: int | None) -> str:
    status_counts = Counter(normalize_status(row.get("状态", "")) for row in rows)
    active_rows = [
        row
        for row in rows
        if normalize_status(row.get("状态", "")) not in INACTIVE_STATUSES
    ]
    done_rows = [
        row for row in active_rows if normalize_status(row.get("状态", "")) in DONE_STATUSES
    ]
    unresolved_rows = [
        row
        for row in active_rows
        if normalize_status(row.get("状态", "")) not in DONE_STATUSES
    ]
    completion_rate = (len(done_rows) / len(active_rows) * 100.0) if active_rows else 0.0

    overdue_rows: list[dict[str, str]] = []
    if current_chapter is not None:
        for row in unresolved_rows:
            target = extract_chapter_num(row.get("计划回收章节", ""))
            if target is not None and target <= current_chapter:
                overdue_rows.append(row)

    lines: list[str] = []
    lines.append("# 长线伏笔统计")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 记录总数：{len(rows)}")
    lines.append(f"- 活跃伏笔：{len(active_rows)}")
    lines.append(f"- 已回收：{len(done_rows)}")
    lines.append(f"- 完成率：{completion_rate:.1f}%")
    if current_chapter is not None:
        lines.append(f"- 当前章节：第{current_chapter}章")
    lines.append("")

    lines.append("## 状态分布")
    lines.append("")
    lines.append("| 状态 | 数量 |")
    lines.append("| --- | ---: |")
    for status, count in sorted(status_counts.items(), key=lambda item: item[0]):
        lines.append(f"| {safe_cell(status)} | {count} |")
    lines.append("")

    lines.append("## 未完成清单")
    lines.append("")
    lines.append("| ID | 主线 | 伏笔内容 | 计划回收章节 | 状态 |")
    lines.append("| --- | --- | --- | --- | --- |")
    if unresolved_rows:
        for row in unresolved_rows:
            lines.append(
                "| {id} | {main} | {detail} | {target} | {status} |".format(
                    id=safe_cell(row.get("id", "")),
                    main=safe_cell(row.get("主线", "")),
                    detail=safe_cell(row.get("伏笔内容", "")),
                    target=safe_cell(row.get("计划回收章节", "")),
                    status=safe_cell(normalize_status(row.get("状态", ""))),
                )
            )
    else:
        lines.append("| - | - | 当前无未完成项 | - | - |")
    lines.append("")

    if current_chapter is not None:
        lines.append("## 逾期待回收")
        lines.append("")
        lines.append("| ID | 伏笔内容 | 计划回收章节 | 当前状态 |")
        lines.append("| --- | --- | --- | --- |")
        if overdue_rows:
            for row in overdue_rows:
                lines.append(
                    "| {id} | {detail} | {target} | {status} |".format(
                        id=safe_cell(row.get("id", "")),
                        detail=safe_cell(row.get("伏笔内容", "")),
                        target=safe_cell(row.get("计划回收章节", "")),
                        status=safe_cell(normalize_status(row.get("状态", ""))),
                    )
                )
        else:
            lines.append("| - | 当前无逾期项 | - | - |")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="根据伏笔 CSV 生成长线统计 Markdown。")
    parser.add_argument("--csv", required=True, help="伏笔追踪 CSV 文件路径。")
    parser.add_argument("--out", help="输出 Markdown 路径。默认写入 CSV 同目录。")
    parser.add_argument(
        "--current-chapter",
        type=int,
        help="可选。用于识别逾期伏笔的当前章节号。",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"找不到 CSV 文件: {csv_path}")

    out_path = Path(args.out).resolve() if args.out else csv_path.with_name(DEFAULT_OUTFILE)
    rows = load_rows(csv_path)
    report = build_markdown(rows, args.current_chapter)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")

    print(f"[OK] 已生成统计文件: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
