#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_README = """# 项目说明

本目录用于单文件夹完成网文创作全流程：
1. 先写总大纲（01）
2. 再写子大纲（02）
3. 在 `风格参考/` 维护样文与风格卡
4. 在 `正文/` 目录逐章输出正文
5. 同步维护设定集（04）
6. 记录并统计长线伏笔（05、06）
7. 维护当前角色状态与行动模式（07）
8. 维护每章读者面信息控制（09）

建议每次开工前后执行：
- 写前体检：`python scripts/narrative_engine.py doctor --project .`
- 写前上下文：`python scripts/narrative_engine.py context --project . --chapter <章节号> --create-chapter`
- 写前分镜：`python scripts/narrative_engine.py storyboard --project . --chapter <章节号> --target-chars 3500 --create-context`
- 交付门禁：`python scripts/narrative_engine.py gate --project . --chapter <章节号>`
"""

FILE_TEMPLATE_MAP = {
    "01-总大纲.md": "outline-template.md",
    "02-子大纲.md": "suboutline-template.md",
    "04-设定集.md": "setting-bible-template.md",
    "05-长线伏笔.csv": "foreshadow-template.csv",
    "07-当前角色状态.md": "character-state-template.md",
    "09-读者面信息.md": "reader-info-template.md",
}

CHAPTERS_DIR = "正文"
FIRST_CHAPTER = "第001章.md"
STYLE_DIR = "风格参考"
STYLE_TEMPLATE_MAP = {
    "01-样文摘录.md": "style-sample-template.md",
    "02-风格卡.md": "style-card-template.md",
}


def write_file(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"文件已存在，使用 --force 覆盖: {path}")
    path.write_text(content, encoding="utf-8", newline="\n")


def build_workspace(root: Path, name: str, force: bool) -> Path:
    skill_root = Path(__file__).resolve().parent.parent
    references_dir = skill_root / "references"
    project_dir = (root / name).resolve()

    if project_dir.exists() and any(project_dir.iterdir()) and not force:
        raise FileExistsError(f"目录非空，使用 --force 覆盖文件: {project_dir}")

    project_dir.mkdir(parents=True, exist_ok=True)
    write_file(project_dir / "00-项目说明.md", PROJECT_README, force=force)

    for target_name, template_name in FILE_TEMPLATE_MAP.items():
        template_path = references_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"缺少模板文件: {template_path}")
        write_file(
            project_dir / target_name,
            template_path.read_text(encoding="utf-8"),
            force=force,
        )

    # 正文采用“目录 + 分章文件”模式，避免单文件过长。
    chapters_dir = project_dir / CHAPTERS_DIR
    chapters_dir.mkdir(parents=True, exist_ok=True)
    chapter_template = references_dir / "draft-template.md"
    if not chapter_template.exists():
        raise FileNotFoundError(f"缺少模板文件: {chapter_template}")
    write_file(
        chapters_dir / FIRST_CHAPTER,
        chapter_template.read_text(encoding="utf-8"),
        force=force,
    )

    style_dir = project_dir / STYLE_DIR
    style_dir.mkdir(parents=True, exist_ok=True)
    for target_name, template_name in STYLE_TEMPLATE_MAP.items():
        template_path = references_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"缺少模板文件: {template_path}")
        write_file(
            style_dir / target_name,
            template_path.read_text(encoding="utf-8"),
            force=force,
        )

    stats_script = skill_root / "scripts" / "foreshadow_stats.py"
    csv_path = project_dir / "05-长线伏笔.csv"
    stats_path = project_dir / "06-长线统计.md"
    subprocess.run(
        [
            sys.executable,
            str(stats_script),
            "--csv",
            str(csv_path),
            "--out",
            str(stats_path),
        ],
        check=True,
    )

    return project_dir


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化网文写作单文件夹工作区。")
    parser.add_argument("--root", default=".", help="项目父目录，默认当前目录。")
    parser.add_argument("--name", required=True, help="作品目录名。")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件。")
    args = parser.parse_args()

    project_dir = build_workspace(Path(args.root), args.name, args.force)
    print(f"[OK] 已初始化项目目录: {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
