# 실행 방법: uvicorn solution:app --reload
# 챕터 02 연습문제 모범 답안
# 필요 패키지: pip install fastapi uvicorn pydantic

from __future__ import annotations

import base64
import gc
import json
import re
import time
from datetime import datetime
from typing import (
    Annotated,
    Any,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
)

from fastapi import FastAPI, HTTPException, Query
from pydantic import (
    BaseModel,
    Field,
    TypeAdapter,
    field_serializer,
    field_validator,
    model_validator,
    BeforeValidator,
    PlainSerializer,
)

app = FastAPI(title="챕터 02 연습문제 모범 답안")


# ============================================================
# 문제 1: 재귀적 트리 구조 모델 설계
# ============================================================

class TreeNode(BaseModel):
    """
    재귀적 트리 구조 모델.
    파일 시스템이나 카테고리 구조를 표현할 수 있다.
    """
    name: str = Field(min_length=1, description="노드 이름")
    node_type: Literal["file", "directory"] = Field(description="노드 타입")
    size: Optional[int] = Field(None, ge=0, description="파일 크기 (바이트)")
    children: Optional[list[TreeNode]] = Field(
        None, description="자식 노드 리스트"
    )
    metadata: dict[str, Any] = Field(default={}, description="메타데이터")

    @model_validator(mode="after")
    def validate_node_consistency(self) -> TreeNode:
        """노드 타입에 따른 일관성 검증"""
        if self.node_type == "file":
            if self.children is not None and len(self.children) > 0:
                raise ValueError("파일 노드는 자식을 가질 수 없습니다")
            if self.size is None:
                raise ValueError("파일 노드는 size가 필수입니다")
            # 파일의 children을 None으로 정리
            self.children = None

        elif self.node_type == "directory":
            if self.size is not None:
                raise ValueError("디렉토리 노드는 size가 None이어야 합니다")
            if self.children is None:
                self.children = []

            # 같은 부모 아래 중복 이름 검사
            names = [child.name for child in self.children]
            duplicates = set(n for n in names if names.count(n) > 1)
            if duplicates:
                raise ValueError(
                    f"중복된 이름이 있습니다: {', '.join(duplicates)}"
                )

        return self

    def total_size(self) -> int:
        """트리 전체의 총 크기를 재귀적으로 계산"""
        if self.node_type == "file":
            return self.size or 0
        total = 0
        for child in (self.children or []):
            total += child.total_size()
        return total

    def to_tree_string(self, indent: int = 0) -> str:
        """트리를 들여쓰기된 문자열로 출력"""
        prefix = "  " * indent
        if self.node_type == "file":
            return f"{prefix}{self.name} ({self.size} bytes)"
        else:
            lines = [f"{prefix}{self.name}/"]
            for child in (self.children or []):
                lines.append(child.to_tree_string(indent + 1))
            return "\n".join(lines)

    def find_node(self, path: str) -> Optional[TreeNode]:
        """경로로 노드를 찾는다 (예: 'docs/readme.md')"""
        parts = path.strip("/").split("/")
        if not parts or parts == [""]:
            return self

        current = self
        for part in parts:
            if current.node_type != "directory" or not current.children:
                return None
            found = None
            for child in current.children:
                if child.name == part:
                    found = child
                    break
            if found is None:
                return None
            current = found
        return current

    def file_count(self) -> int:
        """파일 수를 재귀적으로 계산"""
        if self.node_type == "file":
            return 1
        return sum(child.file_count() for child in (self.children or []))

    def directory_count(self) -> int:
        """디렉토리 수를 재귀적으로 계산 (자기 자신 제외)"""
        if self.node_type == "file":
            return 0
        return sum(
            1 + child.directory_count()
            for child in (self.children or [])
            if child.node_type == "directory"
        )


# ============================================================
# 문제 2: 커스텀 타입과 Validator 체인
# ============================================================

def normalize_korean_phone(v: Any) -> str:
    """한국 전화번호를 정규화하는 검증 함수"""
    if not isinstance(v, str):
        v = str(v)

    # 국제 번호 변환
    v = v.replace("+82", "0").replace("+82-", "0")

    # 숫자만 추출
    digits = re.sub(r"[^\d]", "", v)

    if len(digits) == 11 and digits.startswith("010"):
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    elif len(digits) == 10 and digits.startswith("02"):
        return f"{digits[:2]}-{digits[2:6]}-{digits[6:]}"
    elif len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    else:
        raise ValueError(f"유효하지 않은 전화번호 형식: {v}")


# 커스텀 타입: Annotated + BeforeValidator + PlainSerializer
KoreanPhoneNumber = Annotated[
    str,
    BeforeValidator(normalize_korean_phone),
    Field(pattern=r"^\d{2,3}-\d{3,4}-\d{4}$"),
]


def validate_business_number(v: Any) -> str:
    """사업자등록번호 검증 (체크 디지트 포함)"""
    if not isinstance(v, str):
        v = str(v)

    # 숫자만 추출
    digits = re.sub(r"[^\d]", "", v)

    if len(digits) != 10:
        raise ValueError("사업자등록번호는 10자리여야 합니다")

    # 체크 디지트 검증
    weights = [1, 3, 7, 1, 3, 7, 1, 3, 5]
    total = sum(int(d) * w for d, w in zip(digits[:9], weights))
    total += (int(digits[8]) * 5) // 10
    check_digit = (10 - (total % 10)) % 10

    if check_digit != int(digits[9]):
        raise ValueError("사업자등록번호 체크 디지트가 유효하지 않습니다")

    # 형식화된 문자열 반환
    return f"{digits[:3]}-{digits[3:5]}-{digits[5:]}"


BusinessRegistrationNumber = Annotated[
    str,
    BeforeValidator(validate_business_number),
    Field(pattern=r"^\d{3}-\d{2}-\d{5}$"),
]


class Money(BaseModel):
    """통화 금액 타입"""
    amount: float = Field(ge=0, description="금액 (음수 불가)")
    currency: str = Field(
        default="KRW",
        pattern=r"^[A-Z]{3}$",
        description="통화 코드 (ISO 4217)",
    )

    @field_serializer("amount")
    def serialize_amount(self, v: float) -> str:
        """금액을 천 단위 콤마 형식으로 직렬화"""
        if v == int(v):
            return f"{int(v):,}"
        return f"{v:,.2f}"

    def __str__(self) -> str:
        """문자열 표현: '1,000 KRW'"""
        if self.amount == int(self.amount):
            return f"{int(self.amount):,} {self.currency}"
        return f"{self.amount:,.2f} {self.currency}"


class BusinessProfile(BaseModel):
    """사업자 프로필 모델"""
    company_name: str = Field(min_length=1, description="회사명")
    business_number: BusinessRegistrationNumber = Field(
        description="사업자등록번호"
    )
    phone: KoreanPhoneNumber = Field(description="대표 전화번호")
    capital: Money = Field(description="자본금")
    established_date: Optional[str] = Field(None, description="설립일")


# ============================================================
# 문제 3: 제네릭 페이지네이션 응답 모델
# ============================================================

T = TypeVar("T")


class OffsetPagination(BaseModel, Generic[T]):
    """오프셋 기반 페이지네이션"""
    pagination_type: Literal["offset"] = "offset"
    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_pages: int = 0
    has_next: bool = False
    has_prev: bool = False

    @model_validator(mode="after")
    def calculate_pagination(self) -> OffsetPagination[T]:
        """페이지네이션 메타데이터 자동 계산"""
        if self.total > 0:
            self.total_pages = (
                (self.total + self.page_size - 1) // self.page_size
            )
        else:
            self.total_pages = 0
        self.has_next = self.page < self.total_pages
        self.has_prev = self.page > 1
        return self

    @classmethod
    def from_list(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> OffsetPagination[T]:
        """리스트에서 페이지네이션 응답 생성"""
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )


class CursorPagination(BaseModel, Generic[T]):
    """커서 기반 페이지네이션"""
    pagination_type: Literal["cursor"] = "cursor"
    items: list[T]
    cursor: Optional[str] = Field(None, description="현재 커서")
    next_cursor: Optional[str] = Field(None, description="다음 페이지 커서")
    prev_cursor: Optional[str] = Field(None, description="이전 페이지 커서")
    has_more: bool = False
    page_size: int = Field(ge=1, le=100)

    @classmethod
    def encode_cursor(cls, value: Any) -> str:
        """값을 커서 문자열로 인코딩"""
        return base64.urlsafe_b64encode(
            str(value).encode()
        ).decode()

    @classmethod
    def decode_cursor(cls, cursor: str) -> str:
        """커서 문자열을 값으로 디코딩"""
        return base64.urlsafe_b64decode(cursor.encode()).decode()

    @classmethod
    def from_list(
        cls,
        all_items: list[T],
        cursor: Optional[str],
        page_size: int,
        get_cursor_value,
    ) -> CursorPagination[T]:
        """
        리스트에서 커서 기반 페이지네이션 응답 생성.
        get_cursor_value: 아이템에서 커서 값을 추출하는 함수
        """
        # 커서 위치 찾기
        start_idx = 0
        if cursor:
            decoded = cls.decode_cursor(cursor)
            for i, item in enumerate(all_items):
                if str(get_cursor_value(item)) == decoded:
                    start_idx = i + 1
                    break

        # 페이지 슬라이싱
        page_items = all_items[start_idx:start_idx + page_size]
        has_more = start_idx + page_size < len(all_items)

        # 커서 생성
        next_cursor = None
        if has_more and page_items:
            next_cursor = cls.encode_cursor(
                get_cursor_value(page_items[-1])
            )

        prev_cursor = None
        if start_idx > 0:
            prev_idx = max(0, start_idx - page_size)
            if prev_idx < len(all_items):
                prev_cursor = cls.encode_cursor(
                    get_cursor_value(all_items[prev_idx])
                )

        return cls(
            items=page_items,
            cursor=cursor,
            next_cursor=next_cursor,
            prev_cursor=prev_cursor,
            has_more=has_more,
            page_size=page_size,
        )


# ============================================================
# 문제 4: Pydantic 직렬화 성능 비교
# ============================================================

class Address(BaseModel):
    """주소 모델 (중첩용)"""
    street: str
    city: str
    zip_code: str
    country: str = "KR"


class BenchmarkUser(BaseModel):
    """벤치마크용 복잡한 모델"""
    id: int
    name: str
    email: str
    age: int
    is_active: bool = True
    tags: list[str] = []
    address: Optional[Address] = None
    scores: list[float] = []
    metadata: dict[str, Any] = {}
    created_at: str = "2024-01-01T00:00:00"


# TypeAdapter 미리 생성
benchmark_adapter = TypeAdapter(BenchmarkUser)

# 벤치마크 테스트 데이터
BENCHMARK_DATA = {
    "id": 1,
    "name": "홍길동",
    "email": "hong@example.com",
    "age": 30,
    "is_active": True,
    "tags": ["python", "fastapi", "pydantic"],
    "address": {
        "street": "세종대로 110",
        "city": "서울",
        "zip_code": "03171",
        "country": "KR",
    },
    "scores": [95.5, 87.3, 92.1, 88.7, 91.0],
    "metadata": {"role": "developer", "level": "senior"},
    "created_at": "2024-01-01T00:00:00",
}

BENCHMARK_JSON = json.dumps(BENCHMARK_DATA, ensure_ascii=False).encode("utf-8")


def run_benchmark(iterations: int = 10000) -> dict:
    """성능 벤치마크 실행"""
    results = {"역직렬화": {}, "직렬화": {}}

    # GC 비활성화하여 정확한 측정
    gc.disable()

    # 워밍업
    for _ in range(100):
        BenchmarkUser(**BENCHMARK_DATA)

    # --- 역직렬화 벤치마크 ---

    # 1. 생성자
    start = time.perf_counter()
    for _ in range(iterations):
        BenchmarkUser(**BENCHMARK_DATA)
    constructor_time = time.perf_counter() - start
    base_time = constructor_time

    # 2. model_validate
    start = time.perf_counter()
    for _ in range(iterations):
        BenchmarkUser.model_validate(BENCHMARK_DATA)
    validate_time = time.perf_counter() - start

    # 3. model_validate_json
    start = time.perf_counter()
    for _ in range(iterations):
        BenchmarkUser.model_validate_json(BENCHMARK_JSON)
    validate_json_time = time.perf_counter() - start

    # 4. model_construct (검증 건너뛰기)
    start = time.perf_counter()
    for _ in range(iterations):
        BenchmarkUser.model_construct(**BENCHMARK_DATA)
    construct_time = time.perf_counter() - start

    # 5. TypeAdapter
    start = time.perf_counter()
    for _ in range(iterations):
        benchmark_adapter.validate_python(BENCHMARK_DATA)
    adapter_time = time.perf_counter() - start

    results["역직렬화"] = {
        "Model(**data)": f"{constructor_time:.4f}초 (기준)",
        "model_validate": (
            f"{validate_time:.4f}초 "
            f"({base_time / validate_time:.2f}배)"
        ),
        "model_validate_json": (
            f"{validate_json_time:.4f}초 "
            f"({base_time / validate_json_time:.2f}배)"
        ),
        "model_construct": (
            f"{construct_time:.4f}초 "
            f"({base_time / construct_time:.2f}배)"
        ),
        "TypeAdapter": (
            f"{adapter_time:.4f}초 "
            f"({base_time / adapter_time:.2f}배)"
        ),
    }

    # --- 직렬화 벤치마크 ---
    sample = BenchmarkUser(**BENCHMARK_DATA)

    # 1. model_dump
    start = time.perf_counter()
    for _ in range(iterations):
        sample.model_dump()
    dump_time = time.perf_counter() - start
    dump_base = dump_time

    # 2. model_dump_json
    start = time.perf_counter()
    for _ in range(iterations):
        sample.model_dump_json()
    dump_json_time = time.perf_counter() - start

    # 3. model_dump(exclude_none=True)
    start = time.perf_counter()
    for _ in range(iterations):
        sample.model_dump(exclude_none=True)
    dump_exclude_time = time.perf_counter() - start

    results["직렬화"] = {
        "model_dump": f"{dump_time:.4f}초 (기준)",
        "model_dump_json": (
            f"{dump_json_time:.4f}초 "
            f"({dump_base / dump_json_time:.2f}배)"
        ),
        "model_dump(exclude_none)": (
            f"{dump_exclude_time:.4f}초 "
            f"({dump_base / dump_exclude_time:.2f}배)"
        ),
    }

    gc.enable()
    return results


# ============================================================
# 엔드포인트 정의
# ============================================================

# --- 문제 1 엔드포인트 ---

@app.post("/tree/validate")
async def validate_tree(tree: TreeNode):
    """트리 구조 검증 및 분석"""
    return {
        "검증": "성공",
        "총_크기": tree.total_size(),
        "파일_수": tree.file_count(),
        "디렉토리_수": tree.directory_count(),
        "트리_출력": tree.to_tree_string(),
    }


@app.get("/tree/demo")
async def tree_demo():
    """트리 구조 데모"""
    tree_data = {
        "name": "project",
        "node_type": "directory",
        "children": [
            {
                "name": "src",
                "node_type": "directory",
                "children": [
                    {"name": "main.py", "node_type": "file", "size": 4096},
                    {"name": "utils.py", "node_type": "file", "size": 2048},
                    {
                        "name": "models",
                        "node_type": "directory",
                        "children": [
                            {
                                "name": "user.py",
                                "node_type": "file",
                                "size": 1024,
                            },
                            {
                                "name": "product.py",
                                "node_type": "file",
                                "size": 1536,
                            },
                        ],
                    },
                ],
            },
            {
                "name": "tests",
                "node_type": "directory",
                "children": [
                    {
                        "name": "test_main.py",
                        "node_type": "file",
                        "size": 2048,
                    },
                ],
            },
            {"name": "README.md", "node_type": "file", "size": 512},
        ],
    }

    tree = TreeNode.model_validate(tree_data)
    return {
        "트리_출력": tree.to_tree_string(),
        "총_크기": f"{tree.total_size():,} bytes",
        "파일_수": tree.file_count(),
        "디렉토리_수": tree.directory_count(),
        "검색_결과": {
            "src/main.py": tree.find_node("src/main.py") is not None,
            "src/models/user.py": (
                tree.find_node("src/models/user.py") is not None
            ),
            "nonexistent.py": tree.find_node("nonexistent.py") is not None,
        },
    }


# --- 문제 2 엔드포인트 ---

@app.post("/business/profile", response_model=BusinessProfile)
async def create_business_profile(profile: BusinessProfile):
    """사업자 프로필 생성 (커스텀 타입 검증)"""
    return profile


@app.get("/business/demo")
async def business_demo():
    """커스텀 타입 데모"""
    # 다양한 전화번호 형식 테스트
    phone_tests = [
        "010-1234-5678",
        "01012345678",
        "+82-10-1234-5678",
        "010.1234.5678",
    ]
    phone_results = []
    for phone in phone_tests:
        try:
            normalized = normalize_korean_phone(phone)
            phone_results.append({"입력": phone, "정규화": normalized})
        except ValueError as e:
            phone_results.append({"입력": phone, "오류": str(e)})

    # 사업자등록번호 테스트 (실제 유효한 번호로 테스트하기 어려우므로 형식만)
    return {
        "전화번호_정규화": phone_results,
        "Money_예시": {
            "원화": str(Money(amount=50000000, currency="KRW")),
            "달러": str(Money(amount=1234.56, currency="USD")),
        },
    }


# --- 문제 3 엔드포인트 ---

# 데모용 아이템 데이터
class Item(BaseModel):
    id: int
    name: str
    price: float

demo_items = [
    Item(id=i, name=f"아이템 {i}", price=i * 1000.0)
    for i in range(1, 51)  # 50개 아이템
]


@app.get("/items")
async def list_items(
    pagination: Literal["offset", "cursor"] = Query(
        "offset", description="페이지네이션 방식"
    ),
    page: int = Query(1, ge=1, description="페이지 번호 (오프셋 방식)"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    cursor: Optional[str] = Query(None, description="커서 (커서 방식)"),
):
    """
    아이템 목록 조회.
    pagination 파라미터로 페이지네이션 방식을 선택할 수 있다.
    """
    items_dicts = [item.model_dump() for item in demo_items]

    if pagination == "offset":
        total = len(demo_items)
        start = (page - 1) * size
        end = start + size
        page_items = items_dicts[start:end]

        result = OffsetPagination[dict].from_list(
            items=page_items,
            total=total,
            page=page,
            page_size=size,
        )
        return result.model_dump()

    else:  # cursor
        result = CursorPagination[dict].from_list(
            all_items=items_dicts,
            cursor=cursor,
            page_size=size,
            get_cursor_value=lambda x: x["id"],
        )
        return result.model_dump()


# --- 문제 4 엔드포인트 ---

@app.get("/benchmark")
async def benchmark_endpoint(
    iterations: int = Query(10000, ge=100, le=100000, description="반복 횟수"),
):
    """Pydantic 직렬화/역직렬화 성능 벤치마크"""
    results = run_benchmark(iterations)
    return {
        "반복_횟수": iterations,
        **results,
        "참고": {
            "model_construct": "검증을 건너뛰므로 외부 입력에 사용 금지",
            "model_validate_json": "Rust에서 JSON 파싱+검증을 동시 수행",
            "환경": "결과는 실행 환경에 따라 달라질 수 있음",
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("챕터 02 연습문제 모범 답안 서버")
    print("=" * 60)
    print("\n문제 1 (트리 구조):")
    print("  GET  http://localhost:8000/tree/demo")
    print("  POST http://localhost:8000/tree/validate")
    print("\n문제 2 (커스텀 타입):")
    print("  GET  http://localhost:8000/business/demo")
    print("  POST http://localhost:8000/business/profile")
    print("\n문제 3 (페이지네이션):")
    print("  GET  http://localhost:8000/items?pagination=offset&page=1")
    print("  GET  http://localhost:8000/items?pagination=cursor&size=5")
    print("\n문제 4 (벤치마크):")
    print("  GET  http://localhost:8000/benchmark?iterations=10000")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
