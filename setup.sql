-- create a new database and use the database
CREATE DATABASE IF NOT EXISTS omigra;
USE omigra;

-- create table
CREATE TABLE IF NOT EXISTS accounts (
	id INT AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(100) NOT NULL UNIQUE,
	password VARCHAR(100) NOT NULL,
	email VARCHAR(100) NOT NULL
);
INSERT INTO accounts (username, password, email) VALUES
('testuser', 'testpassword', 'testuser@example.com'),
