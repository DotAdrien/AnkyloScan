-- Création de la base de données 🛡️
CREATE DATABASE IF NOT EXISTS ankyloscan;
USE ankyloscan;

-- Table Users 👤
CREATE TABLE IF NOT EXISTS Users (
    id_users INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL,
    Role VARCHAR(50)
);

-- Table Scan 🔍
CREATE TABLE IF NOT EXISTS Scan (
    id_scan INT AUTO_INCREMENT PRIMARY KEY,
    Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Device 💻
CREATE TABLE IF NOT EXISTS Device (
    id_relation INT AUTO_INCREMENT PRIMARY KEY,
    Mac VARCHAR(17),
    Ip VARCHAR(45),
    Name VARCHAR(255),
    id_scan INT,
    FOREIGN KEY (id_scan) REFERENCES Scan(id_scan) ON DELETE CASCADE
);

-- Table Port 🔌
CREATE TABLE IF NOT EXISTS Port (
    id_port INT AUTO_INCREMENT PRIMARY KEY,
    Service VARCHAR(100),
    id_relation INT,
    FOREIGN KEY (id_relation) REFERENCES Device(id_relation) ON DELETE CASCADE
);

INSERT INTO Users (Name, Email, Password, Role) 
VALUES ('admin', 'admin@gmail.com', 'admin', 'admin');