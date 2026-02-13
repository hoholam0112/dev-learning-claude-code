DROP TABLE IF EXISTS sample_data;

CREATE TABLE sample_data (
  id BIGSERIAL PRIMARY KEY,
  value TEXT NOT NULL
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_readonly') THEN
    CREATE ROLE app_readonly NOLOGIN;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_readwrite') THEN
    CREATE ROLE app_readwrite NOLOGIN;
  END IF;
END $$;

GRANT SELECT ON sample_data TO app_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON sample_data TO app_readwrite;
