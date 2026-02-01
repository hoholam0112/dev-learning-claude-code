# 실행 방법: uvicorn exercise:app --reload
# 필요 패키지: pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart
# 챕터 06 연습 문제 - 직접 코드를 작성해보세요!

from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# ── 보안 설정 ──────────────────────────────────────────────
SECRET_KEY = "학습용-시크릿-키-프로덕션에서는-반드시-변경하세요"
REFRESH_SECRET_KEY = "리프레시-전용-시크릿-키"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# ── 앱 초기화 ──────────────────────────────────────────────
app = FastAPI(title="챕터 06 연습 문제", description="인증과 보안 기초")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# ── 임시 사용자 데이터베이스 ────────────────────────────────
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "hashed_password": pwd_context.hash("testpass"),
        "email": "test@example.com",
        "role": "user",
    },
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("adminpass"),
        "email": "admin@example.com",
        "role": "admin",
    },
}


# ── Pydantic 모델 ─────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class User(BaseModel):
    username: str
    email: str
    role: str


class UserCreate(BaseModel):
    username: str
    password: str
    email: str


class UserCreateResponse(BaseModel):
    username: str
    email: str
    message: str


class TokenVerifyResponse(BaseModel):
    valid: bool
    username: str
    expires_in_seconds: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ── 유틸리티 함수 ──────────────────────────────────────────
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해싱된 비밀번호를 비교합니다."""
    # TODO: pwd_context.verify()를 사용하세요
    pass


def authenticate_user(username: str, password: str) -> dict | None:
    """사용자명과 비밀번호로 인증합니다."""
    # TODO: fake_users_db에서 사용자를 찾고 비밀번호를 검증하세요
    # 실패 시 None 반환
    pass


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT 액세스 토큰을 생성합니다."""
    # TODO: jwt.encode()로 토큰을 생성하세요
    # 힌트: {"sub": username, "exp": expire, "type": "access"}
    pass


def create_refresh_token(data: dict) -> str:
    """JWT 리프레시 토큰을 생성합니다."""
    # TODO: REFRESH_SECRET_KEY로 리프레시 토큰을 생성하세요
    # 힌트: {"sub": username, "exp": expire, "type": "refresh"}
    pass


# ── 의존성 함수 ────────────────────────────────────────────
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """토큰에서 현재 사용자를 추출합니다."""
    # TODO: jwt.decode()로 토큰을 검증하고 사용자 정보를 반환하세요
    # - 리프레시 토큰을 액세스 토큰으로 사용하는 것을 방지 (type 확인)
    # - 만료된 토큰에 대한 명확한 메시지
    pass


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """관리자 권한을 확인하는 의존성입니다."""
    # TODO: current_user.role이 "admin"이 아니면 403 에러
    pass


# ── 엔드포인트 ─────────────────────────────────────────────

# === 문제 1: 회원가입 ===
@app.post("/register", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """새로운 사용자를 등록합니다."""
    # TODO: 중복 사용자 확인 → 비밀번호 해싱 → fake_users_db에 저장
    pass


# === 로그인 (문제 4: 리프레시 토큰 포함) ===
@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """로그인하여 액세스 토큰과 리프레시 토큰을 발급합니다.
    테스트 계정: testuser/testpass, admin/adminpass
    """
    # TODO: authenticate_user로 인증 → 액세스/리프레시 토큰 생성 → 반환
    pass


# === 문제 2: 토큰 검증 ===
@app.get("/token/verify", response_model=TokenVerifyResponse)
async def verify_token(token: str = Depends(oauth2_scheme)):
    """토큰의 유효성을 확인하고 남은 만료 시간을 반환합니다."""
    # TODO: jwt.decode()로 토큰을 디코딩하고 남은 시간 계산
    pass


# === 문제 4: 리프레시 토큰으로 액세스 토큰 갱신 ===
@app.post("/token/refresh", response_model=AccessToken)
async def refresh_access_token(request: RefreshTokenRequest):
    """리프레시 토큰으로 새 액세스 토큰을 발급합니다."""
    # TODO: REFRESH_SECRET_KEY로 리프레시 토큰 검증 → 새 액세스 토큰 발급
    pass


# === 문제 3: 역할 기반 접근 제어 ===
@app.get("/admin/users")
async def get_all_users(admin: User = Depends(get_current_admin_user)):
    """관리자만 접근 가능한 전체 사용자 목록입니다."""
    # TODO: fake_users_db의 사용자 목록을 반환하세요 (비밀번호 제외)
    pass


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """현재 사용자 정보를 반환합니다."""
    # TODO: current_user를 반환하세요
    pass
