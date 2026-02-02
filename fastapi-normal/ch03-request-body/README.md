# Ch03: 요청 본문과 Pydantic 모델

> **난이도**: ⭐⭐ (2/5)
> **선수 지식**: Ch02 (경로 매개변수와 쿼리 매개변수) 완료
> **예상 학습 시간**: 3~4시간

---

## 개요

웹 API에서 클라이언트가 서버로 데이터를 보내는 가장 일반적인 방법은 **요청 본문(Request Body)**입니다.
사용자 등록, 상품 생성, 주문 접수 등 대부분의 POST/PUT 요청은 본문에 데이터를 담아 전송합니다.

FastAPI는 **Pydantic** 라이브러리를 활용하여 요청 본문을 자동으로 파싱하고,
타입을 검증하며, 유효성 검사까지 수행합니다.
이 챕터에서는 안전하고 체계적으로 클라이언트 데이터를 수신하는 방법을 학습합니다.

---

## Pydantic의 역할과 중요성

Pydantic은 Python의 타입 어노테이션을 활용한 **데이터 검증 라이브러리**입니다.
FastAPI에서 Pydantic이 중요한 이유는 다음과 같습니다:

1. **자동 데이터 파싱**: JSON 요청 본문을 Python 객체로 자동 변환합니다.
2. **타입 검증**: 전달된 데이터가 올바른 타입인지 자동으로 확인합니다.
3. **유효성 검사**: 값의 범위, 길이, 형식 등을 세밀하게 검증할 수 있습니다.
4. **자동 문서화**: Swagger UI에 요청 본문의 스키마가 자동으로 표시됩니다.
5. **IDE 지원**: 타입 힌트를 통해 자동 완성과 타입 체크를 지원합니다.

```python
# Pydantic 없이 (위험하고 번거로움)
@app.post("/items")
async def create_item(request: Request):
    body = await request.json()
    name = body.get("name")       # 타입 보장 없음
    price = body.get("price")     # 누락 여부 모름
    # 수동으로 모든 검증을 해야 함...

# Pydantic 사용 (안전하고 간결함)
@app.post("/items")
async def create_item(item: Item):
    # item은 이미 검증된 Item 객체!
    return item
```

---

## 섹션 목록

| 섹션 | 제목 | 핵심 키워드 |
|------|------|------------|
| [sec01](./sec01-pydantic-models/) | Pydantic 기본 모델 | BaseModel, Field, 타입 어노테이션, Optional |
| [sec02](./sec02-nested-models/) | 중첩 모델 | 모델 안의 모델, List[Model], Dict 타입 |
| [sec03](./sec03-form-and-file/) | 폼 데이터와 파일 업로드 | Form(), File(), UploadFile |

---

## 학습 순서

```mermaid
graph LR
    S1[sec01: Pydantic 기본] --> S2[sec02: 중첩 모델]
    S2 --> S3[sec03: 폼/파일 업로드]
```

1. **sec01**: Pydantic BaseModel의 기본 사용법과 Field를 이용한 유효성 검사를 학습합니다.
2. **sec02**: 모델 안에 모델을 중첩하고, 리스트/딕셔너리 타입을 활용하는 방법을 학습합니다.
3. **sec03**: JSON이 아닌 폼 데이터와 파일 업로드를 처리하는 방법을 학습합니다.

---

## 학습 후 체크리스트

- [ ] Pydantic BaseModel을 정의하고 POST 요청의 본문으로 사용할 수 있다
- [ ] Field를 사용하여 값의 범위, 길이 등 유효성 검사 규칙을 설정할 수 있다
- [ ] Optional 필드와 기본값을 적절히 사용할 수 있다
- [ ] 중첩된 모델 구조를 설계할 수 있다
- [ ] List[Model]과 Dict 타입을 요청 본문에서 활용할 수 있다
- [ ] Form 데이터를 수신하고 처리할 수 있다
- [ ] 파일 업로드를 구현할 수 있다
