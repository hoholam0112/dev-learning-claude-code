# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn python-multipart

"""
챕터 09 모범 답안: 파일 업로드와 폼 데이터

문제 1~3의 통합 솔루션입니다.
프로필 이미지 업로드 + CSV 파싱 + 게시글 작성을 포함합니다.
"""

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
app = FastAPI(title="챕터 09 종합 솔루션", description="파일 업로드 + 폼 데이터 종합 예제")

# ── 데이터 저장소 ──────────────────────────────────────────
# 사용자별 프로필 이미지 매핑
user_profiles: dict[int, str] = {}
# 게시글 저장
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


def guess_column_type(values: list[str]) -> str:
    """컬럼의 데이터 타입을 추정합니다."""
    # 비어있는 값 제외
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return "text"

    # 정수 확인
    try:
        for v in non_empty:
            int(v)
        return "integer"
    except ValueError:
        pass

    # 실수 확인
    try:
        for v in non_empty:
            float(v)
        return "float"
    except ValueError:
        pass

    # 불리언 확인
    bool_values = {"true", "false", "yes", "no", "1", "0"}
    if all(v.lower() in bool_values for v in non_empty):
        return "boolean"

    return "text"


# ══════════════════════════════════════════════════════════
# 문제 1: 프로필 이미지 업로드
# ══════════════════════════════════════════════════════════

@app.post("/profile/image", tags=["프로필 이미지"], summary="프로필 이미지 업로드")
async def upload_profile_image(
    user_id: int = Form(..., description="사용자 ID"),
    file: UploadFile = File(..., description="프로필 이미지"),
):
    """
    프로필 이미지를 업로드합니다.
    허용 형식: JPEG, PNG, WebP
    최대 크기: 3MB
    기존 이미지가 있으면 삭제 후 교체합니다.
    """
    # 1. 파일 타입 검증
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="허용되지 않는 파일 형식입니다. JPEG, PNG, WebP만 업로드 가능합니다.",
        )

    # 2. 파일 내용 읽기
    content = await file.read()

    # 3. 파일 크기 검증 (3MB)
    max_size = 3 * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"파일 크기가 3MB를 초과합니다. 현재 크기: {format_size(len(content))}",
        )

    # 4. 기존 프로필 이미지 삭제
    if user_id in user_profiles:
        old_file = PROFILES_DIR / user_profiles[user_id]
        if old_file.exists():
            old_file.unlink()

    # 5. 새 이미지 저장
    saved_name = save_file_to_disk(content, file.filename, PROFILES_DIR)
    user_profiles[user_id] = saved_name

    return {
        "message": "프로필 이미지가 업로드되었습니다",
        "image": {
            "original_name": file.filename,
            "saved_name": saved_name,
            "content_type": file.content_type,
            "size_kb": round(len(content) / 1024, 1),
        },
    }


@app.get("/profile/image/{user_id}", tags=["프로필 이미지"], summary="프로필 이미지 다운로드")
async def get_profile_image(user_id: int):
    """사용자의 프로필 이미지를 다운로드합니다."""
    if user_id not in user_profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 사용자의 프로필 이미지가 없습니다",
        )

    file_path = PROFILES_DIR / user_profiles[user_id]
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="프로필 이미지 파일을 찾을 수 없습니다",
        )

    return FileResponse(path=str(file_path))


@app.delete(
    "/profile/image/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["프로필 이미지"],
    summary="프로필 이미지 삭제",
)
async def delete_profile_image(user_id: int):
    """사용자의 프로필 이미지를 삭제합니다."""
    if user_id not in user_profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 사용자의 프로필 이미지가 없습니다",
        )

    file_path = PROFILES_DIR / user_profiles[user_id]
    if file_path.exists():
        file_path.unlink()

    del user_profiles[user_id]


# ══════════════════════════════════════════════════════════
# 문제 2: CSV 파일 업로드 후 데이터 파싱
# ══════════════════════════════════════════════════════════

@app.post("/upload/csv", tags=["CSV 파싱"], summary="CSV 파일 업로드 및 파싱")
async def upload_and_parse_csv(
    file: UploadFile = File(..., description="CSV 파일"),
):
    """
    CSV 파일을 업로드하고 내용을 파싱합니다.
    파일 정보, 컬럼 목록, 데이터 미리보기를 반환합니다.
    """
    # 1. 파일 타입 검증
    is_csv = (
        file.content_type == "text/csv"
        or (file.filename and file.filename.lower().endswith(".csv"))
    )
    if not is_csv:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV 파일만 업로드 가능합니다 (.csv)",
        )

    # 2. 파일 읽기
    content = await file.read()

    # 3. 크기 제한 (5MB)
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="파일 크기가 5MB를 초과합니다",
        )

    # 4. CSV 파싱
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        # UTF-8 실패 시 EUC-KR 시도 (한국어 CSV 대응)
        try:
            text = content.decode("euc-kr")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="파일 인코딩을 인식할 수 없습니다. UTF-8 또는 EUC-KR 형식이어야 합니다.",
            )

    reader = csv.DictReader(io.StringIO(text))

    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV 파일에 컬럼 헤더가 없습니다",
        )

    columns = list(reader.fieldnames)

    # 5. 모든 행 읽기
    rows = list(reader)
    total_rows = len(rows)

    # 6. 컬럼 타입 추정
    column_types = {}
    for col in columns:
        col_values = [row.get(col, "") for row in rows]
        column_types[col] = guess_column_type(col_values)

    # 7. 미리보기 (처음 5행)
    preview = rows[:5]

    return {
        "filename": file.filename,
        "file_size": format_size(len(content)),
        "total_rows": total_rows,
        "columns": columns,
        "column_count": len(columns),
        "column_types": column_types,
        "preview": preview,
    }


# ══════════════════════════════════════════════════════════
# 문제 3: 폼 기반 게시글 작성
# ══════════════════════════════════════════════════════════

@app.post(
    "/articles",
    status_code=status.HTTP_201_CREATED,
    tags=["게시글"],
    summary="게시글 작성 (폼 + 첨부파일)",
)
async def create_article(
    title: str = Form(..., min_length=1, max_length=100, description="제목"),
    content: str = Form(..., min_length=1, description="본문"),
    author: str = Form(..., description="작성자"),
    category: str = Form("general", description="카테고리"),
    is_public: bool = Form(True, description="공개 여부"),
    thumbnail: UploadFile | None = File(None, description="썸네일 이미지 (선택)"),
    attachments: list[UploadFile] = File(default=[], description="첨부파일 (최대 3개)"),
):
    """
    폼 데이터와 파일을 함께 받아 게시글을 작성합니다.

    - 썸네일: 이미지 파일 1개 (선택)
    - 첨부파일: 최대 3개 (선택)
    """
    global next_article_id

    # 게시글용 디렉토리 생성
    article_dir = ARTICLES_DIR / str(next_article_id)
    article_dir.mkdir(exist_ok=True)

    # 1. 썸네일 처리
    thumbnail_name = None
    if thumbnail and thumbnail.filename:
        if thumbnail.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="썸네일은 JPEG, PNG, WebP 형식만 허용됩니다",
            )
        thumb_content = await thumbnail.read()
        thumbnail_name = save_file_to_disk(thumb_content, thumbnail.filename, article_dir)

    # 2. 첨부파일 처리
    valid_attachments = [f for f in attachments if f.filename]
    if len(valid_attachments) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="첨부파일은 최대 3개까지 업로드할 수 있습니다",
        )

    saved_attachments = []
    for att in valid_attachments:
        att_content = await att.read()

        # 파일 크기 제한 (10MB)
        if len(att_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"파일 '{att.filename}'의 크기가 10MB를 초과합니다",
            )

        saved_name = save_file_to_disk(att_content, att.filename, article_dir)
        saved_attachments.append({
            "name": att.filename,
            "saved_name": saved_name,
            "size": len(att_content),
            "size_formatted": format_size(len(att_content)),
            "content_type": att.content_type,
        })

    # 3. 게시글 저장
    article = {
        "id": next_article_id,
        "title": title,
        "content": content,
        "author": author,
        "category": category,
        "is_public": is_public,
        "thumbnail": thumbnail_name,
        "attachments": saved_attachments,
        "created_at": datetime.utcnow().isoformat(),
    }
    articles_db[next_article_id] = article
    next_article_id += 1

    return {
        "message": "게시글이 작성되었습니다",
        "article": article,
    }


@app.get("/articles", tags=["게시글"], summary="게시글 목록 조회")
async def list_articles(
    category: str | None = None,
    public_only: bool = True,
):
    """
    게시글 목록을 조회합니다.
    카테고리와 공개 여부로 필터링할 수 있습니다.
    """
    articles = list(articles_db.values())

    # 필터링
    if public_only:
        articles = [a for a in articles if a["is_public"]]
    if category:
        articles = [a for a in articles if a["category"] == category]

    # 목록용으로 본문을 줄여서 반환
    result = []
    for article in articles:
        summary = {**article}
        # 본문은 100자까지만 표시
        if len(summary["content"]) > 100:
            summary["content"] = summary["content"][:100] + "..."
        result.append(summary)

    return {"total": len(result), "articles": result}


@app.get("/articles/{article_id}", tags=["게시글"], summary="게시글 상세 조회")
async def get_article(article_id: int):
    """특정 게시글의 상세 정보를 조회합니다."""
    if article_id not in articles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )
    return articles_db[article_id]


@app.delete(
    "/articles/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["게시글"],
    summary="게시글 삭제",
)
async def delete_article(article_id: int):
    """게시글과 관련 파일을 삭제합니다."""
    if article_id not in articles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )

    # 관련 파일 삭제
    article_dir = ARTICLES_DIR / str(article_id)
    if article_dir.exists():
        for file in article_dir.iterdir():
            file.unlink()
        article_dir.rmdir()

    del articles_db[article_id]
