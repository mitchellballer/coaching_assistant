DROP TABLE IF EXISTS athlete;
DROP TABLE IF EXISTS activity;
DROP TABLE IF EXISTS coach;

CREATE TABLE athlete (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  connected_to_strava BOOLEAN,
  strava_bearer_token TEXT,
  strava_bearer_token_expiration INTEGER,
  strava_refresh_token TEXT,
  strava_athlete_id INTEGER,
  coach_id INTEGER
);

CREATE TABLE coach (
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
  FOREIGN KEY (athlete_id) REFERENCES athlete (id)
);