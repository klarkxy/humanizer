#!/usr/bin/env python3
"""Create or complete a grill-your-novel project structure."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "references" / "模板"


def copy_missing(src: Path, dst: Path) -> bool:
    if dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def init_project(project: Path) -> tuple[list[Path], list[Path]]:
    created: list[Path] = []
    skipped: list[Path] = []
    project.mkdir(parents=True, exist_ok=True)

    for src in sorted(TEMPLATE_ROOT.rglob("*")):
        rel = src.relative_to(TEMPLATE_ROOT)
        dst = project / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        if copy_missing(src, dst):
            created.append(dst)
        else:
            skipped.append(dst)

    for dirname in ("大纲", "人物卡", "正文", ".grill"):
        (project / dirname).mkdir(parents=True, exist_ok=True)

    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化或补齐 grill-your-novel 中文小说项目模板。")
    parser.add_argument("project", help="小说项目目录")
    args = parser.parse_args()

    created, skipped = init_project(Path(args.project))
    print(f"项目目录: {Path(args.project).resolve()}")
    print(f"创建文件: {len(created)}")
    print(f"已存在跳过: {len(skipped)}")
    for path in created:
        print(f"+ {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
