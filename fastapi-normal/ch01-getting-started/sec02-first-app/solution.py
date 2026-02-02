# 실행: uvicorn solution:app --reload
# 테스트: http://localhost:8000/docs 에서 확인
# 또는: python solution.py (자체 테스트)
#
# 이 파일은 exercise.py의 모범 답안입니다.

from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


# 문제 1: GET /hello 엔드포인트
# @app.get() 데코레이터를 사용하여 GET 메서드의 엔드포인트를 정의합니다.
# 경로는 "/hello"이며, 딕셔너리를 반환하면 자동으로 JSON 응답이 됩니다.
@app.get("/hello")
def hello():
    return {"message": "안녕하세요, FastAPI!"}


# 문제 2: GET /greet/{name} 엔드포인트
# 경로에 {name}을 넣으면 경로 매개변수(path parameter)가 됩니다.
# 함수의 매개변수 이름(name)이 경로의 {name}과 일치해야 합니다.
# 타입 힌트(: str)를 지정하면 FastAPI가 자동으로 타입 검증을 수행합니다.
# f-string을 사용하여 동적으로 메시지를 생성합니다.
@app.get("/greet/{name}")
def greet(name: str):
    return {"message": f"안녕하세요, {name}님!"}


# --- 테스트 (수정하지 마세요) ---
if __name__ == "__main__":
    client = TestClient(app)

    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "안녕하세요, FastAPI!"}
    print("✓ /hello 테스트 통과")

    response = client.get("/greet/홍길동")
    assert response.status_code == 200
    assert response.json() == {"message": "안녕하세요, 홍길동님!"}
    print("✓ /greet/{name} 테스트 통과")

    print("\n모든 테스트를 통과했습니다!")
