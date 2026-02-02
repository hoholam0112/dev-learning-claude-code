# 섹션 03: 로깅 설정

> **난이도**: ⭐⭐⭐ (3/5)
> **선수 지식**: sec01 로깅 기본, sec02 구조화된 로깅 완료
> **예상 학습 시간**: 1~1.5시간

---

## 학습 목표

- `logging.config.dictConfig`를 사용하여 체계적으로 로깅을 설정할 수 있다
- 여러 핸들러(콘솔, 파일)를 동시에 설정할 수 있다
- 환경별(개발/운영) 로그 설정을 구분하여 적용할 수 있다
- 로깅 베스트 프랙티스를 이해하고 적용할 수 있다

---

## 왜 dictConfig인가?

sec01에서는 코드로 직접 로거, 핸들러, 포매터를 설정했습니다.
프로젝트가 커지면 이 방식은 관리가 어려워집니다.

```python
# ❌ 코드에 설정이 흩어져 있음
logger1 = logging.getLogger("api")
logger1.setLevel(logging.DEBUG)
handler1 = logging.StreamHandler()
handler1.setFormatter(...)
logger1.addHandler(handler1)

logger2 = logging.getLogger("db")
logger2.setLevel(logging.WARNING)
handler2 = logging.FileHandler("db.log")
handler2.setFormatter(...)
logger2.addHandler(handler2)
```

```python
# ✅ dictConfig로 한곳에서 관리
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": { ... },
    "handlers": { ... },
    "loggers": { ... },
}

logging.config.dictConfig(LOGGING_CONFIG)
```

---

## 핵심 개념

### 1. dictConfig 구조

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,                       # 필수: 스키마 버전 (항상 1)
    "disable_existing_loggers": False,   # 기존 로거 비활성화 여부

    "formatters": {                      # 포매터 정의
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },

    "handlers": {                        # 핸들러 정의
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "WARNING",
            "formatter": "default",
            "filename": "app.log",
        },
    },

    "loggers": {                         # 로거 정의
        "myapp": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("myapp")
```

### 2. 주요 설정 항목

| 섹션 | 항목 | 설명 |
|------|------|------|
| `formatters` | `format` | 포맷 문자열 |
| `handlers` | `class` | 핸들러 클래스 경로 |
| `handlers` | `level` | 핸들러별 최소 로그 레벨 |
| `handlers` | `formatter` | 사용할 포매터 이름 |
| `loggers` | `level` | 로거 최소 로그 레벨 |
| `loggers` | `handlers` | 핸들러 이름 리스트 |
| `loggers` | `propagate` | 부모 로거에 전파 여부 |

### 3. `disable_existing_loggers`

```python
# False (권장): 기존 로거를 유지 (uvicorn 등의 로거 포함)
"disable_existing_loggers": False

# True: 기존 로거를 비활성화 (주의: uvicorn 로그가 사라질 수 있음)
"disable_existing_loggers": True
```

---

## 환경별 로그 설정

### 개발 환경 vs 운영 환경

| 항목 | 개발 환경 | 운영 환경 |
|------|-----------|-----------|
| 로그 레벨 | DEBUG (상세 정보) | WARNING (경고 이상만) |
| 포맷 | 읽기 쉬운 텍스트 | JSON (분석 도구 연동) |
| 출력 대상 | 콘솔 | 파일 + 외부 시스템 |
| 성능 영향 | 무시 가능 | 최소화 필요 |

```python
import os

def get_logging_config(environment: str = "development"):
    """환경별 로깅 설정을 반환하는 함수"""

    if environment == "production":
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "format": "%(message)s",  # JSON 포매터에서 처리
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "WARNING",
                    "formatter": "json",
                },
            },
            "loggers": {
                "app": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    else:  # development
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "verbose": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "verbose",
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
```

---

## 파일 핸들러와 로그 로테이션

### RotatingFileHandler

파일 크기가 일정 이상이 되면 자동으로 새 파일을 생성합니다.

```python
"handlers": {
    "file": {
        "class": "logging.handlers.RotatingFileHandler",
        "filename": "app.log",
        "maxBytes": 10485760,    # 10MB
        "backupCount": 5,        # 최대 5개 백업 파일 유지
        "formatter": "default",
    },
}
```

### TimedRotatingFileHandler

시간 기준으로 로그 파일을 로테이션합니다.

```python
"handlers": {
    "file": {
        "class": "logging.handlers.TimedRotatingFileHandler",
        "filename": "app.log",
        "when": "midnight",      # 매일 자정에 로테이션
        "interval": 1,
        "backupCount": 30,       # 30일분 보관
        "formatter": "default",
    },
}
```

---

## 커스텀 핸들러/포매터를 dictConfig에서 사용하기

직접 만든 클래스도 dictConfig에서 사용할 수 있습니다.
`class` 키에 모듈 경로를 지정하면 됩니다.

```python
# my_logging.py에 정의된 커스텀 클래스
"handlers": {
    "custom": {
        "class": "my_logging.JSONFileHandler",
        "level": "INFO",
        "filename": "structured.log",
    },
}
```

> 단, 테스트 시에는 커스텀 핸들러를 직접 코드로 추가하는 것이 더 편리합니다.

---

## 로깅 베스트 프랙티스

### 1. 로거 이름 규칙

```python
# ✅ 모듈별 로거 사용
logger = logging.getLogger(__name__)

# ✅ 기능별 로거 사용
api_logger = logging.getLogger("app.api")
db_logger = logging.getLogger("app.db")
auth_logger = logging.getLogger("app.auth")
```

### 2. 로그 메시지 가이드

```python
# ✅ 좋은 예: 무엇이, 왜 발생했는지 명확
logger.error("DB 연결 실패: host=%s, 재시도 %d/%d", host, retry, max_retry)
logger.info("사용자 로그인 성공: user_id=%d", user_id)

# ❌ 나쁜 예: 정보 부족
logger.error("에러 발생")
logger.info("완료")
```

### 3. 민감 정보 주의

```python
# ❌ 비밀번호, 토큰 등을 로그에 기록하지 않기
logger.info("로그인: user=%s, password=%s", user, password)

# ✅ 민감 정보는 마스킹
logger.info("로그인: user=%s", user)
```

---

## 핵심 정리

1. `logging.config.dictConfig`를 사용하면 **로깅 설정을 한곳에서 관리**할 수 있다
2. `disable_existing_loggers=False`로 설정하여 **기존 로거를 유지**하는 것이 좋다
3. **환경별 설정 함수**를 만들어 개발/운영 로그를 구분할 수 있다
4. `RotatingFileHandler`, `TimedRotatingFileHandler`로 **로그 파일 크기를 관리**할 수 있다
5. 모듈별 로거 이름, 명확한 메시지, 민감 정보 제외 등 **베스트 프랙티스**를 따른다

---

## 다음 단계

이 챕터의 모든 섹션을 완료했습니다!
[Ch11: 예외 처리](../../ch11-exception-handling/README.md)에서 FastAPI의 예외 처리 패턴을 학습합니다.
