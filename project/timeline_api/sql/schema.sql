-- timeline schema

PRAGMA foreign_keys=ON;
DROP TABLE IF EXISTS timeline;
CREATE TABLE timeline(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	user_id INTEGER NOT NULL,
        description TEXT NOT NULL,	
	FOREIGN KEY(user_id) REFERENCES user(id)
);
