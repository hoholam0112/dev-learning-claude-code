# 실행: python solution.py
# 이 파일은 exercise.py의 모범 답안입니다.
# 필요 패키지: pip install python-jose[cryptography]

from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

# --- 설정 ---
SECRET_KEY = "학습용-비밀키-실제-운영에서는-안전한-키를-사용하세요"
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    """
    JWT 액세스 토큰을 생성합니다.

    Args:
        data: 토큰에 담을 데이터 (예: {"sub": "user@example.com"})
        expires_delta: 만료 시간 간격 (기본값: 30분)

    Returns:
        인코딩된 JWT 토큰 문자열
    """
    # 1. 원본 데이터를 변경하지 않기 위해 복사합니다.
    #    dict.copy()를 사용하면 원본 딕셔너리는 그대로 유지됩니다.
    to_encode = data.copy()

    # 2. 만료 시간을 계산합니다.
    #    현재 UTC 시간에 expires_delta를 더합니다.
    #    timezone.utc를 사용하여 시간대를 명확히 합니다.
    expire = datetime.now(timezone.utc) + expires_delta

    # 3. 페이로드에 만료 시간("exp")을 추가합니다.
    #    "exp"는 JWT 표준 클레임으로, python-jose가 자동으로 만료 검증에 사용합니다.
    to_encode.update({"exp": expire})

    # 4. JWT 토큰을 인코딩하여 반환합니다.
    #    jwt.encode()는 페이로드, 비밀 키, 알고리즘을 받아 토큰 문자열을 생성합니다.
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    JWT 토큰을 디코딩하고 검증합니다.

    jwt.decode()는 다음을 자동으로 수행합니다:
    - 서명(Signature) 검증: 토큰이 변조되지 않았는지 확인
    - 만료 시간(exp) 검증: 토큰이 만료되지 않았는지 확인
    - 형식 검증: JWT 구조가 올바른지 확인

    Args:
        token: JWT 토큰 문자열

    Returns:
        디코딩된 페이로드 딕셔너리, 실패 시 None
    """
    try:
        # jwt.decode()로 토큰을 디코딩합니다.
        # algorithms는 반드시 리스트로 전달해야 합니다.
        # 이는 보안상의 이유로, 허용할 알고리즘을 명시적으로 지정하는 것입니다.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # JWTError는 모든 JWT 관련 오류의 부모 클래스입니다:
        # - ExpiredSignatureError: 토큰 만료
        # - JWKError: 키 관련 오류
        # - JWTClaimsError: 클레임 검증 실패
        # - 기타 디코딩/서명 오류
        return None


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
