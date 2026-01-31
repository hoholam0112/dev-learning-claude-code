# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn python-multipart
# 테스트: http://127.0.0.1:8000/docs 에서 Swagger UI로 파일 업로드 테스트

"""
챕터 09 예제 01: 단일/다중 파일 업로드

이 예제에서는 다음을 학습합니다:
- 단일 파일 업로드
- 다중 파일 업로드
- 파일 크기/타입 검증
- 파일 저장 처리
"""

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

# ── 설정 ───────────────────────────────────────────────────
# 업로드 디렉토리 설정 (없으면 자동 생성)
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# 허용되는 이미지 타입
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# 허용되는 문서 타입
ALLOWED_DOC_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

# 모든 허용 타입
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOC_TYPES

# 최대 파일 크기 (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="파일 업로드 예제", description="단일/다중 파일 업로드 예제")


# ── 유틸리티 함수 ──────────────────────────────────────────
def get_unique_filename(original_filename: str) -> str:
    """
    고유한 파일명을 생성합니다.
    UUID를 사용하여 파일명 충돌을 방지합니다.
    """
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4()}{ext}"


def format_file_size(size_bytes: int) -> str:
    """파일 크기를 사람이 읽기 쉬운 형식으로 변환합니다."""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"


async def validate_and_save_file(
    file: UploadFile,
    allowed_types: set[str] | None = None,
    max_size: int = MAX_FILE_SIZE,
) -> dict:
    """
    파일을 검증하고 저장합니다.
    검증 항목: 파일 타입, 파일 크기
    반환: 파일 정보 딕셔너리
    """
    # 1. 파일 타입 검증
    if allowed_types and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않는 파일 형식입니다: {file.content_type}. "
                   f"허용 형식: {', '.join(allowed_types)}",
        )

    # 2. 파일 내용 읽기
    content = await file.read()

    # 3. 파일 크기 검증
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"파일 크기({format_file_size(len(content))})가 "
                   f"제한({format_file_size(max_size)})을 초과합니다",
        )

    # 4. 파일 저장
    unique_name = get_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    return {
        "original_name": file.filename,
        "saved_name": unique_name,
        "content_type": file.content_type,
        "size": len(content),
        "size_formatted": format_file_size(len(content)),
        "path": str(file_path),
    }


# ── 엔드포인트 ─────────────────────────────────────────────

@app.post("/upload/single", summary="단일 파일 업로드")
async def upload_single_file(
    file: UploadFile = File(..., description="업로드할 파일"),
):
    """
    단일 파일을 업로드합니다.
    허용 형식: 이미지(JPEG, PNG, GIF, WebP), 문서(PDF, TXT, CSV, XLSX)
    최대 크기: 10MB
    """
    result = await validate_and_save_file(file, allowed_types=ALLOWED_TYPES)
    return {
        "message": "파일이 성공적으로 업로드되었습니다",
        "file": result,
    }


@app.post("/upload/multiple", summary="다중 파일 업로드")
async def upload_multiple_files(
    files: list[UploadFile] = File(..., description="업로드할 파일들"),
):
    """
    여러 개의 파일을 동시에 업로드합니다.
    각 파일마다 타입과 크기를 검증합니다.
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="한 번에 최대 10개의 파일만 업로드할 수 있습니다",
        )

    results = []
    errors = []

    for i, file in enumerate(files):
        try:
            result = await validate_and_save_file(file, allowed_types=ALLOWED_TYPES)
            results.append(result)
        except HTTPException as e:
            errors.append({
                "index": i,
                "filename": file.filename,
                "error": e.detail,
            })

    return {
        "message": f"{len(results)}개 파일 업로드 성공, {len(errors)}개 실패",
        "uploaded": results,
        "errors": errors,
    }


@app.post("/upload/image", summary="이미지 전용 업로드")
async def upload_image(
    file: UploadFile = File(..., description="업로드할 이미지"),
):
    """
    이미지 파일만 업로드합니다.
    허용 형식: JPEG, PNG, GIF, WebP
    최대 크기: 5MB
    """
    max_image_size = 5 * 1024 * 1024  # 이미지는 5MB로 제한
    result = await validate_and_save_file(
        file,
        allowed_types=ALLOWED_IMAGE_TYPES,
        max_size=max_image_size,
    )
    return {
        "message": "이미지가 성공적으로 업로드되었습니다",
        "image": result,
    }


@app.get("/files", summary="업로드된 파일 목록")
async def list_uploaded_files():
    """업로드 디렉토리에 저장된 파일 목록을 반환합니다."""
    files = []
    for file_path in UPLOAD_DIR.iterdir():
        if file_path.is_file():
            stat = file_path.stat()
            files.append({
                "name": file_path.name,
                "size": format_file_size(stat.st_size),
                "size_bytes": stat.st_size,
            })

    files.sort(key=lambda x: x["name"])
    return {"total_files": len(files), "files": files}


@app.get("/files/{filename}", summary="파일 다운로드")
async def download_file(filename: str):
    """저장된 파일을 다운로드합니다."""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"파일을 찾을 수 없습니다: {filename}",
        )

    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/octet-stream",
    )


@app.delete("/files/{filename}", status_code=status.HTTP_204_NO_CONTENT, summary="파일 삭제")
async def delete_file(filename: str):
    """저장된 파일을 삭제합니다."""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"파일을 찾을 수 없습니다: {filename}",
        )

    file_path.unlink()
