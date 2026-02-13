---
name: learning-material-builder
description: Build structured developer learning materials with prerequisite analysis, chapter and section planning, and section-by-section content generation. Use when a user asks to create programming curriculum, study roadmaps, concept notes, coding exercises, exercise and solution files, or runnable practice tests for a specific language or framework.
---

# Learning Material Builder

## Overview

Create reusable, execution-ready learning content for developers.
Always collect learner intent first, then generate curriculum and section assets in a consistent file structure.

## Workflow

### 1) Collect learner profile and constraints

Ask these first:
- What stack to learn (language/framework and version if relevant)
- Current level (beginner, junior, intermediate, advanced)
- Target outcome (interview, project, production task, fundamentals)
- Time constraints (weeks, weekly hours)
- Prior knowledge and missing prerequisites
- Environment constraints (OS, package manager, runtime version)

Use `scripts/intake_questionnaire.py` to generate and normalize this intake.
Use `references/question-bank.md` when the request is ambiguous.

### 2) Derive prerequisite learning scope

Infer prerequisite modules before core topics.
Examples:
- React request + weak JavaScript basics -> insert JavaScript prerequisite chapter
- FastAPI request + weak Python typing/async -> insert Python prerequisite chapter

Follow `references/curriculum_rules.md` for prerequisite insertion and level scaling.

### 3) Plan chapters and sections

Build a dynamic curriculum based on learner data and topic complexity.
Do not hardcode a fixed chapter count.
Decide scale by:
- learner level
- available study time
- stack complexity
- prerequisite gap size

Use `scripts/curriculum_planner.py` to emit a machine-readable plan JSON.
Use `references/stack_profiles.md` to map framework to file extensions and runtime.

### 4) Generate section assets sequentially

Generate one section at a time in this order:
1. `concept.md`
2. `exercise.md`
3. `exercise.*`
4. `solution.*`
5. runnable test code

Use `scripts/section_generator.py` to create folders and section files.
Generate code filenames as:
- JavaScript: `exercise.js`, `solution.js`, `test.js`
- React: `exercise.jsx`, `solution.jsx`, `test.js`
- Python/FastAPI: `exercise.py`, `solution.py`, `test.py`

For React sections, keep tests runtime-friendly and avoid requiring complex bundler setup by default.

### 5) Produce runnable tests

Use `scripts/test_scaffold.py` to generate assertions for expected behavior.
Prefer simple runtime commands:
- `node test.js`
- `python test.py`

Add exact run instructions to each section's `exercise.md`.

### 6) Validate output quality

Use `scripts/validate_outputs.py` to verify:
- required file presence
- section metadata completeness
- exercise and solution file pairing
- test file presence and basic command guidance

### 7) Research policy

Use web search only when it materially improves quality:
- unstable APIs
- recently changed framework guidance
- best-practice updates that may have changed

Prioritize official documentation and primary sources.
Record source links and rationale in `references/research-notes.md` when external research is used.

## Output Conventions

- Default output language: Korean
- Preserve technical terms in English where clarity matters
- Keep chapter names concise and section slugs stable (`sec01-*`, `sec02-*`)
- Keep explanations practical and avoid abstract theory dumps
- Include at least one edge case in every exercise/test pair

## Resources

- `scripts/intake_questionnaire.py`: Intake question generator and profile normalizer
- `scripts/curriculum_planner.py`: Dynamic chapter and section planner
- `scripts/section_generator.py`: Section file generator
- `scripts/test_scaffold.py`: Runtime test content generator
- `scripts/validate_outputs.py`: Output structure validator
- `references/question-bank.md`: Reusable intent and level questions
- `references/curriculum_rules.md`: Curriculum composition rules
- `references/stack_profiles.md`: Stack-specific file/runtime mapping
- `references/research_policy.md`: Web research policy and citation rules
- `assets/templates/*`: Markdown templates for concept and exercise files
