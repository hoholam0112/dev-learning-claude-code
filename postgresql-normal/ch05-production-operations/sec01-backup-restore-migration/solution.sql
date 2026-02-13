DROP TABLE IF EXISTS backup_lab;

CREATE TABLE backup_lab (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL
);

INSERT INTO backup_lab (name) VALUES ('a'), ('b'), ('c');

-- backup
-- docker exec pg-learning pg_dump -U postgres -d postgres -t backup_lab > backup_lab.sql
-- restore
-- cat backup_lab.sql | docker exec -i pg-learning psql -U postgres -d postgres
