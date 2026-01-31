# 실행 방법: uvicorn solution:app --reload
# 챕터 04 연습 문제 모범 답안

import math
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="챕터 04 연습 문제 답안",
    description="응답 모델과 상태 코드 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 게시글 API (비밀번호 숨기기)
# ============================================================


class PostCreate(BaseModel):
    """게시글 생성 요청 모델"""

    title: str = Field(..., min_length=1, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="내용")
    author: str = Field(..., min_length=1, max_length=50, description="작성자")
    password: str = Field(..., min_length=1, description="비밀번호 (수정/삭제 시 사용)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "첫 글",
                    "content": "안녕하세요!",
                    "author": "홍길동",
                    "password": "1234",
                }
            ]
        }
    }


class PostResponse(BaseModel):
    """게시글 응답 모델 — 비밀번호 제외"""

    id: int
    title: str
    content: str
    author: str
    created_at: str


class PostListResponse(BaseModel):
    """게시글 목록 응답 모델"""

    total: int
    posts: List[PostResponse]


# 게시글 저장소
posts_db: dict[int, dict] = {}
post_next_id: int = 1


@app.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["문제1-게시글"],
)
def create_post(post: PostCreate):
    """게시글을 생성합니다.

    response_model=PostResponse 덕분에 password 필드는 응답에 포함되지 않습니다.
    """
    global post_next_id

    post_data = {
        "id": post_next_id,
        "title": post.title,
        "content": post.content,
        "author": post.author,
        "password": post.password,  # 내부 저장 (응답에는 포함되지 않음)
        "created_at": datetime.now().isoformat(),
    }
    posts_db[post_next_id] = post_data
    post_next_id += 1

    return post_data


@app.get(
    "/posts",
    response_model=PostListResponse,
    tags=["문제1-게시글"],
)
def get_posts():
    """전체 게시글 목록을 조회합니다."""
    return {
        "total": len(posts_db),
        "posts": list(posts_db.values()),
    }


@app.get(
    "/posts/{post_id}",
    response_model=PostResponse,
    tags=["문제1-게시글"],
    responses={
        404: {"description": "게시글을 찾을 수 없음"},
    },
)
def get_post(post_id: int):
    """특정 게시글을 조회합니다."""
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )
    return posts_db[post_id]


@app.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["문제1-게시글"],
    responses={
        403: {"description": "비밀번호 불일치"},
        404: {"description": "게시글을 찾을 수 없음"},
    },
)
def delete_post(post_id: int, password: str = Query(..., description="게시글 비밀번호")):
    """게시글을 삭제합니다.

    비밀번호가 일치하지 않으면 403 에러를 반환합니다.
    """
    if post_id not in posts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다",
        )

    if posts_db[post_id]["password"] != password:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비밀번호가 일치하지 않습니다",
        )

    del posts_db[post_id]
    return None


# ============================================================
# 문제 2: 다양한 상태 코드 반환 API
# ============================================================


class FileCreate(BaseModel):
    """파일 메타데이터 생성 요청 모델"""

    name: str = Field(..., min_length=1, description="파일명")
    size_bytes: int = Field(..., gt=0, description="파일 크기 (바이트)")
    content_type: str = Field(..., description="콘텐츠 타입")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "report.pdf",
                    "size_bytes": 1024000,
                    "content_type": "application/pdf",
                }
            ]
        }
    }


class FileResponse(BaseModel):
    """파일 메타데이터 응답 모델"""

    id: int
    name: str
    size_bytes: int
    content_type: str
    uploaded_at: str


class FileUpdate(BaseModel):
    """파일 메타데이터 수정 요청 모델"""

    name: str = Field(..., min_length=1, description="파일명")
    size_bytes: int = Field(..., gt=0, description="파일 크기 (바이트)")
    content_type: str = Field(..., description="콘텐츠 타입")


# 파일 저장소
files_db: dict[int, dict] = {}
file_next_id: int = 1


@app.post(
    "/files",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["문제2-파일"],
    responses={201: {"description": "파일 메타데이터 등록 성공"}},
)
def create_file(file: FileCreate):
    """파일 메타데이터를 등록합니다."""
    global file_next_id

    file_data = {
        "id": file_next_id,
        "name": file.name,
        "size_bytes": file.size_bytes,
        "content_type": file.content_type,
        "uploaded_at": datetime.now().isoformat(),
    }
    files_db[file_next_id] = file_data
    file_next_id += 1

    return file_data


@app.get(
    "/files/{file_id}",
    response_model=FileResponse,
    tags=["문제2-파일"],
    responses={404: {"description": "파일을 찾을 수 없음"}},
)
def get_file(file_id: int):
    """파일 메타데이터를 조회합니다."""
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일을 찾을 수 없습니다",
        )
    return files_db[file_id]


@app.put(
    "/files/{file_id}",
    response_model=FileResponse,
    tags=["문제2-파일"],
    responses={404: {"description": "파일을 찾을 수 없음"}},
)
def update_file(file_id: int, file: FileUpdate):
    """파일 메타데이터를 수정합니다."""
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일을 찾을 수 없습니다",
        )

    files_db[file_id]["name"] = file.name
    files_db[file_id]["size_bytes"] = file.size_bytes
    files_db[file_id]["content_type"] = file.content_type

    return files_db[file_id]


@app.delete(
    "/files/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["문제2-파일"],
    responses={404: {"description": "파일을 찾을 수 없음"}},
)
def delete_file(file_id: int):
    """파일 메타데이터를 삭제합니다."""
    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일을 찾을 수 없습니다",
        )
    del files_db[file_id]
    return None


@app.post(
    "/files/{file_id}/duplicate",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["문제2-파일"],
    responses={
        201: {"description": "파일 복제 성공"},
        404: {"description": "원본 파일을 찾을 수 없음"},
    },
)
def duplicate_file(file_id: int):
    """파일 메타데이터를 복제합니다.

    원본 파일의 이름에 '_copy'를 추가하여 새 파일을 생성합니다.
    """
    global file_next_id

    if file_id not in files_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="파일을 찾을 수 없습니다",
        )

    original = files_db[file_id]

    # 파일명에 _copy 추가 (확장자 앞에)
    name_parts = original["name"].rsplit(".", 1)
    if len(name_parts) == 2:
        new_name = f"{name_parts[0]}_copy.{name_parts[1]}"
    else:
        new_name = f"{original['name']}_copy"

    new_file = {
        "id": file_next_id,
        "name": new_name,
        "size_bytes": original["size_bytes"],
        "content_type": original["content_type"],
        "uploaded_at": datetime.now().isoformat(),
    }
    files_db[file_next_id] = new_file
    file_next_id += 1

    return new_file


# ============================================================
# 문제 3: 목록 조회 (페이지네이션 응답 모델)
# ============================================================


class ArticleCreate(BaseModel):
    """기사 생성 요청 모델"""

    title: str = Field(..., min_length=1, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="내용")
    author: str = Field(..., min_length=1, max_length=50, description="작성자")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "FastAPI 입문",
                    "content": "FastAPI는 현대적인 웹 프레임워크입니다.",
                    "author": "홍길동",
                }
            ]
        }
    }


class ArticleResponse(BaseModel):
    """기사 응답 모델"""

    id: int
    title: str
    content: str
    author: str
    created_at: str


class PaginatedResponse(BaseModel):
    """페이지네이션 응답 모델"""

    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
    items: List[ArticleResponse]


# 기사 저장소
articles_db: dict[int, dict] = {}
article_next_id: int = 1


@app.post(
    "/articles",
    response_model=ArticleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["문제3-기사"],
)
def create_article(article: ArticleCreate):
    """기사를 작성합니다."""
    global article_next_id

    article_data = {
        "id": article_next_id,
        "title": article.title,
        "content": article.content,
        "author": article.author,
        "created_at": datetime.now().isoformat(),
    }
    articles_db[article_next_id] = article_data
    article_next_id += 1

    return article_data


@app.get(
    "/articles",
    response_model=PaginatedResponse,
    tags=["문제3-기사"],
)
def get_articles(
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    page_size: int = Query(default=10, ge=1, le=50, description="페이지 크기"),
):
    """기사 목록을 페이지네이션으로 조회합니다.

    페이지 정보와 함께 해당 페이지의 기사 목록을 반환합니다.
    """
    all_articles = list(articles_db.values())
    total = len(all_articles)

    # 전체 페이지 수 계산
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # 페이지네이션 슬라이싱
    start = (page - 1) * page_size
    end = start + page_size
    paginated_items = all_articles[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "items": paginated_items,
    }


@app.get(
    "/articles/{article_id}",
    response_model=ArticleResponse,
    tags=["문제3-기사"],
    responses={404: {"description": "기사를 찾을 수 없음"}},
)
def get_article(article_id: int):
    """특정 기사를 조회합니다."""
    if article_id not in articles_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="기사를 찾을 수 없습니다",
        )
    return articles_db[article_id]
