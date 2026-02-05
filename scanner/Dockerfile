FROM python:3.9-slim
RUN apt-get update && apt-get install -y nmap # 🔍 Important pour le scanner

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Installe aussi les dépendances du scanner si elles diffèrent
RUN pip install --no-cache-dir mysql-connector-python 

COPY . .
# Le dossier /scanner sera monté via le docker-compose
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]