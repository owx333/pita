#!/usr/bin/env python3
"""Build trilingual quiz data from English and Chinese exam PDFs."""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence

from deep_translator import GoogleTranslator
from pypdf import PdfReader


QUESTION_COUNT = 75


def read_pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def normalize_text(value: str) -> str:
    value = (
        value.replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2013", "-")
        .replace("\u2014", "-")
    )
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def strip_document_noise(text: str) -> str:
    text = re.sub(r"Page\s+\d+\s+of\s+\d+", "\n", text)
    text = re.sub(r"--\s*\d+\s+of\s+\d+\s*--", "\n", text)
    for marker in (
        "Registered Financial Planner (RFP)",
        "PITA Module 2:",
        "Risk Management and Insurance Planning",
        "Practice Questions",
        "第二单元:",
        "风险管理与保险规划",
        "PITA 练习题",
    ):
        text = text.replace(marker, "")
    return text


def parse_questions(text: str) -> Dict[int, Dict[str, object]]:
    # Chinese PDF has no reliable answer section, so cut only when present.
    if "ANSWERS:" in text:
        text = text.split("ANSWERS:")[0]
    if "答案：" in text:
        text = text.split("答案：")[0]

    text = strip_document_noise(text)
    marker_pattern = re.compile(r"(?m)^\s*(\d{1,2})(?:[\.、．])?\s*")
    markers = list(marker_pattern.finditer(text))
    extracted: Dict[int, Dict[str, object]] = {}

    for idx, marker in enumerate(markers):
        number = int(marker.group(1))
        if number < 1 or number > QUESTION_COUNT or number in extracted:
            continue

        start = marker.start()
        end = markers[idx + 1].start() if idx + 1 < len(markers) else len(text)
        block = text[start:end].strip()
        block = re.sub(r"^\s*\d{1,2}(?:[\.、．])?\s*", "", block, count=1)

        # Prefer canonical option markers like "a.".
        option_markers = list(re.finditer(r"(?im)^\s*([a-dA-D])[.)]\s*", block))
        # Some source lines omit the dot, e.g. "a No further benefits...".
        if len(option_markers) < 4:
            fallback_markers = list(
                re.finditer(r"(?im)^\s*([a-dA-D])\s+(?=[A-Z\"'])", block)
            )
            known_starts = {m.start() for m in option_markers}
            for marker in fallback_markers:
                if marker.start() not in known_starts:
                    option_markers.append(marker)
            option_markers.sort(key=lambda m: m.start())
        options: Dict[str, str] = {}
        if len(option_markers) >= 4:
            question_text = block[: option_markers[0].start()].strip()
            option_markers = option_markers[:4]
            for option_index, option_marker in enumerate(option_markers):
                key = option_marker.group(1).lower()
                option_start = option_marker.end()
                option_end = (
                    option_markers[option_index + 1].start()
                    if option_index + 1 < len(option_markers)
                    else len(block)
                )
                options[key] = normalize_text(block[option_start:option_end])
        else:
            question_text = block

        extracted[number] = {
            "id": number,
            "question": normalize_text(question_text),
            "options": options,
        }

    return extracted


def parse_answers(text: str) -> Dict[int, str]:
    if "ANSWERS:" not in text:
        return {}
    answer_block = text.split("ANSWERS:", maxsplit=1)[1]
    pairs = re.findall(r"(\d{1,2})\.\s*([A-D])", answer_block)
    return {int(number): answer.lower() for number, answer in pairs}


def translate_batch(texts: Sequence[str], batch_size: int = 25) -> Dict[str, str]:
    translator = GoogleTranslator(source="en", target="ms")
    mapping: Dict[str, str] = {}

    unique_items = []
    seen = set()
    for text in texts:
        if not text or text in seen:
            continue
        seen.add(text)
        unique_items.append(text)

    total = len(unique_items)
    if total == 0:
        return mapping

    for i in range(0, total, batch_size):
        chunk = unique_items[i : i + batch_size]
        translated: List[str] = []
        for attempt in range(3):
            try:
                translated = translator.translate_batch(chunk)
                break
            except Exception as error:  # pragma: no cover - transient network path
                if attempt == 2:
                    print(
                        f"[warn] translation failed for chunk {i // batch_size + 1}: {error}",
                        file=sys.stderr,
                    )
                else:
                    time.sleep(1.2 * (attempt + 1))

        if not translated or len(translated) != len(chunk):
            translated = chunk

        for source_text, translated_text in zip(chunk, translated):
            mapping[source_text] = normalize_text(translated_text) or source_text

        done = min(i + batch_size, total)
        print(f"[info] translated {done}/{total}")

    return mapping


def build_questions(english: Dict[int, Dict[str, object]], chinese: Dict[int, Dict[str, object]], answers: Dict[int, str], skip_translate: bool) -> List[Dict[str, object]]:
    english_strings: List[str] = []
    for number in range(1, QUESTION_COUNT + 1):
        en_item = english[number]
        english_strings.append(str(en_item["question"]))
        for option_key in ("a", "b", "c", "d"):
            english_strings.append(str(en_item["options"].get(option_key, "")))

    ms_map = {text: text for text in english_strings} if skip_translate else translate_batch(english_strings)

    questions: List[Dict[str, object]] = []
    for number in range(1, QUESTION_COUNT + 1):
        en_item = english.get(number)
        zh_item = chinese.get(number, {})
        if en_item is None:
            raise ValueError(f"Missing English question {number}")

        question_entry = {
            "id": number,
            "question": {
                "en": en_item["question"],
                "zh": zh_item.get("question", en_item["question"]),
                "ms": ms_map.get(str(en_item["question"]), str(en_item["question"])),
            },
            "options": {},
            "answer": answers.get(number, ""),
        }

        en_options: Dict[str, str] = en_item["options"]  # type: ignore[assignment]
        zh_options: Dict[str, str] = zh_item.get("options", {})  # type: ignore[assignment]
        for option_key in ("a", "b", "c", "d"):
            en_option = en_options.get(option_key, "")
            question_entry["options"][option_key] = {
                "en": en_option,
                "zh": zh_options.get(option_key, en_option),
                "ms": ms_map.get(en_option, en_option),
            }

        questions.append(question_entry)

    return questions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build trilingual quiz JSON from uploaded PDFs."
    )
    parser.add_argument("--english-pdf", type=Path, required=True)
    parser.add_argument("--chinese-pdf", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--skip-translate",
        action="store_true",
        help="Use English as fallback instead of translating to Malay.",
    )
    args = parser.parse_args()

    english_text = read_pdf_text(args.english_pdf)
    chinese_text = read_pdf_text(args.chinese_pdf)

    english_questions = parse_questions(english_text)
    chinese_questions = parse_questions(chinese_text)
    answers = parse_answers(english_text)

    missing_english = [n for n in range(1, QUESTION_COUNT + 1) if n not in english_questions]
    if missing_english:
        raise ValueError(f"Failed to parse English questions: {missing_english}")

    missing_answers = [n for n in range(1, QUESTION_COUNT + 1) if n not in answers]
    if missing_answers:
        raise ValueError(f"Failed to parse answer keys: {missing_answers}")

    questions = build_questions(
        english=english_questions,
        chinese=chinese_questions,
        answers=answers,
        skip_translate=args.skip_translate,
    )

    payload = {
        "meta": {
            "title": {
                "en": "RFP Module 2 Practice Quiz",
                "zh": "RFP 第二单元练习测验",
                "ms": "Kuiz Latihan RFP Modul 2",
            },
            "description": {
                "en": "Trilingual revision quiz generated from the provided exam papers.",
                "zh": "由提供的考卷生成的三语温习测验。",
                "ms": "Kuiz ulang kaji tiga bahasa yang dijana daripada kertas peperiksaan yang diberi.",
            },
            "questionCount": QUESTION_COUNT,
            "source": {
                "englishPdf": str(args.english_pdf),
                "chinesePdf": str(args.chinese_pdf),
            },
        },
        "questions": questions,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[done] wrote {args.output} with {QUESTION_COUNT} questions")


if __name__ == "__main__":
    main()
