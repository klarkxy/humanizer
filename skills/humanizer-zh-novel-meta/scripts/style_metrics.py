#!/usr/bin/env python3
"""统计抽样中文小说章节的机械风格指标。"""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path


HAN_RE = re.compile(r"[\u4e00-\u9fff]")
SENTENCE_SPLIT_RE = re.compile(r"[。！？!?]+")
QUOTE_RE = re.compile(r"[“”\"『』「」]")
INNER_RE = re.compile(r"心想|暗道|想道|想到|他想|她想|我想|念头|心中")
TRANSITION_RE = re.compile(r"然而|但是|可是|却|虽然|因为|所以|于是|随后|接着|然后|不过")
STOPWORDS = set("一个没有只是他们我们你们这个那个自己什么已经可以不是还是知道说道起来出去下来时候")


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def chinese_count(text: str) -> int:
    return len(HAN_RE.findall(text))


def percentile(values: list[int], ratio: float) -> int:
    if not values:
        return 0
    values = sorted(values)
    index = min(len(values) - 1, round((len(values) - 1) * ratio))
    return values[index]


def density_label(value: float) -> str:
    if value < 0.12:
        return "low"
    if value < 0.28:
        return "medium"
    return "high"


def top_terms(text: str, limit: int = 20) -> list[str]:
    terms: collections.Counter[str] = collections.Counter()
    chars = "".join(HAN_RE.findall(text))
    for size in (2, 3, 4):
        for i in range(0, max(0, len(chars) - size + 1)):
            term = chars[i : i + size]
            if any(char in STOPWORDS for char in term):
                continue
            terms[term] += 1
    return [term for term, _ in terms.most_common(limit)]


def main() -> int:
    parser = argparse.ArgumentParser(description="根据抽样章节统计风格指标。")
    parser.add_argument("--work-dir", required=True, type=Path)
    args = parser.parse_args()

    sample_path = args.work_dir / "sampled_chapters.jsonl"
    chapters = load_jsonl(sample_path)
    text = "\n".join(chapter.get("text", "") for chapter in chapters)
    sentences = [sentence.strip() for sentence in SENTENCE_SPLIT_RE.split(text) if sentence.strip()]
    sentence_lengths = [chinese_count(sentence) for sentence in sentences if chinese_count(sentence)]
    paragraphs = [para.strip() for para in re.split(r"\n\s*\n", text) if para.strip()]
    paragraph_lengths = [chinese_count(para) for para in paragraphs if chinese_count(para)]
    quote_sentences = [sentence for sentence in sentences if QUOTE_RE.search(sentence)]

    metrics = {
        "sampled_chapter_count": len(chapters),
        "chinese_char_count": chinese_count(text),
        "sentence": {
            "count": len(sentence_lengths),
            "median": percentile(sentence_lengths, 0.5),
            "p90": percentile(sentence_lengths, 0.9),
            "short_ratio": round(sum(1 for n in sentence_lengths if n <= 15) / max(len(sentence_lengths), 1), 3),
            "long_ratio": round(sum(1 for n in sentence_lengths if n >= 45) / max(len(sentence_lengths), 1), 3),
        },
        "paragraph": {
            "count": len(paragraph_lengths),
            "median": percentile(paragraph_lengths, 0.5),
            "p90": percentile(paragraph_lengths, 0.9),
        },
        "dialogue": {
            "sentence_ratio": round(len(quote_sentences) / max(len(sentences), 1), 3),
            "density": density_label(len(quote_sentences) / max(len(sentences), 1)),
        },
        "inner_mono": {
            "keyword_hits": len(INNER_RE.findall(text)),
            "per_10k_chars": round(len(INNER_RE.findall(text)) * 10000 / max(chinese_count(text), 1), 2),
        },
        "transition_words": {
            "hits": len(TRANSITION_RE.findall(text)),
            "per_10k_chars": round(len(TRANSITION_RE.findall(text)) * 10000 / max(chinese_count(text), 1), 2),
        },
        "punctuation": {
            "period": text.count("。"),
            "exclamation": text.count("！") + text.count("!"),
            "question": text.count("？") + text.count("?"),
            "ellipsis": text.count("……") + text.count("…"),
        },
        "distinctive_terms_candidates": top_terms(text),
    }

    (args.work_dir / "style_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"通过：已写入 {len(chapters)} 个抽样章节的指标")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
