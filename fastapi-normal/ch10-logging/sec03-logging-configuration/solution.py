# 모범 답안: 로깅 설정
# 실행: uvicorn solution:app --reload
# 테스트: python solution.py

import logging
import logging.config
from fastapi import FastAPI
from fastapi.testclient import TestClient


# --- 로그 캡처를 위한 ListHandler ---
class ListHandler(logging.Handler):
    """테스트용: 로그 레코드를 리스트에 저장하는 핸들러"""

    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(self.format(record))


# --- 문제 1: dictConfig로 로거 설정 ---

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
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

# 로거 가져오기
logger = logging.getLogger("app")

# 테스트용 ListHandler 추가 (simple 포매터 적용)
list_handler = ListHandler()
list_handler.setLevel(logging.DEBUG)
simple_formatter = logging.Formatter("%(levelname)s - %(message)s")
list_handler.setFormatter(simple_formatter)
logger.addHandler(list_handler)


# --- 문제 2: 환경별 로그 설정 ---

def get_logging_config(environment: str = "development"):
    """환경별 로깅 설정을 반환하는 함수

    - development: DEBUG 레벨, 상세 포맷
    - production: WARNING 레벨, 간단한 포맷 (JSON 포매터용)
    """
    if environment == "production":
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json_like": {
                    "format": "%(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "WARNING",
                    "formatter": "json_like",
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


app = FastAPI()


@app.get("/hello")
async def hello():
    """인사 엔드포인트 - INFO 로그 기록"""
    logger.info("안녕하세요")
    return {"message": "안녕하세요"}


@app.get("/status")
async def get_status():
    """상태 엔드포인트 - DEBUG와 WARNING 로그를 각각 기록"""
    logger.debug("상태 확인 중...")
    logger.warning("디스크 용량 부족 경고")
    return {"status": "running"}


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # === 문제 1 테스트: dictConfig 로거 ===

    list_handler.records.clear()

    # 테스트 1: dictConfig로 설정한 로거 동작 확인
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "안녕하세요"}
    assert len(list_handler.records) >= 1
    print("✓ dictConfig로 설정한 로거가 정상 동작")

    # 테스트 2: 포맷 확인
    assert "INFO - 안녕하세요" in list_handler.records[0]
    print(f"✓ INFO 레벨 로그가 올바른 포맷으로 기록됨: {list_handler.records[0]}")

    # === 문제 2 테스트: 환경별 로그 설정 ===

    # --- development 모드 테스트 ---
    dev_config = get_logging_config("development")
    logging.config.dictConfig(dev_config)

    # dictConfig 후 로거를 다시 가져오고 ListHandler 재설정
    dev_logger = logging.getLogger("app")
    dev_handler = ListHandler()
    dev_handler.setLevel(logging.DEBUG)
    dev_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    dev_logger.addHandler(dev_handler)

    # development 앱 테스트
    dev_handler.records.clear()
    response = client.get("/status")
    assert response.status_code == 200

    # development 모드에서는 DEBUG 로그가 기록되어야 함
    debug_logs = [r for r in dev_handler.records if "DEBUG" in r]
    assert len(debug_logs) >= 1
    print("✓ development 모드: DEBUG 로그가 기록됨")

    # --- production 모드 테스트 ---
    prod_config = get_logging_config("production")
    logging.config.dictConfig(prod_config)

    # dictConfig 후 로거를 다시 가져오고 ListHandler 재설정
    prod_logger = logging.getLogger("app")
    prod_handler = ListHandler()
    prod_handler.setLevel(logging.DEBUG)  # 핸들러는 모든 레벨 수집
    prod_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
    prod_logger.addHandler(prod_handler)

    # production 앱 테스트
    prod_handler.records.clear()
    response = client.get("/status")
    assert response.status_code == 200

    # production 모드에서는 DEBUG 로그가 기록되지 않아야 함
    debug_logs = [r for r in prod_handler.records if "DEBUG" in r]
    assert len(debug_logs) == 0
    print("✓ production 모드: DEBUG 로그가 기록되지 않음")

    # production 모드에서는 WARNING 로그가 기록되어야 함
    warning_logs = [r for r in prod_handler.records if "WARNING" in r]
    assert len(warning_logs) >= 1
    print("✓ production 모드: WARNING 로그가 기록됨")

    print("\n모든 테스트를 통과했습니다!")
