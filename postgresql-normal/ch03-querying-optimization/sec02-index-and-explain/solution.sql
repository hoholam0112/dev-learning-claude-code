DROP TABLE IF EXISTS events;

CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  payload TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO events (user_id, payload)
SELECT (random() * 100)::int + 1, md5(g::text)
FROM generate_series(1, 10000) AS g;

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM events WHERE user_id = 42;

CREATE INDEX idx_events_user_id ON events(user_id);

EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM events WHERE user_id = 42;
