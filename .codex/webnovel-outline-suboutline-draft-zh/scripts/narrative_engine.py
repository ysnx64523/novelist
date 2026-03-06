#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REQUIRED_FILES = [
    "00-项目说明.md",
    "01-总大纲.md",
    "02-子大纲.md",
    "04-设定集.md",
    "05-长线伏笔.csv",
    "07-当前角色状态.md",
]
REQUIRED_DIRS = ["正文", "风格参考"]
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

CHAPTER_FILE_RE = re.compile(r"^第(\d{3})章\.md$")
CHAPTER_HEADING_RE = re.compile(r"^(?:#{1,6}\s*)?第\s*0*(\d+)\s*章[^\n]*", re.M)
FORESHADOW_ID_RE = re.compile(r"\bF\d{3}\b")
ROLE_ACTION_ROW_RE = re.compile(r"\|\s*第\s*0*(\d+)\s*章\s*\|")

PLACEHOLDER_SNIPPETS = [
    "<章节标题>",
    "（在此写正文）",
    "(在此写正文)",
    "在此写正文",
]

STORYBOARD_REQUIRED_HEADINGS = [
    "## 场景清单",
    "## 章节描写规约（硬约束）",
]
STORYBOARD_SCENE_HEADING_RE = re.compile(r"^###\s*场景\s*\d+", re.M)


@dataclass
class CheckResult:
    name: str
    status: str
    detail: str


def normalize_status(value: str) -> str:
    text = (value or "").strip()
    return text if text else "未标注"


def normalize_id(value: str) -> str:
    return (value or "").strip().upper()


def extract_chapter_num(value: str) -> int | None:
    text = (value or "").strip()
    if not text:
        return None
    match = re.search(r"\d+", text)
    return int(match.group()) if match else None


def safe_cell(value: str) -> str:
    return (value or "").replace("|", "\\|").strip()


def count_non_whitespace(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def chapter_file(project_dir: Path, chapter: int) -> Path:
    return project_dir / "正文" / f"第{chapter:03d}章.md"


def engine_dir(project_dir: Path) -> Path:
    return project_dir / "正文" / ".engine"


def context_file(project_dir: Path, chapter: int) -> Path:
    return engine_dir(project_dir) / f"第{chapter:03d}章-上下文.md"


def storyboard_file(project_dir: Path, chapter: int) -> Path:
    return engine_dir(project_dir) / f"第{chapter:03d}章-分镜纲.md"


def read_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("CSV 为空或缺少表头。")
        missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"CSV 缺少字段: {', '.join(missing)}")
        return [dict(row) for row in reader]


def collect_chapter_files(chapters_dir: Path) -> tuple[dict[int, Path], list[Path]]:
    chapter_files: dict[int, Path] = {}
    invalid_names: list[Path] = []
    if not chapters_dir.exists():
        return chapter_files, invalid_names
    for path in sorted(chapters_dir.glob("*.md")):
        match = CHAPTER_FILE_RE.match(path.name)
        if not match:
            invalid_names.append(path)
            continue
        chapter_num = int(match.group(1))
        chapter_files[chapter_num] = path
    return chapter_files, invalid_names


def split_suboutline_sections(suboutline_text: str) -> dict[int, str]:
    sections: dict[int, str] = {}
    matches = list(CHAPTER_HEADING_RE.finditer(suboutline_text))
    for index, match in enumerate(matches):
        chapter_num = int(match.group(1))
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(suboutline_text)
        sections[chapter_num] = suboutline_text[start:end].strip()
    return sections


def infer_next_chapter(chapter_files: dict[int, Path]) -> int:
    if not chapter_files:
        return 1
    return max(chapter_files) + 1


def find_placeholders(text: str) -> list[str]:
    return [marker for marker in PLACEHOLDER_SNIPPETS if marker in text]


def infer_scene_count(target_chars: int) -> int:
    if target_chars <= 1500:
        return 2
    if target_chars <= 3000:
        return 3
    if target_chars <= 5000:
        return 4
    return 5


def scene_weight_distribution(scene_count: int) -> list[int]:
    if scene_count <= 2:
        return [45, 55]
    if scene_count == 3:
        return [25, 45, 30]
    if scene_count == 4:
        return [20, 30, 30, 20]
    return [18, 24, 24, 20, 14]


def extract_style_constraints(style_card_text: str, max_items: int = 4) -> list[str]:
    lines = [line.strip() for line in style_card_text.splitlines()]
    candidates: list[str] = []
    for line in lines:
        if not line:
            continue
        if line.startswith(("- ", "* ")):
            candidates.append(line[2:].strip())
            continue
        if re.match(r"^\d+\.\s+", line):
            candidates.append(re.sub(r"^\d+\.\s+", "", line).strip())
    return [item for item in candidates if item][:max_items]


def workspace_checks(project_dir: Path) -> list[CheckResult]:
    checks: list[CheckResult] = []

    for dirname in REQUIRED_DIRS:
        target = project_dir / dirname
        if target.is_dir():
            checks.append(CheckResult(f"目录存在：{dirname}", "PASS", str(target)))
        else:
            checks.append(CheckResult(f"目录存在：{dirname}", "FAIL", f"缺少目录：{target}"))

    for filename in REQUIRED_FILES:
        target = project_dir / filename
        if target.is_file():
            checks.append(CheckResult(f"文件存在：{filename}", "PASS", str(target)))
        else:
            checks.append(CheckResult(f"文件存在：{filename}", "FAIL", f"缺少文件：{target}"))

    csv_path = project_dir / "05-长线伏笔.csv"
    if csv_path.exists():
        try:
            _ = load_rows(csv_path)
            checks.append(CheckResult("伏笔 CSV 结构", "PASS", "字段完整"))
        except Exception as exc:  # noqa: BLE001
            checks.append(CheckResult("伏笔 CSV 结构", "FAIL", str(exc)))

    chapters_dir = project_dir / "正文"
    chapter_files, invalid_names = collect_chapter_files(chapters_dir)
    if invalid_names:
        names = ", ".join(path.name for path in invalid_names)
        checks.append(CheckResult("章节命名规范", "FAIL", f"非法文件名：{names}"))
    else:
        checks.append(CheckResult("章节命名规范", "PASS", "符合 第NNN章.md 规则"))

    if chapter_files:
        sorted_nums = sorted(chapter_files)
        gaps = [
            str(num)
            for num in range(sorted_nums[0], sorted_nums[-1] + 1)
            if num not in chapter_files
        ]
        if gaps:
            checks.append(CheckResult("章节连续性", "WARN", f"缺失章节：{', '.join(gaps)}"))
        else:
            checks.append(CheckResult("章节连续性", "PASS", "无缺号"))
    else:
        checks.append(CheckResult("章节连续性", "WARN", "尚无已命名正文章节"))

    suboutline_path = project_dir / "02-子大纲.md"
    if suboutline_path.exists():
        sections = split_suboutline_sections(read_utf8(suboutline_path))
        if sections:
            checks.append(CheckResult("子大纲可解析章节", "PASS", f"共 {len(sections)} 章"))
        else:
            checks.append(
                CheckResult(
                    "子大纲可解析章节",
                    "WARN",
                    "未识别到“第N章”标题，请检查子大纲结构。",
                )
            )

    return checks


def run_foreshadow_stats(project_dir: Path, chapter: int) -> tuple[bool, str]:
    skill_root = Path(__file__).resolve().parent.parent
    script_path = skill_root / "scripts" / "foreshadow_stats.py"
    csv_path = project_dir / "05-长线伏笔.csv"
    out_path = project_dir / "06-长线统计.md"
    command = [
        sys.executable,
        str(script_path),
        "--csv",
        str(csv_path),
        "--out",
        str(out_path),
        "--current-chapter",
        str(chapter),
    ]
    process = subprocess.run(command, capture_output=True, text=True)
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip() or "未知错误"
        return False, detail
    return True, process.stdout.strip() or f"已更新 {out_path}"


def find_recent_role_actions(role_state_text: str, max_rows: int = 5) -> list[str]:
    rows = [
        line.strip()
        for line in role_state_text.splitlines()
        if ROLE_ACTION_ROW_RE.search(line)
    ]
    return rows[-max_rows:]


def build_context_markdown(project_dir: Path, chapter: int) -> str:
    suboutline_path = project_dir / "02-子大纲.md"
    role_state_path = project_dir / "07-当前角色状态.md"
    csv_path = project_dir / "05-长线伏笔.csv"

    suboutline_text = read_utf8(suboutline_path) if suboutline_path.exists() else ""
    role_state_text = read_utf8(role_state_path) if role_state_path.exists() else ""

    sections = split_suboutline_sections(suboutline_text) if suboutline_text else {}
    section_text = sections.get(chapter, "（未在 02-子大纲.md 中找到对应章节）")

    chapter_files, _ = collect_chapter_files(project_dir / "正文")
    previous_chapter = chapter - 1
    previous_path = chapter_files.get(previous_chapter)
    previous_tail = ""
    if previous_path and previous_path.exists():
        previous_text = read_utf8(previous_path).strip()
        previous_tail = previous_text[-1200:] if len(previous_text) > 1200 else previous_text
    else:
        previous_tail = "（无上一章正文或未命名为第NNN章.md）"

    active_rows: list[dict[str, str]] = []
    if csv_path.exists():
        rows = load_rows(csv_path)
        for row in rows:
            status = normalize_status(row.get("状态", ""))
            if status in DONE_STATUSES or status in INACTIVE_STATUSES:
                continue
            first_chapter = extract_chapter_num(row.get("首次埋设章节", ""))
            if first_chapter is None or first_chapter <= chapter:
                active_rows.append(row)

    recent_actions = find_recent_role_actions(role_state_text)
    lines: list[str] = []
    lines.append(f"# 第{chapter:03d}章写作上下文")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 目标章节：第{chapter:03d}章")
    lines.append("")
    lines.append("## 本章子大纲")
    lines.append("")
    lines.append(section_text)
    lines.append("")
    lines.append("## 上一章结尾参考（最多1200字）")
    lines.append("")
    lines.append(previous_tail)
    lines.append("")
    lines.append("## 活跃伏笔（未完成）")
    lines.append("")
    lines.append("| ID | 主线 | 伏笔内容 | 计划回收章节 | 状态 |")
    lines.append("| --- | --- | --- | --- | --- |")
    if active_rows:
        for row in active_rows:
            lines.append(
                "| {id} | {main} | {detail} | {target} | {status} |".format(
                    id=safe_cell(normalize_id(row.get("id", ""))),
                    main=safe_cell(row.get("主线", "")),
                    detail=safe_cell(row.get("伏笔内容", "")),
                    target=safe_cell(row.get("计划回收章节", "")),
                    status=safe_cell(normalize_status(row.get("状态", ""))),
                )
            )
    else:
        lines.append("| - | - | 当前无活跃伏笔 | - | - |")
    lines.append("")
    lines.append("## 角色行动记录（最近5条）")
    lines.append("")
    if recent_actions:
        for row in recent_actions:
            lines.append(f"- `{row}`")
    else:
        lines.append("- （未在 07-当前角色状态.md 中识别到章节行动记录）")
    lines.append("")
    lines.append("## 本章执行清单")
    lines.append("")
    lines.append("- 完成正文后更新 `07-当前角色状态.md` 的本章行动记录。")
    lines.append("- 完成正文后更新 `05-长线伏笔.csv`。")
    lines.append(
        f"- 运行 `python scripts/narrative_engine.py gate --project \"{project_dir}\" --chapter {chapter}` 做门禁验收。"
    )
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_storyboard_markdown(project_dir: Path, chapter: int, target_chars: int) -> str:
    suboutline_path = project_dir / "02-子大纲.md"
    style_card_path = project_dir / "风格参考" / "02-风格卡.md"
    context_path = context_file(project_dir, chapter)

    suboutline_text = read_utf8(suboutline_path) if suboutline_path.exists() else ""
    sections = split_suboutline_sections(suboutline_text) if suboutline_text else {}
    section_text = sections.get(chapter, "（未在 02-子大纲.md 中找到对应章节）")
    context_text = read_utf8(context_path) if context_path.exists() else "（未生成上下文文件）"
    style_card_text = read_utf8(style_card_path) if style_card_path.exists() else ""

    scene_count = infer_scene_count(target_chars)
    weights = scene_weight_distribution(scene_count)
    style_constraints = extract_style_constraints(style_card_text)

    lines: list[str] = []
    lines.append(f"# 第{chapter:03d}章分镜纲")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 目标章节：第{chapter:03d}章")
    lines.append(f"- 目标字数：约 {target_chars} 字")
    lines.append(f"- 建议场景数：{scene_count}")
    lines.append("")
    lines.append("## 本章输入摘要")
    lines.append("")
    lines.append("### 子大纲摘录")
    lines.append("")
    lines.append(section_text)
    lines.append("")
    lines.append("### 上下文摘录（首段）")
    lines.append("")
    context_excerpt = context_text.strip().splitlines()
    if context_excerpt:
        lines.extend(context_excerpt[:16])
    else:
        lines.append("（无）")
    lines.append("")
    lines.append(f"## 场景清单（共{scene_count}场）")
    lines.append("")
    for idx in range(scene_count):
        scene_index = idx + 1
        ratio = weights[idx] if idx < len(weights) else 20
        lines.append(f"### 场景{scene_index}（建议占比 {ratio}%）")
        lines.append("- 场景目的：")
        lines.append("- 时间/地点：")
        lines.append("- 出场角色：")
        lines.append("- 冲突/阻力：")
        lines.append("- 场景动作链（按先后写动作，不写总结）：")
        lines.append("- 感官锚点（视觉/听觉/触觉至少二选一）：")
        lines.append("- 对话任务（每段对话必须推动关系或信息）：")
        lines.append("- 信息投放（新增/确认/误导/保留）：")
        lines.append("- 伏笔操作（埋设/回收，引用ID）：")
        lines.append("- 结尾钩子（把角色推入下一场景）：")
        lines.append("")
    lines.append("## 章节描写规约（硬约束）")
    lines.append("")
    lines.append("- 前20%必须出现冲突、异常或代价信号，禁止日常流水开场。")
    lines.append("- 每个场景至少落地1个可视动作与1个可感知异常，不得只讲结论。")
    lines.append("- 对话字数占比建议 30%-45%，超出时必须删空话与复述。")
    lines.append("- 心理描写必须绑定外部动作或环境触发，不得连续空想。")
    lines.append("- 章末必须给出“不可回避的下一步行动”，而非抽象感想。")
    if style_constraints:
        lines.append("")
        lines.append("### 风格卡约束（自动摘录）")
        lines.append("")
        for item in style_constraints:
            lines.append(f"- {item}")
    lines.append("")
    lines.append("## 写后回写提醒")
    lines.append("")
    lines.append("- 写完正文后回写 `07-当前角色状态.md` 本章行动记录。")
    lines.append("- 写完正文后回写 `05-长线伏笔.csv` 并刷新统计。")
    lines.append(
        f"- 运行 `python scripts/narrative_engine.py gate --project \"{project_dir}\" --chapter {chapter}`。"
    )
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def check_storyboard_quality(storyboard_text: str, min_scenes: int) -> list[CheckResult]:
    checks: list[CheckResult] = []
    missing_headings = [
        heading for heading in STORYBOARD_REQUIRED_HEADINGS if heading not in storyboard_text
    ]
    if missing_headings:
        checks.append(
            CheckResult(
                "分镜纲结构完整性",
                "FAIL",
                f"缺少区块：{', '.join(missing_headings)}",
            )
        )
    else:
        checks.append(CheckResult("分镜纲结构完整性", "PASS", "结构完整"))

    scene_count = len(STORYBOARD_SCENE_HEADING_RE.findall(storyboard_text))
    if scene_count < min_scenes:
        checks.append(
            CheckResult(
                "分镜场景数",
                "FAIL",
                f"仅识别到 {scene_count} 个场景，低于门禁下限 {min_scenes}。",
            )
        )
    else:
        checks.append(CheckResult("分镜场景数", "PASS", f"已识别 {scene_count} 个场景"))

    field_checks = {
        "场景目的：": "场景目的字段",
        "冲突/阻力：": "冲突字段",
        "信息投放（新增/确认/误导/保留）：": "信息投放字段",
        "结尾钩子（把角色推入下一场景）：": "结尾钩子字段",
    }
    for token, label in field_checks.items():
        count = storyboard_text.count(token)
        if count < scene_count:
            checks.append(
                CheckResult(
                    f"分镜字段覆盖：{label}",
                    "WARN",
                    f"字段出现 {count} 次，少于场景数 {scene_count}。",
                )
            )
        else:
            checks.append(CheckResult(f"分镜字段覆盖：{label}", "PASS", "覆盖完整"))
    return checks


def results_summary(results: list[CheckResult]) -> tuple[int, int, int]:
    passed = sum(1 for item in results if item.status == "PASS")
    warned = sum(1 for item in results if item.status == "WARN")
    failed = sum(1 for item in results if item.status == "FAIL")
    return passed, warned, failed


def print_results(results: list[CheckResult]) -> None:
    for item in results:
        print(f"[{item.status}] {item.name} - {item.detail}")


def write_gate_report(
    report_path: Path,
    chapter: int,
    chapter_path: Path,
    char_count: int | None,
    results: list[CheckResult],
) -> None:
    passed, warned, failed = results_summary(results)
    lines: list[str] = []
    lines.append("# 叙事引擎门禁报告")
    lines.append("")
    lines.append(f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- 目标章节：第{chapter:03d}章")
    lines.append(f"- 正文文件：{chapter_path}")
    if char_count is not None:
        lines.append(f"- 正文非空白字符数：{char_count}")
    lines.append(f"- 检查结果：PASS {passed} / WARN {warned} / FAIL {failed}")
    lines.append("")
    lines.append("| 项目 | 状态 | 说明 |")
    lines.append("| --- | --- | --- |")
    for item in results:
        lines.append(
            f"| {safe_cell(item.name)} | {item.status} | {safe_cell(item.detail)} |"
        )
    lines.append("")
    lines.append("## 结论")
    lines.append("")
    if failed > 0:
        lines.append("- 门禁未通过：请先修复所有 `FAIL` 项。")
    elif warned > 0:
        lines.append("- 门禁通过（含警告）：建议修复 `WARN` 项后再交付。")
    else:
        lines.append("- 门禁通过：可进入交付环节。")
    lines.append("")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def cmd_doctor(args: argparse.Namespace) -> int:
    project_dir = Path(args.project).resolve()
    if not project_dir.exists():
        print(f"[FAIL] 项目目录不存在：{project_dir}")
        return 2

    results = workspace_checks(project_dir)
    print_results(results)
    _, warned, failed = results_summary(results)
    if failed > 0:
        return 2
    if warned > 0 and args.strict:
        return 1
    return 0


def cmd_context(args: argparse.Namespace) -> int:
    project_dir = Path(args.project).resolve()
    if not project_dir.exists():
        print(f"[FAIL] 项目目录不存在：{project_dir}")
        return 2

    chapter_files, _ = collect_chapter_files(project_dir / "正文")
    chapter = args.chapter if args.chapter is not None else infer_next_chapter(chapter_files)
    chapter_path = chapter_file(project_dir, chapter)

    if args.create_chapter and not chapter_path.exists():
        skill_root = Path(__file__).resolve().parent.parent
        template_path = skill_root / "references" / "draft-template.md"
        if not template_path.exists():
            print(f"[FAIL] 缺少模板文件：{template_path}")
            return 2
        chapter_path.parent.mkdir(parents=True, exist_ok=True)
        chapter_path.write_text(read_utf8(template_path), encoding="utf-8", newline="\n")
        print(f"[PASS] 已创建章节文件：{chapter_path}")

    output_path = Path(args.out).resolve() if args.out else context_file(project_dir, chapter)
    markdown = build_context_markdown(project_dir, chapter)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8", newline="\n")

    print(f"[PASS] 已生成上下文文件：{output_path}")
    return 0


def cmd_storyboard(args: argparse.Namespace) -> int:
    project_dir = Path(args.project).resolve()
    if not project_dir.exists():
        print(f"[FAIL] 项目目录不存在：{project_dir}")
        return 2

    chapter_files, _ = collect_chapter_files(project_dir / "正文")
    chapter = args.chapter if args.chapter is not None else infer_next_chapter(chapter_files)

    if args.create_context and not context_file(project_dir, chapter).exists():
        markdown = build_context_markdown(project_dir, chapter)
        context_path = context_file(project_dir, chapter)
        context_path.parent.mkdir(parents=True, exist_ok=True)
        context_path.write_text(markdown, encoding="utf-8", newline="\n")
        print(f"[PASS] 已补生成上下文文件：{context_path}")

    chapter_path = chapter_file(project_dir, chapter)
    if args.create_chapter and not chapter_path.exists():
        skill_root = Path(__file__).resolve().parent.parent
        template_path = skill_root / "references" / "draft-template.md"
        if not template_path.exists():
            print(f"[FAIL] 缺少模板文件：{template_path}")
            return 2
        chapter_path.parent.mkdir(parents=True, exist_ok=True)
        chapter_path.write_text(read_utf8(template_path), encoding="utf-8", newline="\n")
        print(f"[PASS] 已创建章节文件：{chapter_path}")

    output_path = Path(args.out).resolve() if args.out else storyboard_file(project_dir, chapter)
    if output_path.exists() and not args.force:
        print(f"[FAIL] 分镜纲已存在，使用 --force 覆盖：{output_path}")
        return 2

    markdown = build_storyboard_markdown(project_dir, chapter, args.target_chars)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8", newline="\n")
    print(f"[PASS] 已生成分镜纲文件：{output_path}")
    return 0


def cmd_gate(args: argparse.Namespace) -> int:
    project_dir = Path(args.project).resolve()
    chapter = int(args.chapter)
    chapter_path = chapter_file(project_dir, chapter)
    report_path = (
        Path(args.report).resolve()
        if args.report
        else project_dir / "08-叙事引擎报告.md"
    )

    results = workspace_checks(project_dir)
    char_count: int | None = None

    if not chapter_path.exists():
        results.append(CheckResult("目标章节存在", "FAIL", f"找不到文件：{chapter_path}"))
    else:
        text = read_utf8(chapter_path)
        char_count = count_non_whitespace(text)
        results.append(CheckResult("目标章节存在", "PASS", str(chapter_path)))

        if chapter > 1 and not chapter_file(project_dir, chapter - 1).exists():
            results.append(
                CheckResult(
                    "前序章节存在",
                    "WARN",
                    f"缺少第{chapter - 1:03d}章，可能导致连贯性风险。",
                )
            )
        else:
            results.append(CheckResult("前序章节存在", "PASS", "前序章节可用"))

        placeholders = find_placeholders(text)
        if placeholders:
            results.append(
                CheckResult(
                    "章节占位符清理",
                    "FAIL",
                    f"检测到占位符：{', '.join(placeholders)}",
                )
            )
        else:
            results.append(CheckResult("章节占位符清理", "PASS", "未发现模板占位符"))

        heading_match = CHAPTER_HEADING_RE.search(text)
        if heading_match and int(heading_match.group(1)) == chapter:
            results.append(CheckResult("章节标题匹配", "PASS", "标题章节号匹配"))
        elif heading_match:
            results.append(
                CheckResult(
                    "章节标题匹配",
                    "WARN",
                    f"正文标题为第{int(heading_match.group(1)):03d}章，与目标章节不一致。",
                )
            )
        else:
            results.append(
                CheckResult("章节标题匹配", "WARN", "未识别到“第N章”标题，建议补充。")
            )

        if char_count < args.min_chars:
            results.append(
                CheckResult(
                    "章节长度建议",
                    "WARN",
                    f"当前非空白字符数 {char_count}，低于建议下限 {args.min_chars}。",
                )
            )
        elif char_count > args.max_chars:
            results.append(
                CheckResult(
                    "章节长度建议",
                    "WARN",
                    f"当前非空白字符数 {char_count}，高于建议上限 {args.max_chars}。",
                )
            )
        else:
            results.append(
                CheckResult("章节长度建议", "PASS", f"字符数 {char_count} 在建议区间内")
            )

        suboutline_path = project_dir / "02-子大纲.md"
        if suboutline_path.exists():
            sections = split_suboutline_sections(read_utf8(suboutline_path))
            if chapter in sections:
                results.append(CheckResult("子大纲覆盖本章", "PASS", "已找到对应章节子大纲"))
            else:
                results.append(
                    CheckResult("子大纲覆盖本章", "FAIL", "子大纲未找到该章节，请先补全。")
                )

        chapter_storyboard_path = storyboard_file(project_dir, chapter)
        if not chapter_storyboard_path.exists():
            results.append(
                CheckResult(
                    "分镜纲中间件",
                    "FAIL",
                    f"缺少分镜纲：{chapter_storyboard_path}（先运行 storyboard 命令）",
                )
            )
        else:
            results.append(CheckResult("分镜纲中间件", "PASS", str(chapter_storyboard_path)))
            storyboard_text = read_utf8(chapter_storyboard_path)
            results.extend(check_storyboard_quality(storyboard_text, args.min_scenes))

        csv_path = project_dir / "05-长线伏笔.csv"
        if csv_path.exists():
            rows = load_rows(csv_path)
            known_ids = {normalize_id(row.get("id", "")) for row in rows if row.get("id")}
            used_ids = {normalize_id(item) for item in FORESHADOW_ID_RE.findall(text)}
            unknown_ids = sorted(item for item in used_ids if item not in known_ids)
            if unknown_ids:
                results.append(
                    CheckResult(
                        "伏笔ID合法性",
                        "FAIL",
                        f"正文出现未登记ID：{', '.join(unknown_ids)}",
                    )
                )
            else:
                results.append(CheckResult("伏笔ID合法性", "PASS", "正文中的伏笔ID均已登记"))

            overdue_rows = []
            for row in rows:
                status = normalize_status(row.get("状态", ""))
                if status in DONE_STATUSES or status in INACTIVE_STATUSES:
                    continue
                target = extract_chapter_num(row.get("计划回收章节", ""))
                if target is not None and target <= chapter:
                    overdue_rows.append(row)
            if overdue_rows:
                ids = ", ".join(
                    normalize_id(row.get("id", "")) or "<空ID>" for row in overdue_rows[:10]
                )
                results.append(
                    CheckResult(
                        "逾期伏笔提醒",
                        "WARN",
                        f"存在 {len(overdue_rows)} 条逾期待回收伏笔：{ids}",
                    )
                )
            else:
                results.append(CheckResult("逾期伏笔提醒", "PASS", "无逾期待回收伏笔"))

        role_state_path = project_dir / "07-当前角色状态.md"
        if role_state_path.exists():
            role_state_text = read_utf8(role_state_path)
            chapter_rows = {int(match.group(1)) for match in ROLE_ACTION_ROW_RE.finditer(role_state_text)}
            if chapter in chapter_rows:
                results.append(CheckResult("角色状态回写", "PASS", "本章行动记录已更新"))
            else:
                results.append(
                    CheckResult(
                        "角色状态回写",
                        "FAIL",
                        "07-当前角色状态.md 未记录本章行动。",
                    )
                )

    stats_ok, stats_detail = run_foreshadow_stats(project_dir, chapter)
    if stats_ok:
        results.append(CheckResult("长线统计刷新", "PASS", stats_detail))
    else:
        results.append(CheckResult("长线统计刷新", "FAIL", stats_detail))

    write_gate_report(report_path, chapter, chapter_path, char_count, results)
    print_results(results)
    print(f"[PASS] 已写入门禁报告：{report_path}")

    _, warned, failed = results_summary(results)
    if failed > 0:
        return 2
    if warned > 0 and args.strict:
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="网文叙事引擎运行器：项目体检、上下文构建、分镜中间件、章节门禁。"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="检查项目结构和关键文件。")
    doctor.add_argument("--project", default=".", help="项目目录路径。")
    doctor.add_argument("--strict", action="store_true", help="将 WARN 视为非通过。")
    doctor.set_defaults(func=cmd_doctor)

    context = subparsers.add_parser("context", help="生成指定章节的写作上下文文件。")
    context.add_argument("--project", default=".", help="项目目录路径。")
    context.add_argument("--chapter", type=int, help="目标章节号；默认自动推断下一章。")
    context.add_argument(
        "--create-chapter",
        action="store_true",
        help="如果目标章节文件不存在，则用正文模板创建。",
    )
    context.add_argument("--out", help="上下文输出文件路径。")
    context.set_defaults(func=cmd_context)

    storyboard = subparsers.add_parser(
        "storyboard", help="生成指定章节的分镜纲中间件。"
    )
    storyboard.add_argument("--project", default=".", help="项目目录路径。")
    storyboard.add_argument(
        "--chapter", type=int, help="目标章节号；默认自动推断下一章。"
    )
    storyboard.add_argument(
        "--target-chars",
        type=int,
        default=3500,
        help="目标章节字数，用于估算场景数量。默认 3500。",
    )
    storyboard.add_argument(
        "--create-context",
        action="store_true",
        help="若本章上下文不存在，先自动生成上下文文件。",
    )
    storyboard.add_argument(
        "--create-chapter",
        action="store_true",
        help="如果目标章节文件不存在，则用正文模板创建。",
    )
    storyboard.add_argument("--out", help="分镜纲输出文件路径。")
    storyboard.add_argument(
        "--force", action="store_true", help="覆盖已存在的分镜纲文件。"
    )
    storyboard.set_defaults(func=cmd_storyboard)

    gate = subparsers.add_parser("gate", help="对指定章节执行交付前门禁检查。")
    gate.add_argument("--project", default=".", help="项目目录路径。")
    gate.add_argument("--chapter", required=True, type=int, help="目标章节号。")
    gate.add_argument(
        "--min-chars",
        type=int,
        default=1500,
        help="章节建议最小非空白字符数，默认 1500。",
    )
    gate.add_argument(
        "--max-chars",
        type=int,
        default=12000,
        help="章节建议最大非空白字符数，默认 12000。",
    )
    gate.add_argument(
        "--report",
        help="门禁报告输出路径，默认 <项目目录>/08-叙事引擎报告.md。",
    )
    gate.add_argument(
        "--min-scenes",
        type=int,
        default=2,
        help="分镜纲至少应包含的场景数，默认 2。",
    )
    gate.add_argument("--strict", action="store_true", help="将 WARN 视为非通过。")
    gate.set_defaults(func=cmd_gate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
