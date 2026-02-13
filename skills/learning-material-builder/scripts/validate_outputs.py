#!/usr/bin/env python3
"""Validate generated learning material directory structure."""

from __future__ import annotations

import argparse
from pathlib import Path

REQUIRED_DOC_FILES = {"concept.md", "exercise.md"}
CODE_GROUPS = [
    {"exercise.js", "solution.js", "test.js"},
    {"exercise.jsx", "solution.jsx", "test.js"},
    {"exercise.py", "solution.py", "test.py"},
]


def has_valid_code_group(files: set[str]) -> bool:
    return any(group.issubset(files) for group in CODE_GROUPS)


def validate_section(section_dir: Path) -> list[str]:
    errors: list[str] = []
    files = {path.name for path in section_dir.iterdir() if path.is_file()}

    for required in REQUIRED_DOC_FILES:
        if required not in files:
            errors.append(f"{section_dir}: missing {required}")

    if not has_valid_code_group(files):
        errors.append(
            f"{section_dir}: missing code file set (exercise.*, solution.*, test.* for js/jsx/py)"
        )
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated curriculum output files.")
    parser.add_argument("--course-dir", required=True, help="Root directory of generated curriculum")
    args = parser.parse_args()

    root = Path(args.course_dir)
    if not root.exists():
        raise SystemExit(f"Directory not found: {root}")

    errors: list[str] = []
    chapters = sorted(path for path in root.iterdir() if path.is_dir() and path.name.startswith("ch"))
    if not chapters:
        errors.append("No chapter directory found (expected chXX-*)")

    for chapter in chapters:
        sections = sorted(path for path in chapter.iterdir() if path.is_dir() and path.name.startswith("sec"))
        if not sections:
            errors.append(f"{chapter}: no section directory found (expected secXX-*)")
            continue
        for section in sections:
            errors.extend(validate_section(section))

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print("Validation passed.")


if __name__ == "__main__":
    main()

