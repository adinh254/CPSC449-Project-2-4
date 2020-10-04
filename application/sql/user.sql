-- user schema

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    UNIQUE(username,email)
);

INSERT INTO user(username, email, password) VALUES('maui-mac','maui_mac123@gmail.com','password1');
INSERT INTO user(username, email, password) VALUES('jim','jimmy@gmail.com','pass2');
INSERT INTO user(username, email, password) VALUES('andrew','A23@gmail.com','passw3');
INSERT INTO user(username, email, password) VALUES('bobby_hill','bob_the_builder@gmail.com','pas4');
COMMIT;
