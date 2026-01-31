# 챕터 01 연습 문제

---

## 문제 1: 자기소개 API 만들기 (기초)

### 설명
자신의 정보를 반환하는 `/me` 엔드포인트를 만드세요.

### 요구사항
- `GET /me` 엔드포인트를 생성합니다
- 다음 정보를 JSON으로 반환합니다:
  - `name`: 이름 (문자열)
  - `age`: 나이 (정수)
  - `hobbies`: 취미 목록 (리스트)

### 예상 출력

```json
{
    "name": "홍길동",
    "age": 25,
    "hobbies": ["코딩", "독서", "게임"]
}
```

<details>
<summary>힌트 보기</summary>

- `@app.get("/me")` 데코레이터를 사용하세요
- Python의 딕셔너리를 반환하면 자동으로 JSON으로 변환됩니다
- 리스트도 JSON 배열로 자동 변환됩니다

</details>

---

## 문제 2: 간단한 계산기 API (기초)

### 설명
사칙연산을 수행하는 계산기 API를 만드세요. 각 연산을 별도의 엔드포인트로 구현합니다.

### 요구사항
- `GET /calc/add/{a}/{b}` — 덧셈
- `GET /calc/subtract/{a}/{b}` — 뺄셈
- `GET /calc/multiply/{a}/{b}` — 곱셈
- `GET /calc/divide/{a}/{b}` — 나눗셈
- `a`와 `b`는 실수(float) 타입입니다
- 나눗셈에서 `b`가 0일 경우 에러 메시지를 반환합니다

### 예상 입출력

```
GET /calc/add/10/3
→ {"operation": "add", "a": 10.0, "b": 3.0, "result": 13.0}

GET /calc/divide/10/0
→ {"operation": "divide", "a": 10.0, "b": 0.0, "error": "0으로 나눌 수 없습니다"}
```

<details>
<summary>힌트 보기</summary>

- 경로 파라미터의 타입을 `float`로 지정하면 자동으로 실수형 변환됩니다
- 나눗셈 함수에서 `if b == 0:` 조건으로 0 나누기를 방지하세요
- 각 연산의 `tags`를 `["계산기"]`로 지정하면 문서에서 그룹화됩니다

</details>

---

## 문제 3: 타임스탬프 API (기초~보통)

### 설명
현재 시간과 서버 정보를 반환하는 API를 만드세요.

### 요구사항
- `GET /time` — 현재 시간 정보를 반환합니다
- `GET /time/{timezone}` — 지정한 타임존의 시간을 반환합니다 (선택사항)
- 반환 정보:
  - `timestamp`: ISO 형식 문자열 (예: "2024-01-15T10:30:00")
  - `unix_timestamp`: Unix 타임스탬프 (실수)
  - `server_info`: 서버 정보 딕셔너리 (Python 버전, 플랫폼)

### 예상 출력

```json
{
    "timestamp": "2024-01-15T10:30:00.123456",
    "unix_timestamp": 1705312200.123456,
    "server_info": {
        "python_version": "3.11.5",
        "platform": "darwin"
    }
}
```

<details>
<summary>힌트 보기</summary>

- `from datetime import datetime` — 현재 시간 가져오기
- `datetime.now().isoformat()` — ISO 형식 문자열 변환
- `datetime.now().timestamp()` — Unix 타임스탬프
- `import sys` → `sys.version` — Python 버전
- `import platform` → `platform.system()` — 운영체제 정보

</details>

---

## 제출 방법

1. `solution.py` 파일에 3개 문제의 답안을 모두 작성하세요
2. `uvicorn solution:app --reload`로 실행하세요
3. `http://localhost:8000/docs`에서 모든 엔드포인트를 테스트하세요
