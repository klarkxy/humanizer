#!/usr/bin/env python3
"""Create or complete a grill-your-novel project structure."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "references" / "模板"

SHAPES = {
    "free": "自由组合：只建最小工作区，由 Agent 按任务补文件。",
    "long": "长篇连载/商业小说：完整小说项目模板。",
    "short": "短篇/中篇/系列短篇：轻量项目，不预设世界书/人物卡/卷纲。",
    "essay": "散文/随笔：轻量项目，不预设剧情工程。",
    "zhihu": "知乎回答/问答型观点文章：轻量项目，不预设小说结构。",
    "nonfiction": "非虚构叙事/人物特写：轻量项目，不预设小说结构。",
}

FULL_TEMPLATE_FILES = [
    "项目总览.md",
    "世界书.md",
    "风格规则.md",
    "伏笔与承诺.md",
    "大纲/全书大纲.md",
    "大纲/卷纲模板.md",
    "大纲/章纲模板.md",
    "人物卡/人物卡模板.md",
]

GRILL_FILES = [
    ".grill/状态.md",
    ".grill/TODO.md",
    ".grill/未决问题.md",
    ".grill/决策记录.md",
    ".grill/冲突记录.md",
    ".grill/待确认修改.md",
]

LIGHT_PROJECT_OVERVIEW = """# 项目总览

## 项目名称
填写作品名、回答题目、系列名或项目代号。

## 作品形态
填写 long / short / essay / zhihu / nonfiction / free，或写自己的分类。

## 当前目标
这次最想推进什么：立意、结构、正文、修订、材料整理、发布版本等。

## 目标读者
谁会读，为什么读，读完希望获得什么。

## 核心问题或核心体验
短篇写核心冲突和结尾回响；散文写主题、经验和意象；知乎回答写问题边界、立场和反驳点。

## 材料边界
哪些是事实、亲历、采访、引用、设定或待确认内容。

## 输出形态
预计篇幅、发布平台、是否需要标题、小标题、注释、参考资料或多版本。

## 已确认边界
列出明确不写、不碰、暂不展开的方向。
"""

LIGHT_STYLE_RULES = """# 风格规则

## 叙述声音
记录语言气质、视角距离、语速、幽默感、情绪浓度。

## 结构偏好
记录常用结构：故事推进、观点递进、问题拆解、意象串联、材料对照等。

## 禁用倾向
记录不想要的腔调、套路、词汇和表达习惯。
"""


def copy_missing(src: Path, dst: Path) -> bool:
    if dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def write_missing(path: Path, text: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return True


def copy_template_file(project: Path, rel: str) -> bool:
    return copy_missing(TEMPLATE_ROOT / rel, project / rel)


def init_project(project: Path, shape: str = "free") -> tuple[list[Path], list[Path]]:
    created: list[Path] = []
    skipped: list[Path] = []
    project.mkdir(parents=True, exist_ok=True)

    (project / ".grill").mkdir(parents=True, exist_ok=True)
    (project / "正文").mkdir(parents=True, exist_ok=True)

    if shape == "long":
        for dirname in ("大纲", "人物卡", "正文", ".grill"):
            (project / dirname).mkdir(parents=True, exist_ok=True)
        rels = FULL_TEMPLATE_FILES + GRILL_FILES
        for rel in rels:
            dst = project / rel
            if copy_template_file(project, rel):
                created.append(dst)
            else:
                skipped.append(dst)
    else:
        light_files = {
            "项目总览.md": LIGHT_PROJECT_OVERVIEW,
            "风格规则.md": LIGHT_STYLE_RULES,
        }
        for rel, text in light_files.items():
            dst = project / rel
            if write_missing(dst, text):
                created.append(dst)
            else:
                skipped.append(dst)
        for rel in GRILL_FILES:
            dst = project / rel
            if copy_template_file(project, rel):
                created.append(dst)
            else:
                skipped.append(dst)

    return created, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化或补齐 grill-your-novel 中文创作项目。")
    parser.add_argument("project", help="项目目录")
    parser.add_argument(
        "--shape",
        choices=sorted(SHAPES),
        default="free",
        help="项目形态；默认 free，只建最小工作区。",
    )
    args = parser.parse_args()

    created, skipped = init_project(Path(args.project), args.shape)
    print(f"项目目录: {Path(args.project).resolve()}")
    print(f"作品形态: {args.shape} - {SHAPES[args.shape]}")
    print(f"创建文件: {len(created)}")
    print(f"已存在跳过: {len(skipped)}")
    for path in created:
        print(f"+ {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
