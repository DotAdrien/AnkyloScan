FROM tobix/pywine:3.11

# On installe FastAPI pour le conteneur Linux 🐧
RUN apt-get update && apt-get install -y python3-pip
# Installation de FastAPI pour le conteneur Linux 🐧
RUN pip3 install --break-system-packages fastapi uvicorn

# Installation de PyInstaller et requests pour Windows via Wine 🪟
RUN wine pip install --break-system-packages pyinstaller requests

WORKDIR /app
COPY compiler_api.py .

CMD ["python3", "-m", "uvicorn", "compiler_api:app", "--host", "0.0.0.0", "--port", "8002"]