"""
sec03 모범 답안: 폼 데이터와 파일 업로드
실행: uvicorn solution:app --reload
테스트: python solution.py
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

@app.post("/login")
async def login(
    username: str = Form(
        ...,
        min_length=3,           # 최소 3자
        description="사용자명"
    ),
    password: str = Form(
        ...,
        min_length=6,           # 최소 6자
        description="비밀번호"
    )
):
    """
    로그인 폼 데이터를 처리합니다.

    Form()을 사용하면 application/x-www-form-urlencoded 또는
    multipart/form-data 형식의 요청을 받을 수 있습니다.

    HTML 폼의 <input name="username"> 값이
    여기서 username 매개변수로 전달됩니다.
    """
    return {
        "message": "로그인 성공",
        "username": username
    }


# ============================================================
# 문제 2: 파일 업로드 API
# ============================================================

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(
        ...,
        description="업로드할 파일"
    )
):
    """
    파일을 업로드하고 파일 정보를 반환합니다.

    UploadFile 객체의 주요 속성:
    - filename: 원본 파일명
    - content_type: MIME 타입 (예: text/plain, image/png)

    파일 내용은 비동기 read() 메서드로 읽습니다.
    """
    # 파일 전체 내용을 읽습니다
    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents)
    }


# ============================================================
# 문제 3: 게시글 생성 API (폼 + 파일)
# ============================================================

@app.post("/posts")
async def create_post(
    title: str = Form(
        ...,
        min_length=2,           # 최소 2자
        description="게시글 제목"
    ),
    content: str = Form(
        default="",             # 선택 필드, 기본값 빈 문자열
        description="게시글 내용"
    ),
    image: Optional[UploadFile] = File(
        default=None,           # 선택 필드, 기본값 None
        description="첨부 이미지 (선택)"
    )
):
    """
    게시글을 생성합니다. 이미지는 선택적으로 첨부할 수 있습니다.

    Form()과 File()은 같은 엔드포인트에서 함께 사용할 수 있습니다.
    둘 다 multipart/form-data 인코딩을 사용하기 때문입니다.

    주의: Form()과 Pydantic BaseModel은 같이 사용할 수 없습니다.
    (서로 다른 Content-Type을 기대하기 때문)
    """
    # 이미지 정보 처리
    image_filename = None
    image_size = 0

    if image is not None:
        # 이미지가 첨부된 경우에만 읽기
        image_contents = await image.read()
        image_filename = image.filename
        image_size = len(image_contents)

    return {
        "message": "게시글이 생성되었습니다",
        "post": {
            "title": title,
            "content": content,
            "image_filename": image_filename,
            "image_size": image_size
        }
    }


# ============================================================
# 테스트 코드
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
    fake_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
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
