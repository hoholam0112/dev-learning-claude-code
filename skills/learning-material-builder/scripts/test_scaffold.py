#!/usr/bin/env python3
"""Generate runtime-friendly test scaffolds for exercise files."""

from __future__ import annotations

import argparse
from pathlib import Path


def generate_js_test() -> str:
    return """// 실행: node test.js
const fs = require("fs");
const path = require("path");

const target = path.join(__dirname, "exercise.js");
if (!fs.existsSync(target)) {
  throw new Error("exercise.js 파일이 없습니다.");
}

const content = fs.readFileSync(target, "utf8");
if (!content.includes("TODO")) {
  console.log("exercise.js에 TODO가 없습니다. 이미 완료했을 수 있습니다.");
}

console.log("기본 구조 점검 완료");
"""


def generate_py_test() -> str:
    return """# 실행: python test.py
from pathlib import Path

target = Path(__file__).with_name("exercise.py")
if not target.exists():
    raise FileNotFoundError("exercise.py 파일이 없습니다.")

text = target.read_text(encoding="utf-8")
if "TODO" not in text:
    print("exercise.py에 TODO가 없습니다. 이미 완료했을 수 있습니다.")

print("기본 구조 점검 완료")
"""


def generate_react_test() -> str:
    return """// 실행: node test.js
const fs = require("fs");
const path = require("path");

const target = path.join(__dirname, "exercise.jsx");
if (!fs.existsSync(target)) {
  throw new Error("exercise.jsx 파일이 없습니다.");
}

const content = fs.readFileSync(target, "utf8");
if (!content.includes("export") && !content.includes("function")) {
  throw new Error("exercise.jsx에 컴포넌트/함수 정의가 없습니다.");
}

console.log("React exercise 구조 점검 완료");
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Create test scaffold content file.")
    parser.add_argument("--stack", required=True, choices=["javascript", "react", "python", "fastapi"])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.stack == "javascript":
        content = generate_js_test()
    elif args.stack == "react":
        content = generate_react_test()
    else:
        content = generate_py_test()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Wrote test scaffold: {output_path}")


if __name__ == "__main__":
    main()

