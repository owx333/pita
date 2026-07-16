#!/usr/bin/env python3
"""Build a varied trilingual 400-question dataset from RFP core facts."""

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

    zh_templates = {
        "a1": [
            "某客户在风险沟通中提到：\n{definition}\n这最符合哪个术语？",
            "根据以下描述，最贴切的术语是：\n{definition}",
            "阅读线索后判断术语：\n{definition}\n应选哪一项？",
            "若出现下列情形：\n{definition}\n通常归类为哪一术语？",
        ],
        "a2": [
            "关于「{term}」，下列哪项描述最准确？",
            "若要向客户解释「{term}」，哪项定义是正确的？",
            "以下对「{term}」的理解，何者最恰当？",
            "在RFP语境中，「{term}」应如何定义？",
        ],
        "a3": [
            "围绕「{term}」这个概念，下列哪一组“术语—解释”配对正确？",
            "关于「{term}」及相近概念，哪组配对是正确的？",
            "以下术语配对中，何者与「{term}」逻辑一致？",
            "在概念配对题中，与「{term}」相关的正确选项是？",
        ],
        "a4": [
            "若以「{term}」为参照，下列哪一组“术语—解释”配对错误？",
            "以下各项里，哪一项与「{term}」的概念关系不正确？",
            "围绕「{term}」的辨错题中，哪组配对是错的？",
            "关于「{term}」与其他术语的对应关系，哪项有误？",
        ],
        "b1": [
            "情境：客户提供了这条关键线索：\n{definition}\n你最可能采用哪个术语进行归纳？",
            "顾问访谈记录显示：\n{definition}\n该信息对应的核心术语是？",
            "在案例分析中出现：\n{definition}\n最应判定为何种术语？",
            "若客户陈述符合以下内容：\n{definition}\n最佳术语判断是？",
        ],
        "b2": [
            "你要向新进顾问说明「{term}」，下列哪项讲法最准确？",
            "培训场景下，关于「{term}」的正确解释是？",
            "在实务答辩中，哪项对「{term}」的定义最稳妥？",
            "针对「{term}」的高难度辨析，正确选项是？",
        ],
        "b3": [
            "以下关于「{term}」的叙述，哪一项错误？",
            "在「{term}」的判断题里，哪项说法不成立？",
            "检视下列陈述，关于「{term}」哪项是错的？",
            "围绕「{term}」的四项描述中，错误的是哪一个？",
        ],
        "b4": [
            "当你以「{term}」作为分析核心时，下列哪组“术语—解释”最可采纳？",
            "在拟定建议书时，围绕「{term}」应采用哪一组正确配对？",
            "关于「{term}」的综合判断，下列配对哪项正确？",
            "若题干以「{term}」为重点，哪组术语配对最合理？",
        ],
    }

    en_templates = {
        "a1": [
            "A client mentions the following during risk discussion:\n{definition}\nWhich term best fits this?",
            "Based on the following description, which term is the best match?\n{definition}",
            "Read the clue and identify the term:\n{definition}\nWhich option is correct?",
            "If the following situation appears:\n{definition}\nWhich term is usually used?",
        ],
        "a2": [
            "Which statement is most accurate about \"{term}\"?",
            "If you explain \"{term}\" to a client, which definition is correct?",
            "Which understanding of \"{term}\" is the most appropriate?",
            "In the RFP context, how should \"{term}\" be defined?",
        ],
        "a3": [
            "Around the concept \"{term}\", which term-definition pair is correct?",
            "For \"{term}\" and similar concepts, which pair is correct?",
            "Which pairing is consistent with the logic of \"{term}\"?",
            "In a concept-matching question, which option aligns with \"{term}\"?",
        ],
        "a4": [
            "Using \"{term}\" as reference, which term-definition pair is incorrect?",
            "Which item is NOT correctly related to the concept of \"{term}\"?",
            "In this error-identification set for \"{term}\", which pair is wrong?",
            "Regarding \"{term}\" and other terms, which mapping is incorrect?",
        ],
        "b1": [
            "Scenario: The client provides this key clue:\n{definition}\nWhich term would you use to classify it?",
            "Consultation notes show:\n{definition}\nWhat is the core term for this information?",
            "In case analysis, you see:\n{definition}\nWhich term should be assigned?",
            "If a client's statement matches this:\n{definition}\nWhat is the best term judgment?",
        ],
        "b2": [
            "You are coaching a new advisor on \"{term}\". Which explanation is most accurate?",
            "In a training setting, what is the correct explanation of \"{term}\"?",
            "In practice defense, which definition of \"{term}\" is most reliable?",
            "For advanced discrimination of \"{term}\", which option is correct?",
        ],
        "b3": [
            "Which of the following statements about \"{term}\" is incorrect?",
            "In this \"{term}\" judgment item, which statement does not hold?",
            "Review the statements below: which one about \"{term}\" is wrong?",
            "Among these four descriptions of \"{term}\", which is incorrect?",
        ],
        "b4": [
            "When \"{term}\" is your analysis focus, which term-definition pair is most acceptable?",
            "While drafting recommendations around \"{term}\", which correct pair should you adopt?",
            "For a comprehensive judgment on \"{term}\", which pairing is correct?",
            "If the stem highlights \"{term}\", which term pair is the most logical?",
        ],
    }

    ms_templates = {
        "a1": [
            "Seorang pelanggan menyatakan perkara berikut semasa perbincangan risiko:\n{definition}\nIstilah manakah paling sesuai?",
            "Berdasarkan penerangan berikut, istilah manakah paling tepat?\n{definition}",
            "Baca petunjuk ini dan kenal pasti istilah:\n{definition}\nPilihan manakah betul?",
            "Jika situasi berikut berlaku:\n{definition}\nIstilah manakah biasanya digunakan?",
        ],
        "a2": [
            "Pernyataan manakah paling tepat tentang \"{term}\"?",
            "Jika anda menerangkan \"{term}\" kepada pelanggan, definisi manakah betul?",
            "Pemahaman manakah tentang \"{term}\" paling sesuai?",
            "Dalam konteks RFP, bagaimana \"{term}\" sepatutnya ditakrifkan?",
        ],
        "a3": [
            "Berkaitan konsep \"{term}\", pasangan istilah-definisi manakah yang betul?",
            "Bagi \"{term}\" dan konsep hampir sama, pasangan manakah yang betul?",
            "Pasangan manakah yang konsisten dengan logik \"{term}\"?",
            "Dalam soalan padanan konsep, pilihan manakah selaras dengan \"{term}\"?",
        ],
        "a4": [
            "Dengan \"{term}\" sebagai rujukan, pasangan istilah-definisi manakah yang salah?",
            "Item manakah yang TIDAK berkaitan dengan betul kepada konsep \"{term}\"?",
            "Dalam set kenal pasti ralat untuk \"{term}\", pasangan manakah salah?",
            "Berkaitan \"{term}\" dan istilah lain, padanan manakah tidak tepat?",
        ],
        "b1": [
            "Situasi: Pelanggan memberikan petunjuk utama ini:\n{definition}\nIstilah manakah yang paling sesuai untuk pengelasan?",
            "Nota konsultasi menunjukkan:\n{definition}\nApakah istilah teras untuk maklumat ini?",
            "Dalam analisis kes, anda melihat:\n{definition}\nIstilah manakah patut ditetapkan?",
            "Jika kenyataan pelanggan sepadan dengan ini:\n{definition}\nApakah pertimbangan istilah terbaik?",
        ],
        "b2": [
            "Anda melatih penasihat baharu tentang \"{term}\". Penerangan manakah paling tepat?",
            "Dalam suasana latihan, apakah penerangan yang betul untuk \"{term}\"?",
            "Dalam pembelaan amali, definisi manakah bagi \"{term}\" paling kukuh?",
            "Untuk pembezaan lanjutan \"{term}\", pilihan manakah betul?",
        ],
        "b3": [
            "Pernyataan manakah tentang \"{term}\" yang tidak betul?",
            "Dalam item penilaian \"{term}\" ini, pernyataan manakah tidak sah?",
            "Semak pernyataan berikut: yang manakah salah tentang \"{term}\"?",
            "Antara empat huraian tentang \"{term}\" ini, yang manakah salah?",
        ],
        "b4": [
            "Apabila \"{term}\" menjadi fokus analisis anda, pasangan istilah-definisi manakah paling sesuai?",
            "Semasa menyediakan cadangan berkaitan \"{term}\", pasangan betul manakah patut dipilih?",
            "Untuk penilaian menyeluruh tentang \"{term}\", pasangan manakah betul?",
            "Jika soalan menekankan \"{term}\", pasangan istilah manakah paling logik?",
        ],
    }

    def templ(kind: str, term_map: Dict[str, str], def_map: Dict[str, str], idx: int) -> Dict[str, str]:
        i = idx % 4
        return make_text(
            en=en_templates[kind][i].format(term=term_map["en"], definition=def_map["en"]),
            zh=zh_templates[kind][i].format(term=term_map["zh"], definition=def_map["zh"]),
            ms=ms_templates[kind][i].format(term=term_map["ms"], definition=def_map["ms"]),
        )

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
                "question": templ("a1", fact_term, fact_def, idx),
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
                "question": templ("a2", fact_term, fact_def, idx),
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
                "question": templ("a3", fact_term, fact_def, idx),
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
                "question": templ("a4", fact_term, fact_def, idx),
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
                "question": templ("b1", fact_term, fact_def, idx),
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
                "question": templ("b2", fact_term, fact_def, idx),
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
                "question": templ("b3", fact_term, fact_def, idx),
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
                "question": templ("b4", fact_term, fact_def, idx),
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
