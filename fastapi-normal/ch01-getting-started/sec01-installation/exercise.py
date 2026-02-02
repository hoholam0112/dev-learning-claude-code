# 실행: python exercise.py
# 이 파일은 설치가 정상적으로 완료되었는지 확인하는 스크립트입니다.


def check_fastapi_installed() -> str:
    """FastAPI가 설치되었는지 확인하고 버전을 반환합니다."""
    # TODO: fastapi 모듈을 import하고 __version__을 반환하세요
    pass


def check_uvicorn_installed() -> str:
    """Uvicorn이 설치되었는지 확인하고 버전을 반환합니다."""
    # TODO: uvicorn 모듈을 import하고 __version__을 반환하세요
    pass


def check_pydantic_installed() -> str:
    """Pydantic이 설치되었는지 확인하고 버전을 반환합니다."""
    # TODO: pydantic 모듈을 import하고 VERSION을 반환하세요
    pass


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
