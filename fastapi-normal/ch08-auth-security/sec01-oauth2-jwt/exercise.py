# 실행: python exercise.py
# 필요 패키지: pip install python-jose[cryptography]

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# --- 설정 ---
SECRET_KEY = "학습용-비밀키-실제-운영에서는-안전한-키를-사용하세요"
ALGORITHM = "HS256"


# TODO: create_access_token 함수를 작성하세요
# 매개변수: data (dict), expires_delta (timedelta, 기본값=timedelta(minutes=30))
# 1. data를 복사합니다 (원본 변경 방지)
# 2. 현재 UTC 시간 + expires_delta로 만료 시간을 계산합니다
# 3. 복사된 데이터에 "exp" 키로 만료 시간을 추가합니다
# 4. jwt.encode()로 인코딩하여 반환합니다
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    pass


# TODO: decode_access_token 함수를 작성하세요
# 매개변수: token (str)
# 1. jwt.decode()로 토큰을 디코딩합니다
#    - algorithms 매개변수는 리스트로 전달합니다: algorithms=[ALGORITHM]
# 2. 성공하면 디코딩된 페이로드(dict)를 반환합니다
# 3. JWTError 예외가 발생하면 None을 반환합니다
def decode_access_token(token: str) -> dict | None:
    pass


# --- 테스트 (수정하지 마세요) ---
if __name__ == "__main__":
    # 토큰 생성 테스트
    token = create_access_token({"sub": "user@example.com", "role": "admin"})
    assert token is not None, "create_access_token이 None을 반환했습니다"
    assert isinstance(token, str), "토큰은 문자열이어야 합니다"
    assert len(token.split(".")) == 3, "JWT는 3개의 파트로 구성되어야 합니다"
    print(f"✓ 토큰 생성 성공: {token[:50]}...")

    # 토큰 디코딩 테스트
    payload = decode_access_token(token)
    assert payload is not None, "decode_access_token이 None을 반환했습니다"
    assert payload["sub"] == "user@example.com", "sub 클레임이 일치하지 않습니다"
    assert payload["role"] == "admin", "role 클레임이 일치하지 않습니다"
    assert "exp" in payload, "exp 클레임이 페이로드에 없습니다"
    print(f"✓ 토큰 디코딩 성공: sub={payload['sub']}")

    # 만료된 토큰 테스트
    expired_token = create_access_token(
        {"sub": "expired@example.com"},
        expires_delta=timedelta(seconds=-1)
    )
    result = decode_access_token(expired_token)
    assert result is None, "만료된 토큰은 None을 반환해야 합니다"
    print("✓ 만료 토큰 검증 테스트 통과")

    # 잘못된 토큰 테스트
    result = decode_access_token("invalid.token.here")
    assert result is None, "잘못된 토큰은 None을 반환해야 합니다"
    print("✓ 잘못된 토큰 검증 테스트 통과")

    print("\n모든 테스트를 통과했습니다!")
