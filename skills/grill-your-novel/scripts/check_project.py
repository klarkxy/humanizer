#!/usr/bin/env python3
"""Validate grill-your-novel project structure without judging story quality."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "references" / "模板"

REQUIRED_FILES = [
    "项目总览.md",
    "世界书.md",
    "风格规则.md",
    "伏笔与承诺.md",
    "大纲/全书大纲.md",
    "大纲/卷纲模板.md",
    "大纲/章纲模板.md",
    "人物卡/人物卡模板.md",
    ".grill/状态.md",
    ".grill/TODO.md",
    ".grill/未决问题.md",
    ".grill/决策记录.md",
    ".grill/冲突记录.md",
    ".grill/待确认修改.md",
]

REQUIRED_DIRS = ["大纲", "人物卡", "正文", ".grill"]

CHAPTER_HEADINGS = [
    "本章功能",
    "开场钩子",
    "主角目标",
    "阻碍与冲突",
    "中段转折",
    "代价或收获",
    "信息增量",
    "情绪增量",
    "结尾钩子",
    "涉及 Canon",
]

TODO_HEADINGS = ["当前进行", "阻塞", "下一步", "暂缓", "已完成", "创作任务", "维护任务"]
PROPOSAL_RE = re.compile(r"^##\s+PENDING-\d{3,}\s*$", re.MULTILINE)
STATUS_RE = re.compile(r"^状态：\s*(待确认|已确认|已应用|已驳回|需改写)\s*$", re.MULTILINE)


def copy_missing(project: Path, rel: str) -> bool:
    src = TEMPLATE_ROOT / rel
    dst = project / rel
    if dst.exists() or not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def count_cjk_chars(text: str) -> int:
    return sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")


def check_project(project: Path, fix: bool = False) -> list[str]:
    findings: list[str] = []

    for dirname in REQUIRED_DIRS:
        path = project / dirname
        if not path.exists():
            if fix:
                path.mkdir(parents=True, exist_ok=True)
                findings.append(f"FIXED missing directory: {dirname}")
            else:
                findings.append(f"Missing directory: {dirname}")
        elif not path.is_dir():
            findings.append(f"Expected directory but found file: {dirname}")

    for rel in REQUIRED_FILES:
        path = project / rel
        if not path.exists():
            if fix and copy_missing(project, rel):
                findings.append(f"FIXED missing file: {rel}")
            else:
                findings.append(f"Missing file: {rel}")

    chapter_template = project / "大纲" / "章纲模板.md"
    if chapter_template.exists():
        text = read_text(chapter_template)
        for heading in CHAPTER_HEADINGS:
            if f"## {heading}" not in text:
                findings.append(f"Chapter template missing heading: {heading}")

    todo = project / ".grill" / "TODO.md"
    if todo.exists():
        text = read_text(todo)
        for heading in TODO_HEADINGS:
            if f"## {heading}" not in text and f"### {heading}" not in text:
                findings.append(f"TODO missing section: {heading}")

    pending = project / ".grill" / "待确认修改.md"
    if pending.exists():
        text = read_text(pending)
        ids = PROPOSAL_RE.findall(text)
        if ids and not STATUS_RE.search(text):
            findings.append("Proposal entries exist but no valid status line was found.")

    manuscript_dir = project / "正文"
    if manuscript_dir.exists():
        for path in sorted(manuscript_dir.glob("*.md")):
            chars = count_cjk_chars(read_text(path))
            if chars and chars < 2000:
                findings.append(f"Chapter may be under 2000 Chinese chars: {path.name} ({chars})")
            if chars > 4000:
                findings.append(f"Chapter exceeds 4000 Chinese chars; consider splitting: {path.name} ({chars})")

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 grill-your-novel 项目结构；不评价创作内容。")
    parser.add_argument("project", help="小说项目目录")
    parser.add_argument("--fix", action="store_true", help="只补齐缺失目录和空模板，不补创作内容")
    args = parser.parse_args()

    project = Path(args.project)
    findings = check_project(project, args.fix)
    if findings:
        print("FOUND:")
        for item in findings:
            print(f"- {item}")
        return 1 if not args.fix else 0
    print("PASS: project structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
