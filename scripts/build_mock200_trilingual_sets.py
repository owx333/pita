#!/usr/bin/env python3
"""Split the existing 400-trilingual set into two trilingual 200 sets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


def to_js(var_name: str, payload: Dict[str, object]) -> str:
    return f"window.{var_name} = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"


def remap_ids(items: List[Dict[str, object]]) -> List[Dict[str, object]]:
    out = []
    for idx, q in enumerate(items, start=1):
        copy = dict(q)
        copy["id"] = idx
        out.append(copy)
    return out


def build_payload(title: Dict[str, str], description: Dict[str, str], questions: List[Dict[str, object]]) -> Dict[str, object]:
    return {
        "meta": {
            "title": title,
            "description": description,
            "questionCount": len(questions),
            "languageMode": "trilingual",
        },
        "questions": questions,
    }


def main() -> None:
    base = Path("/workspace")
    source_path = base / "data/mock400-trilingual.json"
    source = json.loads(source_path.read_text(encoding="utf-8"))
    questions: List[Dict[str, object]] = source.get("questions", [])

    base200 = [q for q in questions if q.get("sourceSet") == "base200"]
    hard200 = [q for q in questions if q.get("sourceSet") == "hard200"]

    if len(base200) != 200 or len(hard200) != 200:
        raise ValueError(f"Expected 200/200 split, got base={len(base200)} hard={len(hard200)}")

    base200 = remap_ids(base200)
    hard200 = remap_ids(hard200)

    payload_base = build_payload(
        title={
            "en": "RFP Module 2 Mock Exam (200 Questions, Trilingual)",
            "zh": "RFP 第二单元模拟考试（200题，三语）",
            "ms": "Peperiksaan Olok-olok RFP Modul 2 (200 soalan, tiga bahasa)",
        },
        description={
            "en": "Core mock set in English, Chinese and Malay.",
            "zh": "基础模拟题库，支持英文、中文、马来文。",
            "ms": "Set simulasi asas dalam Bahasa Inggeris, Cina dan Melayu.",
        },
        questions=base200,
    )

    payload_hard = build_payload(
        title={
            "en": "RFP Module 2 Advanced Mock Exam (200 Questions, Trilingual)",
            "zh": "RFP 第二单元加强模拟考试（200题，三语）",
            "ms": "Peperiksaan Olok-olok Lanjutan RFP Modul 2 (200 soalan, tiga bahasa)",
        },
        description={
            "en": "Advanced mock set in English, Chinese and Malay.",
            "zh": "加强模拟题库，支持英文、中文、马来文。",
            "ms": "Set simulasi lanjutan dalam Bahasa Inggeris, Cina dan Melayu.",
        },
        questions=hard200,
    )

    out_base_json = base / "data/mock200-trilingual.json"
    out_base_js = base / "data/mock200-trilingual-data.js"
    out_hard_json = base / "data/mock200-hard-trilingual.json"
    out_hard_js = base / "data/mock200-hard-trilingual-data.js"

    out_base_json.write_text(json.dumps(payload_base, ensure_ascii=False, indent=2), encoding="utf-8")
    out_base_js.write_text(to_js("__MOCK200_TRI_DATA__", payload_base), encoding="utf-8")
    out_hard_json.write_text(json.dumps(payload_hard, ensure_ascii=False, indent=2), encoding="utf-8")
    out_hard_js.write_text(to_js("__MOCK200_HARD_TRI_DATA__", payload_hard), encoding="utf-8")

    print(f"[done] wrote {out_base_json}")
    print(f"[done] wrote {out_base_js}")
    print(f"[done] wrote {out_hard_json}")
    print(f"[done] wrote {out_hard_js}")


if __name__ == "__main__":
    main()
