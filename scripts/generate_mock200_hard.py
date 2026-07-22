#!/usr/bin/env python3
"""Generate a harder 200-question mock exam dataset."""

from __future__ import annotations

import json
import random
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

    questions: List[Dict[str, object]] = []
    qid = 1

    for fact in facts:
        # Type 1: scenario-based concept recognition
        same_chapter = pick_random_facts(facts, rnd, 3, exclude=fact, chapter=fact.chapter)
        options = build_options(fact.term, [f.term for f in same_chapter], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": "",
                "question": (
                    "客户访谈出现以下核心线索：\n"
                    f"{fact.definition}\n"
                    "最符合的术语是下列哪一项？"
                ),
                "options": options,
                "answer": answer_key(options, fact.term),
                "explanation": f"关键线索直接对应「{fact.term}」：{fact.definition}",
            }
        )
        qid += 1

        # Type 2: choose most accurate statement for concept
        same_chapter_defs = pick_random_facts(facts, rnd, 3, exclude=fact, chapter=fact.chapter)
        definition_options = build_options(
            fact.definition,
            [f.definition for f in same_chapter_defs],
            rnd,
        )
        questions.append(
            {
                "id": qid,
                "chapter": "",
                "question": f"关于「{fact.term}」，下列哪项描述最准确？",
                "options": definition_options,
                "answer": answer_key(definition_options, fact.definition),
                "explanation": f"「{fact.term}」的正确定义为：{fact.definition}",
            }
        )
        qid += 1

        # Type 3: find the incorrect statement
        wrong_fact = pick_random_facts(facts, rnd, 1, exclude=fact)[0]
        wrong_statement = f"{fact.term}是指：{wrong_fact.definition}"
        true_statement_1 = f"{fact.term}是指：{fact.definition}"
        true_statement_2 = f"在考试题中，{fact.term}常用于判断风险或保障处理逻辑。"
        true_statement_3 = f"区分{fact.term}时，应抓住定义中的关键字。"
        options = build_options(
            wrong_statement,
            [true_statement_1, true_statement_2, true_statement_3],
            rnd,
        )
        questions.append(
            {
                "id": qid,
                "chapter": "",
                "question": f"以下关于「{fact.term}」的叙述，哪一项错误？",
                "options": options,
                "answer": answer_key(options, wrong_statement),
                "explanation": (
                    f"错误项把「{fact.term}」定义成了其他术语内容。"
                    f"正确定义应为：{fact.definition}"
                ),
            }
        )
        qid += 1

        # Type 4: pure term-definition matching
        distract_facts = pick_random_facts(facts, rnd, 3, exclude=fact)
        correct = f"{fact.term} — {fact.definition}"
        wrong_1 = f"{distract_facts[0].term} — {fact.definition}"
        wrong_2 = f"{fact.term} — {distract_facts[1].definition}"
        wrong_3 = f"{distract_facts[2].term} — {distract_facts[0].definition}"
        options = build_options(correct, [wrong_1, wrong_2, wrong_3], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": "",
                "question": "下列哪一组“术语—解释”配对正确？",
                "options": options,
                "answer": answer_key(options, correct),
                "explanation": f"正确配对是：{fact.term} — {fact.definition}",
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
                "题型改为考试风格，不显示“加强版”标签前缀。",
                "不再出现“属于哪一章”的题型，改为概念辨析与情境判断。",
                "干扰项刻意靠近相近概念，提升辨析难度。",
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
