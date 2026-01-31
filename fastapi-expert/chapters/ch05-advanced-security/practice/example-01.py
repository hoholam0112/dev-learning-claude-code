# 실행 방법: uvicorn example-01:app --reload
# OAuth2 스코프와 RBAC 구현 예제
# 필요 패키지: pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt]

import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes
from pydantic import BaseModel, Field

# JWT 처리 (python-jose가 없으면 간단한 시뮬레이션 사용)
try:
    from jose import JWTError, jwt
    HAS_JOSE = True
except ImportError:
    HAS_JOSE = False
    import json
    import base64
    import hashlib
    import hmac

# 설정
SECRET_KEY = "your-secret-key-change-in-production-min-256-bits-long"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(
    title="OAuth2 스코프와 RBAC 구현",
    description="세분화된 권한 관리 시스템 예제",
)


# ============================================================
# 1. 권한 시스템 정의
# ============================================================

class Permission(str, Enum):
    """리소스:동작 형태의 권한"""
    USERS_READ = "users:read"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    ORDERS_READ = "orders:read"
    ORDERS_CREATE = "orders:create"
    ADMIN_PANEL = "admin:panel"
    ADMIN_SETTINGS = "admin:settings"


class Role(str, Enum):
    """사용자 역할"""
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


# 역할별 권한 매핑
ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.VIEWER: {
        Permission.USERS_READ,
        Permission.ORDERS_READ,
    },
    Role.EDITOR: {
        Permission.USERS_READ,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.ORDERS_READ,
        Permission.ORDERS_CREATE,
    },
    Role.ADMIN: {
        Permission.USERS_READ,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.USERS_DELETE,
        Permission.ORDERS_READ,
        Permission.ORDERS_CREATE,
        Permission.ADMIN_PANEL,
    },
    Role.SUPER_ADMIN: {p.value for p in Permission},  # 모든 권한
}


# ============================================================
# 2. 사용자 모델 및 데이터
# ============================================================

class UserInDB(BaseModel):
    """데이터베이스의 사용자 모델"""
    id: int
    username: str
    email: str
    hashed_password: str
    role: Role
    is_active: bool = True
    scopes: list[str] = []  # OAuth2 스코프


class UserResponse(BaseModel):
    """응답용 사용자 모델"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    permissions: list[str]


class Token(BaseModel):
    """토큰 응답"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    scopes: list[str]


class TokenData(BaseModel):
    """토큰 페이로드"""
    username: Optional[str] = None
    scopes: list[str] = []


# 시뮬레이션 사용자 데이터베이스
# 비밀번호는 모두 "password123" (실제로는 bcrypt 해시를 사용)
USERS_DB: dict[str, UserInDB] = {
    "admin": UserInDB(
        id=1,
        username="admin",
        email="admin@example.com",
        hashed_password="hashed_password123",
        role=Role.SUPER_ADMIN,
        scopes=list(p.value for p in Permission),
    ),
    "editor": UserInDB(
        id=2,
        username="editor",
        email="editor@example.com",
        hashed_password="hashed_password123",
        role=Role.EDITOR,
        scopes=[
            Permission.USERS_READ,
            Permission.USERS_CREATE,
            Permission.USERS_UPDATE,
            Permission.ORDERS_READ,
            Permission.ORDERS_CREATE,
        ],
    ),
    "viewer": UserInDB(
        id=3,
        username="viewer",
        email="viewer@example.com",
        hashed_password="hashed_password123",
        role=Role.VIEWER,
        scopes=[Permission.USERS_READ, Permission.ORDERS_READ],
    ),
}


# ============================================================
# 3. OAuth2 스키마 및 JWT 함수
# ============================================================

# OAuth2 스코프 정의
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "users:read": "사용자 정보 읽기",
        "users:create": "사용자 생성",
        "users:update": "사용자 수정",
        "users:delete": "사용자 삭제",
        "orders:read": "주문 정보 읽기",
        "orders:create": "주문 생성",
        "admin:panel": "관리자 패널 접근",
        "admin:settings": "관리자 설정 변경",
    },
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증 (시뮬레이션)"""
    return f"hashed_{plain_password}" == hashed_password


def create_access_token(
    data: dict, scopes: list[str], expires_delta: Optional[timedelta] = None,
) -> str:
    """JWT 액세스 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({
        "exp": expire.timestamp(),
        "scopes": scopes,
        "iat": datetime.now(timezone.utc).timestamp(),
    })

    if HAS_JOSE:
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    else:
        # python-jose가 없을 때 간단한 시뮬레이션
        payload = json.dumps(to_encode).encode()
        encoded = base64.urlsafe_b64encode(payload).decode()
        signature = hmac.new(
            SECRET_KEY.encode(), encoded.encode(), hashlib.sha256
        ).hexdigest()
        return f"{encoded}.{signature}"


def decode_access_token(token: str) -> dict:
    """JWT 토큰 디코딩"""
    if HAS_JOSE:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    else:
        # 간단한 시뮬레이션
        parts = token.split(".")
        if len(parts) != 2:
            raise ValueError("유효하지 않은 토큰")
        payload = base64.urlsafe_b64decode(parts[0])
        data = json.loads(payload)
        # 만료 확인
        if data.get("exp", 0) < time.time():
            raise ValueError("토큰이 만료되었습니다")
        return data


# ============================================================
# 4. 인증 의존성
# ============================================================

async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> UserInDB:
    """
    현재 인증된 사용자를 반환하는 의존성.
    SecurityScopes를 사용하여 요구 스코프를 자동 검증한다.
    """
    # 401 응답 헤더 구성
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(username=username, scopes=token_scopes)
    except Exception:
        raise credentials_exception

    # 사용자 조회
    user = USERS_DB.get(token_data.username)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="비활성화된 계정입니다",
        )

    # 스코프 검증: 요구되는 모든 스코프가 토큰에 포함되어야 함
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"권한 부족: '{scope}' 스코프가 필요합니다. "
                       f"현재 스코프: {token_data.scopes}",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def get_current_active_user(
    current_user: UserInDB = Security(get_current_user, scopes=[]),
) -> UserInDB:
    """활성화된 사용자만 반환"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="비활성화된 사용자")
    return current_user


# ============================================================
# 5. RBAC 의존성 팩토리
# ============================================================

def require_role(*roles: Role):
    """특정 역할을 요구하는 의존성 팩토리"""
    async def role_checker(
        current_user: UserInDB = Depends(get_current_active_user),
    ) -> UserInDB:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"역할 부족: {[r.value for r in roles]} 중 하나가 필요합니다. "
                       f"현재 역할: {current_user.role.value}",
            )
        return current_user
    return role_checker


def require_permission(*permissions: Permission):
    """특정 권한을 요구하는 의존성 팩토리"""
    async def permission_checker(
        current_user: UserInDB = Depends(get_current_active_user),
    ) -> UserInDB:
        user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
        missing = [
            p.value for p in permissions if p.value not in user_permissions
        ]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"권한 부족: {missing}",
            )
        return current_user
    return permission_checker


# ============================================================
# 6. 엔드포인트 정의
# ============================================================

@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    로그인 엔드포인트.
    사용자 인증 후 요청된 스코프를 포함한 JWT를 발급한다.

    테스트 계정:
    - admin / password123 (모든 스코프)
    - editor / password123 (읽기/쓰기)
    - viewer / password123 (읽기만)
    """
    user = USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자명 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 요청된 스코프 중 사용자가 가진 스코프만 부여
    granted_scopes = [
        s for s in form_data.scopes if s in user.scopes
    ]
    # 스코프를 지정하지 않으면 사용자의 모든 스코프 부여
    if not form_data.scopes:
        granted_scopes = user.scopes

    access_token = create_access_token(
        data={"sub": user.username},
        scopes=granted_scopes,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return Token(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scopes=granted_scopes,
    )


@app.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: UserInDB = Security(get_current_user, scopes=["users:read"]),
):
    """내 프로필 조회 (users:read 스코프 필요)"""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role.value,
        is_active=current_user.is_active,
        permissions=list(ROLE_PERMISSIONS.get(current_user.role, set())),
    )


@app.get("/users")
async def list_users(
    current_user: UserInDB = Security(get_current_user, scopes=["users:read"]),
):
    """사용자 목록 조회 (users:read 스코프 필요)"""
    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "role": u.role.value,
            }
            for u in USERS_DB.values()
        ],
        "요청자": current_user.username,
    }


@app.post("/users")
async def create_user(
    current_user: UserInDB = Security(
        get_current_user, scopes=["users:create"]
    ),
):
    """사용자 생성 (users:create 스코프 필요)"""
    return {
        "message": "사용자 생성 성공 (시뮬레이션)",
        "created_by": current_user.username,
    }


@app.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserInDB = Depends(
        require_permission(Permission.USERS_DELETE)
    ),
):
    """
    사용자 삭제 (RBAC: USERS_DELETE 권한 필요).
    ADMIN 또는 SUPER_ADMIN 역할만 가능하다.
    """
    return {
        "message": f"사용자 {user_id} 삭제 성공 (시뮬레이션)",
        "deleted_by": current_user.username,
        "role": current_user.role.value,
    }


@app.get("/admin/dashboard")
async def admin_dashboard(
    admin_user: UserInDB = Depends(require_role(Role.ADMIN, Role.SUPER_ADMIN)),
):
    """관리자 대시보드 (ADMIN 이상 역할 필요)"""
    return {
        "dashboard": "관리자 전용 대시보드",
        "admin": admin_user.username,
        "role": admin_user.role.value,
        "통계": {
            "총_사용자": len(USERS_DB),
            "활성_사용자": sum(1 for u in USERS_DB.values() if u.is_active),
        },
    }


@app.get("/admin/settings")
async def admin_settings(
    current_user: UserInDB = Depends(
        require_permission(Permission.ADMIN_SETTINGS)
    ),
):
    """
    관리자 설정 (ADMIN_SETTINGS 권한 필요).
    SUPER_ADMIN만 접근 가능하다.
    """
    return {
        "settings": {
            "유지보수_모드": False,
            "최대_동시접속": 1000,
            "로그_레벨": "INFO",
        },
        "변경자": current_user.username,
    }


@app.get("/permissions/check")
async def check_permissions(
    current_user: UserInDB = Depends(get_current_active_user),
):
    """현재 사용자의 역할과 권한을 확인"""
    user_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
    all_permissions = {p.value for p in Permission}

    return {
        "사용자": current_user.username,
        "역할": current_user.role.value,
        "보유_권한": sorted(user_permissions),
        "미보유_권한": sorted(all_permissions - user_permissions),
        "OAuth2_스코프": current_user.scopes,
    }


@app.get("/")
async def root():
    return {
        "message": "OAuth2 스코프와 RBAC 예제",
        "사용법": {
            "1. 로그인": "POST /token (form data: username, password, scope)",
            "2. 토큰 사용": "Authorization: Bearer <token>",
        },
        "테스트_계정": {
            "admin": "password123 (모든 권한)",
            "editor": "password123 (읽기/쓰기)",
            "viewer": "password123 (읽기 전용)",
        },
    }


if __name__ == "__main__":
    import uvicorn

    print("OAuth2 스코프와 RBAC 서버를 시작합니다...")
    print("API 문서: http://localhost:8000/docs")
    print("\n1. POST /token 으로 로그인 (admin/password123)")
    print("2. 발급받은 토큰으로 각 엔드포인트 접근")
    uvicorn.run(app, host="0.0.0.0", port=8000)
