#!/usr/bin/env python3
"""Build a trilingual 400-question dataset from RFP core facts."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Sequence

from deep_translator import GoogleTranslator

from generate_mock200 import FACTS, Fact


def normalize_text(value: str) -> str:
    return " ".join(str(value).split()).strip()


def translate_items(items: Sequence[str], target_lang: str, batch_size: int = 20) -> Dict[str, str]:
    translator = GoogleTranslator(source="zh-CN", target=target_lang)
    unique = []
    seen = set()
    for text in items:
        t = normalize_text(text)
        if not t or t in seen:
            continue
        seen.add(t)
        unique.append(t)

    mapping: Dict[str, str] = {}
    for i in range(0, len(unique), batch_size):
        chunk = unique[i : i + batch_size]
        translated: List[str] = []
        for attempt in range(3):
            try:
                translated = translator.translate_batch(chunk)
                break
            except Exception as error:  # pragma: no cover
                if attempt == 2:
                    print(f"[warn] {target_lang} batch {i // batch_size + 1} failed: {error}", file=sys.stderr)
                else:
                    time.sleep(1.0 * (attempt + 1))
        if not translated or len(translated) != len(chunk):
            translated = chunk
        for source, target in zip(chunk, translated):
            mapping[source] = normalize_text(target) or source
        print(f"[info] {target_lang}: translated {min(i + batch_size, len(unique))}/{len(unique)}")
    return mapping


def make_map(zh: str, en_map: Dict[str, str], ms_map: Dict[str, str]) -> Dict[str, str]:
    key = normalize_text(zh)
    return {"en": en_map.get(key, key), "zh": key, "ms": ms_map.get(key, key)}


def make_text(en: str, zh: str, ms: str) -> Dict[str, str]:
    return {"en": en, "zh": zh, "ms": ms}


def term_text(term: str, en_map: Dict[str, str], ms_map: Dict[str, str]) -> Dict[str, str]:
    return make_map(term, en_map, ms_map)


def definition_text(definition: str, en_map: Dict[str, str], ms_map: Dict[str, str]) -> Dict[str, str]:
    return make_map(definition, en_map, ms_map)


def pair_text(term: str, definition: str, en_map: Dict[str, str], ms_map: Dict[str, str]) -> Dict[str, str]:
    t = term_text(term, en_map, ms_map)
    d = definition_text(definition, en_map, ms_map)
    return make_text(
        en=f"{t['en']} — {d['en']}",
        zh=f"{term} — {definition}",
        ms=f"{t['ms']} — {d['ms']}",
    )


def statement_define_text(term: str, definition: str, en_map: Dict[str, str], ms_map: Dict[str, str]) -> Dict[str, str]:
    t = term_text(term, en_map, ms_map)
    d = definition_text(definition, en_map, ms_map)
    return make_text(
        en=f"The definition of {t['en']} is: {d['en']}",
        zh=f"{term}是指：{definition}",
        ms=f"Definisi {t['ms']} ialah: {d['ms']}",
    )


def build_options(correct: str, distractors: Sequence[str], rnd) -> Dict[str, str]:
    labels = ["a", "b", "c", "d"]
    pool = [correct] + list(distractors)
    rnd.shuffle(pool)
    return {label: text for label, text in zip(labels, pool)}


def answer_key(options: Dict[str, str], target: str) -> str:
    for key, value in options.items():
        if value == target:
            return key
    raise ValueError("target not in options")


def pick_other_facts(facts: Sequence[Fact], current_index: int, count: int, rnd) -> List[Fact]:
    candidates = [fact for idx, fact in enumerate(facts) if idx != current_index]
    return rnd.sample(candidates, count)


def main() -> None:
    out_json = Path("/workspace/data/mock400-trilingual.json")
    out_js = Path("/workspace/data/mock400-trilingual-data.js")
    rnd = __import__("random").Random(20260717)

    raw_terms = [f.term for f in FACTS]
    raw_defs = [f.definition for f in FACTS]
    en_map = translate_items(raw_terms + raw_defs, target_lang="en")
    ms_map = translate_items(raw_terms + raw_defs, target_lang="ms")

    output_questions: List[Dict[str, object]] = []
    qid = 1

    for idx, fact in enumerate(FACTS):
        fact_term = term_text(fact.term, en_map, ms_map)
        fact_def = definition_text(fact.definition, en_map, ms_map)

        # A1
        others = pick_other_facts(FACTS, idx, 3, rnd)
        options = build_options(fact.term, [x.term for x in others], rnd)
        output_questions.append(
            {
                "id": qid,
                "sourceSet": "base200",
                "chapter": "",
                "question": make_text(
                    en=f"Which term best matches the following definition?\n{fact_def['en']}",
                    zh=f"以下定义对应哪个术语？\n{fact.definition}",
                    ms=f"Istilah manakah paling sepadan dengan definisi berikut?\n{fact_def['ms']}",
                ),
                "options": {k: term_text(v, en_map, ms_map) for k, v in options.items()},
                "answer": answer_key(options, fact.term),
            }
        )
        qid += 1

        # A2
        others = pick_other_facts(FACTS, idx, 3, rnd)
        option_defs = build_options(fact.definition, [x.definition for x in others], rnd)
        output_questions.append(
            {
                "id": qid,
                "sourceSet": "base200",
                "chapter": "",
                "question": make_text(
                    en=f"Which statement is most accurate about \"{fact_term['en']}\"?",
                    zh=f"关于「{fact.term}」，下列哪项描述最准确？",
                    ms=f"Pernyataan manakah paling tepat tentang \"{fact_term['ms']}\"?",
                ),
                "options": {
                    k: definition_text(v, en_map, ms_map) for k, v in option_defs.items()
                },
                "answer": answer_key(option_defs, fact.definition),
            }
        )
        qid += 1

        # A3
        others = pick_other_facts(FACTS, idx, 6, rnd)
        correct_pair = f"{fact.term} — {fact.definition}"
        wrong_1 = f"{others[0].term} — {others[1].definition}"
        wrong_2 = f"{others[2].term} — {others[3].definition}"
        wrong_3 = f"{others[4].term} — {others[5].definition}"
        pair_options = build_options(correct_pair, [wrong_1, wrong_2, wrong_3], rnd)
        output_questions.append(
            {
                "id": qid,
                "sourceSet": "base200",
                "chapter": "",
                "question": make_text(
                    en="Which term-definition pair is correct?",
                    zh="以下哪一组“术语—解释”配对正确？",
                    ms="Pasangan istilah-definisi manakah yang betul?",
                ),
                "options": {
                    k: pair_text(
                        v.split(" — ", maxsplit=1)[0],
                        v.split(" — ", maxsplit=1)[1],
                        en_map,
                        ms_map,
                    )
                    for k, v in pair_options.items()
                },
                "answer": answer_key(pair_options, correct_pair),
            }
        )
        qid += 1

        # A4
        others = pick_other_facts(FACTS, idx, 4, rnd)
        wrong_pair = f"{fact.term} — {others[0].definition}"
        pair_true_1 = f"{others[1].term} — {others[1].definition}"
        pair_true_2 = f"{others[2].term} — {others[2].definition}"
        pair_true_3 = f"{others[3].term} — {others[3].definition}"
        incorrect_pair_options = build_options(wrong_pair, [pair_true_1, pair_true_2, pair_true_3], rnd)
        output_questions.append(
            {
                "id": qid,
                "sourceSet": "base200",
                "chapter": "",
                "question": make_text(
                    en="Which term-definition pair is incorrect?",
                    zh="以下哪一组“术语—解释”配对错误？",
                    ms="Pasangan istilah-definisi manakah yang salah?",
                ),
                "options": {
                    k: pair_text(
                        v.split(" — ", maxsplit=1)[0],
                        v.split(" — ", maxsplit=1)[1],
                        en_map,
                        ms_map,
                    )
                    for k, v in incorrect_pair_options.items()
                },
                "answer": answer_key(incorrect_pair_options, wrong_pair),
            }
        )
        qid += 1

        # B1
        others = pick_other_facts(FACTS, idx, 3, rnd)
        scenario_options = build_options(fact.term, [x.term for x in others], rnd)
        output_questions.append(
            {
                "id": qid,
                "sourceSet": "hard200",
                "chapter": "",
                "question": make_text(
                    en=(
                        "A client interview reveals the following core clue:\n"
                        f"{fact_def['en']}\n"
                        "Which term best fits this clue?"
                    ),
                    zh=f"客户访谈出现以下核心线索：\n{fact.definition}\n最符合的术语是下列哪一项？",
                    ms=(
                        "Temu bual pelanggan mendedahkan petunjuk teras berikut:\n"
                        f"{fact_def['ms']}\n"
                        "Istilah manakah paling sesuai dengan petunjuk ini?"
                    ),
                ),
                "options": {k: term_text(v, en_map, ms_map) for k, v in scenario_options.items()},
                "answer": answer_key(scenario_options, fact.term),
            }
        )
        qid += 1

        # B2
        others = pick_other_facts(FACTS, idx, 3, rnd)
        hard_defs = build_options(fact.definition, [x.definition for x in others], rnd)
        output_questions.append(
            {
                "id": qid,
                "sourceSet": "hard200",
                "chapter": "",
                "question": make_text(
                    en=f"Which statement is most accurate about \"{fact_term['en']}\"?",
                    zh=f"关于「{fact.term}」，下列哪项描述最准确？",
                    ms=f"Pernyataan manakah paling tepat tentang \"{fact_term['ms']}\"?",
                ),
                "options": {k: definition_text(v, en_map, ms_map) for k, v in hard_defs.items()},
                "answer": answer_key(hard_defs, fact.definition),
            }
        )
        qid += 1

        # B3
        other = pick_other_facts(FACTS, idx, 1, rnd)[0]
        wrong_stmt = f"{fact.term}是指：{other.definition}"
        true_stmt_1 = f"{fact.term}是指：{fact.definition}"
        true_stmt_2 = f"在考试题中，{fact.term}常用于判断风险或保障处理逻辑。"
        true_stmt_3 = f"区分{fact.term}时，应抓住定义中的关键字。"
        stmt_options = build_options(wrong_stmt, [true_stmt_1, true_stmt_2, true_stmt_3], rnd)
        option_texts: Dict[str, Dict[str, str]] = {}
        for key, value in stmt_options.items():
            if value.endswith("常用于判断风险或保障处理逻辑。"):
                option_texts[key] = make_text(
                    en=f"In exam questions, {fact_term['en']} is commonly used to assess risk and protection logic.",
                    zh=value,
                    ms=f"Dalam soalan peperiksaan, {fact_term['ms']} biasanya digunakan untuk menilai logik risiko dan perlindungan.",
                )
            elif value.endswith("应抓住定义中的关键字。"):
                option_texts[key] = make_text(
                    en=f"To distinguish {fact_term['en']}, focus on keywords in its definition.",
                    zh=value,
                    ms=f"Untuk membezakan {fact_term['ms']}, fokus pada kata kunci dalam definisinya.",
                )
            else:
                term_part, def_part = value.split("是指：", maxsplit=1)
                option_texts[key] = statement_define_text(term_part, def_part, en_map, ms_map)

        output_questions.append(
            {
                "id": qid,
                "sourceSet": "hard200",
                "chapter": "",
                "question": make_text(
                    en=f"Which of the following statements about \"{fact_term['en']}\" is incorrect?",
                    zh=f"以下关于「{fact.term}」的叙述，哪一项错误？",
                    ms=f"Pernyataan manakah tentang \"{fact_term['ms']}\" yang tidak betul?",
                ),
                "options": option_texts,
                "answer": answer_key(stmt_options, wrong_stmt),
            }
        )
        qid += 1

        # B4
        others = pick_other_facts(FACTS, idx, 3, rnd)
        hard_correct = f"{fact.term} — {fact.definition}"
        hard_wrong_1 = f"{others[0].term} — {fact.definition}"
        hard_wrong_2 = f"{fact.term} — {others[1].definition}"
        hard_wrong_3 = f"{others[2].term} — {others[0].definition}"
        hard_pair_options = build_options(hard_correct, [hard_wrong_1, hard_wrong_2, hard_wrong_3], rnd)
        output_questions.append(
            {
                "id": qid,
                "sourceSet": "hard200",
                "chapter": "",
                "question": make_text(
                    en="Which term-definition pair is correct?",
                    zh="下列哪一组“术语—解释”配对正确？",
                    ms="Pasangan istilah-definisi manakah yang betul?",
                ),
                "options": {
                    k: pair_text(
                        v.split(" — ", maxsplit=1)[0],
                        v.split(" — ", maxsplit=1)[1],
                        en_map,
                        ms_map,
                    )
                    for k, v in hard_pair_options.items()
                },
                "answer": answer_key(hard_pair_options, hard_correct),
            }
        )
        qid += 1

    if len(output_questions) != 400:
        raise ValueError(f"Expected 400 questions, got {len(output_questions)}")

    payload = {
        "meta": {
            "title": {
                "en": "RFP Module 2 Mock Exam (400 Questions, Trilingual)",
                "zh": "RFP 第二单元模拟考试（400题，三语）",
                "ms": "Peperiksaan Olok-olok RFP Modul 2 (400 soalan, tiga bahasa)",
            },
            "description": {
                "en": "Combined core + advanced mock sets with English, Chinese and Malay text.",
                "zh": "整合基础与加强两套题库，提供英文、中文、马来文三语版本。",
                "ms": "Gabungan set simulasi asas dan lanjutan dengan teks Bahasa Inggeris, Cina dan Melayu.",
            },
            "questionCount": 400,
            "source": {
                "baseFacts": "scripts/generate_mock200.py::FACTS",
                "generator": "scripts/generate_mock400_trilingual.py",
            },
        },
        "questions": output_questions,
    }

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    out_js.write_text(
        "window.__MOCK400_DATA__ = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    print(f"[done] wrote {out_json}")
    print(f"[done] wrote {out_js}")


if __name__ == "__main__":
    main()
