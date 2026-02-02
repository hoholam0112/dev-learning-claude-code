# 섹션 02: 첫 번째 FastAPI 앱 - 연습 문제

> **난이도**: ⭐ (1/5)
> **파일**: `exercise.py`

---

## 문제 1: `/hello` 엔드포인트 구현

### 목표
GET 요청을 받아 인사 메시지를 JSON으로 반환하는 엔드포인트를 만드세요.

### 요구 사항

| 항목 | 값 |
|------|-----|
| HTTP 메서드 | GET |
| 경로 | `/hello` |
| 반환값 | `{"message": "안녕하세요, FastAPI!"}` |

### 힌트

```python
@app.get("/경로")
def 함수이름():
    return {"키": "값"}
```

---

## 문제 2: `/greet/{name}` 엔드포인트 구현

### 목표
URL 경로에서 이름을 받아 개인화된 인사 메시지를 반환하는 엔드포인트를 만드세요.

### 요구 사항

| 항목 | 값 |
|------|-----|
| HTTP 메서드 | GET |
| 경로 | `/greet/{name}` |
| 매개변수 | `name` (문자열) |
| 반환값 | `{"message": "안녕하세요, {name}님!"}` |

### 예시

- `GET /greet/홍길동` → `{"message": "안녕하세요, 홍길동님!"}`
- `GET /greet/Alice` → `{"message": "안녕하세요, Alice님!"}`

### 힌트

```python
@app.get("/경로/{매개변수}")
def 함수이름(매개변수: str):
    return {"키": f"값은 {매개변수}입니다"}
```

---

## 실행 및 검증

### 방법 1: 자체 테스트 실행

```bash
python exercise.py
```

성공 시 출력:
```
✓ /hello 테스트 통과
✓ /greet/{name} 테스트 통과

모든 테스트를 통과했습니다!
```

### 방법 2: 서버로 실행

```bash
uvicorn exercise:app --reload
```

브라우저에서 확인:
- `http://localhost:8000/hello`
- `http://localhost:8000/greet/홍길동`
- `http://localhost:8000/docs` (Swagger UI)

---

## 추가 도전 과제 (선택)

1. `GET /about` 엔드포인트를 추가하여 자기 소개를 반환해보세요.
2. `GET /greet/{name}` 에서 `name`이 영어인지 한국어인지 판별하여 다른 메시지를 반환해보세요.
3. Swagger UI(`/docs`)에 접속하여 "Try it out" 기능을 사용해보세요.
