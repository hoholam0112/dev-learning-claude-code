# 모범 답안: 비동기 I/O 작업
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

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
# 문제 1 해답: 동시 데이터 수집 시뮬레이션
# ============================================================

async def fetch_source(source_name: str, delay: float) -> dict:
    """외부 데이터 소스에서 데이터를 가져오는 시뮬레이션.

    asyncio.sleep으로 I/O 작업을 시뮬레이션합니다.
    실제 환경에서는 httpx.AsyncClient로 외부 API를 호출합니다.
    """
    await asyncio.sleep(delay)
    source_data = {
        "users": ["홍길동", "김영희", "이철수"],
        "products": ["노트북", "마우스", "키보드"],
        "orders": ["주문001", "주문002"],
    }
    return {"source": source_name, "items": source_data[source_name]}


@app.get("/aggregate")
async def aggregate_data():
    """여러 데이터 소스에서 동시에 데이터를 수집하는 엔드포인트.

    asyncio.gather를 사용하여 3개 소스를 동시에 호출합니다.
    순차 실행 시 0.9초(0.3+0.2+0.4)가 걸리지만,
    동시 실행으로 약 0.4초(가장 긴 작업 기준)만 소요됩니다.
    """
    start = time.time()

    # asyncio.gather로 3개 소스를 동시에 호출
    users, products, orders = await asyncio.gather(
        fetch_source("users", 0.3),
        fetch_source("products", 0.2),
        fetch_source("orders", 0.4),
    )

    elapsed = time.time() - start
    return {
        "users": users,
        "products": products,
        "orders": orders,
        "elapsed_seconds": round(elapsed, 2),
    }


# ============================================================
# 문제 2 해답: 비동기 배치 처리
# ============================================================

class BatchRequest(BaseModel):
    item_ids: list[int]


async def process_single_item(item_id: int) -> dict:
    """단일 아이템을 비동기적으로 처리하는 헬퍼 함수.

    asyncio.sleep(0.1)으로 I/O 작업을 시뮬레이션합니다.
    """
    await asyncio.sleep(0.1)
    return {"item_id": item_id, "result": f"processed_{item_id}"}


@app.post("/batch")
async def batch_process(request: BatchRequest):
    """여러 아이템을 동시에 처리하는 배치 엔드포인트.

    asyncio.gather를 사용하여 모든 아이템을 동시에 처리합니다.
    5개 아이템 처리 시 순차 0.5초 → 동시 약 0.1초로 단축됩니다.
    """
    start = time.time()

    # 모든 아이템을 동시에 처리
    tasks = [process_single_item(item_id) for item_id in request.item_ids]
    results = await asyncio.gather(*tasks)

    elapsed = time.time() - start
    return {
        "results": list(results),
        "total_processed": len(results),
        "elapsed_seconds": round(elapsed, 2),
    }


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
    assert response.status_code == 200
    data = response.json()

    # 데이터 검증
    assert data["users"]["source"] == "users"
    assert data["users"]["items"] == ["홍길동", "김영희", "이철수"]
    assert data["products"]["source"] == "products"
    assert data["products"]["items"] == ["노트북", "마우스", "키보드"]
    assert data["orders"]["source"] == "orders"
    assert data["orders"]["items"] == ["주문001", "주문002"]
    print(f"  [통과] 동시 수집 완료 - 3개 소스")

    # 시간 검증: 동시 실행이므로 0.8초 이내 (순차면 0.9초 이상)
    assert data["elapsed_seconds"] < 0.8, (
        f"동시 실행인데 {data['elapsed_seconds']}초 걸림 (0.8초 이내여야 함)"
    )
    print(f"  [통과] 동시 실행으로 {data['elapsed_seconds']}초 만에 완료 (0.8초 이내)")

    # 문제 2 테스트: 비동기 배치 처리
    print()
    print("=" * 50)
    print("문제 2: 비동기 배치 처리")
    print("=" * 50)

    response = client.post("/batch", json={"item_ids": [1, 2, 3, 4, 5]})
    assert response.status_code == 200
    data = response.json()

    # 결과 검증
    assert data["total_processed"] == 5
    assert len(data["results"]) == 5
    assert data["results"][0]["item_id"] == 1
    assert data["results"][0]["result"] == "processed_1"
    assert data["results"][4]["item_id"] == 5
    assert data["results"][4]["result"] == "processed_5"
    print(f"  [통과] 5개 아이템 배치 처리 완료")

    # 시간 검증: 동시 처리이므로 0.5초 이내
    assert data["elapsed_seconds"] < 0.5, (
        f"동시 처리인데 {data['elapsed_seconds']}초 걸림 (0.5초 이내여야 함)"
    )
    print(f"  [통과] 동시 처리로 {data['elapsed_seconds']}초 만에 완료 (0.5초 이내)")

    print()
    print("모든 테스트를 통과했습니다!")
