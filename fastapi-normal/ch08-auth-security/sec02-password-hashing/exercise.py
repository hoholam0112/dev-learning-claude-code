# 실행: python exercise.py
# 필요 패키지: pip install "passlib[bcrypt]" bcrypt

from passlib.context import CryptContext

# --- 설정 ---
# bcrypt 알고리즘을 사용하는 해싱 컨텍스트를 생성합니다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# TODO: hash_password 함수를 작성하세요
# 매개변수: plain_password (str) - 평문 비밀번호
# 반환값: str - bcrypt로 해싱된 비밀번호
# pwd_context.hash()를 사용하세요
def hash_password(plain_password: str) -> str:
    pass


# TODO: verify_password 함수를 작성하세요
# 매개변수: plain_password (str) - 사용자가 입력한 평문 비밀번호
#           hashed_password (str) - DB에 저장된 해시된 비밀번호
# 반환값: bool - 일치하면 True, 불일치하면 False
# pwd_context.verify()를 사용하세요
def verify_password(plain_password: str, hashed_password: str) -> bool:
    pass


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
