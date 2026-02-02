# 연습 문제: 미들웨어 기본

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: 요청 로깅 미들웨어

모든 요청에 대해 다음 정보를 `request_log` 리스트에 기록하는 미들웨어를 작성하세요.

### 요구 사항

- 요청의 HTTP 메서드(`method`)와 URL 문자열(`url`)을 딕셔너리로 기록
- `request_log` 리스트에 `append`하여 저장
- 딕셔너리 형식: `{"method": "GET", "url": "http://..."}`

### 힌트

- `request.method`로 HTTP 메서드를 가져올 수 있습니다
- `str(request.url)`로 URL 문자열을 가져올 수 있습니다

---

## 문제 2: 응답 시간 헤더 추가

같은 미들웨어 안에서 모든 응답에 `X-Process-Time` 헤더를 추가하세요.

### 요구 사항

- `time.time()`을 사용하여 요청 처리 시간을 측정
- 처리 시간을 **초 단위 문자열**로 `X-Process-Time` 헤더에 추가
- 예: `X-Process-Time: 0.0012`

### 힌트

- `call_next` 호출 전후로 시간을 측정하면 됩니다
- `response.headers["X-Process-Time"] = str(처리시간)`

---

## 테스트 기대 결과

```
✓ X-Process-Time 헤더: 0.0003
✓ 요청 로그: [{'method': 'GET', 'url': '...'}, {'method': 'GET', 'url': '...'}]

모든 테스트를 통과했습니다!
```
