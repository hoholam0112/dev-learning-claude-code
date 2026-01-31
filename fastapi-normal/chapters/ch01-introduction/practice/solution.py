# 실행 방법: uvicorn solution:app --reload
# 챕터 01 연습 문제 모범 답안

import platform
import sys
from datetime import datetime

from fastapi import FastAPI

app = FastAPI(
    title="챕터 01 연습 문제 답안",
    description="자기소개, 계산기, 타임스탬프 API",
    version="1.0.0",
)

# ============================================================
# 문제 1: 자기소개 API
# ============================================================


@app.get("/me", tags=["자기소개"])
def get_my_profile():
    """자기소개 정보를 반환합니다."""
    return {
        "name": "홍길동",
        "age": 25,
        "hobbies": ["코딩", "독서", "게임"],
    }


# ============================================================
# 문제 2: 간단한 계산기 API
# ============================================================


@app.get("/calc/add/{a}/{b}", tags=["계산기"])
def add(a: float, b: float):
    """두 수의 덧셈을 수행합니다."""
    return {"operation": "add", "a": a, "b": b, "result": a + b}


@app.get("/calc/subtract/{a}/{b}", tags=["계산기"])
def subtract(a: float, b: float):
    """두 수의 뺄셈을 수행합니다."""
    return {"operation": "subtract", "a": a, "b": b, "result": a - b}


@app.get("/calc/multiply/{a}/{b}", tags=["계산기"])
def multiply(a: float, b: float):
    """두 수의 곱셈을 수행합니다."""
    return {"operation": "multiply", "a": a, "b": b, "result": a * b}


@app.get("/calc/divide/{a}/{b}", tags=["계산기"])
def divide(a: float, b: float):
    """두 수의 나눗셈을 수행합니다.

    b가 0인 경우 에러 메시지를 반환합니다.
    """
    if b == 0:
        return {"operation": "divide", "a": a, "b": b, "error": "0으로 나눌 수 없습니다"}
    return {"operation": "divide", "a": a, "b": b, "result": a / b}


# ============================================================
# 문제 3: 타임스탬프 API
# ============================================================


@app.get("/time", tags=["시간"])
def get_current_time():
    """현재 시간과 서버 정보를 반환합니다."""
    now = datetime.now()
    return {
        "timestamp": now.isoformat(),
        "unix_timestamp": now.timestamp(),
        "server_info": {
            "python_version": sys.version.split()[0],
            "platform": platform.system().lower(),
        },
    }


@app.get("/time/{timezone}", tags=["시간"])
def get_time_with_timezone(timezone: str):
    """지정한 타임존 이름과 함께 현재 시간을 반환합니다.

    참고: 이 예제는 간단하게 타임존 이름만 표시합니다.
    실제 타임존 변환은 zoneinfo(Python 3.9+) 모듈을 사용할 수 있습니다.
    """
    now = datetime.now()
    return {
        "timezone": timezone,
        "timestamp": now.isoformat(),
        "unix_timestamp": now.timestamp(),
        "server_info": {
            "python_version": sys.version.split()[0],
            "platform": platform.system().lower(),
        },
    }
