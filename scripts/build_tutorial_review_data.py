#!/usr/bin/env python3
"""Build structured review notes from RFP Module 2 tutorial PDF."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from pypdf import PdfReader

from generate_mock200 import FACTS


PDF_PATH = Path(
    "/workspace/materials/Registred Financial Planning (RFP) Module 2 Tutorial  (Man) _V1.0 as of Nov 2024.pdf"
)
OUT_JSON = Path("/workspace/data/tutorial-review.json")
OUT_JS = Path("/workspace/data/tutorial-review-data.js")


DEFAULT_CHAPTERS = {
    1: "了解风险",
    2: "风险管理",
    3: "保险需求分析",
    4: "人寿保险政策",
    5: "医疗保险",
    6: "养老金",
    7: "保险规划中的普通保险",
    8: "Takaful保险",
    9: "保险的法律原则和相关立法",
    10: "消费者保障和人寿保险行业业务守则",
    11: "SOCSO",
}

LEARNING_OBJECTIVES = [
    "识别财务规划中的风险。",
    "讨论风险与保险在个人财务中的重要性。",
    "分类并识别处理风险的技术。",
    "识别不同类型保险产品与适用场景。",
    "理解保险产品定价、保障与理赔核心逻辑。",
]

MEMORY_CHECKLIST = {
    1: ["风险 / 危险因素 / 风险诱因三者差异", "纯风险 vs 投机风险", "特定风险 vs 基本风险"],
    2: ["四大处理技术：规避、控制、保留、转移", "损失预防 vs 损失降低", "风险管理流程顺序"],
    3: ["需求分析法计算逻辑", "人类生命价值法核心输入", "实际现金价值(ACV)计算方式"],
    4: ["定期、终身、储蓄保单差异", "可保利益何时存在", "不可争辩条款与消费者保障"],
    5: ["重大疾病/医疗险主要保障", "Own occupation vs Any occupation", "常见除外责任"],
    6: ["年金累积期与给付期", "确定年金与终身年金差异", "联合及遗属年金给付逻辑"],
    7: ["机器故障险、雇主责任险、金钱保险用途", "赔偿原则与代位求偿", "家庭保险承保边界"],
    8: ["Tabarru'、Wakalah、Mudharabah", "传统保险与Takaful概念差异", "Al-Maisir含义"],
    9: ["最大诚信原则", "附和合同(adhesion)", "保险合同关键法律要件"],
    10: ["消费者权利（知情、选择、申诉）", "行业守则与披露要求", "代理人合规要求"],
    11: ["SOCSO覆盖范围与豁免", "失效抚恤计划", "常见给付类型与条件"],
}


def read_pdf_text(path: Path) -> str:
    return "\n".join((page.extract_text() or "") for page in PdfReader(str(path)).pages)


def clean_text(value: str) -> str:
    value = value.replace("\u3000", " ")
    value = re.sub(r"Registered Financial Planning Module 2_[^\n]*", "", value)
    value = re.sub(r"Registered Financial Planning \(RFP\) Module 2_[^\n]*", "", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value


def extract_chapter_positions(text: str) -> List[tuple[int, int]]:
    positions: List[tuple[int, int]] = []
    for match in re.finditer(r"第\s*([0-9]{1,2})\s*章", text):
        num = int(match.group(1))
        if 1 <= num <= 11:
            positions.append((num, match.start()))
    # keep first occurrence per chapter in order
    seen = set()
    ordered: List[tuple[int, int]] = []
    for num, idx in sorted(positions, key=lambda x: x[1]):
        if num not in seen:
            seen.add(num)
            ordered.append((num, idx))
    return ordered


def normalize_line(line: str) -> str:
    line = line.replace("\u3000", " ")
    line = re.sub(r"\s+", " ", line).strip()
    line = re.sub(r"^[•·▪▫◆◇○●oO]+\s*", "", line)
    return line


def is_noise_line(line: str) -> bool:
    if not line:
        return True
    if re.fullmatch(r"[0-9\s./:,-]+", line):
        return True
    if re.fullmatch(r"[✓✔✗×><=+\-()（）\[\]]+", line):
        return True
    if line.lower().startswith("registred financial planning"):
        return True
    if line.lower().startswith("registered financial planning"):
        return True
    compact = re.sub(r"\s+", "", line)
    if len(compact) <= 1:
        return True
    return False


def extract_highlights(text: str, start: int, end: int, chapter_num: int, chapter_title: str) -> List[str]:
    segment = text[start:end]
    lines = [normalize_line(line) for line in segment.splitlines()]

    cleaned: List[str] = []
    seen = set()
    title_markers = {
        chapter_title.replace(" ", ""),
        f"第{chapter_num}章:{chapter_title}".replace(" ", ""),
        f"第{chapter_num}章：{chapter_title}".replace(" ", ""),
    }

    for line in lines:
        if is_noise_line(line):
            continue
        compact = re.sub(r"\s+", "", line)
        if compact in seen:
            continue
        if compact in title_markers:
            continue
        if compact.startswith(f"第{chapter_num}章") and len(compact) <= 16:
            continue
        seen.add(compact)
        cleaned.append(line)

    if not cleaned:
        return []

    # Keep the first group of meaningful lines as "quick revision points".
    return cleaned[:16]


def extract_highlights_from_excerpt_blob(
    excerpt: str, chapter_num: int, chapter_title: str
) -> List[str]:
    text = str(excerpt or "").replace("...", " ")
    text = re.sub(r"(第\s*\d+\s*章\s*[:：])", r"\n\1", text)
    text = re.sub(
        r"(风险分类|纯风险的类型|应对风险的态度|个人风险|物业风险|法律责任风险|学习目标|年金的分类|保险类型|风险管理流程)",
        r"\n\1",
        text,
    )
    text = re.sub(r"\s{2,}", "\n", text)
    text = re.sub(r"\s[0-9]{2}\s", "\n", text)
    lines = [normalize_line(line) for line in re.split(r"[\n；;。]+", text)]

    cleaned: List[str] = []
    seen = set()
    title_markers = {
        chapter_title.replace(" ", ""),
        f"第{chapter_num}章:{chapter_title}".replace(" ", ""),
        f"第{chapter_num}章：{chapter_title}".replace(" ", ""),
    }

    for line in lines:
        if is_noise_line(line):
            continue
        compact = re.sub(r"\s+", "", line)
        if compact in seen:
            continue
        if compact in title_markers:
            continue
        if compact.startswith(f"第{chapter_num}章") and len(compact) <= 16:
            continue
        seen.add(compact)
        cleaned.append(line)

    return cleaned[:16]


def build_excerpt_from_highlights(highlights: List[str]) -> str:
    if not highlights:
        return ""
    excerpt = "；".join(highlights[:4]).strip()
    if len(excerpt) > 360:
        return excerpt[:360].rstrip() + "..."
    return excerpt


def facts_by_chapter() -> Dict[int, List[Dict[str, str]]]:
    groups: Dict[int, List[Dict[str, str]]] = defaultdict(list)
    for fact in FACTS:
        match = re.search(r"第\s*([0-9]{1,2})\s*章", fact.chapter)
        if not match:
            continue
        cnum = int(match.group(1))
        groups[cnum].append({"term": fact.term, "definition": fact.definition})
    return groups


def main() -> None:
    chapter_facts = facts_by_chapter()
    chapters = []

    if PDF_PATH.exists():
        raw = read_pdf_text(PDF_PATH)
        text = clean_text(raw)
        chapter_marks = extract_chapter_positions(text)

        for i, (chapter_num, start) in enumerate(chapter_marks):
            end = chapter_marks[i + 1][1] if i + 1 < len(chapter_marks) else len(text)
            chapter_title = DEFAULT_CHAPTERS.get(chapter_num, f"第{chapter_num}章")
            highlights = extract_highlights(text, start, end, chapter_num, chapter_title)
            chapters.append(
                {
                    "id": chapter_num,
                    "title": chapter_title,
                    "sourceExcerpt": build_excerpt_from_highlights(highlights),
                    "sourceHighlights": highlights,
                    "keyTerms": chapter_facts.get(chapter_num, []),
                    "memoryChecklist": MEMORY_CHECKLIST.get(chapter_num, []),
                }
            )
    elif OUT_JSON.exists():
        existing = json.loads(OUT_JSON.read_text(encoding="utf-8"))
        existing_chapters = existing.get("chapters", [])
        for chapter in existing_chapters:
            chapter_num = int(chapter.get("id", 0))
            chapter_title = chapter.get("title") or DEFAULT_CHAPTERS.get(chapter_num, f"第{chapter_num}章")
            highlights = extract_highlights_from_excerpt_blob(
                chapter.get("sourceExcerpt", ""),
                chapter_num,
                chapter_title,
            )
            chapters.append(
                {
                    "id": chapter_num,
                    "title": chapter_title,
                    "sourceExcerpt": build_excerpt_from_highlights(highlights),
                    "sourceHighlights": highlights,
                    "keyTerms": chapter.get("keyTerms") or chapter_facts.get(chapter_num, []),
                    "memoryChecklist": chapter.get("memoryChecklist")
                    or MEMORY_CHECKLIST.get(chapter_num, []),
                }
            )
    else:
        raise FileNotFoundError(
            "Source PDF and existing tutorial-review.json are both unavailable."
        )

    chapters = sorted(chapters, key=lambda item: item["id"])

    payload = {
        "meta": {
            "title": "PITA 教材温习站（Module 2 Tutorial）",
            "sourcePdf": str(PDF_PATH),
            "chapterCount": len(chapters),
            "learningObjectives": LEARNING_OBJECTIVES,
        },
        "chapters": chapters,
    }

    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_JS.write_text(
        "window.__TUTORIAL_REVIEW_DATA__ = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"[done] wrote {OUT_JSON}")
    print(f"[done] wrote {OUT_JS}")


if __name__ == "__main__":
    main()
