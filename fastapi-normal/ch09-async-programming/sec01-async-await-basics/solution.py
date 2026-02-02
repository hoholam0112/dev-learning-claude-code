# 모범 답안: async/await 기본
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

import asyncio
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


# ============================================================
# 문제 1 해답: async def와 def 엔드포인트 비교
# ============================================================

@app.get("/sync")
def sync_endpoint():
    """동기 엔드포인트: 스레드 풀에서 실행됩니다."""
    return {"message": "동기 응답", "type": "sync"}


@app.get("/async")
async def async_endpoint():
    """비동기 엔드포인트: 이벤트 루프에서 직접 실행됩니다."""
    await asyncio.sleep(0)  # 이벤트 루프에 제어권 양보
    return {"message": "비동기 응답", "type": "async"}


# ============================================================
# 문제 2 해답: 비동기 데이터 처리
# ============================================================

async def process_item(item: str) -> dict:
    """아이템을 비동기적으로 처리하는 헬퍼 함수.

    await asyncio.sleep(0.1)으로 I/O 작업을 시뮬레이션합니다.
    """
    await asyncio.sleep(0.1)
    return {"item": item, "status": "processed"}


@app.get("/process")
async def process_items():
    """여러 아이템을 동시에 비동기 처리하는 엔드포인트.

    asyncio.gather를 사용하여 3개 아이템을 동시에 처리합니다.
    순차 실행 시 0.3초가 걸리지만, 동시 실행으로 약 0.1초만 소요됩니다.
    """
    items = ["아이템A", "아이템B", "아이템C"]
    start = time.time()

    # asyncio.gather로 모든 아이템을 동시에 처리
    results = await asyncio.gather(
        *[process_item(item) for item in items]
    )

    elapsed = time.time() - start
    return {
        "results": list(results),
        "elapsed_seconds": round(elapsed, 2),
    }


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 테스트: async def와 def 엔드포인트 비교
    print("=" * 50)
    print("문제 1: async def와 def 엔드포인트 비교")
    print("=" * 50)

    # 동기 엔드포인트 테스트
    response = client.get("/sync")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "동기 응답"
    assert data["type"] == "sync"
    print("  [통과] 동기 엔드포인트 - 200 응답")

    # 비동기 엔드포인트 테스트
    response = client.get("/async")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "비동기 응답"
    assert data["type"] == "async"
    print("  [통과] 비동기 엔드포인트 - 200 응답")

    # 문제 2 테스트: 비동기 데이터 처리
    print()
    print("=" * 50)
    print("문제 2: 비동기 데이터 처리")
    print("=" * 50)

    response = client.get("/process")
    assert response.status_code == 200
    data = response.json()

    # 결과 검증: 3개 아이템이 모두 처리되었는지 확인
    assert len(data["results"]) == 3
    assert data["results"][0]["item"] == "아이템A"
    assert data["results"][0]["status"] == "processed"
    assert data["results"][1]["item"] == "아이템B"
    assert data["results"][2]["item"] == "아이템C"
    print(f"  [통과] 3개 아이템 처리 완료: {data['results']}")

    # 시간 검증: 동시 처리이므로 0.5초 이내 완료
    assert data["elapsed_seconds"] < 0.5, (
        f"동시 처리인데 {data['elapsed_seconds']}초 걸림 (0.5초 이내여야 함)"
    )
    print(f"  [통과] 동시 처리로 {data['elapsed_seconds']}초 만에 완료 (0.5초 이내)")

    print()
    print("모든 테스트를 통과했습니다!")
