# 실행 방법: uvicorn exercise:app --reload
# 챕터 01 연습 문제 - 직접 코드를 작성해보세요!

import platform
import sys
from datetime import datetime

from fastapi import FastAPI

app = FastAPI(
    title="챕터 01 연습 문제",
    description="자기소개, 계산기, 타임스탬프 API",
    version="1.0.0",
)

# ============================================================
# 문제 1: 자기소개 API
# GET /me — 자기소개 정보를 JSON으로 반환합니다
# 반환 필드: name(str), age(int), hobbies(list)
# ============================================================


@app.get("/me", tags=["자기소개"])
def get_my_profile():
    """자기소개 정보를 반환합니다."""
    # TODO: 자기 정보를 딕셔너리로 반환하세요
    pass


# ============================================================
# 문제 2: 간단한 계산기 API
# GET /calc/add/{a}/{b} — 덧셈
# GET /calc/subtract/{a}/{b} — 뺄셈
# GET /calc/multiply/{a}/{b} — 곱셈
# GET /calc/divide/{a}/{b} — 나눗셈 (b가 0이면 에러 메시지)
# a, b는 float 타입
# 반환 형식: {"operation": "...", "a": ..., "b": ..., "result": ...}
# ============================================================


@app.get("/calc/add/{a}/{b}", tags=["계산기"])
def add(a: float, b: float):
    """두 수의 덧셈을 수행합니다."""
    # TODO: 덧셈 결과를 반환하세요
    pass


@app.get("/calc/subtract/{a}/{b}", tags=["계산기"])
def subtract(a: float, b: float):
    """두 수의 뺄셈을 수행합니다."""
    # TODO: 뺄셈 결과를 반환하세요
    pass


@app.get("/calc/multiply/{a}/{b}", tags=["계산기"])
def multiply(a: float, b: float):
    """두 수의 곱셈을 수행합니다."""
    # TODO: 곱셈 결과를 반환하세요
    pass


@app.get("/calc/divide/{a}/{b}", tags=["계산기"])
def divide(a: float, b: float):
    """두 수의 나눗셈을 수행합니다. b가 0인 경우 에러 메시지를 반환합니다."""
    # TODO: b가 0이면 에러 메시지를, 아니면 나눗셈 결과를 반환하세요
    pass


# ============================================================
# 문제 3: 타임스탬프 API
# GET /time — 현재 시간과 서버 정보를 반환합니다
# GET /time/{timezone} — 타임존 이름과 함께 현재 시간을 반환합니다
# 반환 필드: timestamp(ISO 형식), unix_timestamp(float), server_info(dict)
# server_info: python_version, platform
# ============================================================


@app.get("/time", tags=["시간"])
def get_current_time():
    """현재 시간과 서버 정보를 반환합니다."""
    # TODO: 현재 시간(ISO 형식, unix), 서버 정보(Python 버전, 플랫폼)를 반환하세요
    # 힌트: datetime.now(), sys.version, platform.system()
    pass


@app.get("/time/{timezone}", tags=["시간"])
def get_time_with_timezone(timezone: str):
    """지정한 타임존 이름과 함께 현재 시간을 반환합니다."""
    # TODO: timezone 이름과 함께 현재 시간 정보를 반환하세요
    pass
