# 실행: python solution.py
# 이 파일은 exercise.py의 모범 답안입니다.
# 설치가 정상적으로 완료되었는지 확인하는 스크립트입니다.


def check_fastapi_installed() -> str:
    """FastAPI가 설치되었는지 확인하고 버전을 반환합니다."""
    # fastapi 모듈을 import합니다.
    # 대부분의 Python 패키지는 __version__ 속성으로 버전을 제공합니다.
    import fastapi

    return fastapi.__version__


def check_uvicorn_installed() -> str:
    """Uvicorn이 설치되었는지 확인하고 버전을 반환합니다."""
    # uvicorn도 마찬가지로 __version__ 속성을 가지고 있습니다.
    # uvicorn은 FastAPI 앱을 실행하는 ASGI 서버입니다.
    import uvicorn

    return uvicorn.__version__


def check_pydantic_installed() -> str:
    """Pydantic이 설치되었는지 확인하고 버전을 반환합니다."""
    # pydantic은 __version__ 대신 VERSION 상수를 사용합니다.
    # pydantic은 FastAPI의 데이터 검증을 담당하는 핵심 라이브러리입니다.
    # 참고: pydantic v2에서는 __version__도 사용 가능하지만,
    #       VERSION이 공식적으로 문서화된 방법입니다.
    import pydantic

    return pydantic.VERSION


# --- 테스트 (수정하지 마세요) ---
if __name__ == "__main__":
    fastapi_version = check_fastapi_installed()
    assert fastapi_version is not None, "FastAPI가 설치되지 않았습니다"
    print(f"FastAPI 버전: {fastapi_version}")

    uvicorn_version = check_uvicorn_installed()
    assert uvicorn_version is not None, "Uvicorn이 설치되지 않았습니다"
    print(f"Uvicorn 버전: {uvicorn_version}")

    pydantic_version = check_pydantic_installed()
    assert pydantic_version is not None, "Pydantic이 설치되지 않았습니다"
    print(f"Pydantic 버전: {pydantic_version}")

    print("\n모든 패키지가 정상적으로 설치되었습니다!")
