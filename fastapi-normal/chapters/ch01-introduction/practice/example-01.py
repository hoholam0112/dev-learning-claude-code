# 실행 방법: uvicorn example-01:app --reload
# FastAPI 기본 예제 - Hello World API

from fastapi import FastAPI

# FastAPI 애플리케이션 인스턴스 생성
# title과 description은 자동 문서화 페이지에 표시됩니다
app = FastAPI(title="첫 번째 FastAPI", description="Hello World API 예제")


@app.get("/")
def read_root():
    """루트 엔드포인트 - 환영 메시지를 반환합니다."""
    return {"message": "안녕하세요! FastAPI에 오신 것을 환영합니다."}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    """아이템 조회 엔드포인트

    - item_id: 경로 파라미터 (정수형으로 자동 변환)
    - q: 선택적 쿼리 파라미터

    사용 예시:
        GET /items/42
        GET /items/42?q=검색어
    """
    return {"item_id": item_id, "q": q}
