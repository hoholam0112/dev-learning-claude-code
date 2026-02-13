#!/usr/bin/env python3
"""Create a dynamic chapter/section curriculum plan from learner profile inputs."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass


def slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9가-힣 ]+", "", text).strip().lower().replace(" ", "-")
    return re.sub(r"-{2,}", "-", cleaned)


@dataclass
class ChapterTemplate:
    title: str
    sections: list[str]


STACK_TEMPLATES: dict[str, list[ChapterTemplate]] = {
    "javascript": [
        ChapterTemplate("JavaScript 기본 문법", ["변수와 타입", "조건문과 반복문"]),
        ChapterTemplate("함수와 데이터 구조", ["함수 선언과 활용", "객체와 배열"]),
        ChapterTemplate("모던 JavaScript", ["ES6+ 핵심 문법", "비동기 처리"]),
    ],
    "react": [
        ChapterTemplate("React 시작하기", ["React 핵심 개념", "개발 환경 구성"]),
        ChapterTemplate("컴포넌트와 상태", ["Props", "State와 이벤트"]),
        ChapterTemplate("Hooks와 실전 패턴", ["useEffect", "커스텀 훅"]),
    ],
    "fastapi": [
        ChapterTemplate("FastAPI 시작하기", ["설치 및 앱 생성", "개발 서버와 문서"]),
        ChapterTemplate("요청과 응답", ["Path/Query 파라미터", "Pydantic 모델"]),
        ChapterTemplate("실전 API 구성", ["의존성 주입", "인증/예외 처리"]),
    ],
    "python": [
        ChapterTemplate("Python 기초", ["변수/자료형", "제어문"]),
        ChapterTemplate("함수와 모듈", ["함수 설계", "모듈과 패키지"]),
        ChapterTemplate("실전 파이썬", ["파일 처리", "예외 처리"]),
    ],
}


def select_stack(topic: str) -> str:
    value = topic.lower()
    for key in STACK_TEMPLATES:
        if key in value:
            return key
    return "python"


def calculate_target_chapters(level: str, weekly_hours: int, weeks: int, max_available: int) -> int:
    capacity = weekly_hours * weeks
    level_bonus = {"beginner": 0, "junior": 0, "intermediate": 1, "advanced": 2}.get(level, 0)
    if capacity < 12:
        base = 2
    elif capacity < 24:
        base = 3
    else:
        base = 4
    return max(2, min(max_available, base + level_bonus))


def build_prerequisite_chapters(topic: str, known_skills: list[str]) -> list[ChapterTemplate]:
    lower_topic = topic.lower()
    known = {item.strip().lower() for item in known_skills}
    prereq: list[ChapterTemplate] = []
    if "react" in lower_topic and not ({"javascript", "js"} & known):
        prereq.append(ChapterTemplate("선행: JavaScript 기초", ["변수/타입", "함수/배열 기초"]))
    if "fastapi" in lower_topic and "python" not in known:
        prereq.append(ChapterTemplate("선행: Python 기초", ["함수와 타입힌트", "비동기 기초"]))
    return prereq


def chapter_to_dict(chapter_index: int, chapter: ChapterTemplate) -> dict:
    chapter_slug = f"ch{chapter_index:02d}-{slugify(chapter.title)}"
    sections = []
    for section_index, section_title in enumerate(chapter.sections, start=1):
        sections.append(
            {
                "index": section_index,
                "title": section_title,
                "slug": f"sec{section_index:02d}-{slugify(section_title)}",
            }
        )
    return {
        "index": chapter_index,
        "title": chapter.title,
        "slug": chapter_slug,
        "sections": sections,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate chapter/section plan JSON.")
    parser.add_argument("--topic", default="FastAPI")
    parser.add_argument("--level", default="beginner")
    parser.add_argument("--goal", default="기초와 실습 완료")
    parser.add_argument("--weeks", type=int, default=4)
    parser.add_argument("--weekly-hours", type=int, default=4)
    parser.add_argument("--known-skills", default="")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    known_skills = [item.strip() for item in args.known_skills.split(",") if item.strip()]
    stack = select_stack(args.topic)
    base_templates = STACK_TEMPLATES[stack]
    target_count = calculate_target_chapters(args.level, args.weekly_hours, args.weeks, len(base_templates))
    prereq_templates = build_prerequisite_chapters(args.topic, known_skills)
    selected_templates = prereq_templates + base_templates[:target_count]

    chapters = [
        chapter_to_dict(chapter_index=i, chapter=template) for i, template in enumerate(selected_templates, start=1)
    ]

    plan = {
        "topic": args.topic,
        "stack": stack,
        "level": args.level,
        "goal": args.goal,
        "weeks": args.weeks,
        "weekly_hours": args.weekly_hours,
        "known_skills": known_skills,
        "chapters": chapters,
    }

    rendered = json.dumps(plan, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(rendered + "\n")
        print(f"Wrote plan JSON: {args.output}")
    else:
        print(rendered)


if __name__ == "__main__":
    main()

