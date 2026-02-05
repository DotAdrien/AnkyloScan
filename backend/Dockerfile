# Image légère
FROM python:3.9-slim
RUN apt-get update && apt-get install -y nmap
WORKDIR /app

# Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# On expose le port 8001
EXPOSE 8001

# Lancement de l'API sur le port 8001 avec reload
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
