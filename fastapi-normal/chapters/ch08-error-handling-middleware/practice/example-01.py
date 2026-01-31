# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn

"""
챕터 08 예제 01: 에러 처리 (HTTPException, 커스텀 핸들러)

이 예제에서는 다음을 학습합니다:
- HTTPException을 활용한 기본 에러 반환
- 커스텀 예외 클래스 정의
- 전역 예외 핸들러 등록
- 일관된 에러 응답 형식 구현
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# ── 커스텀 예외 클래스 ─────────────────────────────────────
class ItemNotFoundException(Exception):
    """아이템을 찾을 수 없을 때 발생하는 예외"""
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"ID {item_id}인 아이템을 찾을 수 없습니다"


class DuplicateItemException(Exception):
    """중복 아이템이 존재할 때 발생하는 예외"""
    def __init__(self, name: str):
        self.name = name
        self.message = f"'{name}' 이름의 아이템이 이미 존재합니다"


class InsufficientStockException(Exception):
    """재고가 부족할 때 발생하는 예외"""
    def __init__(self, item_id: int, requested: int, available: int):
        self.item_id = item_id
        self.requested = requested
        self.available = available
        self.message = (
            f"재고 부족: ID {item_id} 아이템의 재고는 {available}개이지만 "
            f"{requested}개를 요청했습니다"
        )


# ── Pydantic 모델 ─────────────────────────────────────────
class Item(BaseModel):
    name: str
    price: int
    stock: int = 0


class ErrorResponse(BaseModel):
    """일관된 에러 응답 형식"""
    error: str
    message: str
    timestamp: str
    detail: dict | None = None


# ── 임시 데이터 ────────────────────────────────────────────
items_db: dict[int, dict] = {
    1: {"id": 1, "name": "키보드", "price": 50000, "stock": 10},
    2: {"id": 2, "name": "마우스", "price": 30000, "stock": 5},
    3: {"id": 3, "name": "모니터", "price": 300000, "stock": 2},
}
next_id = 4


# ── FastAPI 앱 ─────────────────────────────────────────────
app = FastAPI(title="에러 처리 예제", description="커스텀 예외와 전역 핸들러 예제")


# ── 전역 예외 핸들러 등록 ──────────────────────────────────

@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    """아이템 미발견 예외를 처리하는 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "ITEM_NOT_FOUND",
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "detail": {"item_id": exc.item_id},
        },
    )


@app.exception_handler(DuplicateItemException)
async def duplicate_item_handler(request: Request, exc: DuplicateItemException):
    """중복 아이템 예외를 처리하는 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "DUPLICATE_ITEM",
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "detail": {"name": exc.name},
        },
    )


@app.exception_handler(InsufficientStockException)
async def insufficient_stock_handler(request: Request, exc: InsufficientStockException):
    """재고 부족 예외를 처리하는 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "INSUFFICIENT_STOCK",
            "message": exc.message,
            "timestamp": datetime.utcnow().isoformat(),
            "detail": {
                "item_id": exc.item_id,
                "requested": exc.requested,
                "available": exc.available,
            },
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """모든 미처리 예외를 잡는 전역 핸들러"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
            "timestamp": datetime.utcnow().isoformat(),
            "detail": None,
        },
    )


# ── 엔드포인트 ─────────────────────────────────────────────

@app.get("/items", summary="전체 아이템 목록")
async def list_items():
    """전체 아이템 목록을 반환합니다."""
    return {"items": list(items_db.values())}


@app.get("/items/{item_id}", summary="아이템 상세 조회")
async def get_item(item_id: int):
    """
    특정 아이템을 조회합니다.
    존재하지 않는 ID를 요청하면 커스텀 예외가 발생합니다.
    """
    if item_id not in items_db:
        # 커스텀 예외 발생 -> item_not_found_handler가 처리
        raise ItemNotFoundException(item_id)
    return items_db[item_id]


@app.post("/items", status_code=status.HTTP_201_CREATED, summary="아이템 생성")
async def create_item(item: Item):
    """
    새로운 아이템을 생성합니다.
    같은 이름의 아이템이 존재하면 중복 예외가 발생합니다.
    """
    global next_id

    # 이름 중복 확인
    for existing_item in items_db.values():
        if existing_item["name"] == item.name:
            raise DuplicateItemException(item.name)

    items_db[next_id] = {
        "id": next_id,
        "name": item.name,
        "price": item.price,
        "stock": item.stock,
    }
    result = items_db[next_id]
    next_id += 1
    return result


@app.post("/items/{item_id}/purchase", summary="아이템 구매")
async def purchase_item(item_id: int, quantity: int = 1):
    """
    아이템을 구매합니다.
    재고가 부족하면 재고 부족 예외가 발생합니다.
    """
    if item_id not in items_db:
        raise ItemNotFoundException(item_id)

    item = items_db[item_id]

    if quantity <= 0:
        # HTTPException을 직접 사용하는 예시
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="구매 수량은 1 이상이어야 합니다",
        )

    if item["stock"] < quantity:
        raise InsufficientStockException(
            item_id=item_id,
            requested=quantity,
            available=item["stock"],
        )

    # 재고 차감
    item["stock"] -= quantity
    return {
        "message": f"'{item['name']}' {quantity}개 구매 완료",
        "remaining_stock": item["stock"],
    }


@app.get("/error-demo", summary="에러 시연 (의도적 오류)")
async def trigger_error():
    """
    의도적으로 처리되지 않은 예외를 발생시킵니다.
    전역 예외 핸들러가 이를 처리합니다.
    """
    # 이 예외는 전역 핸들러(global_exception_handler)가 처리합니다
    raise RuntimeError("이것은 테스트용 내부 오류입니다")
