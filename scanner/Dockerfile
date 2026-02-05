# scanner/Dockerfile
FROM python:3.9-slim

# Installation de nmap et des dépendances système 🔍
RUN apt-get update && apt-get install -y nmap && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python 🐍
# On réutilise mysql-connector-python pour parler à la DB
RUN pip install --no-cache-dir mysql-connector-python

# Copie du code du scanner
COPY . .

# Création du dossier pour les fichiers output
RUN mkdir -p /app/outputs

# Le scanner n'a pas besoin de rester allumé, il est appelé par l'API
# Mais on peut mettre une commande par défaut pour test
CMD ["python", "main.py"]