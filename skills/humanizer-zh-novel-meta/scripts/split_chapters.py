#!/usr/bin/env python3
"""把长篇中文小说拆成 humanizer 生成用的章节产物。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CHAPTER_RE = re.compile(
    r"(?m)^\s*(第[一二三四五六七八九十百千万零〇○两\d]+章[^\n]{0,80}|Chapter\s+\d+[^\n]{0,80}|\d+[\.\、\s]+[^\n]{1,80})\s*$",
    re.IGNORECASE,
)
META_TITLE_RE = re.compile(
    r"请假|通知|上架|感言|总结|加更|卷末|间章|作者的话|作者有话|写在最后|完本|新书|致谢|道歉|公告|闲聊|番外|楔子"
)
HAN_RE = re.compile(r"[\u4e00-\u9fff]")


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"无法解码原文文件：{path}")


def chinese_count(text: str) -> int:
    return len(HAN_RE.findall(text))


def stage_for(index: int, total: int) -> str:
    ratio = index / max(total, 1)
    if ratio <= 0.15:
        return "opening"
    if ratio <= 0.75:
        return "development"
    if ratio <= 0.92:
        return "climax_or_late"
    return "ending"


def split_chapters(text: str) -> list[dict]:
    matches = list(CHAPTER_RE.finditer(text))
    if not matches:
        return []

    chapters: list[dict] = []
    for i, match in enumerate(matches):
        title = re.sub(r"\s+", " ", match.group(1)).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        char_count = chinese_count(body)
        is_meta = bool(META_TITLE_RE.search(title))
        chapters.append(
            {
                "chapter_index": i + 1,
                "chapter_title": title,
                "char_count": char_count,
                "is_meta": is_meta,
                "text": body,
            }
        )
    return chapters


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="把中文小说拆成章节产物。")
    parser.add_argument("source", type=Path, help="小说文本文件路径")
    parser.add_argument("--out-dir", required=True, type=Path, help="输出工作目录")
    parser.add_argument("--min-chapters", type=int, default=20)
    parser.add_argument("--min-chars", type=int, default=100000)
    args = parser.parse_args()

    if not args.source.exists():
        print(f"失败：原文不存在：{args.source}", file=sys.stderr)
        return 2

    text = read_text(args.source)
    total_chinese = chinese_count(text)
    if not text.strip() or total_chinese < args.min_chars:
        print(
            f"失败：原文只有 {total_chinese} 个中文字符；要求不少于 {args.min_chars}",
            file=sys.stderr,
        )
        return 3

    chapters = split_chapters(text)
    body_chapters = [chapter for chapter in chapters if not chapter["is_meta"] and chapter["char_count"] >= 500]

    if len(body_chapters) < args.min_chapters:
        print(
            f"失败：只找到 {len(body_chapters)} 个有效正文章节；要求不少于 {args.min_chapters}",
            file=sys.stderr,
        )
        return 4

    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    total_body = len(body_chapters)
    chapter_map = {
        "source_name": args.source.name,
        "total_chinese_chars": total_chinese,
        "raw_chapter_count": len(chapters),
        "body_chapter_count": total_body,
        "chapters": [],
    }

    chapters_jsonl = out_dir / "chapters.jsonl"
    with chapters_jsonl.open("w", encoding="utf-8") as handle:
        for public_index, chapter in enumerate(body_chapters, start=1):
            mapped = {
                "chapter_index": public_index,
                "source_chapter_index": chapter["chapter_index"],
                "chapter_title": chapter["chapter_title"],
                "char_count": chapter["char_count"],
                "stage": stage_for(public_index, total_body),
                "suitable_for_sample": chapter["char_count"] >= 1000,
            }
            chapter_map["chapters"].append(mapped)
            handle.write(
                json.dumps({**mapped, "text": chapter["text"]}, ensure_ascii=False) + "\n"
            )

    write_json(out_dir / "chapter_map.json", chapter_map)
    print(
        f"通过：已写入 {total_body} 个章节，原文共 {total_chinese} 个中文字符，输出目录 {out_dir}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
