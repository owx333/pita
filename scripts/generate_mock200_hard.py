#!/usr/bin/env python3
"""Generate a harder 200-question mock exam dataset."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence

from generate_mock200 import FACTS, Fact


def build_options(correct: str, distractors: Sequence[str], rnd: random.Random) -> Dict[str, str]:
    labels = ["a", "b", "c", "d"]
    pool = [correct] + list(distractors)
    rnd.shuffle(pool)
    return {label: text for label, text in zip(labels, pool)}


def answer_key(options: Dict[str, str], target: str) -> str:
    for key, value in options.items():
        if value == target:
            return key
    raise ValueError("target not found in options")


def pick_random_facts(
    facts: Sequence[Fact],
    rnd: random.Random,
    count: int,
    exclude: Fact | None = None,
    chapter: str | None = None,
) -> List[Fact]:
    pool = [f for f in facts if f != exclude and (chapter is None or f.chapter == chapter)]
    if len(pool) < count:
        pool = [f for f in facts if f != exclude]
    return rnd.sample(pool, count)


def generate_hard_questions(facts: Sequence[Fact]) -> List[Dict[str, object]]:
    rnd = random.Random(20260716)
    chapter_map: Dict[str, List[Fact]] = defaultdict(list)
    for fact in facts:
        chapter_map[fact.chapter].append(fact)
    chapter_names = list(chapter_map.keys())

    questions: List[Dict[str, object]] = []
    qid = 1

    for fact in facts:
        # Type 1: scenario-based concept recognition
        same_chapter = pick_random_facts(facts, rnd, 3, exclude=fact, chapter=fact.chapter)
        options = build_options(fact.term, [f.term for f in same_chapter], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": (
                    "【加强版·场景判断】客户访谈出现以下核心线索：\n"
                    f"{fact.definition}\n"
                    "若以RFP Module 2框架做归类，最应判定为哪个术语？"
                ),
                "options": options,
                "answer": answer_key(options, fact.term),
                "explanation": f"关键线索直接对应「{fact.term}」：{fact.definition}",
            }
        )
        qid += 1

        # Type 2: chapter mapping
        other_chapters = [ch for ch in chapter_names if ch != fact.chapter]
        chapter_distractors = rnd.sample(other_chapters, 3)
        chapter_options = build_options(fact.chapter, chapter_distractors, rnd)
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": (
                    f"【加强版·章节定位】若考题重点是「{fact.term}」，"
                    "该题最直接归入以下哪一章？"
                ),
                "options": chapter_options,
                "answer": answer_key(chapter_options, fact.chapter),
                "explanation": f"「{fact.term}」属于{fact.chapter}的核心考点。",
            }
        )
        qid += 1

        # Type 3: find the incorrect statement
        wrong_fact = pick_random_facts(facts, rnd, 1, exclude=fact)[0]
        wrong_statement = f"{fact.term}是指：{wrong_fact.definition}"
        true_statement_1 = f"{fact.term}是指：{fact.definition}"
        true_statement_2 = f"{fact.term}属于「{fact.chapter}」的关键概念。"
        true_statement_3 = f"复习{fact.term}时，应和同章概念一起对照记忆。"
        options = build_options(
            wrong_statement,
            [true_statement_1, true_statement_2, true_statement_3],
            rnd,
        )
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": f"【加强版·辨错】以下关于「{fact.term}」的叙述，哪一项错误？",
                "options": options,
                "answer": answer_key(options, wrong_statement),
                "explanation": (
                    f"错误项把「{fact.term}」定义成了其他术语内容。"
                    f"正确定义应为：{fact.definition}"
                ),
            }
        )
        qid += 1

        # Type 4: full triple matching
        distract_facts = pick_random_facts(facts, rnd, 3, exclude=fact)
        correct = f"{fact.chapter} | {fact.term} | {fact.definition}"
        wrong_1 = (
            f"{fact.chapter} | {distract_facts[0].term} | {fact.definition}"
        )
        wrong_2 = (
            f"{distract_facts[1].chapter} | {fact.term} | {fact.definition}"
        )
        wrong_3 = (
            f"{fact.chapter} | {fact.term} | {distract_facts[2].definition}"
        )
        options = build_options(correct, [wrong_1, wrong_2, wrong_3], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": "【加强版·综合配对】下列哪一组“章节 | 术语 | 解释”完全正确？",
                "options": options,
                "answer": answer_key(options, correct),
                "explanation": (
                    f"只有「{fact.chapter} | {fact.term} | {fact.definition}」"
                    "三项同时匹配。"
                ),
            }
        )
        qid += 1

    return questions


def main() -> None:
    out_json = Path("/workspace/data/mock200-hard.json")
    out_js = Path("/workspace/data/mock200-hard-data.js")

    questions = generate_hard_questions(FACTS)
    if len(questions) != 200:
        raise ValueError(f"Expected 200 questions, got {len(questions)}")

    payload = {
        "meta": {
            "title": "RFP Module 2 模拟考试（200题加强版）",
            "language": "zh",
            "difficulty": "hard",
            "questionCount": 200,
            "notes": [
                "题型更偏向场景判断、章节定位和综合配对。",
                "干扰项刻意靠近同章概念，提升辨析难度。",
            ],
            "source": {
                "slidePdf": "/workspace/materials/Registred Financial Planning (RFP) Module 2 Tutorial  (Man) _V1.0 as of Nov 2024.pdf",
                "ebookPdf": "/workspace/materials/E-Book_PCM2_Mandarin.pdf",
            },
        },
        "questions": questions,
    }

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    out_js.write_text(
        "window.__MOCK200_HARD_DATA__ = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    print(f"[done] wrote {out_json}")
    print(f"[done] wrote {out_js}")


if __name__ == "__main__":
    main()
