# 실행: python exercise.py
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


# --- TODO 1: authenticate_user 함수를 작성하세요 ---
# 매개변수: username (str), password (str)
# 1. fake_users_db에서 username으로 사용자를 조회합니다
# 2. 사용자가 없으면 None을 반환합니다
# 3. verify_password()로 비밀번호를 검증합니다
# 4. 비밀번호가 틀리면 None을 반환합니다
# 5. 검증 통과 시 사용자 정보(dict)를 반환합니다
def authenticate_user(username: str, password: str) -> dict | None:
    pass


# --- TODO 2: get_current_user 의존성 함수를 작성하세요 ---
# 매개변수: token (str) - Depends(oauth2_scheme)로 자동 주입됩니다
# 1. decode_access_token()으로 토큰을 디코딩합니다
# 2. 디코딩 실패 시 HTTPException(401)을 발생시킵니다
# 3. 페이로드에서 "sub" (사용자명)을 추출합니다
# 4. "sub"가 없으면 HTTPException(401)을 발생시킵니다
# 5. fake_users_db에서 사용자를 조회합니다
# 6. 사용자가 없으면 HTTPException(401)을 발생시킵니다
# 7. 사용자 정보를 반환합니다
#
# HTTPException 형식:
#   status_code=status.HTTP_401_UNAUTHORIZED,
#   detail="자격 증명을 확인할 수 없습니다",
#   headers={"WWW-Authenticate": "Bearer"},
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    pass


# --- TODO 3: POST /register 엔드포인트를 작성하세요 ---
# 1. fake_users_db에 이미 같은 username이 있으면 HTTPException(400) 발생
#    detail="이미 존재하는 사용자입니다"
# 2. hash_password()로 비밀번호를 해싱합니다
# 3. fake_users_db에 사용자 정보를 저장합니다
#    키: username, 값: {"username": ..., "email": ..., "hashed_password": ...}
# 4. {"message": "회원가입이 완료되었습니다"} 를 반환합니다
@app.post("/register")
async def register(user: UserCreate):
    pass


# --- TODO 4: POST /token 엔드포인트를 작성하세요 ---
# 매개변수: form_data (OAuth2PasswordRequestForm) - Depends()로 주입
# 1. authenticate_user()로 사용자를 인증합니다
# 2. 인증 실패 시 HTTPException(401) 발생
#    detail="사용자명 또는 비밀번호가 올바르지 않습니다"
#    headers={"WWW-Authenticate": "Bearer"}
# 3. create_access_token()으로 토큰을 생성합니다
#    data={"sub": username}
# 4. {"access_token": token, "token_type": "bearer"} 를 반환합니다
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    pass


# --- TODO 5: GET /users/me 엔드포인트를 작성하세요 ---
# 매개변수: current_user (dict) - Depends(get_current_user)로 주입
# 반환값: {"username": ..., "email": ...}
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    pass


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
