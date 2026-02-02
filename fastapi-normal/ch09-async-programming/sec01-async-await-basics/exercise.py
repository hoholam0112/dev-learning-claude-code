# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

import asyncio
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()


# ============================================================
# 문제 1: async def와 def 엔드포인트 비교
# ============================================================

# TODO: GET /sync 동기 엔드포인트를 작성하세요
# - 일반 def로 정의
# - 반환값: {"message": "동기 응답", "type": "sync"}


# TODO: GET /async 비동기 엔드포인트를 작성하세요
# - async def로 정의
# - await asyncio.sleep(0)을 호출
# - 반환값: {"message": "비동기 응답", "type": "async"}


# ============================================================
# 문제 2: 비동기 데이터 처리
# ============================================================

# TODO: process_item 비동기 헬퍼 함수를 작성하세요
# - async def process_item(item: str) -> dict:
# - await asyncio.sleep(0.1)으로 I/O 작업 시뮬레이션
# - 반환값: {"item": item, "status": "processed"}


# TODO: GET /process 비동기 엔드포인트를 작성하세요
# - items = ["아이템A", "아이템B", "아이템C"]
# - time.time()으로 시작 시간 기록
# - asyncio.gather를 사용하여 모든 아이템을 동시에 처리
#   힌트: results = await asyncio.gather(*[process_item(item) for item in items])
# - 소요 시간 계산: elapsed = time.time() - start
# - 반환값: {"results": list(results), "elapsed_seconds": round(elapsed, 2)}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 문제 1 테스트: async def와 def 엔드포인트 비교
    print("=" * 50)
    print("문제 1: async def와 def 엔드포인트 비교")
    print("=" * 50)

    # 동기 엔드포인트 테스트
    response = client.get("/sync")
    assert response.status_code == 200, (
        "GET /sync 엔드포인트가 없습니다. 동기 엔드포인트를 작성하세요."
    )
    data = response.json()
    assert data["message"] == "동기 응답", (
        f"message가 '동기 응답'이어야 합니다. 현재: {data.get('message')}"
    )
    assert data["type"] == "sync", (
        f"type이 'sync'이어야 합니다. 현재: {data.get('type')}"
    )
    print("  [통과] 동기 엔드포인트 - 200 응답")

    # 비동기 엔드포인트 테스트
    response = client.get("/async")
    assert response.status_code == 200, (
        "GET /async 엔드포인트가 없습니다. 비동기 엔드포인트를 작성하세요."
    )
    data = response.json()
    assert data["message"] == "비동기 응답", (
        f"message가 '비동기 응답'이어야 합니다. 현재: {data.get('message')}"
    )
    assert data["type"] == "async", (
        f"type이 'async'이어야 합니다. 현재: {data.get('type')}"
    )
    print("  [통과] 비동기 엔드포인트 - 200 응답")

    # 문제 2 테스트: 비동기 데이터 처리
    print()
    print("=" * 50)
    print("문제 2: 비동기 데이터 처리")
    print("=" * 50)

    response = client.get("/process")
    assert response.status_code == 200, (
        "GET /process 엔드포인트가 없습니다. 비동기 데이터 처리 엔드포인트를 작성하세요."
    )
    data = response.json()

    # 결과 검증: 3개 아이템이 모두 처리되었는지 확인
    assert len(data["results"]) == 3, (
        f"results에 3개의 아이템이 있어야 합니다. 현재: {len(data['results'])}개"
    )
    assert data["results"][0]["item"] == "아이템A", (
        f"첫 번째 아이템이 '아이템A'여야 합니다. 현재: {data['results'][0].get('item')}"
    )
    assert data["results"][0]["status"] == "processed", (
        f"status가 'processed'여야 합니다. 현재: {data['results'][0].get('status')}"
    )
    assert data["results"][1]["item"] == "아이템B"
    assert data["results"][2]["item"] == "아이템C"
    print(f"  [통과] 3개 아이템 처리 완료: {data['results']}")

    # 시간 검증: 동시 처리이므로 0.5초 이내 완료
    assert data["elapsed_seconds"] < 0.5, (
        f"동시 처리인데 {data['elapsed_seconds']}초 걸림 (0.5초 이내여야 함). "
        "asyncio.gather를 사용했는지 확인하세요."
    )
    print(f"  [통과] 동시 처리로 {data['elapsed_seconds']}초 만에 완료 (0.5초 이내)")

    print()
    print("모든 테스트를 통과했습니다!")
