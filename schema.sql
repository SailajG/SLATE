CREATE TABLE user (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  profile_pic TEXT NOT NULL
);

CREATE TABLE user_schedule (
  user_id TEXT NOT NULL,
  day_date TEXT NOT NULL,
  time TEXT NOT NULL,
  PRIMARY KEY (user_id, day_date, time)
);

CREATE TABLE friend_list (
  user_id TEXT NOT NULL,
  friend_id TEXT NOT NULL,
  user_name TEXT NOT NULL,
  friend_name TEXT NOT NULL,
  PRIMARY KEY (user_id, friend_id)
);
