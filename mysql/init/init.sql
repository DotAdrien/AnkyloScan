-- Création de la base de données
CREATE DATABASE IF NOT EXISTS ankyloscan;
USE ankyloscan;

-- Table pour stocker les résultats des scans
CREATE TABLE IF NOT EXISTS scans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip VARCHAR(45) NOT NULL,
    hostname VARCHAR(255) DEFAULT 'Inconnu',
    status VARCHAR(50),
    open_ports TEXT, -- Liste des ports (ex: "80, 443")
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
