# 실행 방법: uvicorn solution:app --reload
# 필요 패키지: pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart

"""
챕터 06 모범 답안: 인증과 보안 기초

문제 1~4의 통합 솔루션입니다.
모든 기능이 하나의 파일에 구현되어 있습니다.
"""

from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# ── 보안 설정 ──────────────────────────────────────────────
SECRET_KEY = "학습용-시크릿-키-프로덕션에서는-반드시-변경하세요"
REFRESH_SECRET_KEY = "리프레시-전용-시크릿-키"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ── 앱 초기화 ──────────────────────────────────────────────
app = FastAPI(title="인증 종합 예제", description="챕터 06 연습문제 모범 답안")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ── 임시 사용자 데이터베이스 ────────────────────────────────
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("testpass"),
        "email": "test@example.com",
        "role": "user",  # 문제 3: 역할 추가
    },
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("adminpass"),
        "email": "admin@example.com",
        "role": "admin",  # 문제 3: 관리자 역할
    },
}


# ── Pydantic 모델 ─────────────────────────────────────────
class Token(BaseModel):
    """토큰 응답 모델 (문제 4: refresh_token 추가)"""
    access_token: str
    refresh_token: str  # 문제 4: 리프레시 토큰 필드
    token_type: str


class AccessToken(BaseModel):
    """액세스 토큰만 반환하는 모델"""
    access_token: str
    token_type: str


class User(BaseModel):
    """사용자 정보 모델"""
    username: str
    email: str
    role: str  # 문제 3: 역할 필드 추가


class UserCreate(BaseModel):
    """문제 1: 회원가입 요청 모델"""
    username: str
    password: str
    email: str


class UserCreateResponse(BaseModel):
    """문제 1: 회원가입 응답 모델"""
    username: str
    email: str
    message: str


class TokenVerifyResponse(BaseModel):
    """문제 2: 토큰 검증 응답 모델"""
    valid: bool
    username: str
    expires_in_seconds: int


class RefreshTokenRequest(BaseModel):
    """문제 4: 리프레시 토큰 요청 모델"""
    refresh_token: str


# ── 유틸리티 함수 ──────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해싱된 비밀번호를 비교합니다."""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> dict | None:
    """사용자명과 비밀번호로 인증합니다."""
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT 액세스 토큰을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """문제 4: JWT 리프레시 토큰을 생성합니다."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    # 리프레시 토큰은 별도의 시크릿 키를 사용합니다
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


# ── 의존성 함수 ────────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """토큰에서 현재 사용자를 추출합니다."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        if username is None:
            raise credentials_exception
        # 문제 4: 리프레시 토큰을 액세스 토큰으로 사용하는 것을 방지
        if token_type != "access":
            raise credentials_exception
    except ExpiredSignatureError:
        # 문제 2: 만료된 토큰에 대한 명확한 메시지
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다. 다시 로그인해주세요.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception

    user = fake_users_db.get(username)
    if user is None:
        raise credentials_exception

    return User(username=user["username"], email=user["email"], role=user["role"])


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """문제 3: 관리자 권한을 확인하는 의존성 함수입니다."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return current_user


# ── 엔드포인트 ─────────────────────────────────────────────

# === 문제 1: 회원가입 ===
@app.post(
    "/register",
    response_model=UserCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
)
async def register(user_data: UserCreate):
    """
    새로운 사용자를 등록합니다.
    이미 존재하는 사용자명이면 400 에러를 반환합니다.
    """
    # 중복 사용자 확인
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 사용자명입니다",
        )

    # 비밀번호 해싱 후 저장
    fake_users_db[user_data.username] = {
        "username": user_data.username,
        "hashed_password": pwd_context.hash(user_data.password),
        "email": user_data.email,
        "role": "user",  # 기본 역할은 일반 사용자
    }

    return UserCreateResponse(
        username=user_data.username,
        email=user_data.email,
        message="회원가입이 완료되었습니다",
    )


# === 로그인 (문제 4: 리프레시 토큰 포함) ===
@app.post("/token", response_model=Token, summary="로그인 (토큰 발급)")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    사용자명과 비밀번호로 로그인합니다.
    액세스 토큰과 리프레시 토큰을 함께 발급합니다.

    테스트 계정:
    - username: testuser, password: testpass
    - username: admin, password: adminpass
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 사용자명 또는 비밀번호입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 토큰 페이로드에 역할 정보 포함 (문제 3)
    token_data = {"sub": user["username"], "role": user["role"]}

    # 액세스 토큰 생성
    access_token = create_access_token(data=token_data)

    # 문제 4: 리프레시 토큰 생성
    refresh_token = create_refresh_token(data={"sub": user["username"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# === 문제 2: 토큰 검증 ===
@app.get("/token/verify", response_model=TokenVerifyResponse, summary="토큰 유효성 확인")
async def verify_token(token: str = Depends(oauth2_scheme)):
    """
    토큰의 유효성을 확인하고 남은 만료 시간을 반환합니다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        exp: int = payload.get("exp")

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
            )

        # 남은 시간 계산 (초 단위)
        now = datetime.utcnow().timestamp()
        expires_in = int(exp - now)

        return TokenVerifyResponse(
            valid=True,
            username=username,
            expires_in_seconds=max(expires_in, 0),
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다. 다시 로그인해주세요.",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
        )


# === 문제 4: 리프레시 토큰으로 액세스 토큰 갱신 ===
@app.post("/token/refresh", response_model=AccessToken, summary="토큰 갱신")
async def refresh_access_token(request: RefreshTokenRequest):
    """
    리프레시 토큰을 사용하여 새로운 액세스 토큰을 발급받습니다.
    """
    try:
        # 리프레시 전용 시크릿 키로 검증
        payload = jwt.decode(
            request.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        # 리프레시 토큰인지 확인
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다",
            )

        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 리프레시 토큰입니다",
            )

        # 사용자 존재 확인
        user = fake_users_db.get(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="사용자를 찾을 수 없습니다",
            )

        # 새로운 액세스 토큰 발급
        token_data = {"sub": username, "role": user["role"]}
        new_access_token = create_access_token(data=token_data)

        return {"access_token": new_access_token, "token_type": "bearer"}

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="리프레시 토큰이 만료되었습니다. 다시 로그인해주세요.",
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다",
        )


# === 문제 3: 역할 기반 접근 제어 ===
@app.get("/admin/users", summary="관리자: 전체 사용자 목록")
async def get_all_users(admin: User = Depends(get_current_admin_user)):
    """관리자만 접근 가능한 전체 사용자 목록입니다."""
    users = [
        {"username": u["username"], "email": u["email"], "role": u["role"]}
        for u in fake_users_db.values()
    ]
    return {"users": users}


@app.get("/users/me", response_model=User, summary="현재 사용자 정보")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """인증된 모든 사용자가 접근 가능합니다."""
    return current_user
