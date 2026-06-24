#!/usr/bin/env python3
"""校验生成的 humanizer-zh 小说风格 skill 目录。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
HAN_RE = re.compile(r"[\u4e00-\u9fff]")
LOCAL_PATH_RE = re.compile(r"([A-Za-z]:\\|\\\\|/Users/|/home/|source\.local\.txt|evidence\.local\.md|tmp/)")
PLACEHOLDER_RE = re.compile(r"(\{[^}\n]+\}|<slug>|<display_name>|<[^>\n]+>)")
REQUIRED_SECTIONS = [
    "默认策略",
    "风格基线",
    "风格证据",
    "去 AI 味规则",
    "完整工作示例",
    "常见场景配方",
    "改写流程",
    "禁区",
    "快速改写检查",
    "边界",
    "自检",
]
RULE_CATEGORY_KEYWORDS = {
    "叙事距离": ["直述情绪", "概述", "过滤词", "贴标签", "过渡", "旁白", "短废话"],
    "词汇与修辞": ["AI 词汇", "三段式", "否定式", "模糊归因", "同义词", "主题总结", "单字"],
    "对话与人物声口": ["对话", "台词", "潜台词", "同声", "称谓", "声口"],
    "场景与信息流": ["设定", "场景", "景物", "结论", "节奏", "段落", "假文学"],
    "情感与内心": ["情感", "内心", "身体反应", "时间", "情绪"],
    "作品风格迁移边界": ["世界观", "术语", "事实", "不新增", "边界", "迁移"],
}


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def parse_frontmatter(text: str, failures: list[str]) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail("SKILL.md missing YAML frontmatter", failures)
        return {}
    fields: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            fail(f"frontmatter 行无效：{raw_line}", failures)
            continue
        key, value = raw_line.split(":", 1)
        fields[key.strip()] = value.strip().strip("\"'")
    extra = set(fields) - {"name", "description"}
    missing = {"name", "description"} - set(fields)
    if extra:
        fail(f"frontmatter 包含不支持的字段：{sorted(extra)}", failures)
    if missing:
        fail(f"frontmatter 缺少字段：{sorted(missing)}", failures)
    return fields


def chinese_count(text: str) -> int:
    return len(HAN_RE.findall(text))


def excerpt_blocks(text: str) -> list[str]:
    blocks: list[str] = []
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "原文短摘录" not in line:
            continue
        collected: list[str] = []
        for next_line in lines[i + 1 :]:
            if next_line.startswith(">"):
                collected.append(next_line.lstrip("> ").strip())
                continue
            if collected:
                break
            if next_line.strip():
                continue
        if collected:
            blocks.append("\n".join(collected))
    return blocks


def count_heading(text: str, prefix: str) -> int:
    return len(re.findall(rf"^{re.escape(prefix)}", text, re.M))


def validate_skill_body(text: str, failures: list[str], *, min_lines: int, max_lines: int) -> None:
    line_count = len(text.splitlines())
    if line_count < min_lines:
        fail(f"SKILL.md 只有 {line_count} 行；公开成品建议不少于 {min_lines} 行", failures)
    if line_count > max_lines:
        fail(f"SKILL.md 有 {line_count} 行；共享成品上限是 {max_lines} 行", failures)

    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in text:
            fail(f"缺少必备章节：{section}", failures)

    evidence_count = count_heading(text, "### 证据 ")
    rule_count = count_heading(text, "### 规则 ")
    example_count = count_heading(text, "### 示例 ")

    if not 10 <= evidence_count <= 16:
        fail(f"风格证据数量为 {evidence_count}；要求 10-16 条", failures)
    if not 20 <= rule_count <= 35:
        fail(f"去 AI 味规则数量为 {rule_count}；要求 20-35 条", failures)
    if not 3 <= example_count <= 6:
        fail(f"完整工作示例数量为 {example_count}；要求 3-6 组", failures)

    missing_categories = []
    for category, keywords in RULE_CATEGORY_KEYWORDS.items():
        if not any(keyword in text for keyword in keywords):
            missing_categories.append(category)
    if missing_categories:
        fail(f"规则池类别覆盖不足，缺少：{missing_categories}", failures)


def validate_meta(skill_dir: Path, failures: list[str]) -> None:
    meta_path = skill_dir / "_meta.json"
    if not meta_path.exists():
        fail("缺少 _meta.json", failures)
        return
    try:
        meta_text = meta_path.read_text(encoding="utf-8")
        meta = json.loads(meta_text)
    except Exception as exc:  # noqa: BLE001
        fail(f"_meta.json 不是合法 JSON：{exc}", failures)
        return

    required = {"name", "display_name", "source_type", "generated_at", "sample_summary", "style_summary", "privacy"}
    missing = required - set(meta)
    if missing:
        fail(f"_meta.json 缺少字段：{sorted(missing)}", failures)
    if LOCAL_PATH_RE.search(meta_text):
        fail("_meta.json 包含本地路径或私有产物引用", failures)
    privacy = meta.get("privacy", {})
    if privacy.get("contains_full_text") is not False:
        fail("privacy.contains_full_text 必须是 false", failures)
    if privacy.get("contains_source_path") is not False:
        fail("privacy.contains_source_path 必须是 false", failures)


def main() -> int:
    parser = argparse.ArgumentParser(description="校验生成的 humanizer skill 目录。")
    parser.add_argument("skill_dir", type=Path)
    parser.add_argument("--max-excerpt-chars", type=int, default=200)
    parser.add_argument("--max-total-excerpt-chars", type=int, default=2400)
    parser.add_argument("--min-lines", type=int, default=450)
    parser.add_argument("--max-lines", type=int, default=1200)
    args = parser.parse_args()

    failures: list[str] = []
    skill_dir = args.skill_dir
    skill_path = skill_dir / "SKILL.md"

    if not skill_path.exists():
        fail("缺少 SKILL.md", failures)
    else:
        text = skill_path.read_text(encoding="utf-8")
        fields = parse_frontmatter(text, failures)
        expected_name = skill_dir.name
        if fields.get("name") != expected_name:
            fail(f"frontmatter name '{fields.get('name')}' 与目录名 '{expected_name}' 不一致", failures)
        if PLACEHOLDER_RE.search(text):
            fail("SKILL.md 包含未替换占位符", failures)
        validate_skill_body(text, failures, min_lines=args.min_lines, max_lines=args.max_lines)
        blocks = excerpt_blocks(text)
        total = 0
        for index, block in enumerate(blocks, start=1):
            count = chinese_count(block)
            total += count
            if count > args.max_excerpt_chars:
                fail(f"原文摘录 {index} 有 {count} 个中文字符；上限是 {args.max_excerpt_chars}", failures)
        if total > args.max_total_excerpt_chars:
            fail(
                f"原文摘录总量 {total} 个中文字符；上限是 {args.max_total_excerpt_chars}",
                failures,
            )

    validate_meta(skill_dir, failures)

    if failures:
        for item in failures:
            print(f"失败：{item}", file=sys.stderr)
        return 1
    print("通过：生成的 skill 合规")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
