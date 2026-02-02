# 실행: uvicorn exercise:app --reload
# 테스트: python exercise.py

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


# TODO 1: dictConfig로 로깅을 설정하세요
# LOGGING_CONFIG 딕셔너리를 작성하고 logging.config.dictConfig()를 호출하세요
# - version: 1
# - disable_existing_loggers: False
# - formatters: "simple" 포매터 (format: "%(levelname)s - %(message)s")
# - handlers: "console" 핸들러 (logging.StreamHandler, DEBUG 레벨, "simple" 포매터)
# - loggers: "app" 로거 (DEBUG 레벨, ["console"] 핸들러, propagate=False)
#
# 힌트:
# LOGGING_CONFIG = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": { "simple": { "format": "%(levelname)s - %(message)s" } },
#     "handlers": { "console": { "class": "logging.StreamHandler", "level": "DEBUG", "formatter": "simple" } },
#     "loggers": { "app": { "level": "DEBUG", "handlers": ["console"], "propagate": False } },
# }
# logging.config.dictConfig(LOGGING_CONFIG)


# TODO 2: 로거를 가져오고 테스트용 ListHandler를 추가하세요
# - logging.getLogger("app")으로 로거 가져오기
# - ListHandler 인스턴스 생성, DEBUG 레벨 설정
# - Formatter("%(levelname)s - %(message)s") 설정
# - 로거에 핸들러 추가
#
# 힌트:
# logger = logging.getLogger("app")
# list_handler = ListHandler()
# list_handler.setLevel(logging.DEBUG)
# list_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
# logger.addHandler(list_handler)


# TODO 3: get_logging_config 함수를 구현하세요
# - environment 파라미터를 받음 (기본값: "development")
# - "development": DEBUG 레벨
#   포맷: "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
# - "production": WARNING 레벨
#   포맷: "%(message)s"
# - 둘 다 "app" 로거 설정, propagate=False
#
# 힌트:
# def get_logging_config(environment: str = "development"):
#     if environment == "production":
#         return { "version": 1, ..., "loggers": {"app": {"level": "WARNING", ...}} }
#     else:
#         return { "version": 1, ..., "loggers": {"app": {"level": "DEBUG", ...}} }


app = FastAPI()


# TODO 4: GET /hello 엔드포인트를 구현하세요
# - logger.info("안녕하세요") 호출
# - {"message": "안녕하세요"} 반환


# TODO 5: GET /status 엔드포인트를 구현하세요
# - logger.debug("상태 확인 중...") 호출
# - logger.warning("디스크 용량 부족 경고") 호출
# - {"status": "running"} 반환


# --- 테스트 ---
if __name__ == "__main__":
    client = TestClient(app)

    # === 문제 1 테스트: dictConfig 로거 ===

    list_handler.records.clear()

    # 테스트 1: dictConfig로 설정한 로거 동작 확인
    response = client.get("/hello")
    assert response.status_code == 200, (
        f"GET /hello의 상태 코드가 200이어야 합니다. 현재: {response.status_code}"
    )
    assert response.json() == {"message": "안녕하세요"}, (
        f"응답 본문이 올바르지 않습니다. 현재: {response.json()}"
    )
    assert len(list_handler.records) >= 1, (
        "로그가 기록되지 않았습니다. dictConfig 설정과 list_handler 추가를 확인하세요."
    )
    print("✓ dictConfig로 설정한 로거가 정상 동작")

    # 테스트 2: 포맷 확인
    assert "INFO - 안녕하세요" in list_handler.records[0], (
        f"로그 포맷이 올바르지 않습니다. 기대: 'INFO - 안녕하세요', 현재: {list_handler.records[0]}"
    )
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
    assert response.status_code == 200, (
        f"GET /status의 상태 코드가 200이어야 합니다. 현재: {response.status_code}"
    )

    # development 모드에서는 DEBUG 로그가 기록되어야 함
    debug_logs = [r for r in dev_handler.records if "DEBUG" in r]
    assert len(debug_logs) >= 1, (
        f"development 모드에서 DEBUG 로그가 기록되어야 합니다. "
        f"현재 기록된 로그: {dev_handler.records}"
    )
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
    assert len(debug_logs) == 0, (
        f"production 모드에서 DEBUG 로그가 기록되면 안 됩니다. "
        f"현재 기록된 로그: {prod_handler.records}"
    )
    print("✓ production 모드: DEBUG 로그가 기록되지 않음")

    # production 모드에서는 WARNING 로그가 기록되어야 함
    warning_logs = [r for r in prod_handler.records if "WARNING" in r]
    assert len(warning_logs) >= 1, (
        f"production 모드에서 WARNING 로그가 기록되어야 합니다. "
        f"현재 기록된 로그: {prod_handler.records}"
    )
    print("✓ production 모드: WARNING 로그가 기록됨")

    print("\n모든 테스트를 통과했습니다!")
