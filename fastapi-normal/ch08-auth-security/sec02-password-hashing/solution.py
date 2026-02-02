# 실행: python solution.py
# 이 파일은 exercise.py의 모범 답안입니다.
# 필요 패키지: pip install "passlib[bcrypt]" bcrypt

from passlib.context import CryptContext

# --- 설정 ---
# bcrypt 알고리즘을 사용하는 해싱 컨텍스트를 생성합니다.
# schemes: 사용할 해싱 알고리즘 목록 (bcrypt를 사용)
# deprecated: "auto"로 설정하면 새 알고리즘 추가 시 기존 알고리즘을 자동으로 비권장 처리합니다.
#             나중에 argon2 등 더 강력한 알고리즘으로 전환할 때 유용합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    평문 비밀번호를 bcrypt로 해싱합니다.

    bcrypt 해싱 과정:
    1. 무작위 솔트(salt)를 생성합니다.
    2. 비밀번호 + 솔트를 입력으로 해싱합니다.
    3. 알고리즘 식별자 + 라운드 수 + 솔트 + 해시를 합쳐 반환합니다.

    결과 형식: $2b$12$<솔트 22자><해시 31자> (총 60자)

    Args:
        plain_password: 평문 비밀번호

    Returns:
        bcrypt로 해싱된 비밀번호 문자열 (60자)
    """
    # pwd_context.hash()는 내부적으로:
    # 1. 무작위 솔트를 생성하고
    # 2. bcrypt 알고리즘으로 해싱하고
    # 3. 결과를 표준 형식의 문자열로 반환합니다.
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해시된 비밀번호를 비교합니다.

    검증 과정:
    1. 해시된 비밀번호에서 솔트를 추출합니다.
    2. 입력된 평문 비밀번호를 같은 솔트로 해싱합니다.
    3. 두 해시값을 비교합니다.

    이 과정을 통해 원본 비밀번호를 알지 못해도 일치 여부를 확인할 수 있습니다.

    Args:
        plain_password: 사용자가 입력한 평문 비밀번호
        hashed_password: 데이터베이스에 저장된 해시된 비밀번호

    Returns:
        일치하면 True, 불일치하면 False
    """
    # pwd_context.verify()는 내부적으로:
    # 1. hashed_password에서 알고리즘, 라운드 수, 솔트를 파싱하고
    # 2. plain_password를 같은 설정으로 해싱하고
    # 3. 결과를 비교하여 True/False를 반환합니다.
    #
    # 주의: 절대 hashed1 == hashed2로 비교하면 안 됩니다!
    # 같은 비밀번호라도 솔트가 달라서 해시값이 다릅니다.
    return pwd_context.verify(plain_password, hashed_password)


# --- 테스트 (수정하지 마세요) ---
if __name__ == "__main__":
    # 테스트 1: 비밀번호 해싱
    password = "secure_password_123"
    hashed = hash_password(password)
    assert hashed is not None, "hash_password가 None을 반환했습니다"
    assert isinstance(hashed, str), "해시된 비밀번호는 문자열이어야 합니다"
    assert len(hashed) == 60, f"bcrypt 해시는 60자여야 합니다 (현재: {len(hashed)}자)"
    assert hashed.startswith("$2b$"), "bcrypt 해시는 '$2b$'로 시작해야 합니다"
    assert hashed != password, "해시된 비밀번호는 원본과 달라야 합니다"
    print("✓ 비밀번호 해싱 성공 (60자 해시 생성)")

    # 테스트 2: 올바른 비밀번호 검증
    is_valid = verify_password(password, hashed)
    assert is_valid is True, "올바른 비밀번호는 True를 반환해야 합니다"
    print("✓ 올바른 비밀번호 검증 통과")

    # 테스트 3: 잘못된 비밀번호 검증
    is_valid = verify_password("wrong_password", hashed)
    assert is_valid is False, "잘못된 비밀번호는 False를 반환해야 합니다"
    print("✓ 잘못된 비밀번호 검증 통과")

    # 테스트 4: 같은 비밀번호를 두 번 해싱하면 다른 해시가 나옴 (솔트 때문)
    hashed_again = hash_password(password)
    assert hashed != hashed_again, "같은 비밀번호의 해시값은 매번 달라야 합니다 (솔트)"
    # 하지만 둘 다 원본 비밀번호와 일치해야 함
    assert verify_password(password, hashed_again) is True
    print("✓ 같은 비밀번호, 다른 해시 확인")

    # 테스트 5: 여러 비밀번호 테스트
    test_passwords = ["hello123", "P@ssw0rd!", "한글비밀번호도OK", "   spaces   "]
    for pw in test_passwords:
        h = hash_password(pw)
        assert verify_password(pw, h) is True, f"'{pw}' 검증 실패"
        assert verify_password(pw + "x", h) is False, f"'{pw}x' 가 통과하면 안 됩니다"
    print("✓ 여러 비밀번호 해싱/검증 통과")

    print("\n모든 테스트를 통과했습니다!")
