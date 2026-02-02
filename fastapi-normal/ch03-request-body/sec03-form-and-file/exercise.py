"""
sec03 연습 문제: 폼 데이터와 파일 업로드
실행: uvicorn exercise:app --reload
테스트: python exercise.py
사전 설치: pip install python-multipart
"""

from fastapi import FastAPI, Form, File, UploadFile
from fastapi.testclient import TestClient
from typing import Optional
import io

app = FastAPI()


# ============================================================
# 문제 1: 로그인 폼 API
# ============================================================

# TODO: POST /login 엔드포인트를 작성하세요
# - username: str (Form, 필수, 최소 3자)
# - password: str (Form, 필수, 최소 6자)
# - 반환값: {"message": "로그인 성공", "username": 사용자명}


# ============================================================
# 문제 2: 파일 업로드 API
# ============================================================

# TODO: POST /upload 엔드포인트를 작성하세요
# - file: UploadFile (File, 필수)
# - 파일 내용을 읽어서 크기를 계산하세요 (contents = await file.read())
# - 반환값: {"filename": 파일명, "content_type": MIME타입, "size": 파일크기}


# ============================================================
# 문제 3: 게시글 생성 API (폼 + 파일)
# ============================================================

# TODO: POST /posts 엔드포인트를 작성하세요
# - title: str (Form, 필수, 최소 2자)
# - content: str (Form, 선택, 기본값 "")
# - image: Optional[UploadFile] (File, 선택, 기본값 None)
# - 반환값: {
#     "message": "게시글이 생성되었습니다",
#     "post": {
#         "title": 제목,
#         "content": 내용,
#         "image_filename": 파일명 또는 None,
#         "image_size": 파일크기 또는 0
#     }
# }


# ============================================================
# 테스트 코드 (수정하지 마세요)
# ============================================================
if __name__ == "__main__":
    client = TestClient(app)

    print("=" * 50)
    print("문제 1: 로그인 폼 API 테스트")
    print("=" * 50)

    # 테스트 1-1: 정상 로그인
    response = client.post("/login", data={
        "username": "hong",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "로그인 성공"
    assert data["username"] == "hong"
    print("[PASS] 정상 로그인 테스트 통과")

    # 테스트 1-2: 사용자명 너무 짧음
    response = client.post("/login", data={
        "username": "ab",
        "password": "secret123"
    })
    assert response.status_code == 422
    print("[PASS] 짧은 사용자명 검증 테스트 통과")

    # 테스트 1-3: 비밀번호 너무 짧음
    response = client.post("/login", data={
        "username": "hong",
        "password": "12345"
    })
    assert response.status_code == 422
    print("[PASS] 짧은 비밀번호 검증 테스트 통과")

    print()
    print("=" * 50)
    print("문제 2: 파일 업로드 API 테스트")
    print("=" * 50)

    # 테스트 2-1: 정상 파일 업로드
    test_content = b"Hello, FastAPI file upload test!"
    test_file = io.BytesIO(test_content)
    response = client.post("/upload", files={
        "file": ("test.txt", test_file, "text/plain")
    })
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["content_type"] == "text/plain"
    assert data["size"] == len(test_content)
    print(f"[PASS] 파일 업로드 테스트 통과 (크기: {data['size']}바이트)")

    # 테스트 2-2: 이미지 파일 업로드
    fake_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # 가짜 PNG 헤더
    image_file = io.BytesIO(fake_image)
    response = client.post("/upload", files={
        "file": ("photo.png", image_file, "image/png")
    })
    assert response.status_code == 200
    assert response.json()["filename"] == "photo.png"
    assert response.json()["content_type"] == "image/png"
    print("[PASS] 이미지 파일 업로드 테스트 통과")

    print()
    print("=" * 50)
    print("문제 3: 게시글 생성 API 테스트")
    print("=" * 50)

    # 테스트 3-1: 이미지 포함 게시글
    post_image = io.BytesIO(b"fake image data for post")
    response = client.post("/posts",
        data={"title": "첫 번째 게시글", "content": "게시글 내용입니다."},
        files={"image": ("post_image.jpg", post_image, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "게시글이 생성되었습니다"
    assert data["post"]["title"] == "첫 번째 게시글"
    assert data["post"]["content"] == "게시글 내용입니다."
    assert data["post"]["image_filename"] == "post_image.jpg"
    assert data["post"]["image_size"] > 0
    print("[PASS] 이미지 포함 게시글 테스트 통과")

    # 테스트 3-2: 이미지 없이 게시글
    response = client.post("/posts",
        data={"title": "텍스트만 있는 글"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["post"]["title"] == "텍스트만 있는 글"
    assert data["post"]["content"] == ""
    assert data["post"]["image_filename"] is None
    assert data["post"]["image_size"] == 0
    print("[PASS] 이미지 없는 게시글 테스트 통과")

    # 테스트 3-3: 제목 너무 짧음
    response = client.post("/posts",
        data={"title": "A"}
    )
    assert response.status_code == 422
    print("[PASS] 짧은 제목 검증 테스트 통과")

    print()
    print("=" * 50)
    print("모든 테스트를 통과했습니다!")
    print("=" * 50)
