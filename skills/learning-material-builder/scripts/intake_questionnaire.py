#!/usr/bin/env python3
"""Generate intake questions and normalize learner profile data."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field


@dataclass
class LearnerProfile:
    topic: str
    level: str
    goal: str = ""
    weeks: int = 4
    weekly_hours: int = 4
    known_skills: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    preferred_language: str = "ko"


def default_questions() -> list[str]:
    return [
        "무엇을 배우고 싶은가?",
        "현재 수준은 어느 정도인가? (입문/초급/중급/고급)",
        "학습 목표는 무엇인가? (취업/프로젝트/업무/기초)",
        "언제까지 학습할 계획인가? (총 주차)",
        "주당 학습 가능 시간은 얼마나 되는가?",
        "이미 알고 있는 선행지식은 무엇인가?",
        "개발 환경 제약이 있는가? (OS/버전/패키지 매니저)",
    ]


def normalize_level(raw: str) -> str:
    value = raw.strip().lower()
    if value in {"입문", "beginner", "novice"}:
        return "beginner"
    if value in {"초급", "junior", "basic"}:
        return "junior"
    if value in {"중급", "intermediate"}:
        return "intermediate"
    if value in {"고급", "advanced", "senior"}:
        return "advanced"
    return "beginner"


def recommend_prerequisites(topic: str, level: str, known_skills: list[str]) -> list[str]:
    topic_key = topic.lower()
    known = {item.lower().strip() for item in known_skills if item.strip()}
    prereq: list[str] = []

    if "react" in topic_key and not ({"javascript", "js"} & known):
        prereq.append("JavaScript basics")
    if "fastapi" in topic_key:
        if "python" not in known:
            prereq.append("Python fundamentals")
        if "async" not in known:
            prereq.append("Python async/await basics")
    if level in {"beginner", "junior"} and "git" not in known:
        prereq.append("Git fundamentals")
    return prereq


def build_profile(args: argparse.Namespace) -> LearnerProfile:
    known = [item.strip() for item in args.known_skills.split(",") if item.strip()]
    constraints = [item.strip() for item in args.constraints.split(",") if item.strip()]
    return LearnerProfile(
        topic=args.topic,
        level=normalize_level(args.level),
        goal=args.goal,
        weeks=args.weeks,
        weekly_hours=args.weekly_hours,
        known_skills=known,
        constraints=constraints,
        preferred_language=args.preferred_language,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate intake questionnaire/profile JSON.")
    parser.add_argument("--topic", default="FastAPI")
    parser.add_argument("--level", default="입문")
    parser.add_argument("--goal", default="기초부터 실습까지 학습")
    parser.add_argument("--weeks", type=int, default=4)
    parser.add_argument("--weekly-hours", type=int, default=4)
    parser.add_argument("--known-skills", default="")
    parser.add_argument("--constraints", default="")
    parser.add_argument("--preferred-language", default="ko", choices=["ko", "en"])
    parser.add_argument("--questions-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.questions_only:
        print("\n".join(f"- {q}" for q in default_questions()))
        return

    profile = build_profile(args)
    profile_data = asdict(profile)
    profile_data["recommended_prerequisites"] = recommend_prerequisites(
        profile.topic, profile.level, profile.known_skills
    )

    if args.json:
        print(json.dumps(profile_data, ensure_ascii=False, indent=2))
        return

    print("# Learner Profile")
    print(json.dumps(profile_data, ensure_ascii=False, indent=2))
    print("\n# Intake Questions")
    for question in default_questions():
        print(f"- {question}")


if __name__ == "__main__":
    main()

