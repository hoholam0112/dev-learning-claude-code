# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

from fastapi import FastAPI, HTTPException, status
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# 가상 데이터베이스
books_db = {
    1: {"id": 1, "title": "파이썬 기초", "author": "홍길동", "price": 25000},
    2: {"id": 2, "title": "FastAPI 입문", "author": "김철수", "price": 30000},
}
book_id_counter = 2


# ── Pydantic 모델 ──

class BookCreate(BaseModel):
    title: str
    author: str
    price: int


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    price: int


# TODO: GET /books/{book_id} 엔드포인트를 작성하세요
# - response_model=BookResponse
# - book_id가 books_db에 없으면 HTTPException 발생
#   - status_code=404
#   - detail=f"ID {book_id}인 도서를 찾을 수 없습니다"
# - 존재하면 해당 도서 반환


# TODO: POST /books 엔드포인트를 작성하세요
# - response_model=BookResponse
# - status_code=status.HTTP_201_CREATED
# - 같은 title의 도서가 이미 있으면 HTTPException 발생
#   - status_code=400
#   - detail=f"'{book.title}' 제목의 도서가 이미 존재합니다"
# - 성공 시 book_id_counter 증가, books_db에 저장, 반환


# TODO: DELETE /books/{book_id} 엔드포인트를 작성하세요
# - status_code=status.HTTP_204_NO_CONTENT
# - user_role: str 쿼리 매개변수를 받으세요 (기본값: "user")
# - book_id가 books_db에 없으면 404 에러
#   - detail="해당 도서를 찾을 수 없습니다"
# - user_role이 "admin"이 아니면 403 에러
#   - detail="도서 삭제 권한이 없습니다. 관리자만 삭제할 수 있습니다"
# - 성공 시 books_db에서 삭제 (아무것도 반환하지 않음)


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 1: 존재하는 도서 조회 (200 OK)
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json()["title"] == "파이썬 기초"
    print("✓ 도서 조회 성공 테스트 통과")

    # 테스트 2: 존재하지 않는 도서 조회 (404 Not Found)
    response = client.get("/books/999")
    assert response.status_code == 404
    assert "999" in response.json()["detail"]
    print("✓ 존재하지 않는 도서 조회 - 404 테스트 통과")

    # 테스트 3: 도서 등록 (201 Created)
    response = client.post("/books", json={
        "title": "Django 마스터",
        "author": "박영희",
        "price": 35000
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Django 마스터"
    assert "id" in data
    print("✓ 도서 등록 - 201 Created 테스트 통과")

    # 테스트 4: 중복 제목 등록 (400 Bad Request)
    response = client.post("/books", json={
        "title": "파이썬 기초",
        "author": "다른 저자",
        "price": 20000
    })
    assert response.status_code == 400
    assert "파이썬 기초" in response.json()["detail"]
    print("✓ 중복 제목 등록 - 400 Bad Request 테스트 통과")

    # 테스트 5: 관리자가 아닌 사용자의 삭제 시도 (403 Forbidden)
    response = client.delete("/books/1", params={"user_role": "user"})
    assert response.status_code == 403
    assert "권한" in response.json()["detail"]
    print("✓ 권한 없는 삭제 - 403 Forbidden 테스트 통과")

    # 테스트 6: 존재하지 않는 도서 삭제 (404 Not Found)
    response = client.delete("/books/999", params={"user_role": "admin"})
    assert response.status_code == 404
    print("✓ 존재하지 않는 도서 삭제 - 404 Not Found 테스트 통과")

    # 테스트 7: 관리자가 삭제 (204 No Content)
    response = client.delete("/books/1", params={"user_role": "admin"})
    assert response.status_code == 204
    assert response.content == b""
    print("✓ 관리자 삭제 - 204 No Content 테스트 통과")

    # 테스트 8: 삭제된 도서 조회 (404 Not Found)
    response = client.get("/books/1")
    assert response.status_code == 404
    print("✓ 삭제된 도서 조회 - 404 Not Found 테스트 통과")

    print("\n모든 테스트를 통과했습니다!")
