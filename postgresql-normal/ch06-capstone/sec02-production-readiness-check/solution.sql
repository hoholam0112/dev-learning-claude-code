-- 1) 활성 연결 수
SELECT count(*) AS active_connections
FROM pg_stat_activity
WHERE state = 'active';

-- 2) autovacuum 통계
SELECT relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;

-- 3) 인덱스 사용률
SELECT relname, seq_scan, idx_scan
FROM pg_stat_user_tables
ORDER BY seq_scan DESC
LIMIT 10;
