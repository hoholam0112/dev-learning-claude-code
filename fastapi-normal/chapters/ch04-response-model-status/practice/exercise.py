# 실행 방법: uvicorn exercise:app --reload
# 챕터 04 연습 문제 - 직접 코드를 작성해보세요!

import math
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="챕터 04 연습 문제",
    description="응답 모델과 상태 코드 활용",
    version="1.0.0",
)

# ============================================================
# 문제 1: 게시글 API (비밀번호 숨기기)
# response_model을 사용하여 비밀번호가 응답에 포함되지 않도록 합니다
# POST /posts — 게시글 생성 (201)
# GET /posts — 목록 조회
# GET /posts/{post_id} — 단건 조회 (404)
# DELETE /posts/{post_id} — 삭제 (비밀번호 확인, 204/403/404)
# ============================================================


class PostCreate(BaseModel):
    """게시글 생성 요청 모델"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)


# TODO: PostResponse 모델을 정의하세요 (비밀번호 제외)
# 필드: id, title, content, author, created_at


# TODO: PostListResponse 모델을 정의하세요
# 필드: total, posts (List[PostResponse])


# 게시글 저장소
posts_db: dict[int, dict] = {}
post_next_id: int = 1


# TODO: POST /posts 엔드포인트를 구현하세요
# - response_model=PostResponse, status_code=201
# - password는 내부 저장, 응답에는 포함되지 않음
# - created_at은 datetime.now().isoformat()으로 생성


# TODO: GET /posts 엔드포인트를 구현하세요
# - response_model=PostListResponse


# TODO: GET /posts/{post_id} 엔드포인트를 구현하세요
# - response_model=PostResponse
# - 없으면 HTTPException(404) 발생


# TODO: DELETE /posts/{post_id} 엔드포인트를 구현하세요
# - status_code=204
# - password 쿼리 파라미터로 비밀번호 확인
# - 비밀번호 불일치 시 HTTPException(403)
# - 게시글 없으면 HTTPException(404)


# ============================================================
# 문제 2: 다양한 상태 코드 반환 API (파일 메타데이터)
# POST /files — 파일 등록 (201)
# GET /files/{file_id} — 조회 (200/404)
# PUT /files/{file_id} — 수정 (200/404)
# DELETE /files/{file_id} — 삭제 (204/404)
# POST /files/{file_id}/duplicate — 복제 (201/404)
# ============================================================


class FileCreate(BaseModel):
    name: str = Field(..., min_length=1)
    size_bytes: int = Field(..., gt=0)
    content_type: str


class FileResponse(BaseModel):
    id: int
    name: str
    size_bytes: int
    content_type: str
    uploaded_at: str


class FileUpdate(BaseModel):
    name: str = Field(..., min_length=1)
    size_bytes: int = Field(..., gt=0)
    content_type: str


# 파일 저장소
files_db: dict[int, dict] = {}
file_next_id: int = 1


# TODO: POST /files 엔드포인트를 구현하세요 (201)


# TODO: GET /files/{file_id} 엔드포인트를 구현하세요 (200/404)


# TODO: PUT /files/{file_id} 엔드포인트를 구현하세요 (200/404)


# TODO: DELETE /files/{file_id} 엔드포인트를 구현하세요 (204/404)


# TODO: POST /files/{file_id}/duplicate 엔드포인트를 구현하세요 (201/404)
# 힌트: 파일명에 _copy 추가 (확장자 앞에)


# ============================================================
# 문제 3: 목록 조회 (페이지네이션 응답 모델)
# POST /articles — 기사 작성 (201)
# GET /articles — 목록 조회 (페이지네이션)
# GET /articles/{article_id} — 단건 조회
# ============================================================


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=50)


class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: str


# TODO: PaginatedResponse 모델을 정의하세요
# 필드: total, page, page_size, total_pages, has_next(bool), has_prev(bool),
#       items(List[ArticleResponse])


# 기사 저장소
articles_db: dict[int, dict] = {}
article_next_id: int = 1


# TODO: POST /articles 엔드포인트를 구현하세요 (201)


# TODO: GET /articles 엔드포인트를 구현하세요
# - response_model=PaginatedResponse
# - page, page_size 쿼리 파라미터
# - total_pages = math.ceil(total / page_size)
# - has_next = page < total_pages
# - has_prev = page > 1


# TODO: GET /articles/{article_id} 엔드포인트를 구현하세요 (200/404)
