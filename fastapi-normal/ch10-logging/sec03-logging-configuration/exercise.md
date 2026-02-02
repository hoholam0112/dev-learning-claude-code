# 연습 문제: 로깅 설정

> **파일**: `exercise.py`
> **실행 방법**: `python exercise.py`

---

## 문제 1: dictConfig로 로거 설정

`logging.config.dictConfig`를 사용하여 로깅을 설정하세요.

### 요구 사항

- `dictConfig`로 로거 설정 (version=1, disable_existing_loggers=False)
- `"simple"` 포매터: `"%(levelname)s - %(message)s"` 포맷
- `"console"` 핸들러: `logging.StreamHandler`, DEBUG 레벨, `"simple"` 포매터
- `"app"` 로거: DEBUG 레벨, `"console"` 핸들러, propagate=False
- 추가로 `ListHandler`를 코드에서 직접 `"app"` 로거에 추가하여 테스트용으로 사용
- `GET /hello` 엔드포인트에서 `logger.info("안녕하세요")` 호출

### 힌트

```python
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
        },
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}
logging.config.dictConfig(LOGGING_CONFIG)
```

---

## 문제 2: 환경별 로그 설정

환경(development/production)에 따라 다른 로깅 설정을 반환하는 함수를 만드세요.

### 요구 사항

- `get_logging_config(environment)` 함수 구현
- **development**: DEBUG 레벨, 포맷 `"%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"`
- **production**: WARNING 레벨, 포맷 `"%(message)s"` (JSON 포매터용)
- `GET /status` 엔드포인트에서 DEBUG와 WARNING 로그를 각각 기록
- development 모드에서는 DEBUG 로그가 기록되는지, production 모드에서는 WARNING만 기록되는지 테스트

### 힌트

```python
def get_logging_config(environment: str = "development"):
    if environment == "production":
        return {
            "version": 1,
            ...
            "loggers": {"app": {"level": "WARNING", ...}},
        }
    else:
        return {
            "version": 1,
            ...
            "loggers": {"app": {"level": "DEBUG", ...}},
        }
```

---

## 테스트 기대 결과

```
✓ dictConfig로 설정한 로거가 정상 동작
✓ INFO 레벨 로그가 올바른 포맷으로 기록됨
✓ development 모드: DEBUG 로그가 기록됨
✓ production 모드: DEBUG 로그가 기록되지 않음
✓ production 모드: WARNING 로그가 기록됨

모든 테스트를 통과했습니다!
```
