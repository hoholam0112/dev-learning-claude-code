# 실행 방법: uvicorn example-01:app --reload
# 필요 패키지: pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart
# 테스트: http://127.0.0.1:8000/docs 에서 Swagger UI로 테스트

"""
챕터 06 예제 01: 간단한 토큰 인증 (OAuth2PasswordBearer)

이 예제에서는 다음을 학습합니다:
- OAuth2 Password Flow를 활용한 로그인
- JWT 토큰 생성 및 검증
- 비밀번호 해싱
- 보호된 엔드포인트 구현
"""

from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ── 보안 설정 ──────────────────────────────────────────────
SECRET_KEY = "학습용-시크릿-키-프로덕션에서는-반드시-변경하세요"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ── 앱 초기화 ──────────────────────────────────────────────
app = FastAPI(title="인증 예제", description="OAuth2 + JWT 기본 인증 예제")

# 비밀번호 해싱 컨텍스트 (bcrypt 알고리즘 사용)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 토큰 추출 의존성 (tokenUrl은 토큰 발급 엔드포인트 경로)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ── 임시 사용자 데이터베이스 ────────────────────────────────
# 실제로는 데이터베이스를 사용해야 합니다
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("testpass"),
        "email": "test@example.com",
    },
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("adminpass"),
        "email": "admin@example.com",
    },
}


# ── Pydantic 모델 ─────────────────────────────────────────
class Token(BaseModel):
    """토큰 응답 모델"""
    access_token: str
    token_type: str


class User(BaseModel):
    """사용자 정보 모델 (비밀번호 제외)"""
    username: str
    email: str


# ── 유틸리티 함수 ──────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해싱된 비밀번호를 비교합니다."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> dict | None:
    """사용자명과 비밀번호로 인증합니다. 실패 시 None을 반환합니다."""
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT 액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    # JWT 인코딩
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ── 의존성 함수 ────────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    토큰에서 현재 사용자를 추출하는 의존성 함수입니다.
    토큰이 유효하지 않으면 401 에러를 반환합니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 사용자 조회
    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception

    return User(username=user["username"], email=user["email"])


# ── 엔드포인트 ─────────────────────────────────────────────
@app.post("/token", response_model=Token, summary="로그인 (토큰 발급)")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    사용자명과 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.

    테스트 계정:
    - username: testuser, password: testpass
    - username: admin, password: adminpass
    """
    # 사용자 인증
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=User, summary="현재 사용자 정보 조회")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    인증된 현재 사용자의 정보를 반환합니다.
    Authorization 헤더에 Bearer 토큰이 필요합니다.
    """
    return current_user


@app.get("/protected-data", summary="보호된 데이터 조회")
async def read_protected_data(current_user: User = Depends(get_current_user)):
    """인증된 사용자만 접근할 수 있는 데이터를 반환합니다."""
    return {
        "message": f"{current_user.username}님, 보호된 데이터에 접근했습니다!",
        "secret_data": [
            {"id": 1, "value": "비밀 데이터 A"},
            {"id": 2, "value": "비밀 데이터 B"},
        ],
    }


@app.get("/public-data", summary="공개 데이터 조회")
async def read_public_data():
    """인증 없이 누구나 접근할 수 있는 공개 데이터입니다."""
    return {
        "message": "이 데이터는 누구나 볼 수 있습니다",
        "data": [
            {"id": 1, "value": "공개 데이터 A"},
            {"id": 2, "value": "공개 데이터 B"},
        ],
    }
