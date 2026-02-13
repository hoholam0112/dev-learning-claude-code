DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE posts (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  title VARCHAR(200) NOT NULL,
  body TEXT NOT NULL
);

INSERT INTO users (email) VALUES ('user1@test.com');
INSERT INTO posts (user_id, title, body) VALUES (1, 'hello', 'first post');
