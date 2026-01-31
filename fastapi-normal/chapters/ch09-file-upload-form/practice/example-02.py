# 실행 방법: uvicorn example-02:app --reload
# 필요 패키지: pip install fastapi uvicorn python-multipart
# 테스트: http://127.0.0.1:8000/docs 에서 Swagger UI로 테스트

"""
챕터 09 예제 02: 폼 데이터 + 파일 동시 처리

이 예제에서는 다음을 학습합니다:
- Form() 필드와 UploadFile을 함께 사용
- 폼 기반 사용자 등록 (프로필 이미지 포함)
- 폼 기반 게시글 작성 (첨부파일 포함)
"""

import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

# ── 설정 ───────────────────────────────────────────────────
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ── 앱 초기화 ──────────────────────────────────────────────
app = FastAPI(
    title="폼 데이터 + 파일 처리 예제",
    description="폼 필드와 파일 업로드를 동시에 처리하는 예제",
)


# ── 임시 데이터 저장소 ─────────────────────────────────────
users_db: dict[int, dict] = {}
posts_db: dict[int, dict] = {}
next_user_id = 1
next_post_id = 1


# ── 유틸리티 함수 ──────────────────────────────────────────
def save_file(content: bytes, original_name: str, subdirectory: str = "") -> str:
    """파일을 저장하고 저장된 파일명을 반환합니다."""
    save_dir = UPLOAD_DIR / subdirectory if subdirectory else UPLOAD_DIR
    save_dir.mkdir(exist_ok=True)

    ext = os.path.splitext(original_name)[1].lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = save_dir / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    return unique_name


# ── 엔드포인트: 기본 폼 처리 ──────────────────────────────

@app.post("/login", summary="폼 기반 로그인")
async def login_form(
    username: str = Form(..., min_length=3, description="사용자명"),
    password: str = Form(..., min_length=6, description="비밀번호"),
    remember_me: bool = Form(False, description="로그인 상태 유지"),
):
    """
    폼 데이터로 로그인합니다.
    Content-Type: application/x-www-form-urlencoded
    """
    # 실제로는 DB에서 사용자를 확인해야 합니다
    return {
        "message": f"{username}님, 로그인에 성공했습니다",
        "remember_me": remember_me,
    }


@app.post("/contact", summary="문의 폼 제출")
async def contact_form(
    name: str = Form(..., description="이름"),
    email: str = Form(..., description="이메일"),
    subject: str = Form(..., description="제목"),
    message: str = Form(..., description="문의 내용"),
    category: str = Form("general", description="문의 카테고리"),
):
    """문의 폼을 제출합니다."""
    return {
        "message": "문의가 접수되었습니다",
        "inquiry": {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "category": category,
            "submitted_at": datetime.utcnow().isoformat(),
        },
    }


# ── 엔드포인트: 폼 + 파일 동시 처리 ──────────────────────

@app.post("/register", summary="회원가입 (프로필 이미지 포함)")
async def register_with_profile(
    username: str = Form(..., min_length=3, max_length=20, description="사용자명"),
    email: str = Form(..., description="이메일"),
    password: str = Form(..., min_length=8, description="비밀번호 (8자 이상)"),
    bio: str = Form("", max_length=200, description="자기소개"),
    profile_image: UploadFile | None = File(None, description="프로필 이미지 (선택)"),
):
    """
    폼 데이터와 프로필 이미지를 함께 받아 회원가입을 처리합니다.
    프로필 이미지는 선택 사항입니다.

    주의: Form()과 UploadFile을 함께 사용할 때는
    Content-Type이 multipart/form-data여야 합니다.
    """
    global next_user_id

    # 프로필 이미지 처리 (선택 사항)
    profile_image_name = None
    if profile_image and profile_image.filename:
        # 이미지 타입 검증
        allowed_types = {"image/jpeg", "image/png", "image/webp"}
        if profile_image.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"프로필 이미지는 JPEG, PNG, WebP만 허용됩니다. "
                       f"업로드된 형식: {profile_image.content_type}",
            )

        content = await profile_image.read()

        # 크기 제한 (2MB)
        if len(content) > 2 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="프로필 이미지는 2MB 이하여야 합니다",
            )

        profile_image_name = save_file(content, profile_image.filename, "profiles")

    # 사용자 저장
    user = {
        "id": next_user_id,
        "username": username,
        "email": email,
        "bio": bio,
        "profile_image": profile_image_name,
        "created_at": datetime.utcnow().isoformat(),
    }
    users_db[next_user_id] = user
    next_user_id += 1

    return {
        "message": "회원가입이 완료되었습니다",
        "user": user,
    }


@app.post("/posts", summary="게시글 작성 (첨부파일 포함)")
async def create_post_with_attachments(
    title: str = Form(..., min_length=1, max_length=100, description="제목"),
    content: str = Form(..., min_length=1, description="본문"),
    category: str = Form("general", description="카테고리"),
    tags: str = Form("", description="태그 (쉼표로 구분)"),
    attachments: list[UploadFile] = File(
        default=[], description="첨부파일 (최대 5개)"
    ),
):
    """
    폼 데이터와 여러 첨부파일을 함께 받아 게시글을 작성합니다.
    첨부파일은 선택 사항이며, 최대 5개까지 업로드 가능합니다.
    """
    global next_post_id

    # 첨부파일 개수 제한
    valid_attachments = [f for f in attachments if f.filename]
    if len(valid_attachments) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="첨부파일은 최대 5개까지 업로드할 수 있습니다",
        )

    # 첨부파일 처리
    saved_files = []
    for file in valid_attachments:
        file_content = await file.read()

        # 파일당 크기 제한 (10MB)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"파일 '{file.filename}'의 크기가 10MB를 초과합니다",
            )

        saved_name = save_file(file_content, file.filename, "attachments")
        saved_files.append({
            "original_name": file.filename,
            "saved_name": saved_name,
            "content_type": file.content_type,
            "size": len(file_content),
        })

    # 태그 파싱
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []

    # 게시글 저장
    post = {
        "id": next_post_id,
        "title": title,
        "content": content,
        "category": category,
        "tags": tag_list,
        "attachments": saved_files,
        "created_at": datetime.utcnow().isoformat(),
    }
    posts_db[next_post_id] = post
    next_post_id += 1

    return {
        "message": "게시글이 작성되었습니다",
        "post": post,
    }


@app.get("/posts", summary="게시글 목록 조회")
async def list_posts():
    """저장된 게시글 목록을 반환합니다."""
    return {
        "total": len(posts_db),
        "posts": list(posts_db.values()),
    }


@app.get("/users", summary="사용자 목록 조회")
async def list_users():
    """등록된 사용자 목록을 반환합니다."""
    return {
        "total": len(users_db),
        "users": list(users_db.values()),
    }


@app.post("/feedback", summary="피드백 제출 (스크린샷 포함)")
async def submit_feedback(
    title: str = Form(..., description="피드백 제목"),
    description: str = Form(..., description="피드백 설명"),
    severity: str = Form("low", description="심각도 (low/medium/high)"),
    screenshot: UploadFile | None = File(None, description="스크린샷 (선택)"),
):
    """
    사용자 피드백을 제출합니다.
    선택적으로 스크린샷을 첨부할 수 있습니다.
    """
    screenshot_info = None
    if screenshot and screenshot.filename:
        content = await screenshot.read()
        saved_name = save_file(content, screenshot.filename, "feedback")
        screenshot_info = {
            "original_name": screenshot.filename,
            "saved_name": saved_name,
            "size": len(content),
        }

    return {
        "message": "피드백이 접수되었습니다. 감사합니다!",
        "feedback": {
            "title": title,
            "description": description,
            "severity": severity,
            "screenshot": screenshot_info,
            "submitted_at": datetime.utcnow().isoformat(),
        },
    }
