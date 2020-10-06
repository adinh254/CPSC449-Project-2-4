-- user schema

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
);

DROP TABLE IF EXISTS user_relations;
CREATE TABLE user_relations (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	follower INTEGER NOT NULL,
	following INTEGER NOT NULL,
	UNIQUE(follower, following)
);

DROP TABLE IF EXISTS timeline;
CREATE TABLE timeline(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	time_stamp TIMESTAMP NOT NULL,
        tweet TEXT NOT NULL	
);

INSERT INTO user(username, email, password) VALUES('maui-mac','maui_mac123@gmail.com','password1');
INSERT INTO user(username, email, password) VALUES('jim','jimmy@gmail.com','pass2');
INSERT INTO user(username, email, password) VALUES('andrew','A23@gmail.com','passw3');
INSERT INTO user(username, email, password) VALUES('bobby_hill','bob_the_builder@gmail.com','pas4');


COMMIT;
