# sec02 Role Security Pooling

## 학습 목표
- 최소 권한 원칙으로 role/user를 설계할 수 있다.
- 애플리케이션 연결 계정과 마이그레이션 계정을 분리할 수 있다.

## 핵심 개념
- superuser 사용 최소화
- 애플리케이션은 필요한 스키마 권한만 부여
- 운영 환경에서는 연결 풀링(pgbouncer) 고려
