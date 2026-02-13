DROP TABLE IF EXISTS events;

-- TODO 1: events(id, user_id, payload, created_at) 테이블 생성
-- TODO 2: generate_series로 10000건 데이터 삽입
-- TODO 3: 인덱스 생성 전 EXPLAIN (ANALYZE, BUFFERS) 실행
-- TODO 4: CREATE INDEX idx_events_user_id ON events(user_id)
-- TODO 5: 인덱스 생성 후 다시 EXPLAIN (ANALYZE, BUFFERS) 실행
