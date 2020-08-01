DROP TABLE IF EXISTS athlete;
DROP TABLE IF EXISTS activity;

CREATE TABLE athlete (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE activity (
  id INTEGER PRIMARY KEY,
  start_date TIMESTAMP NOT NULL,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  distance DOUBLE,
  duration DOUBLE,
  athlete_id INTEGER NOT NULL,
  FOREIGN KEY(athlete_id) REFERENCES athlete(id)
);