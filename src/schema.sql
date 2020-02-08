DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
	userid INTEGER PRIMARY KEY AUTOINCREMENT,
	firstname VARCHAR(20),
	lastname VARCHAR(20),
	email VARCHAR(50) NOT NULL,
	password VARCHAR(50) NOT NULL,
	username VARCHAR(50) NOT NULL
);

DROP TABLE IF EXISTS Issues;
CREATE TABLE Issues (
	issueid INTEGER VARCHAR(20) PRIMARY KEY,
	name VARCHAR(255),
	issuenumber VARCHAR(20)
);

DROP TABLE IF EXISTS Volumes;
CREATE TABLE Volumes (
	volumeid INTEGER VARCHAR(20) PRIMARY KEY,
	name VARCHAR(255),
	volumenumber VARCHAR(20)
);

DROP TABLE IF EXISTS IssuesInVolumes;
CREATE TABLE IssuesInVolumes (
	volumeid VARCHAR(20) NOT NULL,
	issueid VARCHAR(20) NOT NULL,
	FOREIGN KEY (volumeid) REFERENCES Volumes(volumeid),
	FOREIGN KEY (issueid) REFERENCES Issues(issueid),
	UNIQUE (volumeid, issueid)
);

DROP TABLE IF EXISTS UsersIssues;
CREATE TABLE UsersIssues (
	username VARCHAR(50) NOT NULL,
	issueid VARCHAR(20) NOT NULL,
	FOREIGN KEY (username) REFERENCES Users(username),
	FOREIGN KEY (issueid) REFERENCES Issues(issueid),
	UNIQUE (username, issueid)
);

DROP TABLE IF EXISTS UsersVolumes;
CREATE TABLE UsersVolumes (
	username VARCHAR(50) NOT NULL,
	volumeid VARCHAR(20) NOT NULL,
	FOREIGN KEY (username) REFERENCES Users(username),
	FOREIGN KEY (volumeid) REFERENCES Volumes(volumeid),
	UNIQUE (username, volumeid)
);
