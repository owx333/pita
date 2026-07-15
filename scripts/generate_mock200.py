#!/usr/bin/env python3
"""Generate a separate 200-question mock exam page dataset."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class Fact:
    chapter: str
    term: str
    definition: str


FACTS: List[Fact] = [
    Fact("第1章 理解风险", "风险（Risk）", "暴露于不确定并可能造成财务损失的状态。"),
    Fact("第1章 理解风险", "危险因素（Peril）", "导致损失发生的直接原因，例如火灾、车祸、疾病。"),
    Fact("第1章 理解风险", "风险诱因（Hazard）", "会提高损失发生概率或严重程度的条件。"),
    Fact("第1章 理解风险", "物理风险诱因（Physical Hazard）", "由环境或实物条件造成的危险诱因，如电线老化。"),
    Fact("第1章 理解风险", "道德风险诱因（Morale Hazard）", "因态度或行为疏忽导致损失概率上升的诱因。"),
    Fact("第1章 理解风险", "纯风险（Pure Risk）", "只有损失或无损失两种结果，不会带来获利。"),
    Fact("第1章 理解风险", "投机风险（Speculative Risk）", "可能损失也可能获利的风险。"),
    Fact("第1章 理解风险", "特定风险（Particular Risk）", "主要影响个人或个别企业的风险。"),
    Fact("第1章 理解风险", "基本风险（Fundamental Risk）", "影响社会大多数人的系统性风险，如经济衰退。"),
    Fact("第1章 理解风险", "静态风险（Static Risk）", "由社会长期结构问题引起、变化较慢的风险。"),
    Fact("第1章 理解风险", "动态风险（Dynamic Risk）", "由经济、科技、政策变化引起的新风险。"),
    Fact("第2章 风险管理", "风险规避（Risk Avoidance）", "透过不参与某项活动来避免相关风险。"),
    Fact("第2章 风险管理", "风险控制（Risk Control）", "采取措施降低损失发生频率或严重程度。"),
    Fact("第2章 风险管理", "风险保留（Risk Retention）", "由个人或企业自行承担损失后果。"),
    Fact("第2章 风险管理", "风险转移（Risk Transfer）", "把损失财务后果转移给第三方，例如保险公司。"),
    Fact("第2章 风险管理", "损失预防（Loss Prevention）", "降低损失发生的可能性。"),
    Fact("第2章 风险管理", "损失降低（Loss Reduction）", "在损失发生后减少损失程度。"),
    Fact("第2章 风险管理", "替代（Substitution）", "用较低危险的活动或物质替代高风险做法。"),
    Fact("第2章 风险管理", "大数法则（Law of Large Numbers）", "样本越大，实际损失越接近期望损失。"),
    Fact("第3章 保险需求分析", "需求分析法（Needs Analysis）", "以具体财务责任计算保障缺口的保险需求方法。"),
    Fact("第3章 保险需求分析", "人类生命价值法（Human Life Value）", "估算家庭因经济支柱身故而损失的收入现值。"),
    Fact("第3章 保险需求分析", "实际现金价值（Actual Cash Value）", "赔偿金额等于重置成本减去折旧。"),
    Fact("第3章 保险需求分析", "关键人物价值（Key-man Value）", "企业因关键员工离职或身故可能承担的经济损失价值。"),
    Fact("第4章 人寿保单", "可保利益（Insurable Interest）", "投保人对被保险人生命或财产具有合法经济利益关系。"),
    Fact("第4章 人寿保单", "定期寿险（Term Policy）", "在约定期间提供保障，通常保费较低且保障纯粹。"),
    Fact("第4章 人寿保单", "终身寿险（Whole Life Policy）", "保障终身并可累积现金价值。"),
    Fact("第4章 人寿保单", "储蓄/两全保单（Endowment Policy）", "生存至期满或在期内身故都可领取给付。"),
    Fact("第4章 人寿保单", "不可争辩条款（Incontestability Clause）", "保单生效一段时间后，保险人一般不得因早期资料争议拒赔。"),
    Fact("第5章 医疗保险", "重大疾病保险（Critical Illness）", "确诊合约列明疾病时一次性给付保险金。"),
    Fact("第5章 医疗保险", "共同保险（Co-insurance）", "理赔时被保险人与保险公司按比例共同承担医疗费用。"),
    Fact("第5章 医疗保险", "自身职业定义（Own Occupation）", "无法从事原本职业即符合残疾给付条件，定义较宽。"),
    Fact("第5章 医疗保险", "任何职业定义（Any Occupation）", "仅在无法从事合理适任的任何职业时才符合残疾给付。"),
    Fact("第6章 年金", "确定年金（Annuity Certain）", "给付期固定，不依赖受领人生存与否。"),
    Fact("第6章 年金", "联合及遗属年金（Joint & Survivor）", "给付持续至最后一位受领人身故。"),
    Fact("第6章 年金", "累积期（Accumulation Phase）", "年金产品中持续缴费与投资增长的阶段。"),
    Fact("第6章 年金", "给付/清算期（Liquidation Phase）", "年金把累积资产转换为定期现金流的阶段。"),
    Fact("第7章 普通保险", "机器故障险（Machinery Breakdown）", "承保机器突发机械或电气故障造成的损失。"),
    Fact("第7章 普通保险", "雇主责任险（Employer's Liability）", "承保雇主依法对员工工伤事故应承担的赔偿责任。"),
    Fact("第7章 普通保险", "现金/金钱保险（Money Insurance）", "承保现金在场所内或运送途中被抢劫盗窃等损失。"),
    Fact("第7章 普通保险", "代位求偿（Subrogation）", "保险人赔付后可向责任第三方追偿。"),
    Fact("第7章 普通保险", "赔偿原则（Principle of Indemnity）", "理赔目的是恢复损失前财务状态，而非让被保险人获利。"),
    Fact("第8章 回教保险", "Tabarru'（互助捐献）", "参与者将部分供款捐入风险基金以互助共济。"),
    Fact("第8章 回教保险", "Wakalah 模式", "经营者作为代理人管理基金并收取代理费用。"),
    Fact("第8章 回教保险", "Mudharabah 模式", "参与者与经营者按约定比例分享投资利润。"),
    Fact("第8章 回教保险", "Al-Maisir", "伊斯兰金融中被禁止的赌博成分。"),
    Fact("第9章 法律原则", "最大诚信（Utmost Good Faith）", "投保与承保双方都必须充分、诚实披露重大事实。"),
    Fact("第9章 法律原则", "附和合同（Contract of Adhesion）", "条款由保险人拟定，投保人通常只能接受或拒绝。"),
    Fact("第10章 消费者保护", "消费者知情权", "消费者有权获得清晰、完整、可理解的产品信息。"),
    Fact("第11章 SOCSO", "失效抚恤金计划（Invalidity Pension Scheme）", "SOCSO 对失去工作能力成员提供长期收入保障。"),
    Fact("第11章 SOCSO", "家政服务人员豁免（Domestic Servant Exemption）", "家政服务人员通常不属于 SOCSO 一般雇员承保范围。"),
]


def build_options(correct: str, distractors: Sequence[str], rnd: random.Random) -> Dict[str, str]:
    labels = ["a", "b", "c", "d"]
    pool = [correct] + list(distractors)
    rnd.shuffle(pool)
    return {label: text for label, text in zip(labels, pool)}


def answer_key(options: Dict[str, str], target: str) -> str:
    for key, value in options.items():
        if value == target:
            return key
    raise ValueError("target not in options")


def pick_other_facts(facts: Sequence[Fact], current_index: int, count: int, rnd: random.Random) -> List[Fact]:
    candidates = [fact for idx, fact in enumerate(facts) if idx != current_index]
    return rnd.sample(candidates, count)


def generate_questions(facts: Sequence[Fact]) -> List[Dict[str, object]]:
    rnd = random.Random(20260715)
    questions: List[Dict[str, object]] = []
    qid = 1

    for idx, fact in enumerate(facts):
        # Type 1: definition -> term
        others = pick_other_facts(facts, idx, 3, rnd)
        options = build_options(fact.term, [x.term for x in others], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": f"【术语识别】以下定义对应哪个术语？\n{fact.definition}",
                "options": options,
                "answer": answer_key(options, fact.term),
                "explanation": f"正确术语是「{fact.term}」，因为其定义就是：{fact.definition}",
            }
        )
        qid += 1

        # Type 2: term -> definition
        others = pick_other_facts(facts, idx, 3, rnd)
        options = build_options(fact.definition, [x.definition for x in others], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": f"【概念理解】关于「{fact.term}」，下列哪项描述最准确？",
                "options": options,
                "answer": answer_key(options, fact.definition),
                "explanation": f"「{fact.term}」的正确描述为：{fact.definition}",
            }
        )
        qid += 1

        # Type 3: one correct pair
        others = pick_other_facts(facts, idx, 6, rnd)
        wrong_pair_1 = f"{others[0].term} — {others[1].definition}"
        wrong_pair_2 = f"{others[2].term} — {others[3].definition}"
        wrong_pair_3 = f"{others[4].term} — {others[5].definition}"
        correct_pair = f"{fact.term} — {fact.definition}"
        options = build_options(correct_pair, [wrong_pair_1, wrong_pair_2, wrong_pair_3], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": "【配对题】以下哪一组“术语—解释”配对是正确的？",
                "options": options,
                "answer": answer_key(options, correct_pair),
                "explanation": f"正确配对是：{fact.term} — {fact.definition}",
            }
        )
        qid += 1

        # Type 4: one incorrect pair
        others = pick_other_facts(facts, idx, 7, rnd)
        wrong_pair = f"{fact.term} — {others[0].definition}"
        correct_pair_1 = f"{others[1].term} — {others[1].definition}"
        correct_pair_2 = f"{others[2].term} — {others[2].definition}"
        correct_pair_3 = f"{others[3].term} — {others[3].definition}"
        options = build_options(wrong_pair, [correct_pair_1, correct_pair_2, correct_pair_3], rnd)
        questions.append(
            {
                "id": qid,
                "chapter": fact.chapter,
                "question": "【辨识题】以下哪一组“术语—解释”配对是错误的？",
                "options": options,
                "answer": answer_key(options, wrong_pair),
                "explanation": f"错误配对是「{wrong_pair}」。正确解释应为：{fact.definition}",
            }
        )
        qid += 1

    return questions


def main() -> None:
    out_json = Path("/workspace/data/mock200.json")
    out_js = Path("/workspace/data/mock200-data.js")
    out_highlights = Path("/workspace/materials/rfp-slide-highlights.md")

    questions = generate_questions(FACTS)
    if len(questions) != 200:
        raise ValueError(f"Expected 200 questions, got {len(questions)}")

    chapter_focus = [
        "理解风险：风险、危险因素、风险诱因、纯风险/投机风险、特定风险/基本风险。",
        "风险管理：规避、控制、保留、转移，以及损失预防与损失降低。",
        "保险需求分析：需求分析、人类生命价值、实际现金价值、关键人物价值。",
        "人寿保单：定期/终身/储蓄型保单、可保利益与不可争辩条款。",
        "医疗与年金：重大疾病、残疾定义、共同保险、年金类型与阶段。",
        "普通保险：机器故障险、雇主责任险、金钱保险、代位求偿与赔偿原则。",
        "回教保险：Tabarru'、Wakalah、Mudharabah、Al-Maisir。",
        "法律与消费者：最大诚信、附和合同、消费者知情权。",
        "SOCSO：失效抚恤计划与常见承保/豁免概念。",
    ]

    payload = {
        "meta": {
            "title": "RFP Module 2 模拟考试（200题）",
            "language": "zh",
            "questionCount": 200,
            "source": {
                "slidePdf": "/workspace/materials/Registred Financial Planning (RFP) Module 2 Tutorial  (Man) _V1.0 as of Nov 2024.pdf",
                "ebookPdf": "/workspace/materials/E-Book_PCM2_Mandarin.pdf",
            },
            "focus": chapter_focus,
        },
        "questions": questions,
    }

    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    out_js.write_text(
        "window.__MOCK200_DATA__ = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    out_highlights.write_text(
        "# RFP Module 2 Slide 重点整理\n\n"
        + "\n".join(f"- {item}" for item in chapter_focus)
        + "\n",
        encoding="utf-8",
    )

    print(f"[done] wrote {out_json}")
    print(f"[done] wrote {out_js}")
    print(f"[done] wrote {out_highlights}")


if __name__ == "__main__":
    main()
