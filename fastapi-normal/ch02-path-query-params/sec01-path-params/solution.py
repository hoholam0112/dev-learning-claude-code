# 섹션 01: 경로 매개변수 - 모범 답안
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

from enum import Enum
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


# ModelName Enum 클래스 정의
# - str과 Enum을 동시에 상속해야 FastAPI가 문자열로 올바르게 처리합니다
# - Swagger UI에서 드롭다운 목록으로 표시됩니다
class ModelName(str, Enum):
    """머신러닝 모델 이름을 정의하는 Enum"""
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


# GET /users/{user_id} 엔드포인트
# - 경로의 {user_id}와 함수 매개변수 이름이 동일해야 합니다
# - user_id: int 타입 힌트로 자동 타입 변환 및 검증이 수행됩니다
# - 문자열이 들어오면 422 에러가 자동으로 반환됩니다
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    """사용자 프로필을 조회합니다."""
    return {"user_id": user_id, "name": f"사용자_{user_id}"}


# GET /models/{model_name} 엔드포인트
# - model_name의 타입을 ModelName Enum으로 지정합니다
# - Enum에 정의되지 않은 값이 들어오면 422 에러가 반환됩니다
# - model_name.value로 실제 문자열 값에 접근합니다
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    """선택한 모델 정보를 반환합니다."""
    return {
        "model_name": model_name.value,
        "message": f"{model_name.value} 모델이 선택되었습니다",
    }


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
