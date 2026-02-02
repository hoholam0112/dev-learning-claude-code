# 섹션 01: 경로 매개변수 - 연습 문제
# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from enum import Enum
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


# TODO: ModelName Enum 클래스를 정의하세요
# - str과 Enum을 동시에 상속해야 합니다
# - 멤버: alexnet = "alexnet", resnet = "resnet", lenet = "lenet"


# TODO: GET /users/{user_id} 엔드포인트를 작성하세요
# - user_id는 정수(int) 타입이어야 합니다
# - 반환값: {"user_id": user_id, "name": f"사용자_{user_id}"}


# TODO: GET /models/{model_name} 엔드포인트를 작성하세요
# - model_name은 ModelName Enum 타입이어야 합니다
# - 반환값: {"model_name": model_name.value, "message": f"{model_name.value} 모델이 선택되었습니다"}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 1: 사용자 프로필 조회
    response = client.get("/users/42")
    assert response.status_code == 200
    assert response.json() == {"user_id": 42, "name": "사용자_42"}
    print("통과: /users/{user_id} 정상 조회")

    # 테스트 2: 잘못된 타입 검증
    response = client.get("/users/abc")
    assert response.status_code == 422
    print("통과: 잘못된 타입(문자열) 검증")

    # 테스트 3: Enum 경로 매개변수
    response = client.get("/models/alexnet")
    assert response.status_code == 200
    assert response.json() == {
        "model_name": "alexnet",
        "message": "alexnet 모델이 선택되었습니다",
    }
    print("통과: /models/{model_name} 정상 조회")

    # 테스트 4: 잘못된 Enum 값 검증
    response = client.get("/models/invalid")
    assert response.status_code == 422
    print("통과: 잘못된 Enum 값 검증")

    print("\n모든 테스트를 통과했습니다!")
