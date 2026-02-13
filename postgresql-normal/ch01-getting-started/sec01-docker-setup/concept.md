# sec01 Docker Setup

## 학습 목표
- Docker로 PostgreSQL 인스턴스를 띄울 수 있다.
- `psql`로 컨테이너 DB에 접속할 수 있다.
- 기본 점검 쿼리로 상태를 확인할 수 있다.

## 핵심 개념
- 컨테이너는 로컬 환경 차이를 줄여준다.
- 개발용 DB는 재현 가능한 설정이 중요하다.
- `SELECT version();`, `\l`, `\dt`는 기본 진단 명령이다.
