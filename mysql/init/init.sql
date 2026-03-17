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
    file_path VARCHAR(255) NOT NULL,
    status INT DEFAULT 0
);

-- Table SystemLogs pour tes remontées de logs AD 🛡️
CREATE TABLE IF NOT EXISTS SystemLogs (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    event_id INT,
    source VARCHAR(255),
    message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Agents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table Vuln pour les résultats détaillés des scans 😱
CREATE TABLE IF NOT EXISTS Vuln (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_scan INT NOT NULL,
    hosts VARCHAR(255),
    text TEXT,
    FOREIGN KEY (id_scan) REFERENCES Scan(id_scan) ON DELETE CASCADE
);