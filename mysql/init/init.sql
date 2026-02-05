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
    Time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Type VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL
);


INSERT INTO Users (Name, Email, Password, Role) 
VALUES ('admin', 'admin@gmail.com', 'admin', 'admin');