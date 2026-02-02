# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

import asyncio
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

app = FastAPI()


# ============================================================
# 데이터 소스 엔드포인트 (수정하지 마세요)
# ============================================================

@app.get("/source/users")
async def source_users():
    """사용자 데이터 소스 (0.3초 소요)"""
    await asyncio.sleep(0.3)
    return {"source": "users", "items": ["홍길동", "김영희", "이철수"]}


@app.get("/source/products")
async def source_products():
    """상품 데이터 소스 (0.2초 소요)"""
    await asyncio.sleep(0.2)
    return {"source": "products", "items": ["노트북", "마우스", "키보드"]}


@app.get("/source/orders")
async def source_orders():
    """주문 데이터 소스 (0.4초 소요)"""
    await asyncio.sleep(0.4)
    return {"source": "orders", "items": ["주문001", "주문002"]}


# ============================================================
# 문제 1: 동시 데이터 수집 시뮬레이션
# ============================================================

# TODO: fetch_source 비동기 헬퍼 함수를 작성하세요
# - async def fetch_source(source_name: str, delay: float) -> dict:
# - await asyncio.sleep(delay)로 I/O 시뮬레이션
# - source_name에 따른 데이터 반환:
#   "users" → ["홍길동", "김영희", "이철수"]
#   "products" → ["노트북", "마우스", "키보드"]
#   "orders" → ["주문001", "주문002"]
# - 반환값: {"source": source_name, "items": [해당 데이터]}
#
# 힌트: 딕셔너리로 source_name별 데이터를 매핑하면 편리합니다
# source_data = {
#     "users": ["홍길동", "김영희", "이철수"],
#     "products": ["노트북", "마우스", "키보드"],
#     "orders": ["주문001", "주문002"],
# }


# TODO: GET /aggregate 동시 수집 엔드포인트를 작성하세요
# - time.time()으로 시작 시간 기록
# - asyncio.gather로 3개 소스를 동시에 호출:
#   fetch_source("users", 0.3)
#   fetch_source("products", 0.2)
#   fetch_source("orders", 0.4)
# - 소요 시간 계산
# - 반환값: {
#     "users": users 결과,
#     "products": products 결과,
#     "orders": orders 결과,
#     "elapsed_seconds": round(elapsed, 2)
#   }


# ============================================================
# 문제 2: 비동기 배치 처리
# ============================================================

class BatchRequest(BaseModel):
    item_ids: list[int]


# TODO: process_single_item 비동기 헬퍼 함수를 작성하세요
# - async def process_single_item(item_id: int) -> dict:
# - await asyncio.sleep(0.1)으로 처리 시뮬레이션
# - 반환값: {"item_id": item_id, "result": f"processed_{item_id}"}


# TODO: POST /batch 배치 처리 엔드포인트를 작성하세요
# - 매개변수: request (BatchRequest)
# - time.time()으로 시작 시간 기록
# - asyncio.gather로 모든 아이템을 동시에 처리
#   힌트: tasks = [process_single_item(id) for id in request.item_ids]
#         results = await asyncio.gather(*tasks)
# - 반환값: {
#     "results": list(results),
#     "total_processed": len(results),
#     "elapsed_seconds": round(elapsed, 2)
#   }


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 테스트: 동시 데이터 수집 시뮬레이션
    print("=" * 50)
    print("문제 1: 동시 데이터 수집 시뮬레이션")
    print("=" * 50)

    # 개별 소스 엔드포인트 테스트
    response = client.get("/source/users")
    assert response.status_code == 200
    assert response.json()["source"] == "users"
    assert len(response.json()["items"]) == 3

    response = client.get("/source/products")
    assert response.status_code == 200
    assert response.json()["source"] == "products"

    response = client.get("/source/orders")
    assert response.status_code == 200
    assert response.json()["source"] == "orders"
    print("  [통과] 개별 소스 엔드포인트 동작 확인")

    # 동시 수집 엔드포인트 테스트
    response = client.get("/aggregate")
    assert response.status_code == 200, (
        "GET /aggregate 엔드포인트가 없습니다. 동시 수집 엔드포인트를 작성하세요."
    )
    data = response.json()

    # 데이터 검증
    assert data["users"]["source"] == "users", (
        f"users 소스 이름이 'users'여야 합니다. 현재: {data['users'].get('source')}"
    )
    assert data["users"]["items"] == ["홍길동", "김영희", "이철수"], (
        f"users 데이터가 올바르지 않습니다. 현재: {data['users'].get('items')}"
    )
    assert data["products"]["source"] == "products"
    assert data["products"]["items"] == ["노트북", "마우스", "키보드"]
    assert data["orders"]["source"] == "orders"
    assert data["orders"]["items"] == ["주문001", "주문002"]
    print(f"  [통과] 동시 수집 완료 - 3개 소스")

    # 시간 검증: 동시 실행이므로 0.8초 이내 (순차면 0.9초 이상)
    assert data["elapsed_seconds"] < 0.8, (
        f"동시 실행인데 {data['elapsed_seconds']}초 걸림 (0.8초 이내여야 함). "
        "asyncio.gather를 사용했는지 확인하세요."
    )
    print(f"  [통과] 동시 실행으로 {data['elapsed_seconds']}초 만에 완료 (0.8초 이내)")

    # 문제 2 테스트: 비동기 배치 처리
    print()
    print("=" * 50)
    print("문제 2: 비동기 배치 처리")
    print("=" * 50)

    response = client.post("/batch", json={"item_ids": [1, 2, 3, 4, 5]})
    assert response.status_code == 200, (
        "POST /batch 엔드포인트가 없습니다. 배치 처리 엔드포인트를 작성하세요."
    )
    data = response.json()

    # 결과 검증
    assert data["total_processed"] == 5, (
        f"total_processed가 5여야 합니다. 현재: {data.get('total_processed')}"
    )
    assert len(data["results"]) == 5, (
        f"results에 5개 결과가 있어야 합니다. 현재: {len(data.get('results', []))}개"
    )
    assert data["results"][0]["item_id"] == 1, (
        f"첫 번째 결과의 item_id가 1이어야 합니다. 현재: {data['results'][0].get('item_id')}"
    )
    assert data["results"][0]["result"] == "processed_1", (
        f"첫 번째 결과의 result가 'processed_1'이어야 합니다. 현재: {data['results'][0].get('result')}"
    )
    assert data["results"][4]["item_id"] == 5
    assert data["results"][4]["result"] == "processed_5"
    print(f"  [통과] 5개 아이템 배치 처리 완료")

    # 시간 검증: 동시 처리이므로 0.5초 이내
    assert data["elapsed_seconds"] < 0.5, (
        f"동시 처리인데 {data['elapsed_seconds']}초 걸림 (0.5초 이내여야 함). "
        "asyncio.gather를 사용했는지 확인하세요."
    )
    print(f"  [통과] 동시 처리로 {data['elapsed_seconds']}초 만에 완료 (0.5초 이내)")

    print()
    print("모든 테스트를 통과했습니다!")
