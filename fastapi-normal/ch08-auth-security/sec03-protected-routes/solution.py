# 실행: python solution.py
# 이 파일은 exercise.py의 모범 답안입니다.
# 필요 패키지: pip install "fastapi[standard]" "python-jose[cryptography]" "passlib[bcrypt]" bcrypt httpx

from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.testclient import TestClient
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel

# --- 앱 설정 ---
app = FastAPI(title="인증 시스템 연습")

# --- 보안 설정 ---
SECRET_KEY = "학습용-비밀키-실제-운영에서는-안전한-키를-사용하세요"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- 가상 데이터베이스 ---
fake_users_db: dict = {}


# --- Pydantic 모델 ---
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


# --- 유틸리티 함수 (이미 구현됨) ---
def hash_password(plain_password: str) -> str:
    """비밀번호를 bcrypt로 해싱합니다."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호를 검증합니다."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=30)) -> str:
    """JWT 토큰을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """JWT 토큰을 디코딩합니다. 실패 시 None 반환."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def authenticate_user(username: str, password: str) -> dict | None:
    """
    사용자명과 비밀번호로 사용자를 인증합니다.

    인증 과정:
    1. DB에서 사용자를 찾습니다.
    2. 입력된 비밀번호와 저장된 해시를 비교합니다.
    3. 모든 검증을 통과하면 사용자 정보를 반환합니다.

    Args:
        username: 사용자명
        password: 평문 비밀번호

    Returns:
        인증 성공 시 사용자 정보 dict, 실패 시 None
    """
    # 1. DB에서 사용자 조회
    user = fake_users_db.get(username)
    if user is None:
        # 사용자가 존재하지 않음
        return None

    # 2. 비밀번호 검증
    # verify_password는 평문 비밀번호를 해싱하여 저장된 해시와 비교합니다.
    if not verify_password(password, user["hashed_password"]):
        # 비밀번호 불일치
        return None

    # 3. 인증 성공 - 사용자 정보 반환
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    JWT 토큰에서 현재 사용자를 추출하는 의존성 함수.

    이 함수는 보호된 엔드포인트에 Depends()로 주입됩니다.
    OAuth2PasswordBearer가 Authorization 헤더에서 토큰을 자동으로 추출하고,
    이 함수가 토큰을 검증하여 사용자 정보를 반환합니다.

    Args:
        token: OAuth2PasswordBearer에서 추출한 JWT 토큰 문자열

    Returns:
        인증된 사용자 정보 dict

    Raises:
        HTTPException: 토큰이 유효하지 않거나 사용자를 찾을 수 없는 경우
    """
    # 인증 실패 시 반환할 에러를 미리 정의합니다.
    # WWW-Authenticate 헤더는 OAuth2 표준에서 요구하는 사항입니다.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="자격 증명을 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. 토큰 디코딩
    payload = decode_access_token(token)
    if payload is None:
        # 토큰이 만료되었거나 형식이 잘못된 경우
        raise credentials_exception

    # 2. 페이로드에서 사용자 식별자 추출
    # "sub" (subject)은 JWT 표준 클레임으로, 토큰의 주체를 나타냅니다.
    username: str = payload.get("sub")
    if username is None:
        # 토큰에 사용자 정보가 없는 경우
        raise credentials_exception

    # 3. DB에서 사용자 조회
    user = fake_users_db.get(username)
    if user is None:
        # 토큰은 유효하지만 사용자가 DB에 없는 경우
        # (사용자가 삭제되었을 수 있음)
        raise credentials_exception

    # 4. 인증된 사용자 정보 반환
    return user


@app.post("/register")
async def register(user: UserCreate):
    """
    회원가입 엔드포인트.

    새 사용자를 등록합니다. 비밀번호는 bcrypt로 해싱하여 저장합니다.
    절대로 평문 비밀번호를 DB에 저장하지 않습니다.
    """
    # 1. 중복 사용자 확인
    if user.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자입니다"
        )

    # 2. 비밀번호 해싱 후 사용자 정보 저장
    # hash_password()는 bcrypt로 해싱하며, 매번 다른 솔트를 사용합니다.
    fake_users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hash_password(user.password),  # 해시된 비밀번호만 저장!
    }

    # 3. 성공 응답
    return {"message": "회원가입이 완료되었습니다"}


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    로그인 엔드포인트 (토큰 발급).

    OAuth2 Password Flow에 따라:
    1. 폼 데이터로 username과 password를 받습니다.
    2. 자격 증명을 검증합니다.
    3. JWT 액세스 토큰을 발급합니다.

    주의: 이 엔드포인트는 JSON이 아니라 폼 데이터(application/x-www-form-urlencoded)를 받습니다.
    TestClient에서는 json= 대신 data= 를 사용해야 합니다.
    """
    # 1. 사용자 인증
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        # 인증 실패 (사용자 없음 또는 비밀번호 불일치)
        # 보안 상 어떤 이유로 실패했는지 구체적으로 알려주지 않습니다.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. JWT 토큰 생성
    # "sub" 클레임에 사용자명을 넣어 나중에 토큰에서 사용자를 식별합니다.
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    # 3. 토큰 반환 (OAuth2 표준 응답 형식)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    현재 로그인한 사용자 정보 조회 (보호된 엔드포인트).

    Depends(get_current_user)를 통해:
    1. Authorization 헤더에서 JWT 토큰이 자동으로 추출됩니다.
    2. 토큰이 검증되고 사용자 정보가 current_user에 주입됩니다.
    3. 토큰이 없거나 유효하지 않으면 자동으로 401 에러가 반환됩니다.
    """
    # current_user에는 get_current_user가 반환한 사용자 정보가 들어있습니다.
    # hashed_password는 응답에 포함하지 않습니다 (보안).
    return {
        "username": current_user["username"],
        "email": current_user["email"],
    }


# --- 테스트 (수정하지 마세요) ---
if __name__ == "__main__":
    client = TestClient(app)

    # 테스트 전 DB 초기화
    fake_users_db.clear()

    # 테스트 1: 회원가입
    response = client.post("/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 200, f"회원가입 실패: {response.json()}"
    assert "회원가입" in response.json()["message"]
    print("✓ 회원가입 성공")

    # 테스트 2: 로그인 및 토큰 발급
    response = client.post("/token", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200, f"로그인 실패: {response.json()}"
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    access_token = token_data["access_token"]
    print("✓ 로그인 및 토큰 발급 성공")

    # 테스트 3: 보호된 엔드포인트 접근
    response = client.get("/users/me", headers={
        "Authorization": f"Bearer {access_token}"
    })
    assert response.status_code == 200, f"사용자 조회 실패: {response.json()}"
    user_data = response.json()
    assert user_data["username"] == "testuser"
    assert user_data["email"] == "test@example.com"
    print("✓ 보호된 엔드포인트 접근 성공")

    # 테스트 4: 인증 없이 접근 시 401 에러
    response = client.get("/users/me")
    assert response.status_code == 401, "인증 없이 접근했는데 401이 아닙니다"
    print("✓ 인증 없이 접근 시 401 에러 확인")

    # 테스트 5: 잘못된 비밀번호로 로그인
    response = client.post("/token", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == 401, "잘못된 비밀번호인데 401이 아닙니다"
    print("✓ 잘못된 비밀번호로 로그인 실패 확인")

    # 테스트 6: 존재하지 않는 사용자로 로그인
    response = client.post("/token", data={
        "username": "nonexistent",
        "password": "anypassword"
    })
    assert response.status_code == 401, "존재하지 않는 사용자인데 401이 아닙니다"
    print("✓ 존재하지 않는 사용자 로그인 실패 확인")

    # 테스트 7: 잘못된 토큰으로 접근
    response = client.get("/users/me", headers={
        "Authorization": "Bearer invalid.token.here"
    })
    assert response.status_code == 401, "잘못된 토큰인데 401이 아닙니다"
    print("✓ 잘못된 토큰으로 접근 시 401 에러 확인")

    print("\n모든 테스트를 통과했습니다!")
