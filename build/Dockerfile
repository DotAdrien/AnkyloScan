FROM python:3.9-slim

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y wine wine32 gcc-mingw-w64 python3-pip && \
    pip install pyinstaller requests
WORKDIR /app

# Installe les dépendances nécessaires à l'agent
RUN pip install requests
CMD ["pyinstaller", "--onefile", "--noconsole", "ad.py"]