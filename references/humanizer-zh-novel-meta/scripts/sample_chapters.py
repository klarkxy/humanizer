#!/usr/bin/env python3
"""从拆章产物生成确定性的分层抽样方案。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def pick_evenly(items: list[dict], count: int) -> list[dict]:
    if count <= 0 or not items:
        return []
    if count >= len(items):
        return items
    if count == 1:
        return [items[len(items) // 2]]
    step = (len(items) - 1) / (count - 1)
    chosen = []
    seen = set()
    for i in range(count):
        index = round(i * step)
        while index in seen and index + 1 < len(items):
            index += 1
        seen.add(index)
        chosen.append(items[index])
    return chosen


def main() -> int:
    parser = argparse.ArgumentParser(description="生成章节抽样方案。")
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--sample-count", type=int, default=12)
    parser.add_argument("--excerpt-chars", type=int, default=4000)
    args = parser.parse_args()

    chapters = load_jsonl(args.work_dir / "chapters.jsonl")
    eligible = [chapter for chapter in chapters if chapter.get("suitable_for_sample")]
    if not eligible:
        raise SystemExit("失败：没有可抽样章节")

    sample_count = max(8, min(args.sample_count, 16, len(eligible)))
    early = eligible[: len(eligible) // 3]
    middle = eligible[len(eligible) // 3 : (len(eligible) * 2) // 3]
    late = eligible[(len(eligible) * 2) // 3 :]

    early_count = max(1, round(sample_count * 0.3))
    middle_count = max(1, round(sample_count * 0.5))
    late_count = max(1, sample_count - early_count - middle_count)

    selected = pick_evenly(early, early_count) + pick_evenly(middle, middle_count) + pick_evenly(late, late_count)
    selected_by_index = {item["chapter_index"]: item for item in selected}

    while len(selected_by_index) < sample_count:
        for item in eligible:
            selected_by_index.setdefault(item["chapter_index"], item)
            if len(selected_by_index) >= sample_count:
                break

    final = [selected_by_index[key] for key in sorted(selected_by_index)]
    plan = {
        "sample_count": len(final),
        "strategy": "stratified_30_50_20_even_spacing",
        "excerpt_chars_per_chapter": args.excerpt_chars,
        "chapters": [
            {
                "chapter_index": item["chapter_index"],
                "chapter_title": item["chapter_title"],
                "stage": item["stage"],
                "char_count": item["char_count"],
            }
            for item in final
        ],
    }

    (args.work_dir / "sample_plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    with (args.work_dir / "sampled_chapters.jsonl").open("w", encoding="utf-8") as handle:
        for item in final:
            row = dict(item)
            row["text"] = row.get("text", "")[: args.excerpt_chars]
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"通过：已抽样 {len(final)} 个章节")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
