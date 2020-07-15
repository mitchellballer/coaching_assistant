DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS activity;

CREATE TABLE athlete (
  athlete_id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE activity (
  id INTEGER PRIMARY KEY,
  athlete_id INTEGER NOT NULL,
  start_date TIMESTAMP NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  FOREIGN KEY (athlete_id) REFERENCES user (athlete_id)
);