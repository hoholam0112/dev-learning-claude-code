# 실행 방법: uvicorn exercise:app --reload
# 필요 패키지: pip install fastapi uvicorn python-multipart
# 챕터 09 연습 문제 - 직접 코드를 작성해보세요!

import csv
import io
import os
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

# ── 설정 ───────────────────────────────────────────────────
UPLOAD_DIR = Path("uploads")
PROFILES_DIR = UPLOAD_DIR / "profiles"
ARTICLES_DIR = UPLOAD_DIR / "articles"

# 디렉토리 생성
for d in [UPLOAD_DIR, PROFILES_DIR, ARTICLES_DIR]:
    d.mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="챕터 09 연습 문제", description="파일 업로드 + 폼 데이터")

# ── 데이터 저장소 ──────────────────────────────────────────
user_profiles: dict[int, str] = {}
articles_db: dict[int, dict] = {}
next_article_id = 1


# ── 유틸리티 함수 ──────────────────────────────────────────
def save_file_to_disk(content: bytes, original_name: str, directory: Path) -> str:
    """파일을 지정된 디렉토리에 저장하고 저장된 파일명을 반환합니다."""
    ext = os.path.splitext(original_name)[1].lower()
    unique_name = f"{uuid.uuid4()}{ext}"
    file_path = directory / unique_name
    with open(file_path, "wb") as f:
        f.write(content)
    return unique_name


def format_size(size_bytes: int) -> str:
    """바이트를 읽기 쉬운 형식으로 변환합니다."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"


# ══════════════════════════════════════════════════════════
# 문제 1: 프로필 이미지 업로드
# POST /profile/image — 업로드 (user_id: Form, file: File)
# GET /profile/image/{user_id} — 다운로드
# DELETE /profile/image/{user_id} — 삭제 (204)
# 허용 형식: JPEG, PNG, WebP / 최대 3MB
# 기존 이미지가 있으면 삭제 후 교체
# ══════════════════════════════════════════════════════════


@app.post("/profile/image", tags=["프로필 이미지"])
async def upload_profile_image(
    user_id: int = Form(..., description="사용자 ID"),
    file: UploadFile = File(..., description="프로필 이미지"),
):
    """프로필 이미지를 업로드합니다."""
    # TODO: 구현하세요
    # 1. 파일 타입 검증 (ALLOWED_IMAGE_TYPES)
    # 2. 파일 내용 읽기 (await file.read())
    # 3. 파일 크기 검증 (3MB 제한)
    # 4. 기존 프로필 이미지 삭제
    # 5. 새 이미지 저장 (save_file_to_disk 사용)
    pass


@app.get("/profile/image/{user_id}", tags=["프로필 이미지"])
async def get_profile_image(user_id: int):
    """사용자의 프로필 이미지를 다운로드합니다."""
    # TODO: user_profiles에서 파일 경로를 찾아 FileResponse로 반환
    pass


@app.delete("/profile/image/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["프로필 이미지"])
async def delete_profile_image(user_id: int):
    """사용자의 프로필 이미지를 삭제합니다."""
    # TODO: 파일 삭제 및 user_profiles에서 제거
    pass


# ══════════════════════════════════════════════════════════
# 문제 2: CSV 파일 업로드 후 데이터 파싱
# POST /upload/csv — CSV 업로드 및 파싱
# 반환: 파일 정보, 컬럼 목록, 데이터 미리보기 (처음 5행)
# ══════════════════════════════════════════════════════════


@app.post("/upload/csv", tags=["CSV 파싱"])
async def upload_and_parse_csv(
    file: UploadFile = File(..., description="CSV 파일"),
):
    """CSV 파일을 업로드하고 내용을 파싱합니다."""
    # TODO: 구현하세요
    # 1. 파일 타입 검증 (.csv)
    # 2. 파일 읽기 및 크기 제한 (5MB)
    # 3. UTF-8 디코딩 (실패 시 EUC-KR 시도)
    # 4. csv.DictReader로 파싱
    # 5. 컬럼 목록, 행 수, 미리보기(5행) 반환
    pass


# ══════════════════════════════════════════════════════════
# 문제 3: 폼 기반 게시글 작성 (폼 데이터 + 파일 업로드)
# POST /articles — 게시글 작성 (폼 + 썸네일 + 첨부파일)
# GET /articles — 목록 조회
# GET /articles/{article_id} — 상세 조회
# DELETE /articles/{article_id} — 삭제 (204)
# ══════════════════════════════════════════════════════════


@app.post("/articles", status_code=status.HTTP_201_CREATED, tags=["게시글"])
async def create_article(
    title: str = Form(..., min_length=1, max_length=100),
    content: str = Form(..., min_length=1),
    author: str = Form(...),
    category: str = Form("general"),
    is_public: bool = Form(True),
    thumbnail: UploadFile | None = File(None, description="썸네일 이미지 (선택)"),
    attachments: list[UploadFile] = File(default=[], description="첨부파일 (최대 3개)"),
):
    """폼 데이터와 파일을 함께 받아 게시글을 작성합니다."""
    # TODO: 구현하세요
    # 1. 썸네일 처리 (이미지 타입 검증)
    # 2. 첨부파일 처리 (최대 3개, 각 10MB 제한)
    # 3. 게시글 저장
    pass


@app.get("/articles", tags=["게시글"])
async def list_articles(
    category: str | None = None,
    public_only: bool = True,
):
    """게시글 목록을 조회합니다."""
    # TODO: 카테고리/공개 여부 필터링 후 반환
    pass


@app.get("/articles/{article_id}", tags=["게시글"])
async def get_article(article_id: int):
    """특정 게시글의 상세 정보를 조회합니다."""
    # TODO: article_id로 조회, 없으면 404
    pass


@app.delete("/articles/{article_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["게시글"])
async def delete_article(article_id: int):
    """게시글과 관련 파일을 삭제합니다."""
    # TODO: 관련 파일 삭제 후 게시글 삭제
    pass
